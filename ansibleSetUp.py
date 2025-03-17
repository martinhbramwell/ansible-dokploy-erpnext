#!/usr/bin/env python3
import os
import subprocess
import getpass
import json
import sys

# Ensure the script is run with sudo
if os.geteuid() != 0:
    print("This script must be run as root. Use sudo.")
    sys.exit(1)

# Get the sudoer user
SUDO_USER = os.getenv("SUDO_USER")
if not SUDO_USER:
    print("Error: Unable to determine the sudo user.")
    sys.exit(1)

# Define paths relative to the sudoer user
USER_HOME = os.path.expanduser(f"~{SUDO_USER}")
SSH_DIR = os.path.join(USER_HOME, ".ssh")

# Define project path based on the sudoer user's home directory
PROJECT_DIR = os.path.join(USER_HOME, "projects/Logichem/ansible-dokploy-erpnext")
CONFIG_FILE = os.path.join(PROJECT_DIR, "setup_config.json")
VAULT_FILE = os.path.join(PROJECT_DIR, "group_vars/all/vault.yml")
SECRETS_DIR = os.path.join(SSH_DIR, "secrets")
VAULT_PASS_FILE = os.path.join(SECRETS_DIR, ".vault_pass")
SSHPASS_FILE = os.path.join(SECRETS_DIR, "sshpass.txt")
SSH_CONFIG_FILE = os.path.join(SSH_DIR, "config")

# Ensure necessary directories exist
os.makedirs(os.path.join(PROJECT_DIR, "group_vars/all"), exist_ok=True)
os.makedirs(SECRETS_DIR, exist_ok=True)

# Prompt for Ansible Vault password
vault_password = getpass.getpass("Enter Ansible Vault password: ")

# Store Vault password securely
with open(VAULT_PASS_FILE, "w") as f:
    f.write(vaul
        t_password + "\n")
os.chmod(VAULT_PASS_FILE, 0o600)

# Prompt for sudo password
sudo_password = getpass.getpass("Enter sudoer password of target machine user: ")

# Store sudo password in plaintext first (temporarily)
with open(VAULT_FILE, "w") as f:
    f.write(f"ansible_become_pass: {sudo_password}\n")

# Store sudo password for SSH pass
with open(SSHPASS_FILE, "w") as f:
    f.write(sudo_password + "\n")
os.chmod(SSHPASS_FILE, 0o600)

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

def edit_config(config):
    while True:
        print("\nCurrent Configuration:")
        for i, (key, value) in enumerate(config.items(), start=1):
            print(f"{i}. {key}: {value}")
        print("0. Save and Continue")
        choice = input("Enter number to edit or 0 to continue: ")
        if choice == "0":
            break
        try:
            index = int(choice) - 1
            key = list(config.keys())[index]
            new_value = input(f"Enter new value for {key}: ")
            config[key] = new_value
        except (ValueError, IndexError):
            print("Invalid choice, try again.")
    return config

# Load or initialize config
config = load_config()
defaults = {
    "host_alias": "SSH_ALIAS_FOR_TARGET",
    "host_ip_or_name": "DOMAIN_NAME_OR_IP_ADDR",
    "ssh_user": "YOUR_USER_NAME",
    "ssh_port": "22",
    "ssh_path": SSH_DIR,
    "identity_file": "YOUR_SSH_KEY_NAME"
}
for key, value in defaults.items():
    config.setdefault(key, value)
config = edit_config(config)
save_config(config)

# Derive full identity file path
config["identity_file_pub"] = os.path.join(SSH_DIR, config["identity_file"] + ".pub")
config["identity_file"] = os.path.join(SSH_DIR, config["identity_file"])

# Verify if SSH access already works
ssh_test_cmd = [
    "ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=5",
    f"{config['ssh_user']}@{config['host_ip_or_name']}", "exit"
]
ssh_test_result = subprocess.run(ssh_test_cmd, capture_output=True, text=True)
if ssh_test_result.returncode == 0:
    print("SSH login works; skipping configuration.")
    sys.exit(0)

# Verify identity file exists
if not os.path.exists(config["identity_file"]):
    print(f"Error: Identity file '{config['identity_file']}' does not exist.")
    sys.exit(1)
else:
    print(f"Found identity file '{config['identity_file']}'.")

# Configure /etc/hosts if needed
if config["host_ip_or_name"]:
    with open("/etc/hosts", "r+") as hosts_file:
        hosts = hosts_file.read()
        entry = f"{config['host_ip_or_name']} {config['host_alias']}\n"
        if entry not in hosts:
            hosts_file.write(entry)
            print("Added entry to /etc/hosts")

# Configure SSH alias in ~/.ssh/config if it doesn't exist
with open(SSH_CONFIG_FILE, "r+") as ssh_config:
    ssh_config_content = ssh_config.read()
    if f"Host {config['host_alias']}" not in ssh_config_content:
        ssh_config_entry = f"""
# Alias configuration: '{config['host_alias']}'
Host {config['host_alias']}
    User {config['ssh_user']}
    Port {config['ssh_port']}
    HostName {config['host_ip_or_name']}
    ServerAliveInterval 120
    ServerAliveCountMax 20
    IdentityFile {config['identity_file']}
# Alias configuration: '{config['host_alias']}'
"""
        ssh_config.write(ssh_config_entry)
        print(f"Added SSH alias '{config['host_alias']}' to {SSH_CONFIG_FILE}")

print("\nAnsible control machine setup is complete! 🚀")
