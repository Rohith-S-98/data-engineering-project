from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path
from typing import Any, Callable

from scripts.exceptions import PipelineExecutionError
from scripts.job_control import (
    DEFAULT_JOB_RUN_LOG_FILE,
    DEFAULT_STEP_RUN_LOG_FILE,
    create_job_run,
    create_step_run,
    update_job_run,
    update_step_run,
)
from scripts.pipeline_config import load_pipeline_config

DEFAULT_JOB_CONFIG_PATH = "config/jobs/customer_medallion_job.json"


def load_job_config(job_config_path: str = DEFAULT_JOB_CONFIG_PATH) -> dict[str, Any]:
    path = Path(job_config_path)

    if not path.exists():
        raise FileNotFoundError(f"Job config file not found: {job_config_path}")

    with path.open(mode="r", encoding="utf-8") as file:
        job_config = json.load(file)

    required_keys = ["job_name", "environment", "steps"]

    missing_keys = [key for key in required_keys if key not in job_config]
    if missing_keys:
        raise ValueError(f"Missing required job config keys: {missing_keys}")

    if not isinstance(job_config["steps"], list) or not job_config["steps"]:
        raise ValueError("Job config must contain a non-empty steps list")

    for step in job_config["steps"]:
        required_step_keys = ["step_id", "step_name", "module", "function"]
        missing_step_keys = [
            key for key in required_step_keys if key not in step
        ]

        if missing_step_keys:
            raise ValueError(
                f"Missing required step config keys for step={step}: "
                f"{missing_step_keys}"
            )

    return job_config


def _import_step_function(module_name: str, function_name: str) -> Callable[..., Any]:
    module = importlib.import_module(module_name)

    if not hasattr(module, function_name):
        raise AttributeError(
            f"Function '{function_name}' not found in module '{module_name}'"
        )

    return getattr(module, function_name)


def _normalize_result_status(result: Any) -> str:
    if result is None:
        return "SUCCESS"

    return str(result).upper()


def _is_expected_status(
    raw_result: Any,
    normalized_result_status: str,
    expected_success_statuses: list[Any],
) -> bool:
    normalized_expected = []

    for status in expected_success_statuses:
        if status is None:
            normalized_expected.append("SUCCESS")
        else:
            normalized_expected.append(str(status).upper())

    if raw_result is None and None in expected_success_statuses:
        return True

    return normalized_result_status in normalized_expected


def _resolve_step_kwargs(
    step_config: dict[str, Any],
    pipeline_config: dict[str, Any],
) -> dict[str, Any]:
    kwargs = dict(step_config.get("kwargs", {}))

    kwargs_from_config = step_config.get("kwargs_from_config", {})

    for argument_name, config_key in kwargs_from_config.items():
        if config_key not in pipeline_config:
            raise KeyError(
                f"Pipeline config key '{config_key}' required for "
                f"step argument '{argument_name}' was not found"
            )

        kwargs[argument_name] = pipeline_config[config_key]

    return kwargs


def _sort_steps(steps: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(steps, key=lambda step: int(step["step_id"]))


def run_pipeline_orchestrator(
    job_config_path: str = DEFAULT_JOB_CONFIG_PATH,
    raise_on_failure: bool = True,
) -> str:
    job_config = load_job_config(job_config_path)
    pipeline_config = load_pipeline_config()

    job_name = job_config["job_name"]
    environment = job_config.get("environment", pipeline_config["environment"])
    job_run_log_file = job_config.get("job_run_log_file", DEFAULT_JOB_RUN_LOG_FILE)
    step_run_log_file = job_config.get("step_run_log_file", DEFAULT_STEP_RUN_LOG_FILE)
    continue_on_optional_step_failure = job_config.get(
        "continue_on_optional_step_failure",
        True,
    )

    steps = _sort_steps(job_config["steps"])
    total_steps = len(steps)
    successful_steps = 0
    failed_steps = 0
    skipped_steps = 0
    final_status = "SUCCESS"
    error_message = ""

    job_run_id = create_job_run(
        job_name=job_name,
        environment=environment,
        job_run_log_file=job_run_log_file,
    )

    print("=" * 70)
    print("Starting V14 Pipeline Orchestration Job")
    print(f"Job Name: {job_name}")
    print(f"Job Run ID: {job_run_id}")
    print("=" * 70)

    for step_config in steps:
        step_id = int(step_config["step_id"])
        step_name = step_config["step_name"]
        enabled = step_config.get("enabled", True)
        critical = step_config.get("critical", True)

        print("\n" + "-" * 70)
        print(f"Step {step_id}: {step_name}")
        print(f"Enabled : {enabled}")
        print(f"Critical: {critical}")
        print("-" * 70)

        create_step_run(
            job_run_id=job_run_id,
            step_config=step_config,
            step_run_log_file=step_run_log_file,
        )

        if not enabled:
            skipped_steps += 1

            update_step_run(
                job_run_id=job_run_id,
                step_id=step_id,
                status="SKIPPED",
                result_status="SKIPPED",
                step_run_log_file=step_run_log_file,
            )

            print(f"Step skipped: {step_name}")
            continue

        try:
            step_function = _import_step_function(
                module_name=step_config["module"],
                function_name=step_config["function"],
            )
            kwargs = _resolve_step_kwargs(
                step_config=step_config,
                pipeline_config=pipeline_config,
            )

            raw_result = step_function(**kwargs)
            result_status = _normalize_result_status(raw_result)
            expected_statuses = step_config.get(
                "expected_success_statuses",
                ["SUCCESS"],
            )

            if not _is_expected_status(
                raw_result=raw_result,
                normalized_result_status=result_status,
                expected_success_statuses=expected_statuses,
            ):
                raise RuntimeError(
                    f"Step '{step_name}' returned unexpected status "
                    f"'{result_status}'. Expected one of: {expected_statuses}"
                )

            successful_steps += 1

            update_step_run(
                job_run_id=job_run_id,
                step_id=step_id,
                status="SUCCESS",
                result_status=result_status,
                step_run_log_file=step_run_log_file,
            )

            print(f"Step completed successfully: {step_name}")

        except Exception as error:
            failed_steps += 1
            error_message = str(error)

            update_step_run(
                job_run_id=job_run_id,
                step_id=step_id,
                status="FAILED",
                result_status="FAILED",
                error_message=error_message,
                step_run_log_file=step_run_log_file,
            )

            print(f"Step failed: {step_name}")
            print(f"Error Type: {type(error).__name__}")
            print(f"Error Message: {error_message}")

            if critical or not continue_on_optional_step_failure:
                final_status = "FAILED"
                break

            final_status = "SUCCESS_WITH_WARNINGS"
            print("Optional step failed. Continuing job execution.")

    update_job_run(
        job_run_id=job_run_id,
        status=final_status,
        total_steps=total_steps,
        successful_steps=successful_steps,
        failed_steps=failed_steps,
        skipped_steps=skipped_steps,
        error_message=error_message if final_status == "FAILED" else "",
        job_run_log_file=job_run_log_file,
    )

    print("\n" + "=" * 70)
    print("V14 Pipeline Orchestration Job Completed")
    print(f"Final Status    : {final_status}")
    print(f"Total Steps     : {total_steps}")
    print(f"Successful Steps: {successful_steps}")
    print(f"Failed Steps    : {failed_steps}")
    print(f"Skipped Steps   : {skipped_steps}")
    print("=" * 70)

    if final_status == "FAILED" and raise_on_failure:
        raise PipelineExecutionError(
            f"V14 orchestrated job failed: {error_message}"
        ) from None

    return final_status


if __name__ == "__main__":
    status = run_pipeline_orchestrator(raise_on_failure=False)
    sys.exit(0 if status in {"SUCCESS", "SUCCESS_WITH_WARNINGS"} else 1)
