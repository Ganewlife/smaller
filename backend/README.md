# **AssoPilot**

Cette application desktop permet de gérer les ....

---


## **À propos**
Cette application a été conçue pour faciliter la gestion des données essentielles d'une organisation .


## **Prérequis**
Avant de commencer, assurez-vous d'avoir installé les outils suivants sur votre système :
- **Python 3.12+**
- **Node.js 20+**
- **npm** ou **yarn**
- **Git**

---

## **Installation**
Pour installer l'application, suivez les étapes ci-dessous :

1. Clonez ce dépôt :
   ```bash
   git clone https://github.com/ganewlife/smaller.git
   cd votre-repo

## Installez les dépendances pour le backend
- python -m venv venv
- source venv/bin/activate  # (ou `venv\Scripts\activate` sur Windows)
- pip install -r requirements.txt

## Installez les dépendances pour le frontend
- npm install

## Configurez les variables d'environnement (Optionnel, sinon c'est fait pour le test):
FLASK_ENV=development
DATABASE_URL=sqlite:///app.db
SECRET_KEY=super-secret-key

## Initialisez la base de données
- flask db init
- flask db-migrate
- flask db upgrade

## Activez l'environnement virtuel si cela n'a pas été fait
- source venv/bin/activate

## Lancez le serveur backend
- flask run
ou
- python -m flask run

## Dans un autre terminal, restarter dans le dossier racine du projet pour demarrer l'appli
- npm start
