# 📦 Installation Guide

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [System Requirements](#system-requirements)
3. [Installation Steps](#installation-steps)
4. [Verification](#verification)
5. [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Tools
- **Operating System**: Ubuntu 20.04+ / Debian 11+ / macOS / Windows (WSL2)
- **RAM**: Minimum 8GB (16GB recommended)
- **Disk Space**: Minimum 20GB free
- **Internet Connection**: Required for downloading packages

### Software Dependencies
- Git
- Docker & Docker Compose
- Kubernetes (kubectl + Minikube)
- Ansible
- Terraform
- Python 3.9+

## System Requirements

### Minimum Requirements
- CPU: 2 cores
- RAM: 4GB
- Disk: 10GB

### Recommended Requirements
- CPU: 4 cores
- RAM: 8GB
- Disk: 20GB

## Installation Steps

### 1. Install Git

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y git

# Verify installation
git --version
```

### 2. Install Docker

```bash
# Remove old versions (if any)
sudo apt remove docker docker-engine docker.io containerd runc

# Install using convenience script
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add your user to docker group (to run docker without sudo)
sudo usermod -aG docker $USER

# Apply group changes (or logout/login)
newgrp docker

# Verify installation
docker --version
docker run hello-world
```

### 3. Install Docker Compose

```bash
# Download latest version
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# Make it executable
sudo chmod +x /usr/local/bin/docker-compose

# Create symbolic link
sudo ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose

# Verify installation
docker-compose --version
```

### 4. Install kubectl

```bash
# Download latest stable version
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"

# Validate binary (optional)
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl.sha256"
echo "$(cat kubectl.sha256)  kubectl" | sha256sum --check

# Install kubectl
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Verify installation
kubectl version --client
```

### 5. Install Minikube

```bash
# Download Minikube
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64

# Install Minikube
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# Verify installation
minikube version

# Start Minikube with Docker driver
minikube start --driver=docker --cpus=4 --memory=4096

# Verify cluster is running
kubectl cluster-info
kubectl get nodes
```

### 6. Install Ansible

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y software-properties-common
sudo add-apt-repository --yes --update ppa:ansible/ansible
sudo apt install -y ansible

# Verify installation
ansible --version

# Install required Python packages for Ansible
pip3 install kubernetes openshift pyyaml
```

### 7. Install Terraform

```bash
# Add HashiCorp GPG key
wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg

# Add HashiCorp repository
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list

# Install Terraform
sudo apt update
sudo apt install -y terraform

# Verify installation
terraform --version
```

### 8. Install Python and Dependencies

```bash
# Install Python 3.9+
sudo apt update
sudo apt install -y python3 python3-pip python3-venv

# Verify installation
python3 --version
pip3 --version

# Install application dependencies (from project directory)
cd app
pip3 install -r requirements.txt
```

### 9. Clone the Project

```bash
# Clone from your repository
git clone <your-repo-url> transport-optimization-devops
cd transport-optimization-devops

# Or if you extracted from tar
cd transport-optimization-devops
```

### 10. Configure Environment

```bash
# Create .env file for local development
cat > .env << EOF
FLASK_ENV=development
ORS_API_KEY=your_openrouteservice_api_key_here
PORT=5000
EOF

# Make scripts executable (if any)
chmod +x scripts/*.sh
```

## Verification

### Verify All Tools

```bash
# Create a verification script
cat > verify-tools.sh << 'EOF'
#!/bin/bash

echo "🔍 Verifying installed tools..."
echo ""

# Docker
echo -n "Docker: "
docker --version && echo "✅" || echo "❌"

# Docker Compose
echo -n "Docker Compose: "
docker-compose --version && echo "✅" || echo "❌"

# kubectl
echo -n "kubectl: "
kubectl version --client --short && echo "✅" || echo "❌"

# Minikube
echo -n "Minikube: "
minikube version && echo "✅" || echo "❌"

# Ansible
echo -n "Ansible: "
ansible --version | head -n1 && echo "✅" || echo "❌"

# Terraform
echo -n "Terraform: "
terraform --version | head -n1 && echo "✅" || echo "❌"

# Python
echo -n "Python: "
python3 --version && echo "✅" || echo "❌"

echo ""
echo "🎯 Checking Kubernetes cluster..."
kubectl cluster-info && echo "✅ Cluster is running" || echo "❌ Cluster not running"

echo ""
echo "✅ Verification complete!"
EOF

chmod +x verify-tools.sh
./verify-tools.sh
```

### Test Basic Functionality

```bash
# Test Docker
docker run hello-world

# Test Kubernetes
kubectl get nodes

# Test application locally
cd app
python3 app.py
# Open browser: http://localhost:5000
```

## Troubleshooting

### Docker Permission Denied

```bash
# If you get "permission denied" error
sudo usermod -aG docker $USER
newgrp docker

# Or logout and login again
```

### Minikube Won't Start

```bash
# Delete existing cluster
minikube delete

# Start fresh
minikube start --driver=docker --cpus=4 --memory=4096

# If driver issues persist, try virtualbox
minikube start --driver=virtualbox
```

### kubectl Connection Refused

```bash
# Check if Minikube is running
minikube status

# Restart Minikube
minikube stop
minikube start

# Update kubectl config
minikube update-context
```

### Python Module Not Found

```bash
# Install in virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r app/requirements.txt
```

### Port Already in Use

```bash
# Find process using port 5000
lsof -ti:5000

# Kill the process
kill -9 $(lsof -ti:5000)

# Or use different port
export PORT=5001
```

### Terraform State Lock

```bash
# If terraform state is locked
cd terraform
terraform force-unlock <LOCK_ID>
```

### Ansible Connection Issues

```bash
# Test Ansible connectivity
ansible all -i inventory -m ping

# Run with verbose mode
ansible-playbook -i inventory playbooks/setup.yml -vvv
```

## Next Steps

After successful installation:

1. ✅ Read [DEPLOYMENT.md](DEPLOYMENT.md) for deployment instructions
2. ✅ Read [ARCHITECTURE.md](ARCHITECTURE.md) for system architecture
3. ✅ Start with local development: `docker-compose up`
4. ✅ Deploy to Kubernetes: `kubectl apply -f kubernetes/`

## Getting Help

- Check logs: `docker logs <container-name>`
- Kubernetes logs: `kubectl logs <pod-name>`
- GitHub Issues: Create an issue in the repository
- Documentation: Check the docs/ folder

---

**Installation Complete! 🎉**

You're now ready to start working with the Transport Optimization System!
