## Cách mình triển khai Kubernetes 

Phần đầu mình sẽ giải thích K8s hoạt động như thế nào, các khái niệm cốt lõi và vì sao cần chúng. Sau đó, cách mình áp dụng trực tiếp vào dự án này: mục tiêu deploy, các thành phần dùng, cách cấu hình, và các lệnh triển khai sau khi CI đã push image lên Docker Hub.

### 1) Kubernetes là gì và hoạt động ra sao?

- Kubernetes (K8s) là hệ điều hành của hạ tầng container:
  - Ta cung cấp container image để K8s chạy, scale, tự hồi phục, rolling update, rollback…
  - K8s trừu tượng hóa hạ tầng (máy ảo/máy vật lý) thành một cụm (cluster) thống nhất.

- Cấu trúc tổng quan:
  - Cluster: một cụm K8s gồm nhiều Node.
  - Node: máy (VM/physical) chạy container. Mỗi Node có:
    - kubelet: agent nói chuyện với Control Plane và quản lý Pod trên Node.
    - kube-proxy/CNI: điều phối mạng cho Pod/Service.
  - Control Plane: bộ não điều phối (API server, scheduler, controller manager, etcd).

- Đơn vị triển khai cơ bản:
  - Container: tiến trình ứng dụng đóng gói trong image (ví dụ image FastAPI).
  - Pod: 1 hoặc nhiều container chạy cùng nhau (chia network namespace). Pod là đơn vị nhỏ nhất K8s quản lý.
  - ReplicaSet: đảm bảo có N bản sao Pod luôn chạy.
  - Deployment: lớp cao hơn quản lý ReplicaSet, cung cấp rolling update/rollback.
  - Service: cấp địa chỉ IP ổn định để truy cập Pod (vì Pod có thể thay đổi IP). Các loại phổ biến:
    - ClusterIP: truy cập nội bộ cluster.
    - NodePort: mở cổng trên Node để truy cập từ ngoài (phù hợp minikube/dev).
    - LoadBalancer: nhờ cloud provider cấp IP public.
  - Ingress: định tuyến HTTP/HTTPS từ tên miền vào Service (cần Ingress Controller).
  - Namespace: không gian tên để nhóm/tách tài nguyên.
  - ConfigMap/Secret: cấu hình ứng dụng, Secret cho thông tin nhạy cảm.
  - Job/CronJob: chạy task một lần (migration) hoặc theo lịch.
  - Probes (liveness/readiness): K8s gọi các endpoint như `/health` để biết Pod còn sống và đã sẵn sàng nhận traffic chưa.
  - Resource requests/limits: khai báo nhu cầu CPU/RAM và giới hạn sử dụng.
  - HPA (Horizontal Pod Autoscaler): tự tăng/giảm số Pod theo tải (ví dụ CPU > 70%).
  - PDB (PodDisruptionBudget): đảm bảo tối thiểu X Pod luôn chạy trong quá trình bảo trì.

- Luồng triển khai điển hình:
  1. Build image → Push registry (CI làm giúp, mình viết CI trong /.github/workflow/ci.yml).
  2. Apply manifest K8s (ConfigMap/Secret/Job/Deployment/Service…).
  3. Job migration chạy trước để cập nhật schema DB.
  4. Deployment rollout với probes giám sát, rolling update an toàn.
  5. Service/Ingress cung cấp địa chỉ truy cập.

### 2) Áp dụng vào dự án này

Mục tiêu: triển khai Backend FastAPI lên K8s, dùng DB (PostgreSQL cloud) và Redis (cloud). Cho phép health-check, rolling update, và có bước migrate DB an toàn trước khi app nhận traffic.

Các thành phần trong thư mục `k8s/`:
- `configmap.yaml` (ConfigMap): cấu hình không nhạy cảm như `ENVIRONMENT`, `LOG_LEVEL`, `OPENAI_BASE_URL`, `CORS_ORIGINS`.

- `job-migrate.yaml` (Job): chạy `alembic upgrade head` bằng chính image của ứng dụng để cập nhật schema.
- `deploy.yaml` (Deployment + Service):
  - Deployment chạy 2 replica, có `readinessProbe`/`livenessProbe` tới `/health`.
  - Service kiểu `NodePort` (cổng 30080) để test nhanh trên minikube. Trên cloud có thể đổi sang `LoadBalancer`.

Vì sao dùng những thành phần này?
- Job migration: đảm bảo DB luôn ở đúng phiên bản trước khi app chạy, tránh lỗi "relation does not exist".
- Deployment: cho phép rolling update/rollback, tự hồi phục Pod lỗi.
- Probes: đảm bảo chỉ route traffic tới Pod sẵn sàng.
- ConfigMap/Secret: tách cấu hình khỏi image, thay đổi cấu hình không cần build lại.
- Service: cung cấp endpoint ổn định để truy cập app.

### 3) Yêu cầu trước khi deploy

- Có cluster K8s sẵn (minikube hoặc cloud) và `kubectl` trỏ đúng cluster.
- CI đã build/push image đa kiến trúc (linux/amd64, linux/arm64) lên Docker Hub.
- Có file `.env` tại root repo chứa biến môi trường cần thiết (không commit). Xem `.env.example` để biết những thành phần cần thiết

### 4) Các bước triển khai sau khi CI đã push image

Các lệnh dưới đây tận dụng `.env` (grep từ chính shell, không gõ tay từng biến):

1) Nạp `.env` vào shell
```bash
set -a && . ./.env && set +a
: "${K8S_NAMESPACE:?missing}"; : "${IMAGE:?missing}"
```

2) Tạo namespace (nếu chưa có)
```bash
kubectl get ns "$K8S_NAMESPACE" >/dev/null 2>&1 || kubectl create ns "$K8S_NAMESPACE"
```

3) Áp dụng ConfigMap
```bash
kubectl -n "$K8S_NAMESPACE" apply -f k8s/configmap.yaml
# Hoặc patch CORS_ORIGINS trực tiếp từ .env
kubectl -n "$K8S_NAMESPACE" patch configmap eq-backend-config --type merge -p "{\"data\":{\"CORS_ORIGINS\":\"${CORS_ORIGINS}\"}}"
```

4) Tạo/Update Secret từ biến môi trường hiện tại (nguồn là `.env`)
```bash
kubectl -n "$K8S_NAMESPACE" create secret generic eq-backend-secrets \
  --from-literal=DATABASE_URL="$DATABASE_URL" \
  --from-literal=REDIS_URL="$REDIS_URL" \
  --from-literal=SECRET_KEY="$SECRET_KEY" \
  --from-literal=ALGORITHM="$ALGORITHM" \
  --from-literal=ACCESS_TOKEN_EXPIRE_MINUTES="$ACCESS_TOKEN_EXPIRE_MINUTES" \
  --from-literal=GOOGLE_CLIENT_ID="$GOOGLE_CLIENT_ID" \
  --from-literal=GOOGLE_CLIENT_SECRET="$GOOGLE_CLIENT_SECRET" \
  --from-literal=OPENAI_API_KEY="$OPENAI_API_KEY" \
  --dry-run=client -o yaml | kubectl apply -f -
```

5) Chạy Job migration và chờ hoàn tất
```bash
kubectl -n "$K8S_NAMESPACE" delete job eq-backend-migrate --ignore-not-found --wait=true
sed "s#REPLACE_IMG#${IMAGE}#g" k8s/job-migrate.yaml | kubectl -n "$K8S_NAMESPACE" apply -f -
kubectl -n "$K8S_NAMESPACE" wait --for=condition=complete job/eq-backend-migrate --timeout=300s
kubectl -n "$K8S_NAMESPACE" logs job/eq-backend-migrate --all-containers
```

6) Deploy/Update ứng dụng và Service
```bash
sed "s#REPLACE_IMG#${IMAGE}#g" k8s/deploy.yaml | kubectl -n "$K8S_NAMESPACE" apply -f -
kubectl -n "$K8S_NAMESPACE" rollout status deploy/eq-backend
```

7) Lấy URL và smoke test
- Minikube:
```bash
minikube service eq-backend -n "$K8S_NAMESPACE" --url
# Hoặc trực tiếp NodePort 30080 (định nghĩa trong deploy.yaml)
curl http://$(minikube ip):30080/health
curl http://$(minikube ip):30080/health/db
curl http://$(minikube ip):30080/api/v1/topics/
```
- Cloud (LoadBalancer):
```bash
# Đổi Service type thành LoadBalancer trong deploy.yaml trước khi apply
kubectl -n "$K8S_NAMESPACE" get svc eq-backend -w
# Dùng EXTERNAL-IP khi xuất hiện
```

### 5) Những lỗi mình đã gặp phải và đã sửa

- ImagePullBackOff trên ARM
  - Đảm bảo CI build multi-arch (linux/amd64, linux/arm64/v8).

- InvalidImageName / còn thấy chuỗi `REPLACE_IMG` trong pod
  - Kiểm tra biến `IMAGE` đã được nạp từ `.env` và lệnh `sed` đã thay thế trước khi `kubectl apply`.

- `SettingsError` khi parse `CORS_ORIGINS`
  - Gán giá trị JSON hợp lệ: `[]` hoặc `["https://your-frontend"]`.

- Kết nối DB bị từ chối / sai host
  - Trong K8s, không dùng `localhost`. Hãy dùng hostname của managed DB, thêm `?sslmode=require` nếu nhà cung cấp yêu cầu.

- Alembic báo "ok" nhưng không thấy bảng
  - DB có thể đã bị `alembic_version` nhưng chưa có schema. Chạy lại: `alembic stamp base && alembic upgrade head` (điều chỉnh Job nếu muốn cố định).

- 307 khi gọi `/api/...`
  - Một số endpoint yêu cầu dấu `/` ở cuối (ví dụ `/api/v1/topics/`).

### 6) Gợi ý CI cho image

- Nếu bạn dùng Mac như mình, thì cài docker Buildx + QEMU để build multi-arch.
- Tag `latest` hoặc `sha-<commit>` (mình nghĩ nên deploy bằng `sha-<commit>` để rollout/rollback cho chính xác)



