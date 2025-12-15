"""Wrapper functions for dbt commands."""

import subprocess
import sys
import os
from pathlib import Path


def get_dbt_args():
    """Get common dbt arguments."""
    root = Path(__file__).parent.parent.parent
    profiles_dir = root / "dbt_project"

    # Debug output
    print(f"Root directory: {root.absolute()}")
    print(f"Profiles directory: {profiles_dir.absolute()}")

    # Set environment variable for dbt to find profiles
    os.environ["DBT_PROFILES_DIR"] = str(profiles_dir)

    return [
        "--project-dir",
        str(root / "dbt_project"),
        "--profiles-dir",
        str(profiles_dir),
        "--profile",
        "aida_insurance",
        "--no-use-colors",
    ]


def dbt_debug():
    """Run dbt debug."""
    args = get_dbt_args()
    print(f"Running: dbt debug {' '.join(args)}")
    subprocess.run(["dbt", "debug", *args], check=False)


def dbt_deps():
    """Install dbt dependencies."""
    subprocess.run(["dbt", "deps", *get_dbt_args()], check=False)


def dbt_run():
    """Run all dbt models."""
    subprocess.run(["dbt", "run", *get_dbt_args()], check=False)


def dbt_test():
    """Test all dbt models."""
    subprocess.run(["dbt", "test", *get_dbt_args()], check=False)


def dbt_build():
    """Build and test all dbt models."""
    subprocess.run(["dbt", "build", *get_dbt_args()], check=False)


def dbt_clean():
    """Clean dbt artifacts."""
    subprocess.run(["dbt", "clean", *get_dbt_args()], check=False)


def dbt_docs_generate():
    """Generate dbt documentation."""
    subprocess.run(["dbt", "docs", "generate", *get_dbt_args()], check=False)


def dbt_docs_serve():
    """Serve dbt documentation."""
    subprocess.run(["dbt", "docs", "serve", *get_dbt_args()], check=False)


def dbt_run_staging():
    """Run staging models."""
    subprocess.run(["dbt", "run", "--select", "staging", *get_dbt_args()], check=False)


def dbt_run_intermediate():
    """Run intermediate models."""
    subprocess.run(["dbt", "run", "--select", "intermediate", *get_dbt_args()], check=False)


def dbt_run_marts():
    """Run marts models."""
    subprocess.run(["dbt", "run", "--select", "marts", *get_dbt_args()], check=False)


def dbt_test_sources():
    """Test source data."""
    subprocess.run(["dbt", "test", "--select", "source:*", *get_dbt_args()], check=False)
