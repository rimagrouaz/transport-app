# Variables for Transport Optimization Infrastructure

variable "environment" {
  description = "Environment name (dev, staging, production)"
  type        = string
  default     = "development"
}

variable "app_version" {
  description = "Application version tag"
  type        = string
  default     = "latest"
}

variable "docker_image" {
  description = "Docker image name"
  type        = string
  default     = "transport-app"
}

variable "container_name" {
  description = "Docker container name"
  type        = string
  default     = "transport-app-container"
}

variable "network_name" {
  description = "Docker network name"
  type        = string
  default     = "transport-network"
}

variable "app_port" {
  description = "Port to expose the application (Docker)"
  type        = number
  default     = 5000
}

variable "flask_env" {
  description = "Flask environment (development, production)"
  type        = string
  default     = "development"
}

variable "ors_api_key" {
  description = "OpenRouteService API key"
  type        = string
  default     = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6ImIxM2U1NzhhNDJlMjQ1MzZhNTVlYjUyZjBhYzAyY2UzIiwiaCI6Im11cm11cjY0In0="
  sensitive   = true
}

variable "kube_namespace" {
  description = "Kubernetes namespace"
  type        = string
  default     = "transport-app"
}

variable "replica_count" {
  description = "Number of pod replicas"
  type        = number
  default     = 3
}

# Cloud provider variables (for future use)
variable "cloud_provider" {
  description = "Cloud provider (aws, gcp, azure, local)"
  type        = string
  default     = "local"
}

variable "region" {
  description = "Cloud provider region"
  type        = string
  default     = "us-east-1"
}
