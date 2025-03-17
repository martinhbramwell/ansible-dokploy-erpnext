import os
import getpass
import subprocess

SECRETS_DIR = os.path.expanduser("~/.ssh/secrets")
VAULT_PASS_FILE = os.path.join(SECRETS_DIR, ".vault_pass")
SSHPASS_FILE = os.path.join(SECRETS_DIR, "sshpass.txt")
VAULT_FILE = os.path.expanduser("~/projects/Logichem/ansible-dokploy-erpnext/group_vars/all/vault.yml")

def setup_vault():
    """Handles Ansible Vault password storage and encryption of sudo passwords."""
    os.makedirs(SECRETS_DIR, exist_ok=True)

    # Prompt for Ansible Vault password
    vault_password = getpass.getpass("Enter Ansible Vault password: ")
    with open(VAULT_PASS_FILE, "w") as f:
        f.write(vault_password + "\n")
    os.chmod(VAULT_PASS_FILE, 0o600)

    # Prompt for sudo password
    sudo_password = getpass.getpass("Enter sudoer password of target machine user: ")
    with open(SSHPASS_FILE, "w") as f:
        f.write(sudo_password + "\n")
    os.chmod(SSHPASS_FILE, 0o600)

    # Store sudo password in plaintext first (temporarily)
    with open(VAULT_FILE, "w") as f:
        f.write(f"ansible_become_pass: {sudo_password}\n")

    # Encrypt the entire vault.yml file
    encrypt_cmd = [
        "ansible-vault", "encrypt", VAULT_FILE, "--encrypt-vault-id", "default",
        "--vault-password-file", VAULT_PASS_FILE
    ]
    result = subprocess.run(encrypt_cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print("Vault password stored securely in vault.yml")
    else:
        print("Error encrypting password:", result.stderr)
        sys.exit(1)
