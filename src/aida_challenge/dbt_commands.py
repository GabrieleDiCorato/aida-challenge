"""Wrapper functions for dbt commands."""

import subprocess
import sys
import os
import shutil
from pathlib import Path
from datetime import datetime


def _set_project_root():
    """Change to project root directory for relative paths in profiles.yml."""
    root = Path(__file__).parent.parent.parent
    os.chdir(root)
    return root


def _archive_log():
    """Archive dbt.log to timestamped filename after command execution."""
    root = Path(__file__).parent.parent.parent
    log_dir = root / "dbt_project" / "logs"
    default_log = log_dir / "dbt.log"

    if default_log.exists():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archived_log = log_dir / f"dbt_{timestamp}.log"
        shutil.copy2(default_log, archived_log)
        print(f"Log archived to: {archived_log}")
        return archived_log
    return None


def get_dbt_args():
    """Get common dbt arguments with proper paths."""
    root = Path(__file__).parent.parent.parent
    project_dir = root / "dbt_project"

    # Debug output
    print(f"Root directory: {root.absolute()}")
    print(f"Project directory: {project_dir.absolute()}")

    # Set profiles directory to user's home directory (standard dbt location)
    # But allow override via environment variable for local development
    profiles_dir = os.getenv("DBT_PROFILES_DIR")
    if not profiles_dir:
        # Check if profiles.yml exists in project (development setup)
        if (project_dir / "profiles.yml").exists():
            profiles_dir = str(project_dir)
            print(f"Using local profiles directory: {profiles_dir}")
        else:
            # Use default ~/.dbt location
            profiles_dir = str(Path.home() / ".dbt")
            print(f"Using home profiles directory: {profiles_dir}")
    else:
        print(f"Using environment profiles directory: {profiles_dir}")

    os.environ["DBT_PROFILES_DIR"] = profiles_dir

    return [
        "--project-dir",
        str(project_dir),
        "--profiles-dir",
        str(profiles_dir),
        "--profile",
        "aida_insurance",
        "--no-use-colors",
    ]


def dbt_debug():
    """Run dbt debug."""
    _set_project_root()
    args = get_dbt_args()
    print(f"Running: dbt debug {' '.join(args)}")
    subprocess.run(["dbt", "debug", *args], check=False)
    _archive_log()


def dbt_deps():
    """Install dbt dependencies."""
    _set_project_root()
    subprocess.run(["dbt", "deps", *get_dbt_args()], check=False)
    _archive_log()


def dbt_run():
    """Run all dbt models."""
    _set_project_root()
    result = subprocess.run(["dbt", "run", *get_dbt_args()], check=False)
    _archive_log()
    return result.returncode


def dbt_test():
    """Test all dbt models."""
    _set_project_root()
    result = subprocess.run(["dbt", "test", *get_dbt_args()], check=False)
    _archive_log()
    return result.returncode


def dbt_build():
    """Build and test all dbt models."""
    _set_project_root()
    result = subprocess.run(["dbt", "build", *get_dbt_args()], check=False)
    _archive_log()
    return result.returncode


def dbt_clean():
    """Clean dbt artifacts."""
    _set_project_root()
    subprocess.run(["dbt", "clean", *get_dbt_args()], check=False)
    _archive_log()


def dbt_docs_generate():
    """Generate dbt documentation."""
    _set_project_root()
    subprocess.run(["dbt", "docs", "generate", *get_dbt_args()], check=False)
    _archive_log()


def dbt_docs_serve():
    """Serve dbt documentation."""
    _set_project_root()
    subprocess.run(["dbt", "docs", "serve", *get_dbt_args()], check=False)
    _archive_log()


def dbt_run_staging():
    """Run staging models."""
    _set_project_root()
    result = subprocess.run(["dbt", "run", "--select", "staging", *get_dbt_args()], check=False)
    _archive_log()
    return result.returncode


def dbt_run_intermediate():
    """Run intermediate models."""
    _set_project_root()
    result = subprocess.run(
        ["dbt", "run", "--select", "intermediate", *get_dbt_args()], check=False
    )
    _archive_log()
    return result.returncode


def dbt_run_marts():
    """Run marts models."""
    _set_project_root()
    result = subprocess.run(["dbt", "run", "--select", "marts", *get_dbt_args()], check=False)
    _archive_log()
    return result.returncode


def dbt_test_sources():
    """Test source data."""
    _set_project_root()
    result = subprocess.run(["dbt", "test", "--select", "source:*", *get_dbt_args()], check=False)
    _archive_log()
    return result.returncode
