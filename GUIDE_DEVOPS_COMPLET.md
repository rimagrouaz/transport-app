# 🚀 GUIDE DEVOPS COMPLET - Transport Optimization

## 📋 STRUCTURE ANALYSÉE

Votre projet contient :
- ✅ **Docker** : Dockerfile + docker-compose (App + Prometheus + Grafana)
- ✅ **Kubernetes** : Deployment + Service + Ingress + HPA + ConfigMap + Secret
- ✅ **Jenkins** : Pipeline CI/CD complet
- ✅ **Terraform** : Infrastructure as Code (Docker + K8s)
- ✅ **Ansible** : Playbooks automatisation

---

## 🎯 PARCOURS RECOMMANDÉ

```
1. Docker Local (10 min)          ← COMMENCER ICI
2. Docker Compose (15 min)        ← Stack complète
3. Kubernetes Local (30 min)      ← minikube/k3s
4. Jenkins Pipeline (45 min)      ← CI/CD
5. Terraform Deploy (60 min)      ← Infrastructure
6. Cloud Production (variable)    ← AWS/Azure/GCP
```

---

# 🐳 ÉTAPE 1 : DOCKER LOCAL (Le Plus Simple)

## Prérequis

### 1.1 Installer Docker Desktop
```powershell
# Télécharger : https://www.docker.com/products/docker-desktop/
# Installer et redémarrer PC
```

### 1.2 Vérifier Installation
```powershell
docker --version
# Docker version 24.0.0 ou supérieur

docker-compose --version
# Docker Compose version v2.20.0 ou supérieur
```

---

## 1.3 Préparer les Fichiers

### A. Mettre à Jour app.py
```powershell
cd C:\Users\hajar\transport-optimization-worldwide\transport-optimization-devops\app

# Remplacer par la version corrigée
copy C:\Users\hajar\Downloads\app_CLEAN_FINAL.py app.py
copy C:\Users\hajar\Downloads\index_CLEAN_FINAL.html templates\index.html
```

### B. Créer requirements.txt dans /app
```powershell
cd C:\Users\hajar\transport-optimization-worldwide\transport-optimization-devops\app

# Créer requirements.txt
@"
Flask==3.0.0
requests==2.31.0
polyline==2.0.2
haversine==2.8.1
gunicorn==21.2.0
"@ | Out-File -Encoding ASCII requirements.txt
```

### C. Ajouter Endpoint /health dans app.py
```python
# Ajouter à la fin de app.py (avant if __name__ == '__main__':)

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'service': 'transport-api'}), 200

@app.route('/ready')
def ready():
    return jsonify({'status': 'ready'}), 200
```

---

## 1.4 Build Docker Image

### Méthode 1 : Docker Simple
```powershell
cd C:\Users\hajar\transport-optimization-worldwide\transport-optimization-devops

# Build l'image
docker build -t transport-app:v1 -f docker/Dockerfile ./app

# Vérifier
docker images | Select-String "transport-app"
```

### Méthode 2 : Docker Compose (Recommandé)
```powershell
cd C:\Users\hajar\transport-optimization-worldwide\transport-optimization-devops\docker

# Build avec docker-compose
docker-compose build

# Lancer
docker-compose up -d

# Vérifier
docker-compose ps
```

---

## 1.5 Tester

### Test 1 : Health Ch
```powershell
curl http://localhost:5000/health
# {"status":"healthy","service":"transport-api"}
```

### Test 2 : Interface Web
```
http://localhost:5000
```

### Test 3 : Prometheus (Monitoring)
```
http://localhost:9090
```

### Test 4 : Grafana (Visualisation)
```
http://localhost:3000
Username: admin
Password: admin
```

---

## 1.6 Commandes Utiles

```powershell
# Voir les logs
docker-compose logs -f app

# Arrêter
docker-compose stop

# Redémarrer
docker-compose restart

# Supprimer tout
docker-compose down -v
```

---

# ☸️ ÉTAPE 2 : KUBERNETES LOCAL

## 2.1 Installer Minikube

### Windows avec Chocolatey
```powershell
# Installer Chocolatey d'abord (si pas déjà)
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Installer minikube
choco install minikube kubernetes-cli

# Vérifier
minikube version
kubectl version --client
```

---

## 2.2 Démarrer Cluster Local

```powershell
# Démarrer minikube
minikube start --driver=docker --cpus=4 --memory=4096

# Vérifier
kubectl get nodes
# NAME       STATUS   ROLES           AGE   VERSION
# minikube   Ready    control-plane   1m    v1.28.0
```

---

## 2.3 Build & Push Image

### Option A : Registry Local
```powershell
# Utiliser le registry Docker de minikube
eval $(minikube docker-env)

# Build dans minikube
docker build -t transport-app:v1 -f docker/Dockerfile ./app
```

### Option B : Docker Hub
```powershell
# Login Docker Hub
docker login

# Tag l'image
docker tag transport-app:v1 votre-username/transport-app:v1

# Push
docker push votre-username/transport-app:v1
```

---

## 2.4 Créer Secret & ConfigMap

```powershell
cd C:\Users\hajar\transport-optimization-worldwide\kubernetes

# Créer namespace (optionnel)
kubectl create namespace transport

# Créer secret (ORS API Key)
kubectl create secret generic transport-secrets \
  --from-literal=ors-api-key=VOTRE_CLE_ORS \
  -n transport

# Appliquer ConfigMap
kubectl apply -f configmap.yaml -n transport
```

---

## 2.5 Déployer l'Application

### Modifier deployment.yaml

```powershell
# Ouvrir deployment.yaml
notepad C:\Users\hajar\transport-optimization-worldwide\kubernetes\deployment.yaml
```

**Changer ligne 28** :
```yaml
# AVANT
image: your-dockerhub-username/transport-app:latest

# APRÈS (si Docker Hub)
image: votre-username/transport-app:v1

# APRÈS (si local)
image: transport-app:v1
imagePullPolicy: Never  # Ajouter cette ligne
```

### Déployer

```powershell
cd C:\Users\hajar\transport-optimization-worldwide\kubernetes

# Déployer tout
kubectl apply -f deployment.yaml -n transport
kubectl apply -f service.yaml -n transport

# Vérifier pods
kubectl get pods -n transport
# NAME                             READY   STATUS    RESTARTS   AGE
# transport-app-xxxxxxxxxx-xxxxx   1/1     Running   0          30s

# Vérifier services
kubectl get svc -n transport
```

---

## 2.6 Accéder à l'Application

### Méthode 1 : Port Forward
```powershell
kubectl port-forward -n transport svc/transport-app-service 5000:80

# Accéder
http://localhost:5000
```

### Méthode 2 : Minikube Service
```powershell
minikube service transport-app-service -n transport

# Ouvre automatiquement le navigateur
```

### Méthode 3 : Ingress (Avancé)
```powershell
# Activer ingress addon
minikube addons enable ingress

# Appliquer ingress
kubectl apply -f ingress.yaml -n transport

# Obtenir IP
minikube ip
# 192.168.49.2

# Ajouter à hosts (Admin PowerShell)
Add-Content -Path C:\Windows\System32\drivers\etc\hosts -Value "192.168.49.2 transport.local"

# Accéder
http://transport.local
```

---

## 2.7 Monitoring Kubernetes

```powershell
# Dashboard Kubernetes
minikube dashboard

# Logs d'un pod
kubectl logs -f -n transport <pod-name>

# Exec dans un pod
kubectl exec -it -n transport <pod-name> -- /bin/bash

# Scaler
kubectl scale deployment transport-app --replicas=5 -n transport

# Vérifier HPA (Auto-scaling)
kubectl get hpa -n transport
```

---

# 🔄 ÉTAPE 3 : JENKINS CI/CD

## 3.1 Installer Jenkins

### Docker (Plus Simple)
```powershell
cd C:\Users\hajar\transport-optimization-worldwide\transport-optimization-devops\jenkins

# Lancer Jenkins
docker run -d \
  --name jenkins \
  -p 8080:8080 -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home \
  -v /var/run/docker.sock:/var/run/docker.sock \
  jenkins/jenkins:lts

# Obtenir mot de passe initial
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

### Accéder à Jenkins
```
http://localhost:8080
```

---

## 3.2 Configurer Jenkins

### A. Plugins Nécessaires
```
1. Docker Pipeline
2. Kubernetes
3. Git
4. Pipeline
5. Blue Ocean (optionnel, mais joli)
```

### B. Credentials
```
1. Docker Hub :
   - ID: dockerhub-credentials
   - Username: votre-username
   - Password: votre-token

2. Kubernetes :
   - ID: kubeconfig
   - File: ~/.kube/config

3. GitHub (si repo privé) :
   - ID: github-token
   - Token: votre-github-token
```

---

## 3.3 Créer Pipeline

### A. Nouveau Job
```
1. New Item → Pipeline
2. Nom: transport-app-pipeline
3. Pipeline → Definition: Pipeline script from SCM
4. SCM: Git
5. Repository URL: votre-repo-url
6. Script Path: jenkins/Jenkinsfile
```

### B. Modifier Jenkinsfile

```powershell
notepad C:\Users\hajar\transport-optimization-worldwide\transport-optimization-devops\jenkins\Jenkinsfile
```

**Ligne 6** : Changer username Docker Hub
```groovy
DOCKER_IMAGE = 'votre-username/transport-app'
```

---

## 3.4 Lancer le Pipeline

```
1. Ouvrir le job dans Jenkins
2. "Build Now"
3. Voir les logs en temps réel
```

### Étapes du Pipeline
```
🔍 Checkout           → Clone le code
📦 Install Dependencies → pip install
🧪 Run Tests          → pytest
🏗️ Build Docker       → docker build
📤 Push to Registry   → docker push
🚀 Deploy to K8s      → kubectl apply
✅ Verify Deployment  → kubectl get pods
```

---

## 3.5 Webhook Automatique (Optionnel)

### GitHub Webhook
```
1. GitHub → Settings → Webhooks
2. Payload URL: http://votre-jenkins:8080/github-webhook/
3. Content type: application/json
4. Events: Just the push event
5. Active: ✅
```

**Maintenant** : Push code → Jenkins build automatiquement ! 🎉

---

# 🏗️ ÉTAPE 4 : TERRAFORM

## 4.1 Installer Terraform

```powershell
# Avec Chocolatey
choco install terraform

# Vérifier
terraform version
```

---

## 4.2 Préparer Variables

```powershell
cd C:\Users\hajar\transport-optimization-worldwide\terraform

# Créer terraform.tfvars
@"
docker_image = "votre-username/transport-app"
app_version  = "v1"
app_port     = 5000
network_name = "transport-network"
"@ | Out-File -Encoding ASCII terraform.tfvars
```

---

## 4.3 Déployer avec Terraform

```powershell
# Initialize
terraform init

# Plan (voir ce qui sera créé)
terraform plan

# Apply (créer l'infrastructure)
terraform apply

# Entrer "yes" pour confirmer
```

### Ce qui est Créé
```
✅ Docker network
✅ Docker containers
✅ Kubernetes namespace
✅ Kubernetes deployments
✅ Kubernetes services
```

---

## 4.4 Détruire l'Infrastructure

```powershell
# Supprimer tout
terraform destroy

# Entrer "yes" pour confirmer
```

---

# 📦 ÉTAPE 5 : ANSIBLE

## 5.1 Installer Ansible (WSL Required)

```powershell
# Installer WSL
wsl --install

# Dans WSL
sudo apt update
sudo apt install ansible

# Vérifier
ansible --version
```

---

## 5.2 Configurer Inventory

```powershell
cd /mnt/c/Users/hajar/transport-optimization-worldwide/ansible

# Modifier inventory
nano inventory
```

```ini
[local]
localhost ansible_connection=local

[production]
prod-server ansible_host=YOUR_SERVER_IP ansible_user=ubuntu ansible_ssh_private_key_file=~/.ssh/id_rsa
```

---

## 5.3 Lancer Playbook

```bash
cd /mnt/c/Users/hajar/transport-optimization-worldwide/ansible/playbooks

# Déployer
ansible-playbook -i ../inventory deploy.yml

# Avec tags spécifiques
ansible-playbook -i ../inventory deploy.yml --tags docker

# Check mode (dry-run)
ansible-playbook -i ../inventory deploy.yml --check
```

---

# ☁️ ÉTAPE 6 : CLOUD DEPLOYMENT

## 6.1 AWS (Exemple)

### Prérequis
```powershell
# Installer AWS CLI
choco install awscli

# Configurer
aws configure
# AWS Access Key ID: VOTRE_KEY
# AWS Secret Access Key: VOTRE_SECRET
# Default region: eu-west-1
```

### Déployer sur EKS
```bash
# Créer cluster EKS
eksctl create cluster \
  --name transport-cluster \
  --region eu-west-1 \
  --nodes 3 \
  --node-type t3.medium

# Déployer l'app
kubectl apply -f kubernetes/ -n default

# Obtenir URL LoadBalancer
kubectl get svc transport-app-service -o wide
```

---

## 6.2 Azure (Exemple)

```powershell
# Installer Azure CLI
choco install azure-cli

# Login
az login

# Créer AKS cluster
az aks create \
  --resource-group transport-rg \
  --name transport-cluster \
  --node-count 3 \
  --enable-addons monitoring \
  --generate-ssh-keys

# Get credentials
az aks get-credentials --resource-group transport-rg --name transport-cluster

# Déployer
kubectl apply -f kubernetes/
```

---

# 📊 MONITORING & LOGS

## Prometheus Queries

```
http://localhost:9090

# CPU Usage
rate(container_cpu_usage_seconds_total{container="transport-app"}[5m])

# Memory Usage
container_memory_usage_bytes{container="transport-app"}

# HTTP Requests
rate(http_requests_total[5m])
```

## Grafana Dashboards

```
http://localhost:3000

Dashboards Recommandés:
- Kubernetes Cluster Monitoring
- Docker Container Metrics
- Application Performance
```

---

# 🔧 TROUBLESHOOTING

## Docker

### Container ne démarre pas
```powershell
docker logs transport-app
docker exec -it transport-app /bin/bash
```

### Port déjà utilisé
```powershell
# Trouver processus
netstat -ano | findstr :5000

# Tuer processus
taskkill /PID <PID> /F
```

## Kubernetes

### Pod en CrashLoopBackOff
```powershell
kubectl describe pod <pod-name> -n transport
kubectl logs <pod-name> -n transport --previous
```

### Image pull failed
```powershell
# Vérifier secret
kubectl get secrets -n transport

# Recréer
kubectl delete secret transport-secrets -n transport
kubectl create secret docker-registry regcred \
  --docker-server=https://index.docker.io/v1/ \
  --docker-username=votre-username \
  --docker-password=votre-password \
  -n transport
```

---

# ✅ CHECKLIST FINALE

## Local Development
- [ ] Docker Desktop installé
- [ ] app_CLEAN_FINAL.py en place
- [ ] requirements.txt créé
- [ ] Endpoints /health et /ready ajoutés
- [ ] Docker build réussi
- [ ] docker-compose up fonctionne
- [ ] http://localhost:5000 accessible
- [ ] Tests manuels OK

## Kubernetes
- [ ] minikube installé et démarré
- [ ] kubectl configuré
- [ ] Secrets créés
- [ ] Deployment appliqué
- [ ] Pods running
- [ ] Service accessible
- [ ] HPA configuré

## CI/CD
- [ ] Jenkins installé
- [ ] Plugins installés
- [ ] Credentials configurés
- [ ] Pipeline créé
- [ ] Build réussi
- [ ] Tests passent
- [ ] Deploy automatique

## Production
- [ ] Cloud provider choisi
- [ ] Cluster créé
- [ ] App déployée
- [ ] DNS configuré
- [ ] SSL/TLS activé
- [ ] Monitoring actif
- [ ] Backups configurés

---

# 🎯 PARCOURS RECOMMANDÉ POUR VOUS

Basé sur votre projet, je recommande :

### Semaine 1 : Local
1. ✅ Docker local (1h)
2. ✅ Docker Compose (30min)
3. ✅ Tests & validation (30min)

### Semaine 2 : Kubernetes
4. ✅ Minikube setup (1h)
5. ✅ Deploy sur K8s (2h)
6. ✅ Monitoring (1h)

### Semaine 3 : CI/CD
7. ✅ Jenkins setup (2h)
8. ✅ Pipeline (3h)
9. ✅ Automatisation (2h)

### Semaine 4 : Production
10. ✅ Cloud deployment (4h)
11. ✅ DNS & SSL (1h)
12. ✅ Final testing (2h)

---

# 📞 PROCHAINES ÉTAPES

**MAINTENANT, DITES-MOI :**

1. **Avez-vous Docker Desktop installé ?**
2. **Voulez-vous commencer par Docker ou Kubernetes ?**
3. **Quelle plateforme cloud visez-vous ? (AWS/Azure/GCP/None)**
4. **Besoin d'aide pour une étape spécifique ?**

**Je vous guiderai étape par étape ! 🚀**
