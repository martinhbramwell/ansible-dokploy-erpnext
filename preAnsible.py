#!/usr/bin/env python3
import os
import sys
import getpass
import subprocess
import pwd
from config_manager import load_config, save_config, edit_config
from ssh_manager import setup_ssh_access, check_ssh_access
from vault_manager import setup_vault
from host_manager import update_hosts_file

# Import environment validation module
from env_validator import validate_environment

# Validate the environment before doing anything else
validate_environment()

# Ensure the script is run with sudo
if os.geteuid() != 0:
    print("This script must be run as root. Use sudo.")
    sys.exit(1)

# Get the sudoer user's home directory correctly
SUDO_USER = os.getenv("SUDO_USER")
if not SUDO_USER:
    print("Error: Unable to determine the sudo user.")
    sys.exit(1)

USER_HOME = pwd.getpwnam(SUDO_USER).pw_dir

# Correct PROJECT_DIR to be based on the sudo user's home
PROJECT_DIR = os.path.join(USER_HOME, "projects/Logichem/ansible-dokploy-erpnext")

# Set an environment variable so dependent modules know the correct home directory
os.environ["USER_HOME"] = USER_HOME

# Load and edit configuration
config = load_config()
config = edit_config(config)
save_config(config)

# Prompt for Ansible Vault and sudo passwords once
setup_vault()

# Iterate over all targets in config
for target in config.get("targets", []):
    print(f"\nProcessing target: {target['host_alias']} ({target['host_ip_or_name']})")

    # Check if SSH access already works
    if check_ssh_access(target):
        print(f"SSH access confirmed for {target['host_alias']}. Skipping SSH setup.")
    else:
        print(f"Configuring SSH access for {target['host_alias']}...")
        setup_ssh_access(target, configure=True)
        # Double-check SSH access after setup
        if not check_ssh_access(target):
            print(f"ERROR: SSH setup failed for {target['host_alias']}. Skipping this target.")
            continue

    # Update /etc/hosts if needed
    update_hosts_file(target)

print("\nAnsible control machine setup is complete! 🚀")
