from django.urls import path

from . import views

urlpatterns = [
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("register/", views.register, name="register"),
    path("cabinet/", views.cabinet_profile, name="cabinet_profile"),
    path("cabinet/works/", views.cabinet_works, name="cabinet_works"),
    path("cabinet/works/upload/", views.work_upload, name="work_upload"),
    path("cabinet/works/<int:work_id>/delete/", views.work_delete, name="work_delete"),
    path("notifications/", views.notifications_list, name="notifications"),
    path("notifications/unread-count/", views.notifications_unread_count, name="notifications_unread_count"),
]

