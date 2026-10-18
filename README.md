# LITRevu

LITRevu est une application web développée avec Django permettant de demander et de publier des critiques de livres ou d’articles.

Les utilisateurs peuvent créer des demandes de critique sous forme de billets, répondre aux billets existants et consulter un flux personnalisé regroupant leurs publications et celles des comptes qu’ils suivent.

Ce projet pédagogique a été réalisé à partir d’un cahier des charges fourni dans le cadre du parcours OpenClassrooms.

## Fonctionnalités principales

### Authentification

- Inscription avec un modèle utilisateur personnalisé
- Connexion et déconnexion
- Accès aux fonctionnalités métier réservé aux utilisateurs authentifiés

### Billets

- Création d’une demande de critique
- Ajout facultatif d’une image
- Consultation des billets personnels
- Modification réservée à l’auteur
- Suppression par requête POST protégée par CSRF

### Critiques

- Publication d’une critique en réponse à un billet
- Création conjointe d’un billet et de sa critique
- Attribution d’une note comprise entre 0 et 5
- Aperçu du billet associé
- Modification réservée à l’auteur
- Suppression par requête POST protégée par CSRF

### Flux personnalisé

Le flux réunit les billets et les critiques :

- de l’utilisateur connecté ;
- des utilisateurs qu’il suit.

Les publications sont classées de la plus récente à la plus ancienne selon leur date de création.

### Abonnements

- Recherche d’un utilisateur par son nom
- Suggestions d’utilisateurs
- Filtrage dynamique des suggestions côté client
- Abonnement à un utilisateur
- Consultation des utilisateurs suivis
- Désabonnement

L’application empêche également l’auto-abonnement et les abonnements en double.

## Technologies utilisées

- Python 3.13
- Django 6
- SQLite
- Pillow
- HTML5
- CSS personnalisé, sans framework
- JavaScript pour le filtrage dynamique

## Architecture

L’application s’appuie sur trois modèles métier principaux :

- `Ticket` : demande de critique concernant un livre ou un article ;
- `Review` : critique associée à un billet ;
- `UserFollows` : relation d’abonnement entre deux utilisateurs.

Le modèle utilisateur personnalisé hérite de `AbstractUser`.

Les vues génériques de Django assurent les opérations de création, de consultation, de modification et de suppression. Des contrôles d’authentification et de propriété limitent les actions sensibles aux utilisateurs autorisés.

## Accessibilité

L’interface intègre plusieurs pratiques d’accessibilité :

- labels associés aux champs de formulaire ;
- groupes de boutons radio structurés avec `fieldset` et `legend` ;
- lien d’évitement vers le contenu principal ;
- styles de focus visibles pour la navigation au clavier ;
- textes alternatifs pour les images ;
- messages d’erreur associés aux formulaires.

Ces éléments constituent des mesures d’accessibilité intégrées au développement. Ils ne remplacent pas un audit complet de conformité WCAG.

## Installation

### 1. Cloner le dépôt

```bash
git clone https://github.com/AoHaneX/LITRevu.git
cd LITRevu
```

### 2. Créer un environnement virtuel

```bash
python -m venv .venv
```

Sous Windows avec PowerShell :

```powershell
.venv\Scripts\Activate.ps1
```

Sous Windows avec l’invite de commandes :

```bat
.venv\Scripts\activate.bat
```

Sous macOS ou Linux :

```bash
source .venv/bin/activate
```

### 3. Installer les dépendances

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Préparer la base de données

```bash
python manage.py migrate
```

La création d’un compte administrateur est facultative :

```bash
python manage.py createsuperuser
```

Un compte utilisateur standard peut également être créé depuis la page d’inscription de l’application.

### 5. Lancer le serveur

```bash
python manage.py runserver
```

L’application est ensuite accessible à l’adresse suivante :

[http://127.0.0.1:8000/](http://127.0.0.1:8000/)

## Structure du projet

```text
LITRevu/
├── accounts/           # Authentification et utilisateur personnalisé
├── config/             # Configuration principale de Django
├── reviews/            # Billets, critiques, abonnements et flux
├── static/
│   └── css/            # Feuilles de style
├── templates/
│   ├── accounts/       # Interfaces d’inscription et de connexion
│   └── reviews/        # Interfaces métier
├── manage.py
├── requirements.txt
├── README.md
├── Django+app+web_Cahier+des+charges+[2.0].pdf
└── LITReview+-+Schema.pdf
```

## État et limites connues

- Le projet est actuellement prévu pour une exécution locale.
- Aucune démonstration hébergée n’est disponible.
- Les fichiers de tests sont présents, mais les scénarios automatisés restent à implémenter.
- Le blocage d’un utilisateur demandé dans le cahier des charges n’est pas encore implémenté.
- La configuration actuelle de Django est une configuration de développement et ne doit pas être utilisée telle quelle en production.
- Un audit complet d’accessibilité reste à réaliser.

## Documentation

Le dépôt contient :

- le cahier des charges fonctionnel et technique ;
- le schéma de données fourni pour le projet ;
- les instructions d’installation et d’utilisation locale.

## Auteur

**Adrian Stalin Renault**

Projet réalisé dans le cadre du parcours OpenClassrooms.
