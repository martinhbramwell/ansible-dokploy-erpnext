import os
import shutil
import subprocess
import sys

def validate_environment():
    """Validates that required external dependencies are installed,
    that SUDO_ASKPASS is defined and executable, that sudo -A works
    (via 'sudo -A ls -l /root'), and that PyYAML is installed."""
    missing = []

    # Check for sshpass
    if shutil.which("sshpass") is None:
        missing.append("sshpass")

    # Check for SUDO_ASKPASS environment variable
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

    if missing:
        print("ERROR: The following dependencies or configurations are missing:")
        for dep in missing:
            print(" -", dep)
        sys.exit(1)

    # Test that "sudo -A ls -l /root" works.
    result = subprocess.run(["sudo", "-A", "ls", "-l", "/root"],
                            capture_output=True, text=True)
    if result.returncode != 0:
        print("ERROR: 'sudo -A ls -l /root' is not working properly. Please check your SUDO_ASKPASS setup and sudoers configuration.")
        sys.exit(1)

    print("Environment validation passed: All required dependencies and sudo -A configuration are in place.")

if __name__ == "__main__":
    validate_environment()
