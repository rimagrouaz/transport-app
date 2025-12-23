# 🚀 Guide de Déploiement Cloud

## 1. Heroku

### Fichier `Procfile`
```
web: gunicorn --bind 0.0.0.0:$PORT --workers 4 --timeout 120 app:app
```

### Commandes de déploiement
```bash
# Installer Heroku CLI
curl https://cli-assets.heroku.com/install.sh | sh

# Se connecter
heroku login

# Créer l'application
heroku create nom-de-votre-app

# Configurer la clé API
heroku config:set ORS_API_KEY=votre_clé_ici

# Déployer
git push heroku main

# Vérifier les logs
heroku logs --tail
```

**URL** : `https://nom-de-votre-app.herokuapp.com`

---

## 2. Railway

### Configuration
1. Connecter votre repo GitHub
2. Ajouter variable d'environnement :
   - `ORS_API_KEY` = votre clé
3. Deploy automatique

**Commande de build** : `pip install -r requirements.txt`
**Commande de start** : `gunicorn --bind 0.0.0.0:$PORT app:app`

---

## 3. Render

### Fichier `render.yaml`
```yaml
services:
  - type: web
    name: transport-api
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn --bind 0.0.0.0:$PORT app:app
    envVars:
      - key: ORS_API_KEY
        sync: false
      - key: FLASK_ENV
        value: production
```

### Déploiement
1. Connecter GitHub
2. Ajouter `ORS_API_KEY` dans les variables d'environnement
3. Deploy automatique

---

## 4. Google Cloud Run

### Dockerfile (déjà créé)
Le Dockerfile existant est compatible.

### Commandes
```bash
# Authentification
gcloud auth login

# Configurer le projet
gcloud config set project VOTRE_PROJECT_ID

# Build l'image
gcloud builds submit --tag gcr.io/VOTRE_PROJECT_ID/transport-api

# Deploy
gcloud run deploy transport-api \
  --image gcr.io/VOTRE_PROJECT_ID/transport-api \
  --platform managed \
  --region europe-west1 \
  --allow-unauthenticated \
  --set-env-vars ORS_API_KEY=votre_clé
```

---

## 5. AWS Elastic Beanstalk

### Configuration
Créer `ebextensions/python.config`:

```yaml
option_settings:
  aws:elasticbeanstalk:container:python:
    WSGIPath: app:app
  aws:elasticbeanstalk:application:environment:
    ORS_API_KEY: 'votre_clé'
```

### Commandes
```bash
# Installer EB CLI
pip install awsebcli

# Initialiser
eb init -p python-3.11 transport-api

# Créer environnement
eb create transport-api-env

# Déployer
eb deploy
```

---

## 6. DigitalOcean App Platform

### Configuration app.yaml
```yaml
name: transport-api
services:
  - name: api
    source_dir: /
    github:
      repo: votre-username/votre-repo
      branch: main
    build_command: pip install -r requirements.txt
    run_command: gunicorn --bind 0.0.0.0:8080 app:app
    envs:
      - key: ORS_API_KEY
        value: ${ORS_API_KEY}
        type: SECRET
    http_port: 8080
```

---

## 7. Azure App Service

### Commandes
```bash
# Se connecter
az login

# Créer resource group
az group create --name TransportAPIGroup --location westeurope

# Créer app service plan
az appservice plan create --name TransportAPIPlan \
  --resource-group TransportAPIGroup \
  --sku B1 --is-linux

# Créer web app
az webapp create --resource-group TransportAPIGroup \
  --plan TransportAPIPlan \
  --name transport-api-unique \
  --runtime "PYTHON:3.11"

# Configurer variables
az webapp config appsettings set \
  --resource-group TransportAPIGroup \
  --name transport-api-unique \
  --settings ORS_API_KEY="votre_clé"

# Déployer
az webapp up --name transport-api-unique \
  --resource-group TransportAPIGroup
```

---

## 8. Fly.io

### Fichier `fly.toml`
```toml
app = "transport-api"

[build]
  image = "flyio/python:3.11"

[env]
  PORT = "8080"
  FLASK_ENV = "production"

[http_service]
  internal_port = 8080
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 0
```

### Commandes
```bash
# Installer flyctl
curl -L https://fly.io/install.sh | sh

# Se connecter
flyctl auth login

# Lancer l'app
flyctl launch

# Définir secret
flyctl secrets set ORS_API_KEY=votre_clé

# Déployer
flyctl deploy
```

---

## 9. VPS (Ubuntu)

### Installation manuelle sur serveur
```bash
# 1. Se connecter au serveur
ssh user@votre-ip

# 2. Installer Python et dépendances
sudo apt update
sudo apt install python3.11 python3-pip nginx -y

# 3. Cloner le projet
git clone <votre-repo>
cd transport-optimization

# 4. Créer environnement virtuel
python3.11 -m venv venv
source venv/bin/activate

# 5. Installer dépendances
pip install -r requirements.txt

# 6. Créer .env
echo "ORS_API_KEY=votre_clé" > .env

# 7. Créer service systemd
sudo nano /etc/systemd/system/transport-api.service
```

**Contenu du service** :
```ini
[Unit]
Description=Transport API
After=network.target

[Service]
User=www-data
WorkingDirectory=/home/user/transport-optimization
Environment="PATH=/home/user/transport-optimization/venv/bin"
EnvironmentFile=/home/user/transport-optimization/.env
ExecStart=/home/user/transport-optimization/venv/bin/gunicorn \
  --workers 4 \
  --bind 0.0.0.0:5000 \
  --timeout 120 \
  app:app

[Install]
WantedBy=multi-user.target
```

**Configurer Nginx** :
```nginx
server {
    listen 80;
    server_name votre-domaine.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

**Activer et démarrer** :
```bash
sudo systemctl enable transport-api
sudo systemctl start transport-api
sudo systemctl enable nginx
sudo systemctl restart nginx
```

---

## 🔐 SSL/HTTPS

### Avec Let's Encrypt (Nginx)
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d votre-domaine.com
```

---

## 📊 Monitoring

### Logs

**Heroku** : `heroku logs --tail`
**Railway** : Interface web
**Google Cloud** : `gcloud run logs tail transport-api`
**Docker** : `docker-compose logs -f`

### Uptime monitoring

Services recommandés (gratuits) :
- UptimeRobot
- StatusCake
- Better Uptime

---

## 🚨 Variables d'environnement requises

Pour tous les déploiements :
- `ORS_API_KEY` : Clé OpenRouteService (OBLIGATOIRE)
- `FLASK_ENV` : production (recommandé)
- `PORT` : Auto-détecté sur la plupart des plateformes

---

## 💡 Recommandations

### Performance
- Utiliser au moins 512 MB de RAM
- 2-4 workers Gunicorn
- Timeout de 120 secondes

### Sécurité
- Toujours HTTPS en production
- Ne jamais commiter .env
- Utiliser des secrets managers

### Coûts
- **Gratuit** : Heroku, Railway, Render (tiers gratuits)
- **Payant** : À partir de 5-10$/mois

---

## ✅ Checklist de déploiement

- [ ] Clé ORS_API_KEY configurée
- [ ] FLASK_ENV=production
- [ ] HTTPS activé
- [ ] Logs accessibles
- [ ] Health check fonctionne
- [ ] Tests effectués
- [ ] Monitoring configuré
- [ ] Backup/rollback planifié

---

**Bon déploiement ! 🚀**
