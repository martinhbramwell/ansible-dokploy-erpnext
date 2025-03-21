#!/usr/bin/env python3
import os
import sys
import json

from env_validator import validate_environment
from config_manager import load_all_configs, edit_config
from ssh_manager import setup_ssh_access, check_ssh_access
from host_manager import update_hosts_file
from inventory_manager import generate_inventory
from ansible_manager import obtain_roles, choose_inventory_groups, run_group_playbooks

# Use current user's home directory
USER_HOME = os.path.expanduser("~")

# Set the project directory based on the current user's home
PROJECT_DIR = os.path.join(USER_HOME, "projects/Logichem/ansible-dokploy-erpnext")

def preAnsible():
    # Validate environment dependencies, configurations, and required roles.
    validate_environment()

    # Interactively edit, and save configuration (non-secret target details)
    # configs = load_all_configs()
    configs = convert_configs_to_dict(edit_config())
    # save_config(config)

    # print("configs")
    # print(json.dumps(configs, indent=4))

    # Process each target defined in the configuration.
    # for target in config.get("targets", []):
    for config in configs:
        target = configs[config]
        # print("target")
        # print(json.dumps(target, indent=4))
        print(f"\nProcessing target: {target['host_alias']} ({target['host_ip_or_name']})")

        # Check SSH access; if not available, attempt configuration.
        if check_ssh_access(target):
            print(f"SSH access confirmed for {target['host_alias']}. Skipping SSH setup.")
        else:
            print(f"Configuring SSH access for {target['host_alias']}...")
            setup_ssh_access(target, configure=True)
            if not check_ssh_access(target):
                print(f"ERROR: SSH setup failed for {target['host_alias']}. Skipping this target.")
                continue

    # Update /etc/hosts on the control machine (using sudo -A)
    update_hosts_file(target)

    obtain_roles()



    # generate_inventory()
    groups_to_process = choose_inventory_groups()
    if groups_to_process:
        # Proceed with processing the selected groups.
        print("Processing groups:", groups_to_process)
        run_group_playbooks(groups_to_process)
    else:
        print("No groups selected or exiting.")

    print("\nAnsible control machine setup is complete! 🚀")

def convert_configs_to_dict(configs):
    """
    Converts a list of host configuration dictionaries into a dict keyed by host_alias.
    
    For example, given:
    [
        {"host_alias": "erp2nd", "host_ip_or_name": "192.168.122.131", ...},
        {"host_alias": "erptst", "host_ip_or_name": "192.168.122.172", ...}
    ]
    
    It returns:
    {
      "erp2nd": {"host_alias": "erp2nd", "host_ip_or_name": "192.168.122.131", ...},
      "erptst": {"host_alias": "erptst", "host_ip_or_name": "192.168.122.172", ...}
    }
    """
    result = {}
    for conf in configs:
        alias = conf.get("host_alias")
        if alias:
            result[alias] = conf
    return result

if __name__ == "__main__":

    if 0 == 1:
        print("Preparing remote servers...")
        configs = convert_configs_to_dict(load_all_configs())
        # print("configs")
        # print(json.dumps(configs, indent=4))

        for config in configs:
            target = configs[config]
            # print("target")
            # print(json.dumps(target, indent=4))
            print(f"\nProcessing target: {target['host_alias']} ({target['host_ip_or_name']})")
            print(setup_ssh_access(target, configure=True))
            # print(check_ssh_access(target))

            # # Check SSH access; if not available, attempt configuration.
            # if check_ssh_access(target):
            #     print(f"SSH access confirmed for {target['host_alias']}. Skipping SSH setup.")
            # else:
            #     print(f"Configuring SSH access for {target['host_alias']}...")
            #     setup_ssh_access(target, configure=True)
            #     if not check_ssh_access(target):

            #         print(f"ERROR: SSH setup failed for {target['host_alias']}. Skipping this target.")
            #         continue

        print(f" -------------- CURTAILED -----------------")
        sys.exit()

    preAnsible()
