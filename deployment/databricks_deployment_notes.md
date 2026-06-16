# Databricks Deployment Notes

## Purpose

This document describes how this project can be adapted for Databricks.

---

## Suggested Databricks Workflow

A Databricks job can be created with three tasks:

1. Bronze Ingestion
2. Silver DQ Validation
3. Gold Canonical Transformation

---

## Task Order

```text
01_bronze_ingestion
        ↓
02_silver_dq_validation
        ↓
03_gold_canonical