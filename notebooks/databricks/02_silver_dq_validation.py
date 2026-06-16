# Databricks notebook source
# MAGIC %md
# MAGIC # Silver DQ Validation
# MAGIC
# MAGIC This notebook applies config-driven data quality rules and separates valid and quarantined records.

# COMMAND ----------

from scripts.pyspark_silver_dq import run_pyspark_silver_dq

# COMMAND ----------

run_pyspark_silver_dq()