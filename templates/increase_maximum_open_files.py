#!/usr/bin/python3

import os

GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"
CHECK = "\u2713"
CROSS = "\u2717"

GREEN_CHECK = f"{GREEN}{CHECK}{RESET}"
RED_CROSS = f"{RED}{CROSS}{RESET}"

# System defaults for comparison
default_max_user_instances = 128
default_max_queued_events = 16384
default_max_user_watches = 8192

# Total available memory in KB for the inotify settings
available_memory_kb = 2 * 1024 * 1024  # 2 GB in KB

# Calculate the total "weight" based on default values to keep the same ratio
total_weight = default_max_user_watches + default_max_user_watches + default_max_user_watches

# Calculate how much memory each "unit" represents
memory_per_unit = available_memory_kb / total_weight

def allocate():
    # Allocate memory based on the original ratio
    commands = [
        f"sudo sysctl -w fs.inotify.max_user_watches={int(memory_per_unit * default_max_user_watches)} > /dev/null 2>&1",
        f"sudo sysctl -w fs.inotify.max_user_instances={int(memory_per_unit * default_max_user_instances)} > /dev/null 2>&1",
        f"sudo sysctl -w fs.inotify.max_queued_events={int(memory_per_unit * default_max_queued_events)} > /dev/null 2>&1",
    ]

    for command in commands:
        res = os.system(command)
        if res != 0:
            raise Exception(f"Failed to run command: {command} ({res})")
        print(f"{GREEN_CHECK} {command}")


def main():
    try:
        allocate()
    except Exception as e:
        print(f"{RED_CROSS} {e}")
        return
    except KeyboardInterrupt:
        print(f"{RED_CROSS} Aborted")
        return

    print(f"\n{GREEN_CHECK} Successfully allocated memory for inotify")

if __name__ == "__main__":
    main()