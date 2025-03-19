#!/usr/bin/env python3
import json
import os

def generate_inventory():
    """
    Reads the setup_config.json file from the current directory,
    groups targets by their 'group' value, and writes an inventory.ini file.
    
    Expected JSON structure:
    {
        "targets": [
            {
                "host_alias": "erptst",
                "host_ip_or_name": "192.168.122.172",
                "ssh_user": "you",
                "ssh_port": "22",
                "identity_file": "id_rsa",
                "group": "docker_hosts"
            },
            {
                "host_alias": "erp1st",
                "host_ip_or_name": "192.168.122.131",
                "ssh_user": "joe",
                "ssh_port": "22",
                "identity_file": "id_rsa",
                "group": "controllers"
            },
            {
                "host_alias": "erp2nd",
                "host_ip_or_name": "192.168.122.131",
                "ssh_user": "boss",
                "ssh_port": "22",
                "identity_file": "id_rsa",
                "group": "docker_hosts"
            }
        ]
    }
    """
    config_file = "setup_config.json"
    inventory_file = "inventory.ini"
    
    if not os.path.exists(config_file):
        print(f"Error: {config_file} not found in the current directory.")
        return
    
    with open(config_file, "r") as f:
        config = json.load(f)
    
    targets = config.get("targets", [])
    if not targets:
        print("No targets found in configuration.")
        return
    
    # Group targets by the 'group' key.
    groups = {}
    for target in targets:
        group = target.get("group", "ungrouped")
        groups.setdefault(group, []).append(target)
    
    # Build the inventory file content.
    inventory_lines = []
    for group, hosts in groups.items():
        inventory_lines.append(f"[{group}]")
        for host in hosts:
            # Use host_alias as the inventory host entry.
            # You could include ansible_host if desired, e.g.:
            # f"{host['host_alias']} ansible_host={host['host_ip_or_name']} ansible_user={host['ssh_user']} ansible_become=true"
            # But following your example:
            line = f"{host['host_alias']} ansible_user={host['ssh_user']} ansible_become=true"
            inventory_lines.append(line)
        inventory_lines.append("")  # blank line between groups

    inventory_content = "\n".join(inventory_lines)
    
    with open(inventory_file, "w") as f:
        f.write(inventory_content)
    
    print(f"Inventory written to {inventory_file}")

if __name__ == "__main__":
    generate_inventory()
