# LITRevu
Application web Django permettant aux utilisateurs de demander, publier et consulter des critiques de livres et d’articles via un flux personnalisé.


## Structure du projet
- `config/settings.py` : Global Django configuration (apps, database, authentication, templates, static files).
- `config/urls.py` : Root URL routing of the project.
- `accounts/models.py` : Custom user model used for authentication.
- `accounts/views.py` : Views handling login, logout and user registration.
- `accounts/urls.py` : URL routes for authentication pages.
- `reviews/models.py` : Core business models (Ticket, Review, UserFollows).
- `reviews/forms.py` : Forms used to create and edit tickets and reviews.
- `reviews/views.py` : Views implementing CRUD operations for tickets and reviews.
- `reviews/urls.py` : URL routes for ticket and review actions.
- `reviews/admin.py` : Django admin configuration for tickets, reviews and user follows.
- `templates/base.html` : Base template shared by all pages (layout and navigation bar).
- `templates/accounts/home.html` : Public home page with login form and signup access.
- `templates/accounts/signup.html` : User registration page.
- `templates/reviews/ticket_form.html` : Form page for creating and editing tickets.
- `templates/reviews/ticket_confirm_delete.html` : Confirmation page for ticket deletion.
- `templates/reviews/review_form.html` : Form page for creating and editing reviews.
- `templates/reviews/review_confirm_delete.html` : Confirmation page for review deletion.
- `static/css/style.css` : Global stylesheet following WCAG accessibility guidelines.


## Structure des fichiers principaux

- `config/settings.py` : Configuration globale du projet Django (applications, base de données, authentification, fichiers statiques et médias).
- `config/urls.py` : Routes principales du projet et inclusion des URLs des différentes applications.
- `accounts/models.py` : Définition du modèle utilisateur personnalisé utilisé pour l’authentification.
- `accounts/views.py` : Vues liées à l’inscription, la connexion et la déconnexion des utilisateurs.
- `accounts/forms.py` : Formulaires d’inscription des utilisateurs.
- `accounts/urls.py` : Routes pour l’authentification (login, logout, signup).
- `reviews/models.py` : Modèles métier de l’application (Ticket, Review, UserFollows).
- `reviews/forms.py` : Formulaires pour la création et la modification des billets et des critiques.
- `reviews/views.py` : Vues permettant l’ajout, la modification et la suppression des billets et des critiques.
- `reviews/urls.py` : Routes associées aux opérations CRUD sur les billets et les critiques.
- `reviews/admin.py` : Configuration de l’interface d’administration Django pour tester et gérer les modèles.
- `templates/base.html` : Template de base commun à toutes les pages (bandeau, navigation, structure générale).
- `templates/accounts/home.html` : Page d’accueil publique avec formulaire de connexion et accès à l’inscription.
- `templates/accounts/signup.html` : Page d’inscription des utilisateurs.
- `templates/reviews/ticket_form.html` : Page de création et de modification d’un billet.
- `templates/reviews/ticket_confirm_delete.html` : Page de confirmation de suppression d’un billet.
- `templates/reviews/review_form.html` : Page de création et de modification d’une critique.
- `templates/reviews/review_confirm_delete.html` : Page de confirmation de suppression d’une critique.
- `static/css/style.css` : Feuille de style principale du site, conforme aux recommandations d’accessibilité WCAG.