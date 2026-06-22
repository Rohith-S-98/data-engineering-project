# V12.0.0 - SCD Type 2 / Historical Dimension Tracking

## Goal

V12 adds historical customer attribute tracking on top of the existing Delta Lake and Delta MERGE foundation.

Before V12, the pipeline maintained only the latest current customer state in Bronze, Silver, and Gold Delta tables.

After V12, the pipeline also maintains a Customer History SCD Type 2 Delta table.

## New Table

```text
data/gold/customer_history