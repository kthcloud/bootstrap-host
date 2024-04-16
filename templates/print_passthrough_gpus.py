#!/usr/bin/python3

import subprocess
import json
import sys


def output_empty():
    print(json.dumps({"bus_ids": "", "device_ids": "", "has_non_passthrough": False, "requires_configuration": False}))

def output(data):
    print(json.dumps(data))

def run_cmd(cmd):
    proc = subprocess.Popen([cmd], stdout=subprocess.PIPE, shell=True)
    (res, _) = proc.communicate()
    proc.wait()

    return res

gpu_cmd = "lspci -knnmmvvv | jc --lspci"
res = run_cmd(gpu_cmd)
if len(res) == 0:
    output_empty()
    sys.exit(0)

devices = json.loads(res)
bus_ids = []
device_ids = set()
# Run the gpu_cmd to find out what to skip
skip_gpus = [
    {"vendor": "NVIDIA", "device": "RTX A6000"},
]

requires_configuration = False
has_non_passthrough = False

for device in devices:
    skip = False

    for skip_gpu in [item for item in skip_gpus if "device" in device and "vendor" in device]:
        skip = skip_gpu["vendor"].lower() in device["vendor"].lower() and skip_gpu["device"].lower() in device["device"].lower()
        if skip:
            break

    if skip:
        # Check if the device is already set up for passthrough
        if "driver" not in device or "vfio-pci" in device["driver"]:
            requires_configuration = True
        
        has_non_passthrough = True
        continue


    if "NVIDIA" in device["vendor"]:
        bus_ids.append(device["slot"])
        device_ids.add(device["vendor_id"] + ":" + device["device_id"])
        if "driver" not in device or "vfio-pci" not in device["driver"]:
            requires_configuration = True

output({
    "bus_ids": " ".join(bus_ids),
    "device_ids": ",".join(device_ids),
    "has_non_passthrough": has_non_passthrough,
    "requires_configuration": requires_configuration
})