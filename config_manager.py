import os
import json

# Use current user's home directory
USER_HOME = os.path.expanduser("~")
CONFIG_FILE = os.path.join(USER_HOME, "projects/Logichem/ansible-dokploy-erpnext", "setup_config.json")

def load_config():
    """Loads the configuration file or returns an empty default structure."""
    if not os.path.exists(CONFIG_FILE):
        save_config({"targets": []})  # Ensure the file exists
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def save_config(config):
    """Saves the configuration back to the file."""
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

def edit_config(config):
    """Allows the user to modify configuration interactively."""
    while True:
        print("\nCurrent Targets:")
        for i, target in enumerate(config.get("targets", []), start=1):
            print(f"{i}. {target['host_alias']} ({target['host_ip_or_name']})")
        print("0. Save and Continue")
        print("N. Add a new target")

        choice = input("Enter number to edit, 0 to continue, or N to add a target: ").strip().lower()
        
        if choice == "0":
            break
        elif choice == "n":
            new_target = {
                "host_alias": input("Enter alias name: ").strip(),
                "host_ip_or_name": input("Enter IP or domain name: ").strip(),
                "ssh_user": input("Enter SSH username: ").strip(),
                "ssh_port": input("Enter SSH port (default 22): ").strip() or "22",
                "identity_file": input("Enter SSH identity file name (default id_rsa): ").strip() or "id_rsa"
            }
            config["targets"].append(new_target)
        else:
            try:
                index = int(choice) - 1
                target = config["targets"][index]
                print("\nEditing target:", target["host_alias"])
                target["host_alias"] = input(f"Enter alias name [{target['host_alias']}]: ").strip() or target["host_alias"]
                target["host_ip_or_name"] = input(f"Enter IP or domain name [{target['host_ip_or_name']}]: ").strip() or target["host_ip_or_name"]
                target["ssh_user"] = input(f"Enter SSH username [{target['ssh_user']}]: ").strip() or target["ssh_user"]
                target["ssh_port"] = input(f"Enter SSH port [{target['ssh_port']}]: ").strip() or target["ssh_port"]
                target["identity_file"] = input(f"Enter SSH identity file name [{target['identity_file']}]: ").strip() or target["identity_file"]
            except (ValueError, IndexError):
                print("Invalid selection, try again.")
    
    return config
