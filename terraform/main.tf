# Terraform configuration for Transport Optimization Infrastructure
# This example uses local Docker provider for development
# For production, replace with cloud providers (AWS, GCP, Azure)

terraform {
  required_version = ">= 1.0"
  
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.23"
    }
  }
  
  # Backend configuration for state management
  # Uncomment for remote state storage
  # backend "local" {
  #   path = "terraform.tfstate"
  # }
}

# Docker Provider Configuration
provider "docker" {
  host = "unix:///var/run/docker.sock"
}

# Kubernetes Provider Configuration
provider "kubernetes" {
  config_path = "~/.kube/config"
}

# Docker Network
resource "docker_network" "transport_network" {
  name = var.network_name
  
  ipam_config {
    subnet  = "172.20.0.0/16"
    gateway = "172.20.0.1"
  }
}

# Docker Image Build
resource "null_resource" "docker_build" {
  triggers = {
    always_run = timestamp()
  }
  
  provisioner "local-exec" {
    command = <<-EOT
      cd ${path.module}/../docker
      docker build -t ${var.docker_image}:${var.app_version} -f Dockerfile ../app
    EOT
  }
}

# Docker Container
resource "docker_container" "transport_app" {
  depends_on = [null_resource.docker_build]
  
  name  = var.container_name
  image = "${var.docker_image}:${var.app_version}"
  
  ports {
    internal = 5000
    external = var.app_port
  }
  
  env = [
    "FLASK_ENV=${var.flask_env}",
    "PORT=5000",
    "ORS_API_KEY=${var.ors_api_key}"
  ]
  
  networks_advanced {
    name = docker_network.transport_network.name
  }
  
  restart = "unless-stopped"
  
  healthcheck {
    test     = ["CMD", "curl", "-f", "http://localhost:5000/health"]
    interval = "30s"
    timeout  = "10s"
    retries  = 3
  }
}

# Kubernetes Namespace
resource "kubernetes_namespace" "transport" {
  metadata {
    name = var.kube_namespace
    
    labels = {
      app     = "transport-optimization"
      env     = var.environment
      managed = "terraform"
    }
  }
}

# Kubernetes Secret
resource "kubernetes_secret" "transport_secrets" {
  metadata {
    name      = "transport-secrets"
    namespace = kubernetes_namespace.transport.metadata[0].name
  }
  
  data = {
    ors-api-key = var.ors_api_key
  }
  
  type = "Opaque"
}

# Kubernetes ConfigMap
resource "kubernetes_config_map" "transport_config" {
  metadata {
    name      = "transport-app-config"
    namespace = kubernetes_namespace.transport.metadata[0].name
  }
  
  data = {
    FLASK_ENV = var.flask_env
    PORT      = "5000"
    LOG_LEVEL = "INFO"
  }
}

# Kubernetes Deployment
resource "kubernetes_deployment" "transport_app" {
  metadata {
    name      = "transport-app"
    namespace = kubernetes_namespace.transport.metadata[0].name
    
    labels = {
      app     = "transport-app"
      version = var.app_version
    }
  }
  
  spec {
    replicas = var.replica_count
    
    selector {
      match_labels = {
        app = "transport-app"
      }
    }
    
    template {
      metadata {
        labels = {
          app     = "transport-app"
          version = var.app_version
        }
      }
      
      spec {
        container {
          name  = "transport-app"
          image = "${var.docker_image}:${var.app_version}"
          
          port {
            container_port = 5000
            name          = "http"
          }
          
          env {
            name  = "FLASK_ENV"
            value = var.flask_env
          }
          
          env {
            name  = "PORT"
            value = "5000"
          }
          
          env {
            name = "ORS_API_KEY"
            value_from {
              secret_key_ref {
                name = kubernetes_secret.transport_secrets.metadata[0].name
                key  = "ors-api-key"
              }
            }
          }
          
          resources {
            requests = {
              memory = "256Mi"
              cpu    = "250m"
            }
            limits = {
              memory = "512Mi"
              cpu    = "500m"
            }
          }
          
          liveness_probe {
            http_get {
              path = "/health"
              port = 5000
            }
            initial_delay_seconds = 30
            period_seconds        = 10
          }
          
          readiness_probe {
            http_get {
              path = "/ready"
              port = 5000
            }
            initial_delay_seconds = 20
            period_seconds        = 5
          }
        }
      }
    }
  }
}

# Kubernetes Service
resource "kubernetes_service" "transport_service" {
  metadata {
    name      = "transport-app-service"
    namespace = kubernetes_namespace.transport.metadata[0].name
  }
  
  spec {
    type = "NodePort"
    
    selector = {
      app = "transport-app"
    }
    
    port {
      port        = 80
      target_port = 5000
      node_port   = 30080
      protocol    = "TCP"
    }
  }
}

# Output the connection information
output "docker_container_id" {
  value       = docker_container.transport_app.id
  description = "Docker container ID"
}

output "docker_app_url" {
  value       = "http://localhost:${var.app_port}"
  description = "URL to access the application (Docker)"
}

output "kube_namespace" {
  value       = kubernetes_namespace.transport.metadata[0].name
  description = "Kubernetes namespace"
}

output "kube_service_url" {
  value       = "http://localhost:30080"
  description = "URL to access the application (Kubernetes)"
}
