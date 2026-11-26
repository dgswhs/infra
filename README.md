# infra

Infrastructure of the dgswhs organization (Daegu Software Meister High School): the `dgsw.kr` domain and the services behind it.

```
terraform/<provider>/<account>/<region|global>/<component>/
terraform/backend.hcl
kubernetes/apps/<app>/          (once there is a cluster)
```

| Unit | Manages |
|---|---|
| `terraform/cloudflare/dgsw/global/bootstrap/` | R2 bucket `dgsw-tfstate`, which holds every state |
| `terraform/cloudflare/dgsw/global/dgsw-kr/` | Zone `dgsw.kr` and its records |

Pull requests plan every changed Terraform unit. Merging to `main` applies them.

## Bootstrap

`terraform/cloudflare/dgsw/global/bootstrap/` creates the state bucket, so its first apply runs locally. Use a Cloudflare API token with Workers R2 Storage Edit on the DGSW account, and delete it afterwards.

```sh
cd terraform/cloudflare/dgsw/global/bootstrap
mv backend.tf backend.tf.off
export CLOUDFLARE_API_TOKEN=...
terraform init && terraform apply
mv backend.tf.off backend.tf
export AWS_ACCESS_KEY_ID=... AWS_SECRET_ACCESS_KEY=...   # R2 token with Object Read & Write on dgsw-tfstate
terraform init -migrate-state -backend-config=../../../../backend.hcl -backend-config=key=cloudflare/dgsw/global/bootstrap/terraform.tfstate
rm terraform.tfstate terraform.tfstate.backup
```

## Credentials

Create these in the Cloudflare dashboard and store them in GitHub. Repository secrets are for pull requests; the `main` environment overrides them for applies. Limit the `main` environment to the `main` branch.

| Secret | Repository (plan) | `main` environment (apply) |
|---|---|---|
| `CLOUDFLARE_API_TOKEN` | `dgsw-infra-plan`: Zone Read, DNS Read, Workers R2 Storage Read | `dgsw-infra-apply`: the same permissions with Edit |
| `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY` | R2 token `dgsw-tfstate-plan`: Object Read, bucket `dgsw-tfstate` | R2 token `dgsw-tfstate-apply`: Object Read & Write, bucket `dgsw-tfstate` |

Plans run with `-lock=false`, so the read-only R2 token is enough. Applies lock the state with an R2 conditional write (`use_lockfile`).
