#!/usr/bin/env python3
import os
import subprocess
import yaml

# Directory where host-specific variables are stored.
HOST_VARS_DIR = "host_vars"
# Path to the vault password file (adjust as needed).
VAULT_PASS_FILE = os.path.expanduser("~/.ssh/secrets/.vault_pass")

def load_host_config(host):
    """
    Loads and returns the decrypted YAML content from host_vars/<host>.yml.
    Uses the ansible-vault view command.
    """
    host_file = os.path.join(HOST_VARS_DIR, f"{host}.yml")
    if not os.path.exists(host_file):
        return None
    try:
        result = subprocess.run(
            ["ansible-vault", "view", host_file, "--vault-password-file", VAULT_PASS_FILE],
            capture_output=True, text=True, check=True
        )
        data = yaml.safe_load(result.stdout)
        return data if data is not None else {}
    except subprocess.CalledProcessError as e:
        print(f"Error decrypting {host_file}: {e.stderr}")
        return None

def save_host_config(host, config):
    """
    Writes the given host configuration dictionary to host_vars/<host>.yml in plaintext,
    then encrypts it using ansible-vault with the specified vault-id.
    """
    os.makedirs(HOST_VARS_DIR, exist_ok=True)
    host_file = os.path.join(HOST_VARS_DIR, f"{host}.yml")
    # Dump config to plaintext YAML.
    with open(host_file, "w") as f:
        yaml.dump(config, f, default_flow_style=False)
    # Encrypt the file using ansible-vault with a vault-id of "default".
    try:
        subprocess.run(
            [
                "ansible-vault", "encrypt", host_file,
                "--encrypt-vault-id", "default",
                "--vault-password-file", VAULT_PASS_FILE
            ],
            capture_output=True, text=True, check=True
        )
        print(f"Configuration for host '{host}' saved and encrypted.")
    except subprocess.CalledProcessError as e:
        print(f"Error encrypting {host_file}: {e.stderr}")

def load_all_configs():
    """
    Loads all decrypted host configuration files from HOST_VARS_DIR.
    Returns a list of host configuration dictionaries.
    Each file is expected to be named <host_alias>.yml.
    """
    configs = []
    if not os.path.exists(HOST_VARS_DIR):
        os.makedirs(HOST_VARS_DIR, exist_ok=True)
    for file in os.listdir(HOST_VARS_DIR):
        if file.endswith(".yml"):
            host = file[:-4]
            config = load_host_config(host)
            if config is not None:
                if "host_alias" not in config:
                    config["host_alias"] = host
                configs.append(config)
    return configs

def edit_config():
    """
    Provides an interactive command-line interface to view, add, or edit host configurations.
    Non-secret parameters (host alias, IP, SSH user, port, identity file) are edited here.
    When prompted, the user may choose to update the sudo password via vault_manager.
    Returns a list of host configuration dictionaries.
    """
    configs = load_all_configs()
    while True:
        print("\nCurrent Hosts:")
        if configs:
            for idx, conf in enumerate(configs, start=1):
                alias = conf.get("host_alias", "UNKNOWN")
                ip = conf.get("host_ip_or_name", "no IP")
                print(f"{idx}. {alias} ({ip})")
        else:
            print("No host configurations found.")
        print("0. Save and Continue")
        print("N. Add a new host")
        choice = input("Enter number to edit, 0 to continue, or N to add a host: ").strip().lower()
        if choice == "0":
            break
        elif choice == "n":
            new_conf = {}
            new_conf["host_alias"] = input("Enter alias name: ").strip()
            new_conf["host_ip_or_name"] = input("Enter IP or domain name: ").strip()
            new_conf["ssh_user"] = input("Enter SSH username: ").strip()
            new_conf["ansible_become_pass"] = input("Enter sudoer user password: ").strip()
            new_conf["ssh_port"] = input("Enter SSH port (default 22): ").strip() or "22"
            new_conf["identity_file"] = input("Enter SSH identity file name (default id_rsa): ").strip() or "id_rsa"
            # Save new configuration
            save_host_config(new_conf["host_alias"], new_conf)
            configs.append(new_conf)
        else:
            try:
                index = int(choice) - 1
                if index < 0 or index >= len(configs):
                    print("Invalid selection, try again.")
                    continue
                conf = configs[index]
                print(f"\nEditing host: {conf.get('host_alias')}")
                conf["host_alias"] = input(f"Enter alias name [{conf.get('host_alias')}]: ").strip() or conf.get("host_alias")
                conf["host_ip_or_name"] = input(f"Enter IP or domain name [{conf.get('host_ip_or_name')}]: ").strip() or conf.get("host_ip_or_name")
                conf["ssh_user"] = input(f"Enter SSH username [{conf.get('ssh_user')}]: ").strip() or conf.get("ssh_user")
                conf["ansible_become_pass"] = input(f"Enter sudoer user password [{conf.get('ansible_become_pass')}]: ").strip() or conf.get("ansible_become_pass")
                conf["ssh_port"] = input(f"Enter SSH port [{conf.get('ssh_port')}]: ").strip() or conf.get("ssh_port")
                conf["identity_file"] = input(f"Enter SSH identity file name [{conf.get('identity_file')}]: ").strip() or conf.get("identity_file")
                # update_choice = input(f"Do you want to update the sudo password for '{conf.get('host_alias')}'? (y/N): ").strip().lower()
                # if update_choice == 'y':
                #     from vault_manager import update_vault_for_target
                #     update_vault_for_target(conf)
                # Save updated configuration
                save_host_config(conf["host_alias"], conf)
                configs[index] = conf
            except (ValueError, IndexError):
                print("Invalid selection, try again.")
    return configs

if __name__ == "__main__":
    all_configs = edit_config()
    print("\nFinal host configurations:")
    for conf in all_configs:
        print(conf)
