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
skip_gpus = ["RTX A600"]

requires_configuration = False
has_non_passthrough = False

for device in devices:
    should_skip = False
    for skip_gpu in [item for item in skip_gpus if "device" in device]:
        if skip_gpu in device["device"]:
            break

    if should_skip:
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