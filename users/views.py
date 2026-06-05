from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from main.models import Enrollment, Notification, StudentWork

from .forms import RegisterForm, StudentProfileForm, WorkUploadForm
from .models import CustomUser


def user_login(request):
    if request.method == "POST":
        username_or_email = (request.POST.get("username") or "").strip()
        password = request.POST.get("password") or ""

        # Разрешаем вход по email: в регистрации username = email
        user = authenticate(request, username=username_or_email, password=password)
        if user is None:
            user = authenticate(request, username=username_or_email.lower(), password=password)

        if user is not None:
            login(request, user)
            return redirect("home")

        messages.error(request, "Неверные данные для входа.")

    return render(request, "users/login.html")


def user_logout(request):
    logout(request)
    return redirect("home")


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Регистрация успешна!")
            return redirect("home")
    else:
        form = RegisterForm()

    return render(request, "users/register.html", {"form": form})


@login_required
def cabinet_profile(request):
    # Личный кабинет доступен ученику (и можно оставить доступным всем ролям)
    user: CustomUser = request.user

    if request.method == "POST":
        form = StudentProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Данные сохранены.")
            return redirect("cabinet_profile")
    else:
        form = StudentProfileForm(instance=user)

    return render(request, "users/cabinet_profile.html", {"form": form})


@login_required
def cabinet_works(request):
    user: CustomUser = request.user
    works = StudentWork.objects.select_related("course").filter(student=user).order_by("-created_at")
    return render(request, "users/cabinet_works.html", {"works": works})


@login_required
def work_upload(request):
    user: CustomUser = request.user
    if user.role != CustomUser.ROLE_STUDENT and not user.is_superuser:
        return redirect("home")

    if request.method == "POST":
        form = WorkUploadForm(request.POST, request.FILES)
        if form.is_valid():
            work: StudentWork = form.save(commit=False)
            work.student = user
            work.status = StudentWork.STATUS_PENDING
            work.is_visible = True
            work.save()
            messages.success(request, "Работа загружена и отправлена на модерацию.")
            return redirect("cabinet_works")
    else:
        form = WorkUploadForm()

    return render(request, "users/work_upload.html", {"form": form})


@login_required
def work_delete(request, work_id: int):
    user: CustomUser = request.user
    work = get_object_or_404(StudentWork, id=work_id, student=user)
    if work.status == StudentWork.STATUS_APPROVED:
        messages.error(request, "Одобренную работу удалить нельзя.")
        return redirect("cabinet_works")

    work.delete()
    messages.success(request, "Работа удалена.")
    return redirect("cabinet_works")


@login_required
def notifications_list(request):
    qs = Notification.objects.filter(user=request.user).order_by("-created_at")
    # Непрочитанные должны быть выделены — поэтому сначала фиксируем список, потом помечаем как прочитанные
    items = list(qs)
    qs.filter(is_read=False).update(is_read=True)
    return render(request, "users/notifications.html", {"items": items})


@login_required
def notifications_unread_count(request):
    count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({"count": count})
