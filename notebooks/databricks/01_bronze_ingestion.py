# Databricks notebook source
# MAGIC %md
# MAGIC # Bronze Ingestion
# MAGIC
# MAGIC This notebook represents the Bronze ingestion layer.
# MAGIC It reads raw customer data and writes it into the Bronze layer.

# COMMAND ----------

from scripts.pyspark_bronze_ingestion import run_bronze_ingestion

# COMMAND ----------

run_bronze_ingestion()