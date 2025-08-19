from django.urls import path

from accounts.views import PostLoginRedirectView
from . import views

app_name = "workspaces"

urlpatterns = [
    path("dg/", views.DGWorkspaceView.as_view(), name="dg"),
    path("rh/", views.RHWorkspaceView.as_view(), name="rh"),
    path("actuaire/", views.ActuaireWorkspaceView.as_view(), name="actuaire"),
    path("commercial/", views.CommercialWorkspaceView.as_view(), name="commercial"),
    path("redacteur/", views.RedacteurWorkspaceView.as_view(), name="redacteur"),
    path("gestionnaire/", views.GestionnaireWorkspaceView.as_view(), name="gestionnaire"),
    path("comptable/", views.ComptableWorkspaceView.as_view(), name="comptable"),
    path("me/", PostLoginRedirectView.as_view(), name="me"),
]
