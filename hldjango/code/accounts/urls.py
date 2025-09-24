from django.urls import include, path

from .views import ProfileView, ProfileEditView, ExportEmailsView



urlpatterns = [
    path("profile/edit", ProfileEditView.as_view(), name="accountEditProfile"),
    path("profile/edit/<int:pk>", ProfileEditView.as_view(), name="accountEditProfile"),
    path("profile", ProfileView.as_view(), name="accountProfile"),
    path("profile/<int:pk>", ProfileView.as_view(), name="accountProfile"),
    path("export-emails/", ExportEmailsView.as_view(), name="exportEmails"),
    path("export-emails/<int:group_id>", ExportEmailsView.as_view(), name="exportEmails"),
]
