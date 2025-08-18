## EQ Backend

Backend dịch vụ EmoStagram (FastAPI + SQLAlchemy), có healthcheck, metrics, migrations Alembic, CI/CD GitHub Actions và triển khai mẫu trên GKE.


### Stack chính
- FastAPI, Uvicorn
- SQLAlchemy 2.x, Alembic
- PostgreSQL, Redis
- Pytest (unit/integration), Coverage
- Prometheus metrics (prometheus-fastapi-instrumentator)
- GitHub Actions (CI, CD → GKE Autopilot qua OIDC/WIF)

### Cấu trúc thư mục (rút gọn)
```
eq_test_backend/
  app/                  # mã nguồn FastAPI
  k8s/                  # manifest K8s (Kustomize)
  .github/workflows/    # CI/CD pipelines
  Dockerfile
  requirements.txt      # phục vụ dev/CI dạng pip
  pyproject.toml        # poetry (Dockerfile dùng poetry để build image)
```

### Tính năng chính
- REST API v1 (xem `app/api/v1/`), tài liệu OpenAPI tại `/docs`.
- Health check: `/health` (đính kèm metadata lần triển khai gần nhất)
- Prometheus metrics: `/metrics`
- CORS cấu hình qua `CORS_ORIGINS` (JSON list)
- Job migrate trước khi rollout (K8s hook dạng Job)

---

## Chạy cục bộ

### 1) Chuẩn bị
- Python 3.12
- PostgreSQL cục bộ hoặc Docker (gợi ý dùng compose kèm repo)

```
# chạy Postgres + Prometheus + Grafana (tùy chọn)
docker compose -f docker-compose.yml up -d postgres

python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Tạo file `.env` (không commit) đặt tại `eq_test_backend/`:
```
DATABASE_URL=postgresql://eq_user:eq_pass@localhost:5432/eq_test
REDIS_URL=redis://localhost:6379/0

SECRET_KEY=change-me
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

GOOGLE_CLIENT_ID=xxx
GOOGLE_CLIENT_SECRET=xxx

OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=https://api.openai.com/v1
```

Lưu ý: CORS cấu hình trong `k8s/configmap.yaml` khi chạy K8s; với local dev có thể để mặc định.

### 2) Migrate + seed
```
alembic upgrade head
python -c "from app.seed_data import seed; seed()"
```

### 3) Chạy API
```
uvicorn app.main:app --host 0.0.0.0 --port 5001 --reload
```

Mở:
- OpenAPI: http://localhost:5001/docs
- Health:  http://localhost:5001/health
- Metrics: http://localhost:5001/metrics

---

## Test
```
pytest -q
```
CI sẽ chạy đầy đủ test và báo coverage (ngưỡng 40% trong pipeline mẫu).

---

## CI/CD (GitHub Actions)

### CI (build + test + image)
Workflow `CI Pipeline`:
- Chạy unit/integration tests, security checks
- Build/push image đa kiến trúc (amd64, arm64) lên Docker Hub
- Tag: `latest` (nhánh main) và `sha-<commit>` (mọi commit) – CD dùng tag `sha-<commit>` để rollout chính xác

### CD (triển khai GKE Autopilot)
Workflow `CD - Deploy to GKE`:
- Trigger bởi `workflow_run` của CI (khi CI xanh) hoặc chạy tay (workflow_dispatch)
- OIDC + Workload Identity Federation (không cần lưu kubeconfig/JSON key)
- Các bước chính:
  1) Apply `k8s/configmap.yaml`
  2) Ghi metadata triển khai (DEPLOYED_AT/SHA/IMAGE/BY) vào ConfigMap
  3) Tạo/Update `Secret eq-backend-secrets` từ GitHub Secrets
  4) Apply `k8s/` (Kustomize) → chạy Job migrate (Alembic) → rollout Deployment
  5) Gửi Discord webhook trạng thái (thành công/thất bại, kèm EXTERNAL-IP)

Yêu cầu Secrets (GitHub → Settings → Secrets and variables → Actions):
- `DOCKERHUB_USERNAME`, `DOCKERHUB_TOKEN`
- `K8S_NAMESPACE` (vd: `eq-backend`)
- `DATABASE_URL`, `REDIS_URL`, `SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `OPENAI_API_KEY`, `CORS_ORIGINS`
- `GCP_PROJECT`, `GKE_CLUSTER`, `GKE_LOCATION`
- `WORKLOAD_IDENTITY_PROVIDER` (dạng `projects/<PROJECT_NUMBER>/locations/global/workloadIdentityPools/github-pool/providers/github-provider`)
- `GCP_SA_EMAIL` (vd: `eq-backend-deployer@<PROJECT_ID>.iam.gserviceaccount.com`)
- (Tùy chọn) `DISCORD_WEBHOOK`

Chi tiết cơ chế OIDC/WIF và cách tạo provider/SA: xem mục CD trong `deployment.md`.

---

## Triển khai trên Kubernetes (Kustomize)

Thư mục `k8s/` đã bao gồm:
- `configmap.yaml`: ENV non-secret (như `ENVIRONMENT`, `LOG_LEVEL`, `OPENAI_BASE_URL`, `CORS_ORIGINS`)
- `job-migrate.yaml`: Job chạy `alembic upgrade head` trước khi rollout
- `deploy.yaml`: Deployment + Service (Service = `LoadBalancer` cho GKE)
- `kustomization.yaml`: gom resource + set image tag

Triển khai thủ công (khi đã có secret `eq-backend-secrets`):
```
kubectl create ns eq-backend 2>/dev/null || true
kubectl -n eq-backend apply -f k8s/configmap.yaml
kubectl -n eq-backend create secret generic eq-backend-secrets \
  --from-env-file=.env.secrets \
  --dry-run=client -o yaml | kubectl apply -f -

kubectl apply -k k8s/
kubectl -n eq-backend wait --for=condition=complete job/eq-backend-migrate --timeout=300s
kubectl -n eq-backend rollout status deploy/eq-backend
kubectl -n eq-backend get svc eq-backend -w
```

> Gợi ý tiết kiệm chi phí khi dùng GKE Autopilot: xóa Service `LoadBalancer` và scale `replicas=0` khi không dùng. Bật lại chỉ cần `kubectl apply -k k8s/`.

---

## Cấu hình & biến môi trường

Biến bắt buộc (qua `.env` khi dev hoặc Secret/ConfigMap khi K8s):
- `DATABASE_URL`: chuỗi kết nối PostgreSQL (managed DB khuyến nghị, thêm `?sslmode=require` nếu cần)
- `REDIS_URL`: chuỗi kết nối Redis Cloud
- `SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`
- `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`
- `OPENAI_API_KEY`, `OPENAI_BASE_URL`
- `CORS_ORIGINS` (JSON list, ví dụ `[]` hoặc `["https://your-frontend"]`) – không dùng `"*"` khi có `allow_credentials=True`

Metadata triển khai (được CD ghi vào ConfigMap để hiển thị ở `/health`):
- `DEPLOYED_AT`, `DEPLOY_SHA`, `DEPLOY_IMAGE`, `DEPLOY_BY`

---

## Troubleshooting nhanh
- Pod kẹt `ImagePullBackOff`: kiểm tra image tag `sha-<commit>` đã được CI push
- Job migrate timeout: kiểm tra `DATABASE_URL`/firewall/SSL; `CORS_ORIGINS` phải là JSON list
- CD OIDC lỗi `unauthorized_client`: kiểm tra `attributeCondition` của WIF provider (`attribute.repository=='<OWNER>/<REPO>'`) và binding SA

---

## License
MIT 

