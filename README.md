# 🚀 Projet DevOps Complet — Pipeline CI/CD avec Kubernetes & Monitoring

Pipeline DevOps de bout en bout : du code source jusqu'au monitoring en production, en passant par les tests automatiques, la containerisation Docker, l'orchestration Kubernetes et la visualisation Grafana.

---


## Vue d'ensemble

Ce projet met en place une chaîne DevOps complète, proche d'un contexte réel d'entreprise. L'objectif est d'automatiser l'ensemble du cycle de vie d'une application web, depuis l'écriture du code jusqu'à la surveillance de son comportement en production.

Le pipeline suit ce flux :

```
Code → Tests → Build → Docker → CI/CD → Kubernetes → Prometheus → Grafana
```

Chaque `git push` sur la branche `main` déclenche automatiquement les tests, construit l'image Docker et la pousse sur Docker Hub. Le déploiement sur Kubernetes est ensuite appliqué, et Prometheus collecte les métriques de l'application toutes les 15 secondes pour les afficher dans Grafana.

---

## Stack technique

| Étape | Outil | Rôle |
|-------|-------|------|
| Gestion du code | Git + GitHub | Versioning, branches, collaboration |
| Tests | Pytest | Tests unitaires automatiques |
| Build | pip + requirements.txt | Gestion des dépendances Python |
| Containerisation | Docker | Empaquetage de l'application |
| Registre d'images | Docker Hub | Stockage des images Docker |
| CI/CD | GitHub Actions | Automatisation du pipeline |
| Orchestration | Kubernetes (docker-desktop) | Déploiement et haute disponibilité |
| Collecte métriques | Prometheus | Scraping et stockage des métriques |
| Visualisation | Grafana | Dashboards et graphiques temps réel |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        GitHub                                │
│  ┌──────────┐    push     ┌─────────────────────────────┐   │
│  │   Code   │ ──────────► │     GitHub Actions           │   │
│  └──────────┘             │  ┌────────┐  ┌───────────┐  │   │
│                           │  │  Test  │─►│   Build   │  │   │
│                           │  └────────┘  └─────┬─────┘  │   │
│                           └───────────────────-│-────────┘   │
└───────────────────────────────────────────────-│─────────────┘
                                                 │ push image
                                                 ▼
                                         ┌──────────────┐
                                         │  Docker Hub  │
                                         └──────┬───────┘
                                                │ pull image
                                                ▼
┌───────────────────────────────────────────────────────────────┐
│                    Kubernetes Cluster                          │
│                                                               │
│   ┌─────────────────────────────────────┐                     │
│   │         flask-app Deployment        │                     │
│   │  ┌─────────────┐ ┌─────────────┐   │                     │
│   │  │    Pod 1    │ │    Pod 2    │   │  replicas: 2        │
│   │  │  Flask App  │ │  Flask App  │   │                     │
│   │  │  :5000      │ │  :5000      │   │                     │
│   │  └──────┬──────┘ └──────┬──────┘   │                     │
│   └─────────│───────────────│───────────┘                     │
│             └───────┬───────┘                                 │
│                     │ /metrics (toutes les 15s)               │
│                     ▼                                         │
│   ┌─────────────────────────┐                                 │
│   │       Prometheus        │                                 │
│   │   collecte & stocke     │                                 │
│   └────────────┬────────────┘                                 │
│                │ interroge                                    │
│                ▼                                              │
│   ┌─────────────────────────┐                                 │
│   │         Grafana         │                                 │
│   │   dashboards & graphs   │                                 │
│   └─────────────────────────┘                                 │
└───────────────────────────────────────────────────────────────┘
```

---

## Structure du projet

```
devops-app/
├── .github/
│   └── workflows/
│       └── ci-cd.yml          ← Pipeline GitHub Actions
├── app/
│   ├── main.py                ← Application Flask (3 routes)
│   └── requirements.txt       ← Dépendances Python
├── tests/
│   └── test_app.py            ← Tests automatiques Pytest
├── k8s/
│   ├── deployment.yaml        ← Déploiement Kubernetes (2 replicas)
│   ├── service.yaml           ← Service Kubernetes (exposition du port)
│   └── servicemonitor.yaml    ← Configuration scraping Prometheus
├── Dockerfile                 ← Recette de construction de l'image
├── .gitignore                 ← Fichiers exclus du versioning
└── README.md                  ← Ce fichier
```

---

## Prérequis

Avant de commencer, assure-toi d'avoir installé :

- **Python 3.13+** — [python.org](https://python.org)
- **Docker Desktop** — avec Kubernetes activé dans les paramètres
- **kubectl** — inclus avec Docker Desktop
- **Git** — [git-scm.com](https://git-scm.com)
- Un compte **GitHub** et un compte **Docker Hub**

Vérification rapide :

```bash
python --version
docker --version
kubectl version --client
git --version
```

---

## Installation et lancement

### 1. Cloner le projet

```bash
git clone https://github.com/Corosor/devops-app.git
cd devops-app
```

### 2. Installer les dépendances

```bash
pip install -r app/requirements.txt
```

### 3. Lancer l'application en local

```bash
python app/main.py
```

L'application est accessible sur `http://localhost:5000`.

---

## L'application Flask

L'application est une API Python Flask qui expose trois routes :

| Route | Description | Utilisé par |
|-------|-------------|-------------|
| `GET /` | Retourne le statut de l'application | Utilisateurs / tests |
| `GET /health` | Vérifie que l'app est en bonne santé | Kubernetes (readiness/liveness probes) |
| `GET /metrics` | Expose les métriques au format Prometheus | Prometheus (scraping automatique) |

**Exemple de réponse sur `GET /` :**
```json
{
  "message": "Hello DevOps !",
  "status": "running"
}
```

**Exemple de réponse sur `GET /health` :**
```json
{
  "status": "healthy",
  "timestamp": 1780081413.635
}
```

**Exemple de métriques sur `GET /metrics` :**
```
# HELP app_requests_total Nombre total de requêtes
# TYPE app_requests_total counter
app_requests_total{endpoint="/"} 127.0
app_requests_total{endpoint="/health"} 677.0
```

La métrique `app_requests_total` compte le nombre de requêtes reçues par endpoint depuis le démarrage du pod. Ce compteur ne se remet jamais à zéro — Prometheus calcule le taux de requêtes par seconde en comparant les valeurs successives avec la fonction `rate()`.

---

## Tests automatiques

Les tests vérifient que chaque route répond correctement.

### Lancer les tests

```bash
python -m pytest tests/ -v
```

### Résultat attendu

```
tests/test_app.py::test_home               PASSED
tests/test_app.py::test_health             PASSED
tests/test_app.py::test_metrics            PASSED
tests/test_app.py::test_route_inexistante  PASSED

4 passed in 1.2s
```

### Description des tests

| Test | Ce qu'il vérifie |
|------|-----------------|
| `test_home` | `GET /` retourne 200 avec `status: running` |
| `test_health` | `GET /health` retourne 200 avec `status: healthy` |
| `test_metrics` | `GET /metrics` retourne 200 |
| `test_route_inexistante` | Une route inconnue retourne 404 |

---

## Docker

### Construire l'image

```bash
docker build -t devops-app:v1 .
```

### Lancer le conteneur

```bash
docker run -p 5000:5000 devops-app:v1
```

Teste ensuite `http://localhost:5000` dans le navigateur.

### Pousser sur Docker Hub

```bash
docker tag devops-app:v1 TON-USERNAME/devops-app:latest
docker push TON-USERNAME/devops-app:latest
```

### Explication du Dockerfile

```dockerfile
FROM python:3.13-slim       # Image de base légère avec Python
WORKDIR /app                # Dossier de travail dans le conteneur
COPY app/requirements.txt . # Copie les dépendances en premier (cache Docker)
RUN pip install -r requirements.txt  # Installe les dépendances
COPY app/ .                 # Copie le code source
EXPOSE 5000                 # Déclare le port d'écoute
CMD ["python", "main.py"]   # Commande de démarrage
```

L'ordre `requirements.txt` avant le code source est intentionnel : Docker met chaque étape en cache. Tant que les dépendances ne changent pas, `pip install` n'est pas relancé à chaque rebuild, ce qui accélère les builds.

---

## Pipeline CI/CD — GitHub Actions

### Déclenchement

Le pipeline se déclenche automatiquement à chaque `git push` sur la branche `main`.

### Flux du pipeline

```
git push
    │
    ▼
┌───────────────────────┐
│   Job 1 : test        │
│  • checkout du code   │
│  • install Python     │
│  • pip install        │
│  • pytest tests/ -v   │
└───────────┬───────────┘
            │ si tests OK
            ▼
┌───────────────────────┐
│   Job 2 : build       │
│  • checkout du code   │
│  • docker login       │
│  • docker build       │
│  • docker push        │
└───────────────────────┘
```

### Secrets GitHub nécessaires

| Nom du secret | Description |
|---------------|-------------|
| `DOCKER_USERNAME` | Nom d'utilisateur Docker Hub |
| `DOCKER_PASSWORD` | Token d'accès Docker Hub (Read & Write) |

Ces secrets se configurent dans : **GitHub → Settings → Secrets and variables → Actions**.

### Fichier `.github/workflows/ci-cd.yml`

```yaml
name: DevOps Pipeline

on:
  push:
    branches:
      - main

jobs:
  test:
    name: Tests automatiques
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.13'
      - name: Installer les dependances
        run: pip install -r app/requirements.txt
      - name: Lancer les tests
        run: python -m pytest tests/ -v

  build:
    name: Build et Push Docker
    runs-on: ubuntu-latest
    needs: test
    steps:
      - uses: actions/checkout@v4
      - name: Login DockerHub
        run: echo "${{ secrets.DOCKER_PASSWORD }}" | docker login -u "${{ secrets.DOCKER_USERNAME }}" --password-stdin
      - name: Build et Push
        run: |
          docker build -t ${{ secrets.DOCKER_USERNAME }}/devops-app:latest .
          docker push ${{ secrets.DOCKER_USERNAME }}/devops-app:latest
```

---

## Déploiement Kubernetes

### Prérequis

Docker Desktop doit être démarré avec Kubernetes activé.

### Déployer l'application

```bash
# Vérifier que le cluster est prêt
kubectl get nodes

# Déployer l'application
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# Vérifier que les pods tournent
kubectl get pods
```

Résultat attendu :

```
NAME                         READY   STATUS    RESTARTS   AGE
flask-app-85c786b594-pw6nc   1/1     Running   0          2m
flask-app-85c786b594-7dgfj   1/1     Running   0          2m
```

### Accéder à l'application

```bash
kubectl port-forward svc/flask-app 5000:5000
```

Puis ouvre `http://localhost:5000` dans le navigateur.

### Fonctionnalités Kubernetes configurées

**Replicas (haute disponibilité)** : `replicas: 2` garantit que 2 pods tournent en permanence. Si l'un tombe, Kubernetes en recrée un automatiquement.

**ReadinessProbe** : Kubernetes interroge `/health` toutes les 10 secondes. Tant que la probe échoue, le pod ne reçoit aucun trafic.

**LivenessProbe** : Kubernetes interroge `/health` toutes les 20 secondes. Si la probe échoue, le pod est redémarré automatiquement.

---

## Monitoring — Prometheus & Grafana

### Architecture du monitoring

```
App Flask (/metrics)
    │
    │  scrape toutes les 15s
    ▼
Prometheus  ←── ServiceMonitor (k8s/servicemonitor.yaml)
    │
    │  interroge
    ▼
Grafana  →  Dashboard  →  Graphiques temps réel
```

### Installer la stack de monitoring

```bash
# Via Helm (kube-prometheus-stack)
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install monitoring prometheus-community/kube-prometheus-stack
```

### Appliquer le ServiceMonitor

```bash
kubectl apply -f k8s/servicemonitor.yaml
```

Le ServiceMonitor dit à Prometheus : "scrape le Service `flask-app` sur le port `http` au chemin `/metrics` toutes les 15 secondes."

### Accéder à Prometheus

```bash
kubectl port-forward svc/monitoring-kube-prometheus-prometheus 9090:9090
```

Ouvre `http://localhost:9090` et vérifie que `flask-app-monitor` affiche **2/2 up** dans l'onglet **Targets**.

### Accéder à Grafana

```bash
kubectl port-forward pod/grafana-new 3002:3000
```

Ouvre `http://localhost:3002`.

```
Login    : admin
Password : devops123
```

### Configurer la source de données Prometheus

1. **Connections → Data Sources → Add new data source → Prometheus**
2. URL : `http://monitoring-kube-prometheus-prometheus:9090`
3. Clique **Save & Test** → "Successfully queried the Prometheus API" ✅

### Requêtes Prometheus utiles dans Grafana

| Requête | Description |
|---------|-------------|
| `app_requests_total` | Compteur total de requêtes par endpoint |
| `rate(app_requests_total[1m])` | Taux de requêtes par seconde sur la dernière minute |
| `app_requests_total{exported_endpoint="/"}` | Requêtes uniquement sur `/` |
| `app_requests_total{exported_endpoint="/health"}` | Requêtes uniquement sur `/health` |

---

## Démonstration — Haute disponibilité

Cette démonstration montre que Kubernetes recrée automatiquement un pod mort.

**Terminal 1 — Surveiller les pods en temps réel :**

```bash
kubectl get pods -w
```

**Terminal 2 — Supprimer un pod :**

```bash
kubectl delete pod flask-app-85c786b594-pw6nc
```

**Résultat dans le Terminal 1 :**

```
flask-app-85c786b594-pw6nc   1/1   Running      →  Terminating
flask-app-85c786b594-newid   0/1   Pending      →  ContainerCreating  →  Running
```

Le pod mort est remplacé en moins de 10 secondes. Pendant ce temps, le second pod continue de répondre aux requêtes — aucune interruption de service.

---

## Guide de démarrage rapide

À chaque nouvelle session, lance les commandes dans cet ordre :

```bash
# 1. Vérifier que tout tourne
kubectl get pods

# 2. Exposer l'application
kubectl port-forward svc/flask-app 5000:5000

# 3. Exposer Grafana (dans un autre terminal)
kubectl port-forward pod/grafana-new 3002:3000

# 4. Exposer Prometheus (optionnel, pour vérifier les targets)
kubectl port-forward svc/monitoring-kube-prometheus-prometheus 9090:9090
```

URLs disponibles :

| URL | Description |
|-----|-------------|
| `http://localhost:5000/` | Application Flask |
| `http://localhost:5000/health` | Statut de santé |
| `http://localhost:5000/metrics` | Métriques brutes |
| `http://localhost:9090` | Interface Prometheus |
| `http://localhost:3002` | Dashboard Grafana |

---

## Commandes utiles

```bash
# Voir tous les pods
kubectl get pods

# Voir les logs d'un pod
kubectl logs NOM-DU-POD

# Décrire un pod (debug)
kubectl describe pod NOM-DU-POD

# Redémarrer un déploiement
kubectl rollout restart deployment/flask-app

# Vérifier le statut du rollout
kubectl rollout status deployment/flask-app

# Voir les services
kubectl get svc

# Voir les ServiceMonitors
kubectl get servicemonitor

# Lancer les tests
python -m pytest tests/ -v

# Builder l'image Docker
docker build -t devops-app:v1 .

# Voir les images Docker
docker images
```

---

## Auteur

Projet réalisé dans le cadre d'un mini-projet DevOps — pipeline complet de bout en bout.