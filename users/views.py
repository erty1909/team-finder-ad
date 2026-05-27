import json
from http import HTTPStatus

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from team_finder.pagination import paginate

from .forms import ChangePasswordForm, EditProfileForm, LoginForm, RegisterForm
from .models import Skill, User

SKILLS_AUTOCOMPLETE_LIMIT = 10


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(reverse("projects:list"))
    else:
        form = RegisterForm()
    return render(request, "users/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data["email"],
                password=form.cleaned_data["password"],
            )
            if user:
                login(request, user)
                return redirect(reverse("projects:list"))
            form.add_error(None, "Неверный имейл или пароль")
    else:
        form = LoginForm()
    return render(request, "users/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect(reverse("projects:list"))


def user_detail(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    return render(request, "users/user-details.html", {"user": user})


@login_required
def edit_profile(request):
    if request.method == "POST":
        form = EditProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect(reverse("users:detail", kwargs={"user_id": request.user.id}))
    else:
        form = EditProfileForm(instance=request.user)
    return render(request, "users/edit_profile.html", {"form": form})


@login_required
def change_password(request):
    if request.method == "POST":
        form = ChangePasswordForm(request.user, request.POST)
        if form.is_valid():
            request.user.set_password(form.cleaned_data["new_password1"])
            request.user.save()
            login(request, request.user)
            return redirect(reverse("users:detail", kwargs={"user_id": request.user.id}))
    else:
        form = ChangePasswordForm(request.user)
    return render(request, "users/change_password.html", {"form": form})


def users_list(request):
    skill_name = request.GET.get("skill", "").strip()
    all_skills = Skill.objects.all()
    participants = User.objects.order_by("-id")
    active_skill = None

    if skill_name:
        participants = participants.filter(skills__name=skill_name).distinct()
        active_skill = skill_name

    page_obj, pagination_query = paginate(participants, request)

    return render(
        request,
        "users/participants.html",
        {
            "participants": page_obj,
            "page_obj": page_obj,
            "pagination_query": pagination_query,
            "all_skills": all_skills,
            "active_skill": active_skill,
        },
    )


def skills_autocomplete(request):
    q = request.GET.get("q", "").strip()
    qs = Skill.objects.filter(name__istartswith=q).order_by("name")[:SKILLS_AUTOCOMPLETE_LIMIT]
    data = [{"id": s.id, "name": s.name} for s in qs]
    return JsonResponse(data, safe=False)


@login_required
@require_POST
def add_skill(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    if request.user != user:
        return JsonResponse({"error": "Forbidden"}, status=HTTPStatus.FORBIDDEN)

    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        body = {}

    skill_id = body.get("skill_id")
    name = body.get("name", "").strip()
    created = False
    added = False

    if skill_id:
        skill = get_object_or_404(Skill, pk=skill_id)
    elif name:
        skill, created = Skill.objects.get_or_create(name=name)
    else:
        return JsonResponse(
            {"error": "skill_id or name required"},
            status=HTTPStatus.BAD_REQUEST,
        )

    if not user.skills.filter(pk=skill.pk).exists():
        user.skills.add(skill)
        added = True

    return JsonResponse({
        "skill_id": skill.id,
        "name": skill.name,
        "created": created,
        "added": added,
    })


@login_required
@require_POST
def remove_skill(request, user_id, skill_id):
    user = get_object_or_404(User, pk=user_id)
    if request.user != user:
        return JsonResponse({"error": "Forbidden"}, status=HTTPStatus.FORBIDDEN)
    skill = get_object_or_404(Skill, pk=skill_id)
    if not user.skills.filter(pk=skill.pk).exists():
        return JsonResponse({"error": "Skill not assigned"}, status=HTTPStatus.BAD_REQUEST)
    user.skills.remove(skill)
    return JsonResponse({"status": "ok"})
