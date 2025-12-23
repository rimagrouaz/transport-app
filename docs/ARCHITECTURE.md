# 🏗️ Architecture Documentation

## Table of Contents
1. [System Overview](#system-overview)
2. [Architecture Diagram](#architecture-diagram)
3. [Components](#components)
4. [DevOps Pipeline](#devops-pipeline)
5. [Technology Stack](#technology-stack)
6. [Network Architecture](#network-architecture)
7. [Security Architecture](#security-architecture)

## System Overview

The Transport Optimization System is a cloud-native application designed to provide intelligent route optimization for public transportation. It analyzes urban density, traffic patterns, and suggests optimal routes for buses and other modes of transport.

### Key Features
- Multi-modal route planning (car, bus, bike, walking)
- Real-time bus position simulation
- Urban density analysis
- CO₂ emissions estimation
- Interactive map visualization
- RESTful API

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Layer                               │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐           │
│  │ Browser │  │  Mobile │  │   API   │  │  CLI    │           │
│  │  Client │  │   App   │  │ Clients │  │  Tools  │           │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘           │
└───────┼───────────┼────────────┼────────────┼─────────────────┘
        │           │            │            │
        └───────────┴────────────┴────────────┘
                     │
┌────────────────────┼─────────────────────────────────────────────┐
│                    │    Ingress Layer                            │
│    ┌───────────────▼──────────────┐                             │
│    │  Kubernetes Ingress          │                             │
│    │  (NGINX Ingress Controller)  │                             │
│    └───────────────┬──────────────┘                             │
└────────────────────┼──────────────────────────────────────────────┘
                     │
┌────────────────────┼──────────────────────────────────────────────┐
│                    │    Application Layer                         │
│    ┌───────────────▼──────────────┐                             │
│    │  Kubernetes Service          │                             │
│    │  (Load Balancer)             │                             │
│    └───────────────┬──────────────┘                             │
│                    │                                              │
│    ┌───────────────┴──────────────┐                             │
│    │                               │                             │
│    ▼                               ▼                             │
│ ┌─────────┐  ┌─────────┐  ┌─────────┐                          │
│ │  Pod 1  │  │  Pod 2  │  │  Pod 3  │  ... (Auto-scaling)      │
│ │ Flask   │  │ Flask   │  │ Flask   │                          │
│ │ App     │  │ App     │  │ App     │                          │
│ └────┬────┘  └────┬────┘  └────┬────┘                          │
└──────┼────────────┼─────────────┼──────────────────────────────┘
       │            │             │
       └────────────┴─────────────┘
                    │
┌───────────────────┼──────────────────────────────────────────────┐
│                   │    External Services Layer                   │
│    ┌──────────────┴─────────────┐                               │
│    │                             │                               │
│    ▼                             ▼                               │
│ ┌──────────────────┐  ┌──────────────────┐                     │
│ │ OpenRouteService │  │ Photon Geocoding │                     │
│ │      API         │  │      API         │                     │
│ └──────────────────┘  └──────────────────┘                     │
└───────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────┐
│                      DevOps Pipeline                              │
│                                                                   │
│  ┌────────┐   ┌─────────┐   ┌────────┐   ┌──────────┐         │
│  │  Git   │ → │ Jenkins │ → │ Docker │ → │ Kubernetes│         │
│  │ GitHub │   │   CI    │   │  Build │   │  Deploy   │         │
│  └────────┘   └─────────┘   └────────┘   └──────────┘         │
│                     ↓             ↓             ↓                │
│            ┌─────────────┐  ┌──────────┐  ┌──────────┐         │
│            │  Security   │  │ Terraform│  │ Ansible  │         │
│            │  Scanning   │  │   IaC    │  │  Config  │         │
│            └─────────────┘  └──────────┘  └──────────┘         │
└───────────────────────────────────────────────────────────────────┘
```

## Components

### 1. Frontend
- **Technology**: HTML5, CSS3, JavaScript (ES6+)
- **Map Library**: Leaflet.js
- **Features**:
  - Interactive map interface
  - Route visualization
  - Real-time bus tracking
  - Responsive design

### 2. Backend API
- **Framework**: Flask (Python 3.9)
- **Server**: Gunicorn (Production)
- **Features**:
  - RESTful API endpoints
  - Route calculation
  - Geocoding integration
  - Urban density analysis
  - CO₂ emissions calculation

### 3. Containerization
- **Docker**: Application containerization
- **Multi-stage builds**: Optimized image size
- **Security**: Non-root user, minimal base image

### 4. Orchestration
- **Kubernetes**: Container orchestration
- **Components**:
  - Deployments (3 replicas)
  - Services (LoadBalancer, NodePort)
  - Ingress (NGINX)
  - HorizontalPodAutoscaler
  - ConfigMaps & Secrets

### 5. CI/CD Pipeline
- **Source Control**: Git/GitHub
- **CI**: Jenkins / GitHub Actions
- **Build**: Docker
- **Test**: pytest, coverage
- **Security**: Trivy, Safety
- **Deploy**: kubectl, Ansible

### 6. Infrastructure as Code
- **Terraform**: Infrastructure provisioning
- **Ansible**: Configuration management
- **Features**:
  - Automated deployment
  - Consistent environments
  - Version control

## DevOps Pipeline

### CI/CD Workflow

```
┌──────────────┐
│ Code Commit  │
│  (Git Push)  │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Checkout   │
│     Code     │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Install    │
│ Dependencies │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Run Tests   │
│   (pytest)   │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Security   │
│    Scans     │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│    Build     │
│ Docker Image │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Image      │
│   Scanning   │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Push to    │
│   Registry   │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Deploy to  │
│  Kubernetes  │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│    Smoke     │
│    Tests     │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Success!   │
│   Notify     │
└──────────────┘
```

## Technology Stack

### Development
| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | HTML5, CSS3, JS | User Interface |
| Maps | Leaflet.js | Map Visualization |
| Backend | Flask (Python) | API Server |
| Server | Gunicorn | WSGI Server |

### DevOps Tools
| Tool | Version | Purpose |
|------|---------|---------|
| Git | 2.x | Version Control |
| Docker | 20.10+ | Containerization |
| Kubernetes | 1.27+ | Orchestration |
| Jenkins | 2.x | CI/CD |
| Ansible | 2.10+ | Configuration Management |
| Terraform | 1.0+ | Infrastructure as Code |

### Monitoring & Security
| Tool | Purpose |
|------|---------|
| Trivy | Container Scanning |
| Safety | Dependency Checking |
| Prometheus | Metrics Collection |
| Grafana | Visualization |

## Network Architecture

### Kubernetes Networking

```
┌─────────────────────────────────────────┐
│         Ingress Controller              │
│         (NGINX)                         │
│         Port: 80, 443                   │
└─────────────┬───────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│         Service (LoadBalancer)          │
│         transport-app-service           │
│         Port: 80 → 5000                │
└─────────────┬───────────────────────────┘
              │
       ┌──────┴──────┐
       │             │
       ▼             ▼
┌──────────┐  ┌──────────┐
│  Pod 1   │  │  Pod 2   │
│  IP: x.x │  │  IP: y.y │
│  :5000   │  │  :5000   │
└──────────┘  └──────────┘
```

### Port Mapping
- **External**: 80 (HTTP), 443 (HTTPS)
- **NodePort**: 30080
- **Container**: 5000
- **Application**: 5000 (Flask)

## Security Architecture

### Security Layers

1. **Container Security**
   - Non-root user (UID 1000)
   - Read-only root filesystem
   - Dropped capabilities
   - Security scanning (Trivy)

2. **Kubernetes Security**
   - RBAC policies
   - Network policies
   - Resource limits
   - Secrets management
   - Pod security policies

3. **Application Security**
   - CORS configuration
   - Input validation
   - Rate limiting
   - HTTPS enforcement

4. **CI/CD Security**
   - Code scanning
   - Dependency checking
   - Image scanning
   - Secret scanning

### Secrets Management

```yaml
Secrets Storage:
├── Kubernetes Secrets (base64 encoded)
│   ├── ors-api-key
│   └── database-credentials (if needed)
├── Environment Variables
│   ├── FLASK_ENV
│   └── PORT
└── ConfigMaps (non-sensitive)
    ├── LOG_LEVEL
    └── FEATURE_FLAGS
```

## Scalability

### Horizontal Scaling
- **HPA Configuration**:
  - Min Replicas: 2
  - Max Replicas: 10
  - CPU Threshold: 70%
  - Memory Threshold: 80%

### Vertical Scaling
- **Resource Requests**:
  - CPU: 250m
  - Memory: 256Mi
- **Resource Limits**:
  - CPU: 500m
  - Memory: 512Mi

## High Availability

### Application Layer
- Multiple pod replicas (3+)
- Health checks (liveness & readiness)
- Rolling updates (zero downtime)
- Pod disruption budgets

### Infrastructure Layer
- Multi-node Kubernetes cluster
- Load balancing
- Auto-healing
- Backup & restore procedures

## Monitoring & Logging

### Metrics
- **Application Metrics**:
  - Request count
  - Response time
  - Error rate
  - Active connections

- **System Metrics**:
  - CPU usage
  - Memory usage
  - Network I/O
  - Disk usage

### Logging
- Centralized logging
- Log aggregation
- Log rotation
- Retention policies

## Data Flow

```
1. User Request
   └→ Browser → Ingress → Service → Pod

2. Route Calculation
   └→ Pod → OpenRouteService API → Response

3. Geocoding
   └→ Pod → Photon API → Coordinates

4. Response
   └→ Pod → Service → Ingress → Browser
```

## Disaster Recovery

### Backup Strategy
- **What to Backup**:
  - Kubernetes manifests
  - ConfigMaps & Secrets
  - Application code (Git)
  - Docker images (Registry)

### Recovery Procedures
1. Restore from Git repository
2. Rebuild Docker images
3. Apply Kubernetes manifests
4. Verify functionality

## Performance Optimization

### Application Level
- Gunicorn worker processes (4)
- Connection pooling
- Caching strategies
- Async operations

### Infrastructure Level
- Resource optimization
- Load balancing
- CDN integration
- Database indexing (if applicable)

---

**Architecture Documentation v1.0**

Last Updated: 2024
