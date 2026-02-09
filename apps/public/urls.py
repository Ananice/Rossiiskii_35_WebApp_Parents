from django.urls import path
from . import views

app_name = "public"

urlpatterns = [
    path("", views.index, name="index"),

    path("about/", views.page, {"slug": "about"}, name="about"),
    path("features/", views.page, {"slug": "features"}, name="features"),
    path("roles/", views.page, {"slug": "roles"}, name="roles"),
    path("security/", views.page, {"slug": "security"}, name="security"),
    path("docs/", views.page, {"slug": "docs"}, name="docs"),
    path("faq/", views.page, {"slug": "faq"}, name="faq"),

    path("news/", views.news_list, name="news"),
    path("sitemap/", views.page, {"slug": "sitemap"}, name="sitemap"),

    path("contacts/", views.contacts, name="contacts"),
    path("contacts/success/<str:public_id>/", views.contacts_success, name="contacts_success"),

    path("privacy/", views.page, {"slug": "privacy"}, name="privacy"),
    path("terms/", views.page, {"slug": "terms"}, name="terms"),

    path("staff/feedback/", views.staff_feedback_list, name="staff_feedback_list"),
    path("staff/feedback/<str:public_id>/", views.staff_feedback_detail, name="staff_feedback_detail"),
    path("staff/feedback/<str:public_id>/attachment/", views.staff_feedback_attachment, name="staff_feedback_attachment"),
]
