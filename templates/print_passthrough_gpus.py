#!/usr/bin/python3

import subprocess
import json
import sys
import os
import yaml

def output_empty():
    print(json.dumps({"bus_ids": "", "device_ids": "", "has_non_passthrough": False, "requires_configuration": False}))
    sys.exit(0)

def output(data):
    print(json.dumps(data))
    sys.exit(0)

def run_cmd(cmd):
    proc = subprocess.Popen([cmd], stdout=subprocess.PIPE, shell=True)
    (res, _) = proc.communicate()
    proc.wait()
    return res

def load_config():
    possible_places = [
        "/etc/kthcloud/config.yml",
        "/etc/kthcloud/config.yaml",
        "./config.yml",
        "./config.yaml"
    ]

    config = None
    for file in possible_places:
        if os.path.exists(file):
            with open(file, "r") as f:
                config = yaml.safe_load(f)
                break

    if config is None:
        raise ValueError("Failed to load config file")

    return config


def main():
    config = load_config()

    gpu_cmd = "lspci -knnmmvvv | jc --lspci"
    res = run_cmd(gpu_cmd)
    if len(res) == 0:
        output_empty()

    devices = json.loads(res)
    bus_ids = []
    device_ids = set()

    # Which GPUs that should not be passthrough
    # Any name in the config will be regex matched against the device name
    skip_gpus = []
    if "noPassthroughGpus" in config:
        skip_gpus = config["noPassthroughGpus"]

    requires_configuration = False
    has_non_passthrough = False

    for device in devices:
        skip = False

        if "driver" not in device:
            continue

        for skip_gpu in [item for item in skip_gpus if "device" in device]:
            skip = skip_gpu.lower() in device["device"].lower()
            if skip:
                break

        if skip:
            # Check if the device is already set up for passthrough
            if device["driver"] != "nvidia":
                requires_configuration = True
            
            has_non_passthrough = True
            continue


        if "NVIDIA" in device["vendor"]:
            if device["driver"] != "vfio-pci":
                requires_configuration = True

            bus_ids.append(device["slot"])
            device_ids.add(device["vendor_id"] + ":" + device["device_id"])

    output({
        "bus_ids": " ".join(bus_ids),
        "device_ids": ",".join(device_ids),
        "has_non_passthrough": has_non_passthrough,
        "requires_configuration": requires_configuration
    })

if __name__ == "__main__":
    try:
        main() 
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        exit(1)
    except KeyboardInterrupt:
        print("Interrupted by user", file=sys.stderr)
        exit(1)