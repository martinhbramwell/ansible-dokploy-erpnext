import os
import getpass
import subprocess
import sys
import pwd

# Determine the sudoer user's home directory and UID/GID
user_home = os.environ.get("USER_HOME")
if not user_home:
    sudo_user = os.getenv("SUDO_USER")
    if sudo_user:
        user_info = pwd.getpwnam(sudo_user)
        user_home = user_info.pw_dir
        SUDO_UID = user_info.pw_uid
        SUDO_GID = user_info.pw_gid
    else:
        user_home = os.path.expanduser("~")
        SUDO_UID, SUDO_GID = os.getuid(), os.getgid()
else:
    sudo_user = os.getenv("SUDO_USER")
    if sudo_user:
        user_info = pwd.getpwnam(sudo_user)
        SUDO_UID = user_info.pw_uid
        SUDO_GID = user_info.pw_gid
    else:
        SUDO_UID, SUDO_GID = os.getuid(), os.getgid()

SECRETS_DIR = os.path.join(user_home, ".ssh", "secrets")
VAULT_PASS_FILE = os.path.join(SECRETS_DIR, ".vault_pass")
SSHPASS_FILE = os.path.join(SECRETS_DIR, "sshpass.txt")
VAULT_FILE = os.path.join(user_home, "projects/Logichem/ansible-dokploy-erpnext", "group_vars", "all", "vault.yml")

def setup_vault():
    """Handles Ansible Vault password storage and encryption of sudo passwords."""
    os.makedirs(SECRETS_DIR, exist_ok=True)

    # Prompt for Ansible Vault password and write it to file
    vault_password = getpass.getpass("Enter Ansible Vault password: ")
    with open(VAULT_PASS_FILE, "w") as f:
        f.write(vault_password + "\n")
    os.chmod(VAULT_PASS_FILE, 0o600)
    os.chown(VAULT_PASS_FILE, SUDO_UID, SUDO_GID)

    # Prompt for sudo password and write it to file
    sudo_password = getpass.getpass("Enter sudoer password of target machine user: ")
    with open(SSHPASS_FILE, "w") as f:
        f.write(sudo_password + "\n")
    os.chmod(SSHPASS_FILE, 0o600)
    os.chown(SSHPASS_FILE, SUDO_UID, SUDO_GID)

    # Write the sudo password in plaintext (temporarily) to the vault file
    os.makedirs(os.path.dirname(VAULT_FILE), exist_ok=True)
    with open(VAULT_FILE, "w") as f:
        f.write(f"ansible_become_pass: {sudo_password}\n")
    os.chown(VAULT_FILE, SUDO_UID, SUDO_GID)

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
