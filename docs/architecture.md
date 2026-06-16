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