# Outputs for Transport Optimization Infrastructure

output "environment" {
  description = "Deployment environment"
  value       = var.environment
}

output "application_version" {
  description = "Application version deployed"
  value       = var.app_version
}

output "docker_access_info" {
  description = "Docker container access information"
  value = {
    container_name = var.container_name
    app_url        = "http://localhost:${var.app_port}"
    health_check   = "http://localhost:${var.app_port}/health"
  }
}

output "kubernetes_access_info" {
  description = "Kubernetes deployment access information"
  value = {
    namespace    = var.kube_namespace
    replicas     = var.replica_count
    service_url  = "http://localhost:30080"
    health_check = "http://localhost:30080/health"
  }
}

output "useful_commands" {
  description = "Useful commands for managing the infrastructure"
  value = {
    docker = {
      logs    = "docker logs ${var.container_name}"
      restart = "docker restart ${var.container_name}"
      stop    = "docker stop ${var.container_name}"
      shell   = "docker exec -it ${var.container_name} /bin/sh"
    }
    kubernetes = {
      pods    = "kubectl get pods -n ${var.kube_namespace}"
      logs    = "kubectl logs -l app=transport-app -n ${var.kube_namespace}"
      service = "kubectl get svc -n ${var.kube_namespace}"
      scale   = "kubectl scale deployment transport-app --replicas=5 -n ${var.kube_namespace}"
    }
  }
}
