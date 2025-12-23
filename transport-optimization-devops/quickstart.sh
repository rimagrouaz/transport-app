#!/bin/bash

# Transport Optimization - Quick Start Script
# This script helps you quickly get started with the application

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_header() {
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Main script
main() {
    print_header "🚀 Transport Optimization - Quick Start"
    
    # Check prerequisites
    print_info "Checking prerequisites..."
    
    if ! command_exists docker; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    print_success "Docker is installed"
    
    if ! command_exists docker-compose; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    print_success "Docker Compose is installed"
    
    # Show menu
    echo ""
    echo "How would you like to start the application?"
    echo ""
    echo "1) Local Development (Python)"
    echo "2) Docker Compose (Recommended for beginners)"
    echo "3) Kubernetes (Minikube)"
    echo "4) Full Setup (Install all tools)"
    echo "5) Exit"
    echo ""
    read -p "Enter your choice [1-5]: " choice
    
    case $choice in
        1)
            start_local
            ;;
        2)
            start_docker_compose
            ;;
        3)
            start_kubernetes
            ;;
        4)
            full_setup
            ;;
        5)
            print_info "Exiting..."
            exit 0
            ;;
        *)
            print_error "Invalid choice"
            exit 1
            ;;
    esac
}

# Start local development
start_local() {
    print_header "🐍 Starting Local Development"
    
    cd app
    
    print_info "Installing dependencies..."
    pip3 install -r requirements.txt
    
    print_info "Starting Flask application..."
    export FLASK_ENV=development
    export PORT=5000
    
    print_success "Application starting..."
    print_info "Access at: http://localhost:5000"
    
    python3 app.py
}

# Start with Docker Compose
start_docker_compose() {
    print_header "🐳 Starting with Docker Compose"
    
    print_info "Building and starting containers..."
    cd docker
    docker-compose up -d
    
    print_success "Containers started!"
    print_info "Application URL: http://localhost:5000"
    print_info "Grafana URL: http://localhost:3000 (admin/admin)"
    print_info "Prometheus URL: http://localhost:9090"
    
    echo ""
    print_info "View logs: docker-compose logs -f"
    print_info "Stop containers: docker-compose down"
}

# Start with Kubernetes
start_kubernetes() {
    print_header "☸️  Starting with Kubernetes"
    
    # Check if kubectl and minikube are installed
    if ! command_exists kubectl; then
        print_error "kubectl is not installed. Please install kubectl first."
        exit 1
    fi
    
    if ! command_exists minikube; then
        print_error "Minikube is not installed. Please install Minikube first."
        exit 1
    fi
    
    # Check if Minikube is running
    print_info "Checking Minikube status..."
    if ! minikube status >/dev/null 2>&1; then
        print_info "Starting Minikube..."
        minikube start --driver=docker --cpus=4 --memory=4096
        
        print_info "Enabling addons..."
        minikube addons enable ingress
        minikube addons enable metrics-server
    fi
    print_success "Minikube is running"
    
    # Apply Kubernetes manifests
    print_info "Deploying application to Kubernetes..."
    kubectl apply -f kubernetes/
    
    print_info "Waiting for deployment..."
    kubectl wait --for=condition=available --timeout=300s deployment/transport-app
    
    print_success "Application deployed!"
    
    # Get access URL
    print_info "Getting service URL..."
    SERVICE_URL=$(minikube service transport-app-service --url)
    
    print_success "Deployment complete!"
    print_info "Application URL: $SERVICE_URL"
    print_info "Or access via: http://localhost:30080 (with minikube tunnel)"
    
    echo ""
    print_info "Useful commands:"
    echo "  - View pods: kubectl get pods"
    echo "  - View logs: kubectl logs -l app=transport-app -f"
    echo "  - Scale: kubectl scale deployment transport-app --replicas=5"
}

# Full setup
full_setup() {
    print_header "🛠️  Full Setup"
    
    print_info "This will install all required tools..."
    print_warning "This may take several minutes..."
    
    read -p "Continue? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
    
    print_info "Running Ansible setup playbook..."
    cd ansible
    
    if ! command_exists ansible; then
        print_error "Ansible is not installed. Installing Ansible..."
        sudo apt update
        sudo apt install -y ansible
    fi
    
    ansible-playbook -i inventory playbooks/setup.yml
    
    print_success "Setup complete!"
}

# Run main function
main
