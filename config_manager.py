#!/usr/bin/env python3
import os
import subprocess
import yaml
import json

# Directory where host-specific variables are stored.
HOST_VARS_DIR = "host_vars"
# Path to the vault password file (adjust as needed).
VAULT_PASS_FILE = os.path.expanduser("~/.ssh/secrets/.vault_pass")
# Path to the configuration schema JSON file.
SCHEMA_FILE = "config_schema.json"

def load_schema():
    """
    Loads and returns the configuration schema from SCHEMA_FILE.
    The schema defines the available configuration keys, full names, and default values.
    """
    if not os.path.exists(SCHEMA_FILE):
        print(f"Schema file {SCHEMA_FILE} not found.")
        return {}
    with open(SCHEMA_FILE, "r") as f:
        return json.load(f)

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
    It uses the schema (loaded from config_schema.json) to prompt for each parameter.
    Returns a list of host configuration dictionaries.
    """
    schema = load_schema()
    if not schema:
        print("No schema loaded; cannot proceed.")
        return []
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
            for key, meta in schema.items():
                full_name = meta.get("full_name", key)
                default_val = meta.get("default", "")
                prompt = f"Enter {full_name}"
                if default_val:
                    prompt += f" [{default_val}]"
                prompt += ": "
                value = input(prompt).strip()
                if not value:
                    value = default_val
                new_conf[key] = value
            # Save new configuration using the host_alias as filename.
            if "host_alias" in new_conf and new_conf["host_alias"]:
                save_host_config(new_conf["host_alias"], new_conf)
                configs.append(new_conf)
            else:
                print("host_alias is required; skipping entry.")
        else:
            try:
                index = int(choice) - 1
                if index < 0 or index >= len(configs):
                    print("Invalid selection, try again.")
                    continue
                conf = configs[index]
                print(f"\nEditing host: {conf.get('host_alias')}")
                for key, meta in schema.items():
                    full_name = meta.get("full_name", key)
                    current_val = conf.get(key, meta.get("default", ""))
                    prompt = f"Enter {full_name} [{current_val}]: "
                    new_val = input(prompt).strip()
                    if new_val:
                        conf[key] = new_val
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
