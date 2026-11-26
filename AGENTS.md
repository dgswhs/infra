# infra

Terraform manages everything outside clusters. `kubernetes/` will hold everything inside clusters once there is one.

This repository is public. Account IDs, zone IDs and DNS records may appear in code; credentials never do.

## Layout
- `terraform/<provider>/<account>/<region|global>/<component>/` is one root module with one state.
- `<account>` is a human label for a Cloudflare account, `dgsw` for the DGSW account. Real account IDs live in the unit's code, never in paths.
- Environments are accounts or projects, never folders or workspaces. Use only the default workspace.
- Split a unit before it nears 100 resources, or when parts change at different rates.
- `terraform/modules/<name>/` only once a second unit needs the same code. Prefer a registry module over writing one.
- Folder names are lowercase words joined by `-`, like `dgsw-kr`.
- Globally unique names (buckets, apps, tokens) are `dgsw-<purpose>`.

## Terraform units
- Files: `backend.tf`, `terraform.tf`, `providers.tf`, `main.tf`, `variables.tf`, `outputs.tf`, `locals.tf`. Create only the ones the unit needs.
- `backend.tf` holds only an empty `backend "s3" {}` inside `terraform {}`. CI passes `terraform/backend.hcl` (the R2 bucket `dgsw-tfstate`) and the key from the unit path.
- `terraform.tf` pins `required_version` and every provider with `~>`.
- Commit `.terraform.lock.hcl` with hashes for both platforms: `terraform providers lock -platform=linux_amd64 -platform=darwin_arm64`.
- Use providers maintained by the service's own company. No providers written by third parties.
- Read another unit's values through `terraform_remote_state`, limited to its outputs. Write its `key` as a literal string; CI reads it to order units.
- Adopt existing resources with `import` blocks. Stop managing one without destroying it with a `removed` block. Delete either block in a follow-up pull request once applied.
- After an apply, the next plan must show no changes. If a provider keeps reporting a diff, fix the config or stop managing that resource.

## Providers and credentials
Credentials never go in code. CI gets them from repository secrets and the `main` environment; only a person can create them.

| Provider | Pull request (plan) | `main` (apply) |
|---|---|---|
| State (R2) | `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, Object Read | same names in the `main` environment, Object Read & Write |
| Cloudflare | `CLOUDFLARE_API_TOKEN`, read-only | `CLOUDFLARE_API_TOKEN` from the `main` environment, write |

- Apply jobs run in the `main` GitHub environment, which only the `main` branch can deploy to.
- Workflows from forks get no secrets. Keep the organization setting that requires approval before outside contributors' workflows run.
- A new provider needs its credentials wired into `.github/workflows/terraform.yml` as env vars, with a read-only credential for plans when the service offers one, and a row in the table above. Ask the user to create the credentials.

## Commands
- `mise install`
- `terraform fmt -recursive`
- In a unit: `terraform init -backend=false`, then `terraform validate`.
- `actionlint` after editing workflows.
- There are no cloud credentials locally. Verify a change by opening a pull request and reading each unit's plan in the CI logs.

## Code
- English only. No comments unless the code cannot say why; one line at most.
- Pin actions to a full commit SHA followed by `# <version>`. Renovate reads that comment.
- Names are lowercase snake_case. No resource named after its type, like `cloudflare_r2_bucket.bucket`.

## Commits and pull requests
- `type: description`, lowercase, no period. Types: feat, fix, chore, refactor, docs.
- One logical change per commit.
- `main` takes changes only through pull requests with a passing `terraform` check, merged by squash. The pull request title becomes the commit title, so it follows the same format.

## Never
- `terraform apply`, `destroy`, `import`, or `state` commands locally. Apply runs only from CI in the `main` environment. The one exception is the first apply of `terraform/cloudflare/dgsw/global/bootstrap/`, which creates the state bucket.
- Rename or move a unit folder without asking. Its state key moves with it.
- Rename the `terraform` job, or change its environment. The ruleset requires the check, and apply credentials live in that environment.
- Commit state, plans, `*.tfvars`, or credentials.
- Create cloud resources outside Terraform.
