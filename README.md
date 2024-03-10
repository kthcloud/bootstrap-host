# 🛠️ kthcloud/boostrap-host

*This repository is meant to replace the [kthcloud/ansible-setup-host](https://github.com/kthcloud/ansible-setup-host) repository.*

This Ansible playbook will setup a kthcloud host with all the necessary settings and tools to be used as a kthcloud host.
This include configuring libvirt, settings up GPU passthrough, and installing [kthcloud/host-api](https://github.com/kthcloud/host-api).

The playbook is designed to be run locally on the host, and is fetched automatically in a cloud-init script. The cloud-init scripts are kept in the private admin repository. 
