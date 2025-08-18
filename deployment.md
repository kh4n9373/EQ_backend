## Cách mình triển khai project bày trên Kubernetes 

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
- CI đã build/push image lên Docker Hub.
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

4) Tạo/Update Secret từ file `.env.secrets` (gọn, không gõ từng biến)
```bash
# .env.secrets chỉ chứa các dòng key=value nhạy cảm, ví dụ:
# DATABASE_URL=postgresql://<user>:<pass>@<host>:5432/<db>?sslmode=require
# REDIS_URL=redis://:<password>@<redis-host>:6379/0
# SECRET_KEY=...
# ALGORITHM=HS256
# ACCESS_TOKEN_EXPIRE_MINUTES=30
# GOOGLE_CLIENT_ID=...
# GOOGLE_CLIENT_SECRET=...
# OPENAI_API_KEY=...

kubectl -n "$K8S_NAMESPACE" create secret generic eq-backend-secrets \
  --from-env-file=.env.secrets \
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




### 7) Triển khai lên GKE (Google Kubernetes Engine)

Phần này tóm tắt toàn bộ quy trình tự tay triển khai Backend lên GKE Autopilot từ con số 0 đến chạy được, và cách “tắt/giảm phí” khi không dùng.

1) Chuẩn bị tài khoản và công cụ
- Tạo tài khoản Google Cloud và kích hoạt Free Trial (thường được $300).
- Cài gcloud SDK và kubectl trên máy local.
- Tạo Project (trong dự án này thì là `emostagram`). Lấy `PROJECT_ID`.

2) Đăng nhập và chọn project
```bash
gcloud auth login
gcloud config set project <PROJECT_ID>
```

3) Bật các API cần thiết
```bash
gcloud services enable container.googleapis.com iamcredentials.googleapis.com sts.googleapis.com
```

4) Tạo Autopilot cluster (hoặc tạo bằng UI trên google console)
```bash
gcloud container clusters create-auto autopilot-cluster-1 \
  --region australia-southeast1 \
  --project <PROJECT_ID>
```

5) Kết nối kubectl tới cluster
```bash
gcloud container clusters get-credentials autopilot-cluster-1 \
  --region australia-southeast1 --project <PROJECT_ID>
kubectl get ns
```

6) Chuẩn bị manifests của dự án (đã có sẵn trong `eq_test_backend/k8s/`)
- `k8s/kustomization.yaml` gộp `configmap.yaml`, `job-migrate.yaml`, `deploy.yaml`, set `namespace: eq-backend` và `images.newTag`.
- `k8s/deploy.yaml` đã để Service kiểu `LoadBalancer` cho GKE.

7) Tạo namespace và Secret, dùng secret từ `.env`)
```bash
kubectl create ns eq-backend 2>/dev/null || true
kubectl -n eq-backend apply -f eq_test_backend/k8s/configmap.yaml
kubectl -n eq-backend create secret generic eq-backend-secrets \
  --from-env-file=.env \
  --dry-run=client -o yaml | kubectl apply -f -
```

8) Deploy (migrate trước rồi app)
```bash
kubectl apply -k eq_test_backend/k8s
kubectl -n eq-backend wait --for=condition=complete job/eq-backend-migrate --timeout=300s || \
kubectl -n eq-backend logs job/eq-backend-migrate --all-containers
kubectl -n eq-backend rollout status deploy/eq-backend
kubectl -n eq-backend get svc eq-backend -w    # lấy EXTERNAL-IP
```

9) Smoke test
```bash
curl http://<EXTERNAL-IP>/health
curl http://<EXTERNAL-IP>/health/db
curl http://<EXTERNAL-IP>/api/v1/topics/
```

10) Giảm phí/tắt khi không dùng
- Nếu còn dùng lại sớm (khuyên dùng):
```bash
# Xóa Service LoadBalancer để ngừng phí LB
kubectl -n eq-backend delete svc eq-backend
# Dừng app (replicas=0)
kubectl -n eq-backend scale deploy/eq-backend --replicas=0
```
- Nếu muốn 0 chi phí tuyệt đối: xóa cluster :v
```bash
gcloud container clusters delete autopilot-cluster-1 \
  --region australia-southeast1 --project <PROJECT_ID> --quiet
```

11) Bật lại 
```bash
# Nếu chỉ scale=0 hoặc đã xóa Service:
kubectl apply -k eq_test_backend/k8s
kubectl -n eq-backend wait --for=condition=complete job/eq-backend-migrate --timeout=300s || \
kubectl -n eq-backend logs job/eq-backend-migrate --all-containers
kubectl -n eq-backend rollout status deploy/eq-backend
kubectl -n eq-backend get svc eq-backend -w
```

Ghi chú:
- Autopilot có thể mất vài phút để cấp node lần đầu; đặt `resources.requests/limits` hợp lý giúp scheduler dễ sắp chỗ.
- Hãy đổi `images.newTag` trong `k8s/kustomization.yaml` sang tag build của CI (ví dụ `sha-<commit>`) để rollout/rollback chính xác.

### 8) Chi tiết về file cd.yml

Mục tiêu: Khi push lên `main`, GitHub Actions sẽ tự động deploy phiên bản mới lên GKE bằng cơ chế OIDC (không cần lưu kubeconfig/JSON key trong repo).

1) Cơ chế tổng quan
- GitHub Actions (runner) dùng OpenID Connect (OIDC) phát hành một token danh tính ngắn hạn.
- Google Cloud xác thực token OIDC này qua Workload Identity Federation (WIF) và cho phép runner “mạo danh” (impersonate) một Service Account (SA) trong GCP.
- Sau khi xác thực, workflow gọi `get-gke-credentials` để có kubecontext → chạy `kubectl` apply Kustomize (`k8s/`), chạy Job migrate, set image, scale replicas.

2) Các secret cần cấu hình trong GitHub (Settings → Secrets and variables → Actions)
- `GCP_PROJECT`: Project ID GCP (ví dụ `emostagram`).
- `GKE_CLUSTER`: Tên cluster GKE (ví dụ `autopilot-cluster-1`).
- `GKE_LOCATION`: Vùng của cluster (ví dụ `australia-southeast1`).
- `WORKLOAD_IDENTITY_PROVIDER`: Đường dẫn đầy đủ của WIF provider, dạng `projects/<PROJECT_NUMBER>/locations/global/workloadIdentityPools/github-pool/providers/github-provider`.
- `GCP_SA_EMAIL`: Email của Service Account triển khai, ví dụ `eq-backend-deployer@<PROJECT_ID>.iam.gserviceaccount.com`.
- `K8S_NAMESPACE`: Namespace đích (ví dụ `eq-backend`).
- `DOCKERHUB_USERNAME`: Tài khoản Docker Hub để tạo tag image.
- App secrets: `CORS_ORIGINS` (JSON list), `DATABASE_URL`, `REDIS_URL`, `SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `OPENAI_API_KEY`.

3) OIDC là gì? Workload Identity Federation là gì?
- OIDC: chuẩn xác thực mở, cho phép GitHub phát hành token danh tính cho workflow run. Token này dùng để xin quyền truy cập trong GCP mà không cần lưu key lâu dài.
- WIF: cơ chế của GCP để “liên kết” danh tính bên ngoài (GitHub OIDC) với một Service Account trong GCP. Nhờ đó, workflow có thể impersonate SA mà không cần key.

4) Tạo WIF + Provider + Service Account 
```bash
export PROJECT=<PROJECT_ID>
gcloud config set project "$PROJECT"

gcloud iam workload-identity-pools create github-pool \
  --project="$PROJECT" --location=global --display-name="GitHub OIDC Pool"
gcloud iam workload-identity-pools providers create-oidc github-provider \
  --project="$PROJECT" --location=global --workload-identity-pool=github-pool \
  --display-name="GitHub Provider" \
  --issuer-uri="https://token.actions.githubusercontent.com" \
  --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository" \
  --attribute-condition="attribute.repository=='<OWNER>/<REPO>'"

# Tạo SA để deploy
gcloud iam service-accounts create eq-backend-deployer \
  --project="$PROJECT" --display-name="Eq backend deployer"

# Gán quyền tối thiểu (triển khai k8s)
gcloud projects add-iam-policy-binding "$PROJECT" \
  --member="serviceAccount:eq-backend-deployer@${PROJECT}.iam.gserviceaccount.com" \
  --role="roles/container.admin"

# Cho phép GitHub OIDC mạo danh SA
POOL_NAME=$(gcloud iam workload-identity-pools describe github-pool --location=global --project="$PROJECT" --format='value(name)')
gcloud iam service-accounts add-iam-policy-binding "eq-backend-deployer@${PROJECT}.iam.gserviceaccount.com" \
  --project="$PROJECT" \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/${POOL_NAME}/attribute.repository/<OWNER>/<REPO>"

# Lấy PROJECT_NUMBER và in ra WORKLOAD_IDENTITY_PROVIDER
PROJ_NUM=$(gcloud projects describe "$PROJECT" --format='value(projectNumber)')
echo "WORKLOAD_IDENTITY_PROVIDER=projects/${PROJ_NUM}/locations/global/workloadIdentityPools/github-pool/providers/github-provider"
echo "GCP_SA_EMAIL=eq-backend-deployer@${PROJECT}.iam.gserviceaccount.com"
```

5) Lấy thông tin cluster
```bash
gcloud container clusters list --format='table(name,location,status)'
# GKE_CLUSTER, GKE_LOCATION
```

6) cd.yml làm gì khi chạy?
- Auth GCP qua OIDC → `get-gke-credentials` lấy kubecontext.
- Apply `k8s/configmap.yaml`.
- Tạo/cập nhật `Secret eq-backend-secrets` từ secrets ở GitHub.
- Apply `k8s/` (Kustomize), chạy Job migrate (đợi hoàn tất).
- Set image của Deployment sang tag build mới và scale `replicas=1`.
- In thông tin Service (LoadBalancer) để kiểm tra.
