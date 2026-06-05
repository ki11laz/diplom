from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render

from users.models import CustomUser

from .forms import (
    ApplicationRequestForm,
    ApplicationStatusForm,
    CourseForm,
    EnrollmentStatusForm,
    GalleryWorkAdminForm,
    NewsCommentForm,
    NewsForm,
    NotificationSendForm,
    WorkModerationForm,
)
from .models import ApplicationRequest, Course, Enrollment, News, NewsComment, Notification, StudentWork


def _admin_guard(request):
    # Проверка прав администратора по ТЗ
    if request.user.role != "admin" and not request.user.is_superuser:
        return False
    return True


def _create_notification(user, title: str, text: str):
    Notification.objects.create(user=user, title=title, text=text)


def home(request):
    popular_courses = Course.objects.filter(is_active=True).order_by("-created_at")[:3]
    last_news = News.objects.filter(is_published=True).order_by("-created_at")[:3]
    gallery_qs = StudentWork.objects.filter(status=StudentWork.STATUS_APPROVED, is_visible=True)
    gallery_items = gallery_qs.order_by("-created_at")[:4]
    drawing_of_the_day = gallery_qs.order_by("?").first()

    selected_course = None
    course_id = (request.GET.get("course") or "").strip()
    if course_id.isdigit():
        selected_course = Course.objects.filter(id=int(course_id), is_active=True).first()

    success = False
    if request.method == "POST":
        form = ApplicationRequestForm(request.POST)
        if form.is_valid():
            app = form.save(commit=False)
            posted_course_id = (request.POST.get("course_id") or "").strip()
            if posted_course_id.isdigit():
                app.course = Course.objects.filter(id=int(posted_course_id), is_active=True).first()
            app.save()
            success = True
            form = ApplicationRequestForm()
    else:
        initial = {}
        if selected_course:
            initial["message"] = f"Хочу записаться на курс «{selected_course.title}»."
        form = ApplicationRequestForm(initial=initial)

    return render(
        request,
        "main/home.html",
        {
            "popular_courses": popular_courses,
            "last_news": last_news,
            "gallery_items": gallery_items,
            "drawing_of_the_day": drawing_of_the_day,
            "form": form,
            "success": success,
            "selected_course": selected_course,
        },
    )


def courses_list(request):
    qs = Course.objects.filter(is_active=True).order_by("title")
    age = (request.GET.get("age") or "").strip()
    direction = (request.GET.get("direction") or "").strip()

    if age:
        qs = qs.filter(age_group=age)
    if direction:
        qs = qs.filter(direction=direction)

    paginator = Paginator(qs, 9)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "main/courses_list.html",
        {
            "page_obj": page_obj,
            "age": age,
            "direction": direction,
            "age_choices": Course.AGE_CHOICES,
            "direction_choices": Course.DIRECTION_CHOICES,
        },
    )


def course_detail(request, slug: str):
    course = get_object_or_404(Course, slug=slug)
    is_student = request.user.is_authenticated and (
        request.user.role == CustomUser.ROLE_STUDENT or request.user.is_superuser
    )

    return render(
        request,
        "main/course_detail.html",
        {
            "course": course,
            "is_student": is_student,
        },
    )


def gallery(request):
    qs = StudentWork.objects.filter(status=StudentWork.STATUS_APPROVED, is_visible=True).select_related("course")
    course_id = (request.GET.get("course") or "").strip()
    technique = (request.GET.get("technique") or "").strip()

    if course_id:
        qs = qs.filter(course_id=course_id)
    if technique:
        qs = qs.filter(technique=technique)

    courses = Course.objects.filter(is_active=True).order_by("title")
    return render(
        request,
        "main/gallery.html",
        {
            "items": qs.order_by("-created_at"),
            "courses": courses,
            "course_id": course_id,
            "technique": technique,
            "technique_choices": StudentWork.TECHNIQUE_CHOICES,
        },
    )


def news_list(request):
    qs = News.objects.filter(is_published=True).order_by("-created_at")
    paginator = Paginator(qs, 6)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "main/news_list.html", {"page_obj": page_obj})


def news_detail(request, slug: str):
    item = get_object_or_404(News, slug=slug, is_published=True)
    comments = NewsComment.objects.select_related("user").filter(news=item).order_by("created_at")

    if request.method == "POST":
        if not request.user.is_authenticated:
            messages.info(request, "Чтобы оставить комментарий, войдите в аккаунт.")
            return redirect("login")
        form = NewsCommentForm(request.POST)
        if form.is_valid():
            comment: NewsComment = form.save(commit=False)
            comment.news = item
            comment.user = request.user
            comment.save()
            return redirect("news_detail", slug=item.slug)
    else:
        form = NewsCommentForm()

    return render(
        request,
        "main/news_detail.html",
        {
            "item": item,
            "comments": comments,
            "form": form,
        },
    )


def contacts(request):
    return render(request, "main/contacts.html")


# ==========================
# Административная панель
# ==========================


@login_required
def manage_dashboard(request):
    if not _admin_guard(request):
        return redirect("home")

    total_courses = Course.objects.count()
    total_students = CustomUser.objects.filter(role=CustomUser.ROLE_STUDENT).count()
    new_applications = ApplicationRequest.objects.filter(status=ApplicationRequest.STATUS_NEW).count()
    works_pending = StudentWork.objects.filter(status=StudentWork.STATUS_PENDING).count()

    return render(
        request,
        "manage/dashboard.html",
        {
            "total_courses": total_courses,
            "total_students": total_students,
            "new_applications": new_applications,
            "works_pending": works_pending,
        },
    )


@login_required
def manage_courses(request):
    if not _admin_guard(request):
        return redirect("home")

    courses = Course.objects.order_by("-created_at")
    return render(request, "manage/courses_list.html", {"courses": courses})


@login_required
def manage_course_add(request):
    if not _admin_guard(request):
        return redirect("home")

    if request.method == "POST":
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Курс добавлен.")
            return redirect("manage_courses")
        messages.error(request, "Не удалось добавить курс. Проверьте поля формы.")
        return redirect("manage_courses")
    else:
        form = CourseForm()
    return render(request, "manage/course_add.html", {"form": form})


@login_required
def manage_course_edit(request, course_id: int):
    if not _admin_guard(request):
        return redirect("home")

    course = get_object_or_404(Course, id=course_id)
    if request.method == "POST":
        form = CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, "Курс обновлён.")
            return redirect("manage_courses")
    else:
        form = CourseForm(instance=course)

    return render(request, "manage/course_edit.html", {"form": form, "course": course})


@login_required
def manage_course_delete(request, course_id: int):
    if not _admin_guard(request):
        return redirect("home")

    course = get_object_or_404(Course, id=course_id)
    course.delete()
    messages.success(request, "Курс удалён.")
    return redirect("manage_courses")


@login_required
def manage_course_enrollments(request, course_id: int):
    if not _admin_guard(request):
        return redirect("home")

    course = get_object_or_404(Course, id=course_id)
    enrollments = Enrollment.objects.filter(course=course).select_related("student").order_by("-created_at")

    if request.method == "POST":
        enrollment_id = request.POST.get("enrollment_id")
        enrollment = get_object_or_404(Enrollment, id=enrollment_id, course=course)
        form = EnrollmentStatusForm(request.POST, instance=enrollment)
        if form.is_valid():
            form.save()
            messages.success(request, "Статус записи обновлён.")
        return redirect("manage_course_enrollments", course_id=course.id)

    return render(request, "manage/course_enrollments.html", {"course": course, "enrollments": enrollments})


@login_required
def manage_gallery(request):
    if not _admin_guard(request):
        return redirect("home")

    if request.method == "POST":
        form = GalleryWorkAdminForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Работа добавлена.")
            return redirect("manage_gallery")
    else:
        form = GalleryWorkAdminForm()

    works = StudentWork.objects.select_related("course", "student").order_by("-created_at")
    return render(request, "manage/gallery.html", {"works": works, "form": form})


@login_required
def manage_work_toggle(request, work_id: int):
    if not _admin_guard(request):
        return redirect("home")

    work = get_object_or_404(StudentWork, id=work_id)
    work.is_visible = not work.is_visible
    work.save(update_fields=["is_visible"])
    return redirect("manage_gallery")


@login_required
def manage_work_edit(request, work_id: int):
    if not _admin_guard(request):
        return redirect("home")

    work = get_object_or_404(StudentWork, id=work_id)
    if request.method == "POST":
        form = GalleryWorkAdminForm(request.POST, request.FILES, instance=work)
        if form.is_valid():
            form.save()
            messages.success(request, "Работа обновлена.")
            return redirect("manage_gallery")
    else:
        form = GalleryWorkAdminForm(instance=work)
    return render(request, "manage/work_edit.html", {"form": form, "work": work})


@login_required
def manage_work_delete(request, work_id: int):
    if not _admin_guard(request):
        return redirect("home")
    work = get_object_or_404(StudentWork, id=work_id)
    work.delete()
    messages.success(request, "Работа удалена.")
    return redirect("manage_gallery")


@login_required
def manage_applications(request):
    if not _admin_guard(request):
        return redirect("home")

    status = (request.GET.get("status") or "").strip()
    qs = ApplicationRequest.objects.select_related("course").order_by("-created_at")
    if status:
        qs = qs.filter(status=status)

    if request.method == "POST":
        app_id = request.POST.get("app_id")
        app = get_object_or_404(ApplicationRequest, id=app_id)
        form = ApplicationStatusForm(request.POST, instance=app)
        if form.is_valid():
            form.save()
        return redirect(f"/manage/applications/?status={status}" if status else "manage_applications")

    return render(
        request,
        "manage/applications.html",
        {
            "items": qs,
            "status": status,
            "status_choices": ApplicationRequest.STATUS_CHOICES,
        },
    )


@login_required
def manage_news(request):
    if not _admin_guard(request):
        return redirect("home")

    items = News.objects.order_by("-created_at")
    return render(request, "manage/news_list.html", {"items": items})


@login_required
def manage_news_add(request):
    if not _admin_guard(request):
        return redirect("home")

    if request.method == "POST":
        form = NewsForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Новость добавлена.")
            return redirect("manage_news")
        messages.error(request, "Не удалось добавить новость. Проверьте поля формы.")
        return redirect("manage_news")
    else:
        form = NewsForm()
    return render(request, "manage/news_add.html", {"form": form})


@login_required
def manage_news_edit(request, news_id: int):
    if not _admin_guard(request):
        return redirect("home")

    item = get_object_or_404(News, id=news_id)
    if request.method == "POST":
        form = NewsForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, "Новость обновлена.")
            return redirect("manage_news")
    else:
        form = NewsForm(instance=item)
    return render(request, "manage/news_edit.html", {"form": form, "item": item})


@login_required
def manage_news_toggle(request, news_id: int):
    if not _admin_guard(request):
        return redirect("home")

    item = get_object_or_404(News, id=news_id)
    item.is_published = not item.is_published
    item.save(update_fields=["is_published"])
    return redirect("manage_news")


@login_required
def manage_news_delete(request, news_id: int):
    if not _admin_guard(request):
        return redirect("home")
    item = get_object_or_404(News, id=news_id)
    item.delete()
    return redirect("manage_news")


@login_required
def manage_works_moderation(request):
    if not _admin_guard(request):
        return redirect("home")

    status = (request.GET.get("status") or "").strip()
    qs = StudentWork.objects.select_related("student", "course").order_by("-created_at")
    if status:
        qs = qs.filter(status=status)

    if request.method == "POST":
        work_id = request.POST.get("work_id")
        work = get_object_or_404(StudentWork, id=work_id)
        old_status = work.status
        form = WorkModerationForm(request.POST, instance=work)
        if form.is_valid():
            form.save()
            # Уведомления ученику при изменении статуса
            if work.student and old_status != work.status and work.status in (
                StudentWork.STATUS_APPROVED,
                StudentWork.STATUS_REJECTED,
            ):
                title = "Статус работы изменён"
                text = f"Ваша работа «{work.title}» теперь: {work.get_status_display()}."
                _create_notification(work.student, title, text)
        return redirect(f"/manage/works/?status={status}" if status else "manage_works_moderation")

    return render(
        request,
        "manage/works_moderation.html",
        {
            "items": qs,
            "status": status,
            "status_choices": StudentWork.STATUS_CHOICES,
        },
    )


@login_required
def manage_send_notification(request):
    if not _admin_guard(request):
        return redirect("home")

    students = CustomUser.objects.filter(role=CustomUser.ROLE_STUDENT).order_by("first_name", "last_name")
    student_choices = [(str(s.id), s.__str__()) for s in students]

    if request.method == "POST":
        form = NotificationSendForm(request.POST, student_choices=student_choices)
        if form.is_valid():
            recipient = form.cleaned_data["recipient"]
            title = form.cleaned_data["title"]
            text = form.cleaned_data["text"]

            if recipient == "all":
                for s in students:
                    _create_notification(s, title, text)
            else:
                user = get_object_or_404(CustomUser, id=int(recipient))
                _create_notification(user, title, text)

            messages.success(request, "Уведомление отправлено.")
            return redirect("manage_dashboard")
    else:
        form = NotificationSendForm(student_choices=student_choices)

    return render(request, "manage/notify.html", {"form": form})
