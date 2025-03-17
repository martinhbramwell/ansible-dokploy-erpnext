import os
import subprocess
import tempfile

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
    """Uses sshpass to push the SSH key to the target.
    
    The sudo (or SSH) password for the target is obtained from the vault.
    A temporary file is created to hold the password for use with sshpass,
    and is deleted immediately after use.
    """
    print(f"Pushing SSH key to {target['host_alias']}...")
    
    # Obtain the sudo password for this target from the vault.
    # We import the load_vault_data() function from vault_manager.
    try:
        from vault_manager import load_vault_data
    except ImportError:
        print("Error: Could not import vault_manager.")
        return

    vault_data = load_vault_data()
    key = target.get("host_alias", target.get("host_ip_or_name"))
    if key not in vault_data:
        print(f"Error: No password for '{key}' found in the vault.")
        return
    sudo_password = vault_data[key]
    
    # Create a temporary file containing the password.
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
        temp_file.write(sudo_password)
        temp_file.flush()
        temp_name = temp_file.name

    try:
        push_key_cmd = [
            "sshpass", "-f", temp_name,
            "ssh-copy-id", "-o", "StrictHostKeyChecking=no",
            "-i", os.path.join(USER_HOME, ".ssh", f"{target['identity_file']}.pub"),
            f"{target['ssh_user']}@{target['host_ip_or_name']}"
        ]
        subprocess.run(push_key_cmd, check=True)
    finally:
        os.remove(temp_name)

def setup_ssh_access(target, configure=False):
    """Handles SSH setup, only configuring if needed."""
    if check_ssh_access(target):
        return True  # SSH is already set up

    if configure:
        add_ssh_alias(target)
        push_ssh_key(target)

    return check_ssh_access(target)  # Recheck after configuration
