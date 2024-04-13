#!/usr/bin/python3

import rancher
import yaml
import os

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

    rancher_client.list_clusters()

    

if __name__ == "__main__":
    main()