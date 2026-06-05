from django import forms

from .models import ApplicationRequest, Course, News, NewsComment, StudentWork, Enrollment, Notification


class ApplicationRequestForm(forms.ModelForm):
    class Meta:
        model = ApplicationRequest
        fields = ("name", "phone", "email", "message")
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "message": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = (
            "title",
            "short_description",
            "description",
            "price",
            "age_group",
            "direction",
            "image",
            "schedule",
            "is_active",
        )
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "short_description": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 6}),
            "price": forms.NumberInput(attrs={"class": "form-control"}),
            "age_group": forms.Select(attrs={"class": "form-select"}),
            "direction": forms.Select(attrs={"class": "form-select"}),
            "image": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "schedule": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = ("title", "short_text", "text", "image", "is_published")
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "short_text": forms.TextInput(attrs={"class": "form-control"}),
            "text": forms.Textarea(attrs={"class": "form-control", "rows": 8}),
            "image": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "is_published": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class NewsCommentForm(forms.ModelForm):
    class Meta:
        model = NewsComment
        fields = ("text",)
        widgets = {
            "text": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Напишите комментарий…",
                }
            )
        }


class GalleryWorkAdminForm(forms.ModelForm):
    class Meta:
        model = StudentWork
        fields = (
            "title",
            "image",
            "student",
            "technique",
            "course",
            "status",
            "is_visible",
        )
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "image": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "student": forms.Select(attrs={"class": "form-select"}),
            "technique": forms.Select(attrs={"class": "form-select"}),
            "course": forms.Select(attrs={"class": "form-select"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "is_visible": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class EnrollmentStatusForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ("status",)
        widgets = {"status": forms.Select(attrs={"class": "form-select", "onchange": "this.form.submit()"})}


class ApplicationStatusForm(forms.ModelForm):
    class Meta:
        model = ApplicationRequest
        fields = ("status",)
        widgets = {"status": forms.Select(attrs={"class": "form-select", "onchange": "this.form.submit()"})}


class WorkModerationForm(forms.ModelForm):
    class Meta:
        model = StudentWork
        fields = ("status", "admin_comment")
        widgets = {
            "status": forms.Select(attrs={"class": "form-select", "onchange": "this.form.submit()"}),
            "admin_comment": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
        }


class NotificationSendForm(forms.Form):
    recipient = forms.ChoiceField(
        label="Получатель",
        choices=(("all", "Все ученики"),),
        required=True,
    )
    title = forms.CharField(label="Заголовок", max_length=255)
    text = forms.CharField(label="Текст", widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        student_choices = kwargs.pop("student_choices", [])
        super().__init__(*args, **kwargs)
        self.fields["recipient"].choices = (("all", "Все ученики"),) + tuple(student_choices)
        self.fields["recipient"].widget.attrs.update({"class": "form-select"})
        self.fields["title"].widget.attrs.update({"class": "form-control"})
        self.fields["text"].widget.attrs.update({"class": "form-control", "rows": 5})

