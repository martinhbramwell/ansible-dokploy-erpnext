import os
import getpass
import subprocess
import sys
import yaml

# Use current user's home directory
USER_HOME = os.path.expanduser("~")
SECRETS_DIR = os.path.join(USER_HOME, ".ssh", "secrets")
VAULT_PASS_FILE = os.path.join(SECRETS_DIR, ".vault_pass")
SSHPASS_FILE = os.path.join(SECRETS_DIR, "sshpass.txt")
VAULT_FILE = os.path.join(
    USER_HOME,
    "projects/Logichem/ansible-dokploy-erpnext",
    "group_vars",
    "all",
    "vault.yml"
)

def ensure_vault_password():
    """Ensure that the Ansible vault password is stored in VAULT_PASS_FILE."""
    os.makedirs(SECRETS_DIR, exist_ok=True)
    if not os.path.exists(VAULT_PASS_FILE):
        vault_password = getpass.getpass("Enter Ansible Vault password: ")
        with open(VAULT_PASS_FILE, "w") as f:
            f.write(vault_password + "\n")
        os.chmod(VAULT_PASS_FILE, 0o600)

def load_vault_data():
    """Return a dictionary from vault.yml if it exists, else an empty dict."""
    if os.path.exists(VAULT_FILE):
        try:
            result = subprocess.run(
                ["ansible-vault", "view", VAULT_FILE, "--vault-password-file", VAULT_PASS_FILE],
                capture_output=True, text=True, check=True
            )
            data = yaml.safe_load(result.stdout)
            return data if data is not None else {}
        except subprocess.CalledProcessError as e:
            print("Error decrypting vault file:", e.stderr)
            sys.exit(1)
    else:
        return {}

def write_and_encrypt_vault(data):
    """Write the YAML data to VAULT_FILE in plaintext then encrypt it using ansible-vault."""
    os.makedirs(os.path.dirname(VAULT_FILE), exist_ok=True)
    with open(VAULT_FILE, "w") as f:
        yaml.dump(data, f, default_flow_style=False)
    encrypt_cmd = [
        "ansible-vault", "encrypt", VAULT_FILE, "--encrypt-vault-id", "default",
        "--vault-password-file", VAULT_PASS_FILE
    ]
    result = subprocess.run(encrypt_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("Error encrypting vault file:", result.stderr)
        sys.exit(1)
    else:
        print("Vault file updated successfully.")

def setup_vault_for_target(target):
    """
    For the given target, check if its sudo password is recorded in the vault.
    If not present, prompt the user to add it.
    """
    ensure_vault_password()
    vault_data = load_vault_data()

    # Use host_alias if available; otherwise, use host_ip_or_name as key.
    key = target.get("host_alias", target.get("host_ip_or_name"))
    if key in vault_data:
        print(f"Sudo password for '{key}' already exists in the vault.")
        print("If you wish to update it, please use the update option.")
        return

    sudo_password = getpass.getpass(f"Enter sudo password for target '{key}': ")
    vault_data[key] = sudo_password
    write_and_encrypt_vault(vault_data)

def update_vault_for_target(target):
    """
    For the given target, update the sudo password in the vault.
    This function decrypts the vault, prompts for a replacement password,
    overwrites the existing record, and re-encrypts the file.
    """
    ensure_vault_password()
    vault_data = load_vault_data()

    key = target.get("host_alias", target.get("host_ip_or_name"))
    if key not in vault_data:
        print(f"No existing sudo password for '{key}' found. Adding new record.")
        sudo_password = getpass.getpass(f"Enter sudo password for target '{key}': ")
        vault_data[key] = sudo_password
    else:
        new_password = getpass.getpass(f"Enter new sudo password for target '{key}': ")
        vault_data[key] = new_password

    write_and_encrypt_vault(vault_data)
