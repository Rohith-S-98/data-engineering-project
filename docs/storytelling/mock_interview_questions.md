# Mock Interview Questions

## Project Explanation

1. Explain your Data Engineering project in two minutes.
2. Why did you choose medallion architecture?
3. What happens when data quality rules fail?
4. How does quarantine work in your project?
5. How does the watermark framework prevent duplicate processing?
6. Why did you add SCD Type 2 history tracking?
7. What is the difference between audit logging and observability?
8. How do alerting and SLA monitoring improve pipeline reliability?
9. What does the retry and replay framework solve?
10. How does your project move from local implementation toward cloud deployment readiness?

## PySpark / Databricks / Lakehouse

1. What is the difference between Bronze, Silver, and Gold layers?
2. How would this project run differently in Databricks compared to local Python?
3. What is Delta Lake and why is it useful?
4. Explain merge/upsert in a lakehouse table.
5. What is partition pruning?
6. Why can too many partition columns hurt performance?
7. What are clustering columns used for?
8. How would you monitor a Databricks job failure?

## Azure / ADF / CI-CD

1. Where would Azure Data Factory fit in this project?
2. What does a Databricks activity do in ADF?
3. How would secrets be handled in Azure or Databricks?
4. What quality gates would you add to CI/CD?
5. Why should live API calls not be mandatory in CI?
6. What should happen before a release tag is created?

## Apexon / IQVIA Mapping

1. How does your project connect to IQVIA-style MDM work?
2. Where do OneKey or Veeva-style sources fit in the flow?
3. How would you explain landing to staging to canonical transformation?
4. How would failed records be handled in a real client pipeline?
5. How would you explain Reltio-style JSON payload generation?

## Behavioral / Storytelling

1. Tell me about a time you improved a pipeline.
2. Tell me about a production issue and how you debugged it.
3. Tell me about a time you learned a new tool quickly.
4. Tell me about a time you handled unclear requirements.
5. Tell me about a time you used documentation to improve handover.

## Short Answer Template

Use this pattern:

```text
Context: What problem existed?
Action: What did I build or improve?
Result: What became safer, clearer, faster, or more reliable?
Production angle: How would this scale in a real project?
```
