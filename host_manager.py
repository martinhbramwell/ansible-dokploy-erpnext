import os

HOSTS_FILE = "/etc/hosts"

def update_hosts_file(target):
    """Adds the target alias to /etc/hosts if not already present."""
    entry = f"{target['host_ip_or_name']} {target['host_alias']}\n"

    with open(HOSTS_FILE, "r+") as hosts_file:
        hosts = hosts_file.readlines()
        if any(entry.strip() in line.strip() for line in hosts):
            print(f"{target['host_alias']} is already in /etc/hosts. Skipping update.")
            return

        # Append the new entry and save
        hosts_file.write(entry)
        print(f"Added {target['host_alias']} to /etc/hosts")
