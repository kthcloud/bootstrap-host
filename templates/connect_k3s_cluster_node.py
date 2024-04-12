#!/usr/bin/python3

import sys
import os
import yaml

k3s_curl = "curl -sfL https://get.k3s.io"
k3s_version = "v1.27.11+k3s1"


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
        cmd = f"{k3s_curl} | | INSTALL_K3S_VERSION={k3s_version} INSTALL_K3S_EXEC=\"server --write-kubeconfig-mode=644 --disable=traefik --disable=servicelb\" sh -"
        os.system(cmd)

    elif nodeType == "worker":
        print("Joining an existing K3s cluster")

        # Run curl command to install K3s
        cmd = f"{k3s_curl} | K3S_URL={server_url} K3S_TOKEN={token} sh -"
        os.system(cmd)


def main():
    config = load_config()

    # Get the role of the node
    nodeType = config["nodeType"]
    if nodeType == "worker":
        try:
            server_url = config["k3s"]["serverUrl"]
            token = config["k3s"]["nodeToken"]
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
