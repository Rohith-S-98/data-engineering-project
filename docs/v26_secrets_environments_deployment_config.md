# V26.0.0 - Secrets, Environments, and Deployment Configuration

V26 adds a production-style environment and credential-reference layer to the data engineering project.

## Goal

The goal is to keep real credentials out of Git while still documenting how dev, test, and prod deployments would reference credentials safely.

## Added Files

```text
.env.example
config/environments/dev.json
config/environments/test.json
config/environments/prod.json
scripts/validate_secret_environment_config.py
tests/test_v26_secret_environment_config.py
docs/v26_secrets_environments_deployment_config.md
```

## Environment Strategy

```text
dev  - local development style configuration
test - local test validation configuration
prod - production-style deployment configuration that requires approval
```

## Credential Reference Strategy

Real credentials are not stored in repository files. Environment configs store references only:

```text
ENV:CUSTOMER_SOURCE_API_CREDENTIAL
ENV:CUSTOMER_DATABASE_CREDENTIAL
ENV:DATABRICKS_WORKSPACE_CREDENTIAL
ENV:AZURE_STORAGE_CREDENTIAL
```

This simulates the same production pattern used with environment variables, Databricks secret scopes, Azure Key Vault, or CI/CD deployment variables.

## Validation

Run:

```bash
python -m scripts.validate_secret_environment_config
python -m unittest tests.test_v26_secret_environment_config
```

The validator checks:

```text
required dev/test/prod environment files exist
required environment config keys are present
credential references use ENV:NAME format
prod requires approval
.env.example uses placeholder values
potential hardcoded credential literals are rejected in config-style files
```

## Interview Explanation

I added a secret-safe environment configuration layer to my data engineering project. Instead of committing real credentials, the project stores only environment-specific metadata and credential references. The validator ensures dev, test, and prod configs exist, credential fields use ENV references, production requires approval, and hardcoded credential-like values are not committed. This mirrors how production data pipelines use environment variables, secret scopes, Azure Key Vault, and CI/CD variables.

## Apexon / IQVIA Mapping

In an IQVIA-style Databricks and Azure project, source credentials, storage credentials, Databricks workspace credentials, and API credentials should not be hardcoded in notebooks or configs. They should be referenced through secret scopes, Key Vault, or deployment variables. V26 documents and validates that pattern locally.
