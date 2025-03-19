#!/usr/bin/env python3
import os
import sys
import subprocess
import glob
import yaml

def obtain_roles():
    """
    Searches all YAML files in the "playbooks" directory for any occurrences
    of a "roles:" key, builds a set of the roles found, and installs each role
    via ansible-galaxy into ${HOME}/.ansible/roles.
    """
    # (Code for obtain_roles as implemented previously)
    pass  # Assume this function exists as defined earlier

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


