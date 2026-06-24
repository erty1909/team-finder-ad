from http import HTTPStatus

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from team_finder.pagination import paginate

from .constants import STATUS_CLOSED, STATUS_OPEN
from .forms import ProjectForm
from .models import Project


def project_list(request):
    projects = (
        Project.objects
        .select_related("owner")
        .prefetch_related("participants")
        .order_by("-created_at", "-id")
        .all()
    )
    page_obj, pagination_query = paginate(projects, request)
    return render(
        request,
        "projects/project_list.html",
        {"projects": page_obj, "page_obj": page_obj, "pagination_query": pagination_query},
    )


def project_detail(request, project_id):
    project = get_object_or_404(
        Project.objects.select_related("owner").prefetch_related("participants"),
        pk=project_id,
    )
    return render(request, "projects/project-details.html", {"project": project})


@login_required
def create_project(request):
    form = ProjectForm(request.POST or None)
    if form.is_valid():
        project = form.save(commit=False)
        project.owner = request.user
        project.save()
        project.participants.add(request.user)
        return redirect("projects:detail", project_id=project.id)
    return render(request, "projects/create-project.html", {"form": form, "is_edit": False})


@login_required
def edit_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id, owner=request.user)
    form = ProjectForm(request.POST or None, instance=project)
    if form.is_valid():
        form.save()
        return redirect("projects:detail", project_id=project.id)
    return render(request, "projects/create-project.html", {"form": form, "is_edit": True})


@login_required
@require_POST
def complete_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id, owner=request.user)
    if project.status != STATUS_OPEN:
        return JsonResponse(
            {"status": "error", "detail": "already closed"},
            status=HTTPStatus.BAD_REQUEST,
        )
    project.status = STATUS_CLOSED
    project.save()
    return JsonResponse({"status": "ok", "project_status": STATUS_CLOSED})


@login_required
@require_POST
def toggle_participate(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    user = request.user

    if user == project.owner:
        return JsonResponse(
            {"status": "error", "detail": "owner cannot toggle"},
            status=HTTPStatus.BAD_REQUEST,
        )

    if project.participants.filter(pk=user.pk).exists():
        project.participants.remove(user)
        return JsonResponse({"status": "ok", "participant": False})

    project.participants.add(user)
    return JsonResponse({"status": "ok", "participant": True})
