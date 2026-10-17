# Drupal SRE Actions

A curated collection of production-grade GitHub Composite Actions and Reusable Workflows tailored for Drupal platform engineering, Site Reliability Engineering (SRE), continuous patching, test execution by directory, and automated quality gates.

---

## Architectural Overview

This repository provides reusable components adhering to the following SRE operational pillars:

1. **Continuous Automated Patching:** Safe, unattended core and module updates with changelog generation and PR automation.
2. **Pending Updates & Security Status:** Proactive detection of outdated releases, security advisories, and pending database updates (`hook_update_N`).
3. **Directory-Based Automated Testing:** Targeted PHPUnit test executions (Unit, Kernel, Functional) directed at any module or folder with ephemeral SQLite configuration.
4. **Shift-Left Quality & Linting:** Strict adherence to Drupal and DrupalPractice standards, Twig syntax checks, and YAML validation.
5. **Drift Detection:** Verification of configuration synchronization between active database states and version-controlled sync directories (`config/sync`).
6. **Disaster Recovery & Backup Validation:** Automated restoration of SQL dumps into ephemeral databases measuring RTO thresholds and schema health.
7. **Security & Vulnerability Gates:** Automated CVE advisory scanning (`composer audit`) and zero-tolerance secret leakage detection.
8. **Runtime Observability & Smoke Testing:** Synthetic availability probes enforcing TTFB latency SLOs and TLS certificate expiry thresholds.

```text
drupal-sre-actions/
├── actions/
│   ├── drupal-composer-update/         # Composer update automation & PR generation
│   ├── drupal-update-status-check/     # Detects pending core/contrib & DB updates
│   ├── drupal-test-runner/             # Runs PHPUnit targeted at a specific folder
│   ├── drupal-backup-verification/     # Ephemeral SQL dump restoration & RTO check
│   ├── drupal-code-standards/          # PHPCS (Drupal/DrupalPractice), Twig & YAML
│   ├── drupal-static-analysis/         # PHPStan with phpstan-drupal extensions
│   ├── drupal-config-drift/            # Configuration sync & database drift checks
│   ├── drupal-db-sanity-check/         # Ephemeral update & schema verification
│   ├── composer-security-audit/        # Advisory check (CVE) & abandoned package audit
│   ├── synthetic-smoke-test/           # SRE latency SLO & healthcheck synthetic probe
│   ├── secret-scan/                    # Gitleaks / regex secret scanner
│   └── semantic-release/               # SemVer bump, git tagging & GitHub Release
├── tests/
│   └── fixtures/
│       └── sample_module/              # Mock Drupal module with Unit tests & templates
└── .github/
    └── workflows/
        ├── test-actions.yml            # Self-testing CI executing actions on fixtures
        ├── release.yml                 # Semantic release workflow
        ├── reusable-drupal-ci.yml      # Complete CI pipeline
        ├── reusable-drupal-update.yml  # Scheduled/dispatched update pipeline
        ├── reusable-smoke-test.yml     # Post-deployment synthetic validation
        └── reusable-semantic-release.yml # Reusable tagging and release workflow
```

---

## Actions Catalog

### 1. `drupal-update-status-check`

Checks for pending Drupal core/contrib releases, available security updates, and unapplied database updates (`hook_update_N` / `post_update`).

#### Inputs

| Name | Description | Default | Required |
|------|-------------|---------|----------|
| `working-directory` | Path containing `composer.json` | `.` | No |
| `php-version` | PHP runtime version | `8.2` | No |
| `drush-binary` | Path to Drush executable | `vendor/bin/drush` | No |
| `fail-on-security-updates` | Fail step if security updates exist | `true` | No |
| `fail-on-pending-db-updates` | Fail step if unapplied DB updates exist | `false` | No |

#### Outputs

| Name | Description |
|------|-------------|
| `security-updates-count` | Number of pending security updates |
| `outdated-packages-count` | Number of outdated direct Drupal packages |
| `pending-db-updates-count` | Number of pending database migrations |
| `has-pending-updates` | `true` if any package or schema updates are pending |

---

### 2. `drupal-test-runner`

Executes PHPUnit tests targeting any arbitrary folder or custom module path. Automatically handles in-memory SQLite database setups for Kernel and Functional tests without requiring an external MySQL container.

#### Inputs

| Name | Description | Default | Required |
|------|-------------|---------|----------|
| `test-directory` | Directory path containing tests to execute | - | Yes |
| `working-directory` | Project root directory | `.` | No |
| `php-version` | PHP runtime version | `8.2` | No |
| `phpunit-binary` | Path to PHPUnit executable | `vendor/bin/phpunit` | No |
| `phpunit-config` | Custom `phpunit.xml` path (auto-generated if omitted) | `""` | No |
| `test-filter` | Filter pattern for tests | `""` | No |
| `db-url` | Database connection string | `sqlite://localhost//tmp/drupal_test.sqlite` | No |
| `generate-junit` | Generate JUnit XML report | `true` | No |

#### Outputs

| Name | Description |
|------|-------------|
| `total-tests` | Total number of executed tests |
| `total-assertions` | Total number of assertions verified |
| `failures-count` | Number of failed tests |
| `errors-count` | Number of runtime test errors |
| `status` | `success` or `failure` |

---

### 3. `drupal-backup-verification`

SRE disaster recovery verification: loads an SQL backup dump into an ephemeral database, calculates restoration duration against Recovery Time Objectives (RTO), and verifies schema integrity.

#### Inputs

| Name | Description | Default | Required |
|------|-------------|---------|----------|
| `backup-file` | Path to SQL dump (`.sql`, `.sql.gz`, `.sql.bz2`) | - | Yes |
| `db-host` | Database host | `127.0.0.1` | No |
| `db-port` | Database port | `3306` | No |
| `db-user` | Database user | `root` | No |
| `db-password` | Database password | `root` | No |
| `db-name` | Target test database name | `drupal_restore_test` | No |
| `max-restore-time-seconds` | Maximum allowed restore duration (RTO limit) | `300` | No |

#### Outputs

| Name | Description |
|------|-------------|
| `restore-time-seconds` | Elapsed restoration time in seconds |
| `tables-count` | Count of restored database tables |
| `status` | `success` or `failure` |

---

### 4. `drupal-composer-update`

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

---

### 5. `drupal-code-standards`

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

### 6. `drupal-config-drift`

Detects configuration drift between the active Drupal database state and the export directory (`config/sync`), preventing accidental configuration loss during deployments.

#### Inputs

| Name | Description | Default | Required |
|------|-------------|---------|----------|
| `working-directory` | Path to Drupal root directory | `.` | No |
| `php-version` | PHP runtime version | `8.2` | No |
| `drush-binary` | Path to Drush executable | `vendor/bin/drush` | No |
| `sync-directory` | Path to sync directory | `config/sync` | No |
| `fail-on-drift` | Fail execution if discrepancies exist | `true` | No |

---

### 7. `drupal-static-analysis`

Executes PHPStan configured with `mglaman/phpstan-drupal` to identify deprecated API calls, invalid function arguments, and breaking typing bugs prior to merges.

---

### 8. `drupal-db-sanity-check`

Runs dry-run simulations of pending database migrations (`drush updatedb`) and checks entity schema definitions for mismatches.

---

### 9. `composer-security-audit`

Scans dependencies against official security advisory databases (CVE feeds and Drupal Security Advisories).

---

### 10. `synthetic-smoke-test`

Performs SRE synthetic probes evaluating HTTP response status, TTFB latency SLOs, TLS certificate expiration dates, and payload assertion.

---

### 11. `secret-scan`

Scans repositories for leaked API keys, database credentials, salts, and private keys using Gitleaks and fallback regex patterns.

---

### 12. `semantic-release`

Calculates semantic versions from Conventional Commits, generates structured Markdown release notes grouped by type, pushes annotated git tags, maintains floating major tags (e.g. `v1`), and publishes GitHub Releases via GitHub CLI.

#### Inputs

| Name | Description | Default | Required |
|------|-------------|---------|----------|
| `bump` | Bump strategy: `auto` (Conventional Commits), `patch`, `minor`, `major`, or explicit semver | `auto` | No |
| `tag-prefix` | Prefix for git tags | `v` | No |
| `initial-version` | Initial version when no tags exist | `1.0.0` | No |
| `update-major-tag` | Whether to maintain a floating major tag (e.g. `v1`) | `true` | No |
| `create-release` | Whether to publish a GitHub Release | `true` | No |
| `draft` | Whether the created GitHub Release is marked as draft | `false` | No |
| `prerelease` | Whether the created GitHub Release is marked as prerelease | `false` | No |
| `github-token` | GitHub token with `contents: write` permission | `${{ github.token }}` | No |

#### Outputs

| Name | Description |
|------|-------------|
| `version` | Calculated version string (e.g. `1.1.0`) |
| `tag` | Full tag name (e.g. `v1.1.0`) |
| `major-tag` | Floating major tag name (e.g. `v1`) |
| `previous-version` | Previous version string |
| `previous-tag` | Previous git tag name |
| `bump-type` | Applied bump type (`major`, `minor`, `patch`, `initial`, `explicit`, `none`) |
| `has-bump` | `true` if a new version was bumped |
| `release-url` | URL of published GitHub Release |
| `changelog-path` | Filepath to generated Markdown changelog |

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
    uses: zer0sh/drupal-sre-actions/.github/workflows/reusable-drupal-ci.yml@main
    with:
      php-version: '8.3'
      paths: 'web/modules/custom web/themes/custom'
      enable-phpstan: true
      enable-audit: true
      enable-secret-scan: true
      enable-config-drift: true
```

### Targeted Folder Test Runner Workflow

Execute unit/functional tests on a specific custom module:

```yaml
name: Module Tests

on: [push, pull_request]

jobs:
  test-module:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run Tests in Specific Folder
        uses: zer0sh/drupal-sre-actions/actions/drupal-test-runner@main
        with:
          php-version: '8.3'
          test-directory: 'web/modules/custom/my_module/tests'
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
    uses: zer0sh/drupal-sre-actions/.github/workflows/reusable-drupal-update.yml@main
    with:
      php-version: '8.3'
      packages: 'drupal/core-*'
    secrets:
      token: ${{ secrets.PAT_GITHUB_TOKEN }}
```

### Automated Semantic Release & Tagging

Add the following to `.github/workflows/release.yml` to automatically release on push or manual trigger:

```yaml
name: Release

on:
  push:
    branches: [main]
  workflow_dispatch:
    inputs:
      bump:
        description: 'Version bump strategy (auto, patch, minor, major, or version)'
        required: false
        default: 'auto'
        type: string

jobs:
  release:
    uses: zer0sh/drupal-sre-actions/.github/workflows/reusable-semantic-release.yml@main
    with:
      bump: ${{ inputs.bump || 'auto' }}
      update-major-tag: true
      create-release: true
    secrets:
      token: ${{ secrets.GITHUB_TOKEN }}
```

---

## License

This project is licensed under the terms of the [MIT License](LICENSE).

