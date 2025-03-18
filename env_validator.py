import os
import shutil
import subprocess
import sys

def validate_environment():
    """Validates that required external dependencies, configurations, and roles are in place.
    
    Checks:
      - sshpass is installed.
      - SUDO_ASKPASS is defined and points to an executable file.
      - PyYAML is installed.
      - Sudo askpass functionality (via 'sudo -A ls -l /root') works.
    """
    missing = []

    # Check for sshpass
    if shutil.which("sshpass") is None:
        missing.append("sshpass")

    # Check for SUDO_ASKPASS environment variable and executable file
    sudo_askpass = os.environ.get("SUDO_ASKPASS")
    if not sudo_askpass:
        missing.append("SUDO_ASKPASS environment variable is not set")
    else:
        if not (os.path.exists(sudo_askpass) and os.access(sudo_askpass, os.X_OK)):
            missing.append("SUDO_ASKPASS program is not found or not executable")

    # Check for PyYAML installation
    try:
        import yaml  # noqa: F401
    except ImportError:
        missing.append("PyYAML (pip install pyyaml)")

    # Test that "sudo -A ls -l /root" works.
    result = subprocess.run(["sudo", "-A", "ls", "-l", "/root"],
                            capture_output=True, text=True)
    if result.returncode != 0:
        print("ERROR: 'sudo -A ls -l /root' is not working properly. Please check your SUDO_ASKPASS setup and sudoers configuration.")
        sys.exit(1)

    print("Environment validation passed: All required dependencies, configurations, and roles are in place.")

if __name__ == "__main__":
    validate_environment()
