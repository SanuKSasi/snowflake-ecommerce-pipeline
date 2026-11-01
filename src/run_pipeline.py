
import subprocess
import sys
import time

from src.utils.logger import get_logger


logger = get_logger("ECOMMERCE_PIPELINE")

steps = [
    ("STAGING Transformation", "src.transformation.create_staging"),
    ("CORE Transformation", "src.transformation.create_core"),
    ("ANALYTICS Transformation", "src.transformation.create_analytics"),
    ("CORE Validation", "src.validation.validate_core"),
    ("ANALYTICS Validation", "src.validation.validate_analytics")
]


def run_pipeline():

    pipeline_start = time.time()
    execution_summary = []

    logger.info("ECOMMERCE DATA PIPELINE STARTED")

    for step_name, module_name in steps:

        step_start = time.time()
        logger.info("Started: %s", step_name)

        try:
            result = subprocess.run(
                [sys.executable, "-m", module_name],
                check=False
            )

            duration = time.time() - step_start

            if result.returncode != 0:
                raise RuntimeError(
                    f"Process exited with code {result.returncode}"
                )

            status = "SUCCESS"

            logger.info(
                "Completed: %s | Duration: %.2f seconds",
                step_name,
                duration
            )

        except Exception:
            duration = time.time() - step_start
            status = "FAILED"

            logger.exception("Failed: %s", step_name)

            execution_summary.append(
                (step_name, status, duration)
            )
            break

        execution_summary.append(
            (step_name, status, duration)
        )

    total_duration = time.time() - pipeline_start

    print("\n" + "=" * 65)
    print("             PIPELINE EXECUTION SUMMARY")
    print("=" * 65)

    print(f"{'STEP':<30} {'STATUS':<15} {'DURATION':>12}")
    print("-" * 65)

    for name, status, duration in execution_summary:
        print(f"{name:<30} {status:<15} {duration:>9.2f} sec")

    print("-" * 65)
    print(f"Total execution time: {total_duration:.2f} seconds")

    if len(execution_summary) == len(steps) and all(
        status == "SUCCESS"
        for _, status, _ in execution_summary
    ):
        print("FINAL STATUS: SUCCESS")
        logger.info("PIPELINE COMPLETED SUCCESSFULLY")
    else:
        print("FINAL STATUS: FAILED")
        logger.error("PIPELINE FAILED")

        sys.exit(1)


if __name__ == "__main__":
    run_pipeline()
