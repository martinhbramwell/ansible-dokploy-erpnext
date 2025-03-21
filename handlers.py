#!/usr/bin/env python3

def edit_string(current, default, full_name):
    """
    Prompts the user for a string value.
    Shows the current value or the default if none.
    Returns the entered value, or if empty, the current/default value.
    """
    prompt = f"Enter {full_name}"
    if current:
        prompt += f" [{current}]"
    elif default:
        prompt += f" [{default}]"
    prompt += ": "
    new_val = input(prompt).strip()
    return new_val if new_val else (current if current is not None else default)

def edit_string_list(current, default, full_name):
    """
    Prompts the user for a list of single-line items.
    Instructs the user to enter one item per line and press Enter on an empty line to finish.
    Returns a list of strings.
    """
    print(f"\nEditing {full_name}.")
    if current:
        print(f"Current values: {', '.join(current)}")
    else:
        print("No current values.")
    print("Enter one item per line. Press Enter on an empty line to finish.")
    items = []
    while True:
        line = input("Item: ").strip()
        if line == "":
            break
        items.append(line)
    return items if items else (current if current is not None else default)

def edit_peer_list(current, default, full_name):
    """
    Prompts the user to edit a list of peer configurations.
    Each peer is a dictionary with keys: public_key, allowed_ips, endpoint.
    
    - First, displays the current list (if any) with numbers.
    - Then, offers options:
         E: Edit an existing peer (by number),
         A: Add a new peer,
         F: Finish editing.
    - For editing or adding, each field is prompted with the current value as default.
    - For allowed_ips, the user enters a comma-separated list which is converted to a YAML list.
    
    Returns the updated list of peer dictionaries.
    """
    print(f"\nEditing {full_name}.")
    peers = current if current is not None else []
    while True:
        if peers:
            print("Current peers:")
            for idx, peer in enumerate(peers, start=1):
                allowed_ips_display = ", ".join(peer.get("allowed_ips", []))
                print(f"  {idx}. public_key: {peer.get('public_key', '')}, allowed_ips: [{allowed_ips_display}], endpoint: {peer.get('endpoint', '')}")
        else:
            print("No current peers.")
        print("\nOptions:")
        print("  E: Edit an existing peer (enter the peer number)")
        print("  A: Add a new peer")
        print("  F: Finish editing peers")
        choice = input("Enter option (E/A/F): ").strip().lower()
        if choice == "f":
            break
        elif choice == "a":
            print("\nAdding a new peer:")
            public_key = input("Enter public_key: ").strip()
            if not public_key:
                print("public_key is required for a new peer; skipping addition.")
                continue
            allowed_ips_input = input("Enter allowed_ips (comma-separated): ").strip()
            allowed_ips_list = [ip.strip() for ip in allowed_ips_input.split(",") if ip.strip()]
            endpoint = input("Enter endpoint: ").strip()
            new_peer = {
                "public_key": public_key,
                "allowed_ips": allowed_ips_list,
                "endpoint": endpoint
            }
            peers.append(new_peer)
        elif choice.isdigit():
            idx = int(choice) - 1
            if idx < 0 or idx >= len(peers):
                print("Invalid peer number; please try again.")
                continue
            peer = peers[idx]
            print(f"\nEditing peer {idx+1}:")
            public_key = input(f"Enter public_key [{peer.get('public_key', '')}]: ").strip() or peer.get("public_key", "")
            allowed_ips_current = ", ".join(peer.get("allowed_ips", []))
            allowed_ips_input = input(f"Enter allowed_ips (comma-separated) [{allowed_ips_current}]: ").strip()
            if allowed_ips_input:
                allowed_ips_list = [ip.strip() for ip in allowed_ips_input.split(",") if ip.strip()]
            else:
                allowed_ips_list = peer.get("allowed_ips", [])
            endpoint = input(f"Enter endpoint [{peer.get('endpoint', '')}]: ").strip() or peer.get("endpoint", "")
            peer["public_key"] = public_key
            peer["allowed_ips"] = allowed_ips_list
            peer["endpoint"] = endpoint
            peers[idx] = peer
        else:
            print("Invalid option. Please enter a number for editing, or 'A' to add, or 'F' to finish.")
    return peers if peers else (current if current is not None else default)

def edit_embedded_file(current, default, full_name):
    """
    Prompts the user for a file path.
    The returned value is embedded using a constant template so that the final result is:
      {{ lookup('file', '/path/to/file') }}
    """
    print(f"\nEditing {full_name}.")
    # Define the template parts.
    prefix = "{{ lookup('file', '"
    suffix = "') }}"
    # If current is set and appears to be already in the expected format, extract the file path.
    if current and current.startswith("{{") and current.endswith("}}"):
        # We assume the current value starts with prefix and ends with suffix.
        current_value = current[len(prefix):-len(suffix)]
    else:
        current_value = current or default
    user_input = input(f"Enter file path [{current_value}]: ").strip()
    # file_path = user_input if user_input else current_value
    # Return exactly: {{ lookup('file', '/path/to/file') }}
    return f"{{{{ lookup('file', '{user_input}') }}}}"


if __name__ == "__main__":
    # Test the edit_embedded_file handler from the command line.
    print("Testing edit_embedded_file()")
    current = ""
    default = "/etc/wireguard/privatekey"
    full_name = "Private key path"

    
    result = edit_embedded_file(current, default, full_name)
    # result = f"\"{{{{ lookup('file', '{default}') }}}}\""
    print("\nCorrect Result:")
    print("{{ lookup(\'file\', \'/etc/wireguard/privatekey\') }}")
    print("Result:")
    print(result)

