# Install Python3 and pip
apt-get update && apt-get install -y python3 python3-pip

# Install Ansible using Python pip
pip3 install ansible

# Clone the specified git repository
cd /home/cloud
git clone https://github.com/kthcloud/ansible-setup-host.git

# Run the Ansible playbook
cd /home/cloud/ansible-setup-host
ansible-playbook setup-host.yml