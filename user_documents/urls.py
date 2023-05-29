from django.urls import path
from . import views

app_name = 'user_documents'

urlpatterns = [
    path("", views.IndexPageView.as_view(), name="index"),
]
