#!/usr/bin/python3

import sys
import os
import yaml

k3s_curl = "curl -sfL https://get.k3s.io"


def load_config():
    possible_places = [
        "/etc/kthcloud/setup-config.yml",
        "/etc/kthcloud/setup-config.yaml"
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


def connect(nodeType: str, server_url: str = None, token: str = None):
    """
        Connect as a cluster node to the K3s system cluster

        This can be either as a server or an agent (master=server, worker=agent)

        server_url and token are required if role is "worker"
    """

    if nodeType not in ["master", "worker"]:
        raise ValueError("Role must be either 'master' or 'worker'")

    if nodeType == "worker" and (server_url is None or token is None):
        raise ValueError("server_url and token are required for worker nodes")

    if nodeType == "master":
        print("Creating a new K3s cluster")

        # Run curl command to install K3s
        cmd = f"{k3s_curl} | sh -"
        os.system(cmd)
        # Set permission for kubeconfig
        os.system("chmod 644 /etc/rancher/k3s/k3s.yaml")

    elif nodeType == "worker":
        print("Joining an existing K3s cluster")

        # Run curl command to install K3s
        cmd = f"{k3s_curl} | K3S_URL={server_url} K3S_TOKEN={token} sh -"
        os.system(cmd)


def main():
    config = load_config()

    # Get the role of the node
    nodeType = config["k8s"]["nodeType"]
    if nodeType == "worker":
        try:
            server_url = config["k8s"]["server_url"]
            token = config["k8s"]["token"]
        except KeyError:
            raise ValueError(
                "server_url and token are required for worker nodes")
        
        connect(nodeType, server_url, token)
    else:
        connect(nodeType)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
