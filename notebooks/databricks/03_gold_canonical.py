# Databricks notebook source
# MAGIC %md
# MAGIC # Gold Canonical Transformation
# MAGIC
# MAGIC This notebook transforms valid Silver records into a canonical customer model and exports JSON payload.

# COMMAND ----------

from scripts.pyspark_gold_canonical import run_pyspark_gold_canonical

# COMMAND ----------

run_pyspark_gold_canonical()