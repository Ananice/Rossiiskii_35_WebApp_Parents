from django import forms
from .models import Feedback

MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5 MB

ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # docx
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",        # xlsx
}


class FeedbackForm(forms.ModelForm):
    file = forms.FileField(required=False, label="Вложение (до 5 МБ)")

    class Meta:
        model = Feedback
        fields = ["name", "email", "phone", "subject", "message", "consent_pd"]
        widgets = {"message": forms.Textarea(attrs={"rows": 5})}

    def clean_consent_pd(self):
        consent = self.cleaned_data.get("consent_pd")
        if not consent:
            raise forms.ValidationError("Для отправки обращения необходимо согласие на обработку ПДн.")
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
