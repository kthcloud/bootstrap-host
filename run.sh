# Install Python3 and pip
apt-get update && apt-get install -y python3 python3-pip

# Install Ansible using Python pip
pip3 install ansible

# Run the ansible playbook
ansible-playbook setup-host.yml