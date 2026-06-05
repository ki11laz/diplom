from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import CustomUser
from main.models import Course, StudentWork


class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Логин или email")


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(label="Имя", max_length=150)
    last_name = forms.CharField(label="Фамилия", max_length=150)
    email = forms.EmailField(label="Email")
    phone = forms.CharField(label="Телефон", max_length=30)

    class Meta:
        model = CustomUser
        fields = ("first_name", "last_name", "email", "phone", "password1", "password2")
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        # Роль после регистрации — ученик
        user.role = CustomUser.ROLE_STUDENT
        user.username = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ("first_name", "email", "phone", "avatar")
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "avatar": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }


class WorkUploadForm(forms.ModelForm):
    class Meta:
        model = StudentWork
        fields = ("title", "image", "description", "course", "technique")
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "image": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "technique": forms.Select(attrs={"class": "form-select"}),
        }

    course = forms.ModelChoiceField(
        label="К какому курсу относится",
        queryset=Course.objects.filter(is_active=True).order_by("title"),
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )

