import os
import subprocess

HOSTS_FILE = "/etc/hosts"

def update_hosts_file(target):
    """Adds the target alias to /etc/hosts if not already present using sudo -A and tee."""
    entry = f"{target['host_ip_or_name']} {target['host_alias']}\n"

    # Read /etc/hosts (which is typically world-readable)
    try:
        with open(HOSTS_FILE, "r") as hosts_file:
            hosts = hosts_file.read()
    except Exception as e:
        print("ERROR reading /etc/hosts:", e)
        return

    if entry.strip() in hosts:
        print(f"{target['host_alias']} is already in {HOSTS_FILE}. Skipping update.")
        return

    # Use sudo -A and tee to append the entry to /etc/hosts
    try:
        # The command echoes the entry and pipes it to sudo -A tee -a /etc/hosts
        cmd = f'echo "{entry.strip()}" | sudo -A tee -a {HOSTS_FILE}'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Added {target['host_alias']} to {HOSTS_FILE}")
        else:
            print("ERROR updating /etc/hosts:", result.stderr)
    except Exception as e:
        print("Exception while updating /etc/hosts:", e)
