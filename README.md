# Drupal SRE Actions

A curated collection of production-grade GitHub Composite Actions and Reusable Workflows tailored for Drupal platform engineering, Site Reliability Engineering (SRE), continuous patching, and automated quality gates.

---

## Architectural Overview

This repository provides reusable components adhering to the following SRE operational pillars:

1. **Continuous Automated Patching:** Safe, unattended core and module updates with changelog generation and PR automation.
2. **Shift-Left Quality & Linting:** Strict adherence to Drupal and DrupalPractice standards, Twig syntax checks, and YAML validation.
3. **Drift Detection:** Verification of configuration synchronization between active database states and version-controlled sync directories (`config/sync`).
4. **Security & Vulnerability Gates:** Automated CVE advisory scanning (`composer audit`) and zero-tolerance secret leakage detection.
5. **Runtime Observability & Smoke Testing:** Synthetic availability probes enforcing TTFB latency SLOs and TLS certificate expiry thresholds.

```text
drupal-sre-actions/
├── actions/
│   ├── drupal-composer-update/      # Composer update automation & PR generation
│   ├── drupal-code-standards/       # PHPCS (Drupal/DrupalPractice), Twig & YAML
│   ├── drupal-static-analysis/      # PHPStan with phpstan-drupal extensions
│   ├── drupal-config-drift/         # Configuration sync & database drift checks
│   ├── drupal-db-sanity-check/      # Ephemeral update & schema verification
│   ├── composer-security-audit/     # Advisory check (CVE) & abandoned package audit
│   ├── synthetic-smoke-test/        # SRE latency SLO & healthcheck synthetic probe
│   └── secret-scan/                 # Gitleaks / regex secret scanner
└── .github/
    └── workflows/
        ├── reusable-drupal-ci.yml     # Complete CI pipeline
        ├── reusable-drupal-update.yml # Scheduled/dispatched update pipeline
        └── reusable-smoke-test.yml    # Post-deployment synthetic validation
```

---

## Actions Catalog

### 1. `drupal-composer-update`

Automates updates for Drupal core and contributed modules, produces a formatted Markdown comparison table of updated packages, and opens/updates a Pull Request.

#### Inputs

| Name | Description | Default | Required |
|------|-------------|---------|----------|
| `working-directory` | Path to directory containing `composer.json` | `.` | No |
| `php-version` | PHP runtime version | `8.2` | No |
| `packages` | Specific packages to update (e.g. `drupal/core-*`) | `""` (all) | No |
| `dependency-args` | Flags passed to `composer update` | `--with-all-dependencies` | No |
| `create-pr` | Whether to automatically create/update a PR | `true` | No |
| `branch-name` | Target branch name | `chore/drupal-automated-updates` | No |
| `base-branch` | Base branch for the PR | `main` | No |
| `pr-title` | Pull request title | `chore(deps): automated Drupal updates` | No |
| `github-token` | GitHub token with write permissions | `${{ github.token }}` | No |

#### Outputs

| Name | Description |
|------|-------------|
| `has-updates` | `true` if `composer.lock` was modified |
| `updated-packages` | Markdown table of updated packages and version diffs |
| `pr-url` | URL of the created or updated PR |

---

### 2. `drupal-code-standards`

Enforces coding standards across custom modules and themes using PHP_CodeSniffer with Drupal Coder standards, Twig syntax checks, and YAML validation.

#### Inputs

| Name | Description | Default | Required |
|------|-------------|---------|----------|
| `working-directory` | Working directory path | `.` | No |
| `php-version` | PHP runtime version | `8.2` | No |
| `paths` | Directories or files to analyze | `web/modules/custom web/themes/custom` | No |
| `standard` | PHPCS standard ruleset | `Drupal,DrupalPractice` | No |
| `extensions` | Comma-separated file extensions to validate | `php,module,theme,install,inc,profile,test` | No |
| `fail-on-warning` | Whether warnings fail the job | `false` | No |
| `check-twig` | Validate Twig template syntax | `true` | No |
| `check-yaml` | Validate YAML structure in target paths | `true` | No |

---

### 3. `drupal-config-drift`

Detects configuration drift between the active Drupal database state and the export directory (`config/sync`), preventing accidental configuration loss during deployments.

#### Inputs

| Name | Description | Default | Required |
|------|-------------|---------|----------|
| `working-directory` | Path to Drupal root directory | `.` | No |
| `php-version` | PHP runtime version | `8.2` | No |
| `drush-binary` | Path to Drush executable | `vendor/bin/drush` | No |
| `sync-directory` | Path to sync directory | `config/sync` | No |
| `fail-on-drift` | Fail execution if discrepancies exist | `true` | No |

#### Outputs

| Name | Description |
|------|-------------|
| `drift-detected` | `true` if discrepancies exist |
| `diff-summary` | Summary of drifted configuration files |

---

### 4. `drupal-static-analysis`

Executes PHPStan configured with `mglaman/phpstan-drupal` to identify deprecated API calls, invalid function arguments, and breaking typing bugs prior to merges.

#### Inputs

| Name | Description | Default | Required |
|------|-------------|---------|----------|
| `working-directory` | Working directory path | `.` | No |
| `php-version` | PHP runtime version | `8.2` | No |
| `paths` | Paths to analyze | `web/modules/custom` | No |
| `level` | PHPStan rule level (0 to 9) | `1` | No |
| `memory-limit` | Memory limit | `1G` | No |
| `config-file` | Optional path to `phpstan.neon` | `""` | No |

---

### 5. `drupal-db-sanity-check`

Runs dry-run simulations of pending database migrations (`drush updatedb`) and checks entity schema definitions for mismatches.

#### Inputs

| Name | Description | Default | Required |
|------|-------------|---------|----------|
| `working-directory` | Drupal root directory | `.` | No |
| `drush-binary` | Path to Drush binary | `vendor/bin/drush` | No |
| `fail-on-pending-updates`| Fail if pending `hook_update_N` exist | `false` | No |
| `fail-on-schema-mismatch`| Fail if entity definitions mismatch | `true` | No |

---

### 6. `composer-security-audit`

Scans dependencies against official security advisory databases (CVE feeds and Drupal Security Advisories).

#### Inputs

| Name | Description | Default | Required |
|------|-------------|---------|----------|
| `working-directory` | Path containing `composer.json` | `.` | No |
| `fail-on-vulnerability` | Fail job on active CVE detection | `true` | No |
| `abandoned` | Policy for abandoned packages (`fail`, `report`, `ignore`) | `report` | No |

---

### 7. `synthetic-smoke-test`

Performs SRE synthetic probes evaluating HTTP response status, TTFB latency SLOs, TLS certificate expiration dates, and payload assertion.

#### Inputs

| Name | Description | Default | Required |
|------|-------------|---------|----------|
| `target-url` | Endpoint URL to probe | - | Yes |
| `expected-status` | Expected HTTP status code | `200` | No |
| `max-ttfb-ms` | Maximum acceptable TTFB in ms | `800` | No |
| `ssl-min-days` | Minimum remaining days for TLS validity | `14` | No |
| `json-field-check` | Python expression verifying payload | `""` | No |
| `retries` | Number of probe retries | `3` | No |

---

### 8. `secret-scan`

Scans repositories for leaked API keys, database credentials, salts, and private keys using Gitleaks and fallback regex patterns.

---

## Reusable Workflows Usage

### Pull Request CI Workflow

Add the following to `.github/workflows/ci.yml` in any Drupal project repository:

```yaml
name: CI Pipeline

on:
  pull_request:
    branches: [main, develop]

jobs:
  drupal-ci:
    uses: zero-sh/drupal-sre-actions/.github/workflows/reusable-drupal-ci.yml@main
    with:
      php-version: '8.3'
      paths: 'web/modules/custom web/themes/custom'
      enable-phpstan: true
      enable-audit: true
      enable-secret-scan: true
      enable-config-drift: true
```

### Scheduled Dependency Updates

Add the following to `.github/workflows/scheduled-updates.yml`:

```yaml
name: Automated Drupal Updates

on:
  schedule:
    - cron: '0 6 * * 1' # Runs every Monday at 06:00 UTC
  workflow_dispatch:

jobs:
  updates:
    uses: zero-sh/drupal-sre-actions/.github/workflows/reusable-drupal-update.yml@main
    with:
      php-version: '8.3'
      packages: 'drupal/core-*'
    secrets:
      token: ${{ secrets.PAT_GITHUB_TOKEN }}
```

### Post-Deployment Smoke Test

Add the following to `.github/workflows/post-deploy.yml`:

```yaml
name: Post-Deployment Smoke Verification

on:
  deployment_status:
    states: [success]

jobs:
  health-check:
    uses: zero-sh/drupal-sre-actions/.github/workflows/reusable-smoke-test.yml@main
    with:
      target-url: 'https://drupal.example.com/healthz'
      expected-status: '200'
      max-ttfb-ms: '500'
      ssl-min-days: '21'
      json-field-check: 'status == "healthy"'
```

---

## License

This project is licensed under the terms of the [MIT License](LICENSE).
