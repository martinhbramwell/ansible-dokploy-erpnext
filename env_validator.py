import shutil
import sys

def validate_environment():
    """Validates that required external dependencies are installed."""
    missing = []

    # Check for sshpass
    if shutil.which("sshpass") is None:
        missing.append("sshpass")
    
    # Future checks can be added here, for example:
    # if shutil.which("ansible") is None:
    #     missing.append("ansible")

    if missing:
        print("ERROR: The following dependencies are missing: " + ", ".join(missing))
        print("Please install the missing dependencies and try again.")
        sys.exit(1)
    else:
        print("Environment validation passed: All required dependencies are installed.")

if __name__ == "__main__":
    validate_environment()
