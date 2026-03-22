from django import forms
from .models import Feedback

MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5 MB

ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}

FIELD_CLASS = {"class": "form-control"}
FIELD_CLASS_SELECT = {"class": "form-select"}


class FeedbackForm(forms.ModelForm):
    file = forms.FileField(
        required=False,
        label="Вложение",
        widget=forms.ClearableFileInput(attrs={"class": "form-control"}),
    )

    class Meta:
        model = Feedback
        fields = ["name", "email", "phone", "subject", "message", "consent_pd"]
        widgets = {
            "name": forms.TextInput(attrs={
                **FIELD_CLASS,
                "placeholder": "Иванова Мария Петровна",
            }),
            "email": forms.EmailInput(attrs={
                **FIELD_CLASS,
                "placeholder": "example@mail.ru",
            }),
            "phone": forms.TextInput(attrs={
                **FIELD_CLASS,
                "placeholder": "+7 (___) ___-__-__",
            }),
            "subject": forms.TextInput(attrs={
                **FIELD_CLASS,
                "placeholder": "Кратко опишите тему",
            }),
            "message": forms.Textarea(attrs={
                **FIELD_CLASS,
                "rows": 5,
                "placeholder": "Подробно опишите ваш вопрос или обращение...",
            }),
            "consent_pd": forms.CheckboxInput(attrs={
                "class": "form-check-input",
            }),
        }

    def clean_consent_pd(self):
        consent = self.cleaned_data.get("consent_pd")
        if not consent:
            raise forms.ValidationError(
                "Для отправки обращения необходимо согласие на обработку ПДн."
            )
        return consent

    def clean_file(self):
        f = self.cleaned_data.get("file")
        if not f:
            return f
        if f.size > MAX_UPLOAD_SIZE:
            raise forms.ValidationError("Файл слишком большой. Максимум 5 МБ.")
        content_type = getattr(f, "content_type", "")
        if content_type and content_type not in ALLOWED_CONTENT_TYPES:
            raise forms.ValidationError("Недопустимый тип файла.")
        return f
