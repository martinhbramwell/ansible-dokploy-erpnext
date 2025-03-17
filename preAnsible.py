#!/usr/bin/env python3
import os
import sys

from env_validator import validate_environment
from config_manager import load_config, save_config, edit_config
from ssh_manager import setup_ssh_access, check_ssh_access
from vault_manager import setup_vault_for_target
from host_manager import update_hosts_file

# Use current user's home directory
USER_HOME = os.path.expanduser("~")

# Set the project directory based on the current user's home
PROJECT_DIR = os.path.join(USER_HOME, "projects/Logichem/ansible-dokploy-erpnext")

# Validate environment dependencies (e.g., sshpass, SUDO_ASKPASS, sudo -A)
validate_environment()

# Load, interactively edit, and save configuration
config = load_config()
config = edit_config(config)
save_config(config)

# For each target, ensure its sudo password is recorded in the vault.
for target in config.get("targets", []):
    setup_vault_for_target(target)

# Process each target defined in the configuration
for target in config.get("targets", []):
    print(f"\nProcessing target: {target['host_alias']} ({target['host_ip_or_name']})")

    if check_ssh_access(target):
        print(f"SSH access confirmed for {target['host_alias']}. Skipping SSH setup.")
    else:
        print(f"Configuring SSH access for {target['host_alias']}...")
        setup_ssh_access(target, configure=True)
        if not check_ssh_access(target):
            print(f"ERROR: SSH setup failed for {target['host_alias']}. Skipping this target.")
            continue

    # Update /etc/hosts with target information if needed (uses sudo -A internally)
    update_hosts_file(target)

print("\nAnsible control machine setup is complete! 🚀")
