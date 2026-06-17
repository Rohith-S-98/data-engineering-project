Watermark Flow
Raw input
↓
Read last committed watermark
↓
Filter records where created_date > last_watermark
↓
Write incremental records to Bronze
↓
Stage new watermark
↓
Run Silver DQ
↓
Run Gold Canonical
↓
Commit watermark only after pipeline success
Why Pending Watermark Is Needed
The watermark should not be committed immediately after Bronze.
If Bronze succeeds but Silver DQ fails, committing the watermark would cause failed records to be skipped in the next run.
Therefore, V9 stages the watermark first and commits it only after all pipeline stages complete successfully.
Watermark Store
Committed watermark file:
data/audit/watermark_store.json
Pending watermark file:
data/audit/pending_watermark_updates.json
Run Test
python -m tests.test_watermark_manager
Run Pipeline
python -m scripts.pyspark_pipeline_runner
Version
v9.0.0 - Incremental Load and Watermark Framework

---

# Step 9 — Update README

Add this section:

```markdown
## v9.0.0 - Incremental Load and Watermark Framework

V9 adds incremental data processing using a watermark column.

### Features

- Reads last committed watermark
- Filters only new records
- Stages pending watermark after Bronze
- Commits watermark only after full pipeline success
- Prevents data loss when DQ validation fails

### Main Files

```text
scripts/watermark_manager.py
tests/test_watermark_manager.py
docs/v9_incremental_load_watermark.md
Test
python -m tests.test_watermark_manager
Run Pipeline
python -m scripts.pyspark_pipeline_runner

---

# Step 10 — Commit and tag V9

After the test passes:

```bash
git status
git add .
git commit -m "v9.0.0 add incremental load and watermark framework"
git tag v9.0.0
git push origin main
git push origin v9.0.0
V9 completion checklist
Run:
python -m tests.test_watermark_manager
python -m scripts.pyspark_pipeline_runner
cat data/audit/pending_watermark_updates.json
cat data/audit/watermark_store.json
git tag
For your current dirty DQ data, pipeline may stop at Silver, but V9 is still working if:
Watermark staged
Watermark not committed because pipeline failed
For clean DQ data, V9 is fully complete if:
Watermark staged
Pipeline completed successfully
Watermark committed
v9.0.0 tag exists