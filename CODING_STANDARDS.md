Python : Django 5, CBV (ListView, CreateView…), django-filter pour filtres, services (services.py) pour logique métier, signals.py pour transitions.

DB : SQLite (dev). Timestamps cohérents.

Sécurité : permissions par Group + checks objet côté vues/services.

Front : templates/base.html, composants tables (DataTables init), charts via endpoints JSON.

Tests : pytest + pytest-django, tests modèles/services/urls/views basiques.

Commits : style court et clair (“catalog: add Product/Coverage models + admin”).

Definition of Done (par tâche) : modèles + admin + migrations + urls + vues + templates + permissions + tests verts + doc courte dans README d’app.