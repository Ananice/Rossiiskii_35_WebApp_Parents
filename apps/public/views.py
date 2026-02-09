from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404

from .forms import FeedbackForm
from .models import Feedback, News


def _public_base_context(title, breadcrumbs):
    return {"page_title": title, "breadcrumbs": breadcrumbs}


def index(request):
    ctx = _public_base_context("Главная", [("Главная", None)])
    return render(request, "public/index.html", ctx)


def page(request, slug):
    pages = {
        "about": ("О проекте", "public/pages/about.html"),
        "features": ("Возможности", "public/pages/features.html"),
        "roles": ("Роли", "public/pages/roles.html"),
        "security": ("Безопасность", "public/pages/security.html"),
        "docs": ("Документация", "public/pages/docs.html"),
        "faq": ("FAQ", "public/pages/faq.html"),
        "sitemap": ("Карта сайта", "public/pages/sitemap.html"),
        "privacy": ("Политика ПДн", "public/pages/privacy.html"),
        "terms": ("Пользовательское соглашение", "public/pages/terms.html"),
    }

    if slug not in pages:
        raise Http404()

    title, template = pages[slug]
    ctx = _public_base_context(title, [("Главная", "/"), (title, None)])
    return render(request, template, ctx)


def news_list(request):
    items = News.objects.filter(is_published=True)
    ctx = _public_base_context("Новости", [("Главная", "/"), ("Новости", None)])
    ctx["items"] = items
    return render(request, "public/news/list.html", ctx)


def contacts(request):
    if request.method == "POST":
        form = FeedbackForm(request.POST, request.FILES)
        if form.is_valid():
            fb = form.save(commit=False)

            f = form.cleaned_data.get("file")
            if f:
                fb.file_name = f.name
                fb.file_content_type = getattr(f, "content_type", "") or ""
                fb.file_size = f.size
                fb.file_data = f.read()

            fb.save()
            return redirect("public:contacts_success", public_id=fb.public_id)
    else:
        form = FeedbackForm()

    ctx = _public_base_context("Обратная связь", [("Главная", "/"), ("Обратная связь", None)])
    ctx["form"] = form
    return render(request, "public/contacts/form.html", ctx)


def contacts_success(request, public_id):
    ctx = _public_base_context(
        "Обращение отправлено",
        [("Главная", "/"), ("Обратная связь", "/contacts/"), ("Успешно", None)],
    )
    ctx["public_id"] = public_id
    return render(request, "public/contacts/success.html", ctx)


def _is_staff_role(user):
    return getattr(user, "role", None) in ("admin", "employee")
    
def _is_admin(user):
    return getattr(user, "role", None) == "admin"


@login_required
def staff_feedback_list(request):
    if not _is_staff_role(request.user):
        return HttpResponse("Доступ запрещён", status=403)

    items = Feedback.objects.all()
    return render(request, "public/staff/feedback_list.html", {"items": items})


@login_required
def staff_feedback_detail(request, public_id):
    if not _is_staff_role(request.user):
        return HttpResponse("Доступ запрещён", status=403)

    fb = get_object_or_404(Feedback, public_id=public_id)
    return render(request, "public/staff/feedback_detail.html", {"fb": fb})


@login_required
def staff_feedback_attachment(request, public_id):
    if not _is_admin(request.user):
        return HttpResponse("Доступ запрещён", status=403)

    fb = get_object_or_404(Feedback, public_id=public_id)
    if not fb.file_data:
        raise Http404()

    resp = HttpResponse(fb.file_data, content_type=fb.file_content_type or "application/octet-stream")
    filename = fb.file_name or "attachment.bin"
    resp["Content-Disposition"] = f'attachment; filename="{filename}"'
    return resp
