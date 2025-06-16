import os
import subprocess
import sys
from pathlib import Path

ENV_NAME = "data-analysis-proj"
APP_MODULE = "src.app.app"

def is_conda_env_created(env_name):
    """Check if a conda environment exists."""
    result = subprocess.run(["conda", "env", "list"], capture_output=True, text=True)
    return env_name in result.stdout

def create_conda_env():
    """Create a conda environment using environment.yml."""
    print("[INFO] Creating Conda environment...")
    result = subprocess.run(["conda", "env", "create", "-f", "environment.yml"])
    if result.returncode != 0:
        print("[ERROR] Failed to create Conda environment.")
        sys.exit(1)
    print("[INFO] Environment created successfully.")

def run_app_in_conda(env_name: str):
    """Run the app inside the given Conda environment."""
    print(f"[INFO] Launching app in Conda env '{env_name}'...")
    result = subprocess.run([
        "conda", "run", "-n", env_name, "python", "-m", APP_MODULE
    ])
    if result.returncode != 0:
        print("[ERROR] App failed to launch. See output above.")
        sys.exit(result.returncode)

if __name__ == "__main__":
    if not is_conda_env_created(ENV_NAME):
        if not Path("environment.yml").exists():
            print("[ERROR] environment.yml file not found!")
            sys.exit(1)
        create_conda_env()
    
    run_app_in_conda(ENV_NAME)
