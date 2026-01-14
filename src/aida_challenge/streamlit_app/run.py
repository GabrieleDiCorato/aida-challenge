"""
Launcher script for the AIDA Challenge Streamlit Dashboard.
"""

import sys
import subprocess
from pathlib import Path


def main():
    """Launch the Streamlit app."""
    # Get the path to the app.py file
    app_path = Path(__file__).parent / "app.py"

    # Launch streamlit with the app
    cmd = ["streamlit", "run", str(app_path)]

    # Pass any additional arguments to streamlit
    if len(sys.argv) > 1:
        cmd.extend(sys.argv[1:])

    # Run streamlit
    subprocess.run(cmd)


if __name__ == "__main__":
    main()
