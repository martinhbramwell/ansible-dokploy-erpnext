#!/usr/bin/env python3
import os
import sys
import subprocess
import glob
import yaml


def find_roles_in_data(data, roles_set):
    """
    Recursively traverse the YAML data structure to find role inclusion declarations.
    When a key 'ansible.builtin.include_role' is found, if its value is a dict,
    the function extracts the role name from the 'name' key and adds it to roles_set.
    """
    if isinstance(data, dict):
        for key, value in data.items():
            if key == "ansible.builtin.include_role":
                if isinstance(value, dict):
                    role_name = value.get("name")
                    if role_name:
                        roles_set.add(role_name)
                elif isinstance(value, str):
                    roles_set.add(value)
            else:
                find_roles_in_data(value, roles_set)
    elif isinstance(data, list):
        for element in data:
            find_roles_in_data(element, roles_set)

def obtain_roles():
    """
    Searches all YAML files in the "playbooks" directory for any occurrences
    of a "roles:" key, builds a set of the roles found, and installs each role
    via ansible-galaxy into ${HOME}/.ansible/roles.
    """
    roles_found = set()
    playbooks_dir = "playbooks"
    # Collect YAML files (both .yml and .yaml) in the playbooks directory.
    yaml_files = glob.glob(os.path.join(playbooks_dir, "*.yml")) + glob.glob(os.path.join(playbooks_dir, "*.yaml"))
    
    if not yaml_files:
        print("No YAML files found in the 'playbooks' directory.")
        return

    for yaml_file in yaml_files:
        try:
            with open(yaml_file, "r") as f:
                print(f"Examining YAML file: {yaml_file}.")
                # In case a file has multiple YAML documents, use safe_load_all.
                docs = yaml.safe_load_all(f)
                for doc in docs:
                    if doc is not None:
                        find_roles_in_data(doc, roles_found)
        except Exception as e:
            print(f"Error processing file '{yaml_file}': {e}")

    if not roles_found:
        print("No roles found in the playbooks directory.")
        return

    print("Roles found in playbooks:")
    for role in sorted(roles_found):
        print(f"  - {role}")

    # Get the user's home directory.
    home = os.environ.get("HOME")
    if not home:
        print("Error: HOME environment variable is not set.")
        return

    roles_path = os.path.join(home, ".ansible", "roles")
    os.makedirs(roles_path, exist_ok=True)

    # Install each role via ansible-galaxy.
    for role in sorted(roles_found):
        command = f"ansible-galaxy install {role} --roles-path {roles_path}"
        print(f"Installing role: {role}")
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error installing {role}:\n{result.stderr}")
        else:
            print(f"Successfully installed {role}")

def choose_inventory_groups():
    """
    Reads 'inventory.ini' from the current directory, extracts group names,
    and presents a numbered list with options to process one group, all groups, or exit.
    Returns a list of group names or None if the user exits.
    """
    inventory_file = "inventory.ini"
    if not os.path.exists(inventory_file):
        print(f"Error: {inventory_file} not found in the current directory.")
        return None

    groups = []
    with open(inventory_file, "r") as f:
        for line in f:
            line = line.strip()
            if line.startswith("[") and line.endswith("]"):
                group_name = line[1:-1].strip()
                if group_name:
                    groups.append(group_name)

    if not groups:
        print("No groups found in the inventory file.")
        return None

    print("Select a group to process:")
    for index, group in enumerate(groups, start=1):
        print(f"{index}. {group}")
    print(f"{len(groups)+1}. All groups")
    print(f"{len(groups)+2}. Exit")

    while True:
        try:
            choice = int(input("Enter your choice number: "))
        except ValueError:
            print("Invalid input. Please enter a number.")
            continue

        if choice == len(groups) + 2:
            print("Exiting...")
            return None
        elif choice == len(groups) + 1:
            return groups
        elif 1 <= choice <= len(groups):
            return [groups[choice - 1]]
        else:
            print("Choice out of range. Please try again.")

def run_group_playbooks(selected_groups):
    """
    Iterates through the provided list of group names and, for each,
    executes the playbook <group>.yml using the inventory file 'inventory.ini'.
    
    Example command for group 'docker_hosts':
      ansible-playbook -i inventory.ini docker_hosts.yml
    """
    inventory_file = "inventory.ini"
    for group in selected_groups:
        playbook = f"{group}.yml"
        command = f"ansible-playbook -i {inventory_file} ./playbooks/{playbook}"
        print(f"Executing playbook for group '{group}': {command}")
        result = subprocess.run(command, shell=True, stdout=sys.stdout, stderr=sys.stderr, text=True)
        if result.returncode != 0:
            print(f"Error executing playbook for group '{group}':\n{result.stderr}")
        else:
            print(f"Successfully executed playbook for group '{group}'.\nOutput:\n{result.stdout}")

if __name__ == "__main__":
    # For testing purposes, allow the user to choose groups and run playbooks.
    selected_groups = choose_inventory_groups()
    if selected_groups:
        run_group_playbooks(selected_groups)
    else:
        print("No groups selected or exiting.")


