#!/usr/bin/python3

import rancher
import yaml
import os
import datetime

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"
CHECK = "\u2713"
CROSS = "\u2717"


def log_ok(msg):
    now = datetime.datetime.now()
    print(f"{now} {GREEN}{CHECK}{RESET} {msg}")


def log_error(msg):
    now = datetime.datetime.now()
    print(f"{now} {RED}{CROSS}{RESET} {msg}")


def roles_to_url_list(roles):
    rancher_roles = []
    for role in roles:
        if role == "control-plane":
            rancher_roles.append("--controlplane")
        elif role == "etcd":
            rancher_roles.append("--etcd")
        elif role == "worker":
            rancher_roles.append("--worker")
        else:
            raise ValueError(f"Invalid role: {role}")

    return " ".join(rancher_roles)

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
        raise ValueError("Config file is empty")

    return config


def main():
    config = load_config()

    rancher_client = rancher.Client(url=config['rancher']['url'],
                                    access_key=config['rancher']['apiKey'],
                                    secret_key=config['rancher']['secret'], verify=False)

    res = rancher_client.list_cluster()

    search_for = config['rancher']['clusterName']
    log_ok(f"Searching for cluster with name: {search_for}")

    # Find the cluster with the specified name
    clusters = res['data']
    cluster_id = None
    for cluster in clusters:
        if cluster['name'] == search_for:
            cluster_id = cluster['id']
            break

    if cluster_id is None:
        log_error("Cluster not found")
        return

    log_ok(f"Found cluster with ID: {cluster_id}")

    log_ok(
        f"Searching for node registration command for cluster with ID: {cluster_id}")

    # Get the registration token for the cluster
    res = rancher_client.list_cluster_registration_token()

    tokens = res['data']
    nodeCommand = None
    for token in tokens:
        if token['clusterId'] == cluster_id:
            nodeCommand = token['nodeCommand']
            break

    if nodeCommand is None:
        log_error("Node registration command not found")
        return

    # Trim whitespace
    nodeCommand = nodeCommand.strip()
    log_ok(f"Node registration command ({nodeCommand[:50]}...)")

    # Run the node registration command
    roles = config['rancher']['roles']
    url_roles = roles_to_url_list(roles)

    cmd = f"{nodeCommand} {url_roles}"
    log_ok(f"Full command: {cmd}")

    os.system(cmd)

if __name__ == "__main__":
    main()
