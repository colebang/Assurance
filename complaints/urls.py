from django.urls import path

from . import views

app_name = "complaints"

urlpatterns = [
    path("", views.ComplaintListView.as_view(), name="complaint_list"),
    path("new/", views.ComplaintCreateView.as_view(), name="complaint_create"),
    path("<int:pk>/", views.ComplaintDetailView.as_view(), name="complaint_detail"),
    path("<int:pk>/answer/", views.ComplaintAnswerView.as_view(), name="complaint_answer"),
    path("<int:pk>/close/", views.ComplaintCloseView.as_view(), name="complaint_close"),
]
