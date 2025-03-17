import os
import subprocess

# Use current user's home directory
USER_HOME = os.path.expanduser("~")
SSH_CONFIG_FILE = os.path.join(USER_HOME, ".ssh", "config")

def check_ssh_access(target):
    """Checks if SSH access is already set up for the target."""
    ssh_test_cmd = [
        "ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=5",
        f"{target['ssh_user']}@{target['host_ip_or_name']}", "exit"
    ]
    result = subprocess.run(ssh_test_cmd, capture_output=True, text=True)
    return result.returncode == 0

def add_ssh_alias(target):
    """Adds an SSH alias to SSH_CONFIG_FILE if it doesn't already exist."""
    if os.path.exists(SSH_CONFIG_FILE):
        with open(SSH_CONFIG_FILE, "r") as ssh_config:
            if f"Host {target['host_alias']}" in ssh_config.read():
                return  # Alias already exists

    ssh_config_entry = f"""
# Alias configuration: {target['host_alias']}
Host {target['host_alias']}
    User {target['ssh_user']}
    Port {target['ssh_port']}
    HostName {target['host_ip_or_name']}
    ServerAliveInterval 120
    ServerAliveCountMax 20
    IdentityFile {os.path.join(USER_HOME, ".ssh", target['identity_file'])}
# Alias configuration: {target['host_alias']}
"""
    os.makedirs(os.path.dirname(SSH_CONFIG_FILE), exist_ok=True)
    with open(SSH_CONFIG_FILE, "a") as ssh_config:
        ssh_config.write(ssh_config_entry)
    print(f"Added SSH alias '{target['host_alias']}' to {SSH_CONFIG_FILE}")

def push_ssh_key(target):
    """Uses sshpass to push the SSH key to the target."""
    print(f"Pushing SSH key to {target['host_alias']}...")
    sshpass_file = os.path.join(USER_HOME, ".ssh", "secrets", "sshpass.txt")

    push_key_cmd = [
        "sshpass", "-f", sshpass_file,
        "ssh-copy-id", "-o", "StrictHostKeyChecking=no",
        "-i", os.path.join(USER_HOME, ".ssh", f"{target['identity_file']}.pub"),
        f"{target['ssh_user']}@{target['host_ip_or_name']}"
    ]
    subprocess.run(push_key_cmd, check=True)

def setup_ssh_access(target, configure=False):
    """Handles SSH setup, only configuring if needed."""
    if check_ssh_access(target):
        return True  # SSH is already set up

    if configure:
        add_ssh_alias(target)
        push_ssh_key(target)

    return check_ssh_access(target)  # Recheck after configuration
