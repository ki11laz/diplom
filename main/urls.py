from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("courses/", views.courses_list, name="courses"),
    path("courses/<slug:slug>/", views.course_detail, name="course_detail"),
    path("gallery/", views.gallery, name="gallery"),
    path("news/", views.news_list, name="news"),
    path("news/<slug:slug>/", views.news_detail, name="news_detail"),
    path("contacts/", views.contacts, name="contacts"),
    # Административная часть (не Django admin)
    path("manage/", views.manage_dashboard, name="manage_dashboard"),
    path("manage/courses/", views.manage_courses, name="manage_courses"),
    path("manage/courses/add/", views.manage_course_add, name="manage_course_add"),
    path("manage/courses/<int:course_id>/edit/", views.manage_course_edit, name="manage_course_edit"),
    path("manage/courses/<int:course_id>/delete/", views.manage_course_delete, name="manage_course_delete"),
    path("manage/courses/<int:course_id>/enrollments/", views.manage_course_enrollments, name="manage_course_enrollments"),
    path("manage/gallery/", views.manage_gallery, name="manage_gallery"),
    path("manage/gallery/<int:work_id>/edit/", views.manage_work_edit, name="manage_work_edit"),
    path("manage/gallery/<int:work_id>/toggle/", views.manage_work_toggle, name="manage_work_toggle"),
    path("manage/gallery/<int:work_id>/delete/", views.manage_work_delete, name="manage_work_delete"),
    path("manage/applications/", views.manage_applications, name="manage_applications"),
    path("manage/news/", views.manage_news, name="manage_news"),
    path("manage/news/add/", views.manage_news_add, name="manage_news_add"),
    path("manage/news/<int:news_id>/edit/", views.manage_news_edit, name="manage_news_edit"),
    path("manage/news/<int:news_id>/toggle/", views.manage_news_toggle, name="manage_news_toggle"),
    path("manage/news/<int:news_id>/delete/", views.manage_news_delete, name="manage_news_delete"),
    path("manage/works/", views.manage_works_moderation, name="manage_works_moderation"),
    path("manage/notify/", views.manage_send_notification, name="manage_send_notification"),
]

