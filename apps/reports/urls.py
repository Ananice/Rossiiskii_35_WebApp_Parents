from django.urls import path
from . import views

app_name = "reports"

urlpatterns = [
    path("", views.reports_index, name="index"),
    path("export/messages/xlsx/", views.export_messages_xlsx, name="export_messages_xlsx"),
]
