# Architecture Overview

## Project Summary

This project simulates an enterprise-style customer data engineering pipeline.

It has two implementations:

1. Python-based config-driven DQ pipeline
2. PySpark-based medallion architecture pipeline

The PySpark version follows a Bronze, Silver, and Gold layer design similar to Databricks workloads.

---

## High-Level Flow

```text
Raw Customer CSV
        ↓
Bronze Layer
        ↓
Silver DQ Layer
        ↓
Gold Canonical Layer
        ↓
Reltio-Style JSON Payload

---

## Production-Style Configuration Layer

The pipeline uses a centralized JSON config file to manage environment-specific paths and runtime settings.

Config file:

```text
config/pipeline/local_config.json
```

Config loader:

```text
scripts/pipeline_config.py
```

This allows the pipeline to avoid hardcoded paths inside Bronze, Silver, and Gold scripts.

The same pipeline logic can be reused across different environments by changing the config file.

Example environments:

```text
local
dev
qa
prod
```

This improves maintainability and makes the project closer to enterprise data engineering practices.
