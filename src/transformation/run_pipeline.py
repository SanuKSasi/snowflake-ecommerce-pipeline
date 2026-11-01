import subprocess
import sys

steps = [
    ("STAGING Transformation", "src.transformation.create_staging"),
    ("CORE Transformation", "src.transformation.create_core"),
    ("ANALYTICS Transformation", "src.transformation.create_analytics"),
    ("CORE Validation", "src.validation.validate_core"),
    ("ANALYTICS Validation", "src.validation.validate_analytics")
]

for step_name, module_name in steps:
    print(f"\n{'=' * 60}")
    print(f"Running: {step_name}")
    print(f"{'=' * 60}")

    result = subprocess.run(
        [sys.executable, "-m", module_name],
        check=False
    )

    if result.returncode != 0:
        print(f"\nPipeline failed at: {step_name}")
        sys.exit(result.returncode)

print("\nAll pipeline steps completed successfully!")