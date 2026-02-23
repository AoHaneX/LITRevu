# LITRevu
LITReview est une application web développée avec Django permettant :

* de demander des critiques sur un livre ou un article (Tickets)

* de publier des critiques (Reviews)

* de suivre d'autres utilisateurs

* de consulter un flux personnalisé combinant billets et critiques

* Ce projet correspond au MVP demandé dans le cahier des charges.

## 🚀 Fonctionnalités principales:

### 👤 Authentification:

* Inscription avec modèle utilisateur personnalisé

* Connexion / Déconnexion

* Accès protégé aux pages authentifiées

### 📝 Billets (Tickets)

* Création d’un billet avec image optionnelle

* Modification (réservée à l’auteur)

* Suppression via méthode POST

* Liste des billets personnels

### ⭐ Critiques (Reviews)

* Création d’une critique liée à un billet(Ou création du billet si aucun billet saisit)

* Modification (réservée à l’auteur)

* Suppression via méthode POST

* Aperçu du ticket sur la page de création/modification

### 🔄 Flux

Affichage des billets et critiques :

* de l’utilisateur courant

* des utilisateurs suivis

* Tri par date décroissante

### 👥 Abonnements

* Suivre ou se désabonner d'un utilisateur

* Liste des utilisateurs suivis

* Suggestions d’utilisateurs

* nRecherche dynamique côté client

### 🏗️ Technologies utilisées

* Python 3.13

* Django 6

* SQLite

* HTML5

* CSS personnalisé (sans framework)

* JavaScript (filtrage dynamique)

### ♿ Accessibilité (WCAG)

* L’interface respecte les bonnes pratiques WCAG :

* Labels associés aux champs de formulaire

* Fieldset/legend pour les groupes de radios

* Skip link pour navigation clavier

* Focus visible

* Contraste suffisant

* Attributs alt pour les images

* Actions sensibles via POST + CSRF

### ⚙️ Installation
#### 1️⃣ Cloner le repository
`git clone https://github.com/AoHaneX/LITRevu.git`

`cd LITReview`
#### 2️⃣ Créer un environnement virtuel
`python -m venv venv`

Activer l’environnement :

Windows:

`venv\Scripts\activate`

macOS / Linux

`source venv/bin/activate`
#### 3️⃣ Installer les dépendances
`pip install -r requirements.txt`

Si le fichier n’existe pas :

`pip install django`

#### 4️⃣ Base de données

Le projet utilise SQLite, voici comment créer une base de données locale:
```
python manage.py migrate

python manage.py createsuperuser
```
#### 5️⃣ Lancer le serveur
`python manage.py runserver`

Accéder à l’application par l'url:

http://127.0.0.1:8000/

### 📁 Structure du projet
```
WebDjango/
│
├── accounts/        # Authentification & utilisateur personnalisé
├── reviews/         # Tickets, Reviews, Follow, Feed
├── templates/
│   ├── accounts/
│   └── reviews/
├── static/
│   └── css/
├── config/          # Settings & configuration
└── manage.py
```

### Auteur:
STALIN--RENAULT Adrian

*Projet réalisé dans le cadre du parcours OpenClassrooms.*
