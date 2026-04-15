from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core.management import call_command
from django_q.tasks import async_task
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import System, TaskHistory
from .serializers import TaskHistorySerializer
from .services import hdbalm_wrapper, diff_engine
from django.conf import settings

# --- UI VIEWS ---
@login_required
def home(request):
    systems = System.objects.all().order_by('name', 'tenant')
    return render(request, 'delivery_units/home.html', {'systems': systems})

@login_required
def list_dus(request):
    system_id = request.GET.get('system_id')
    if not system_id: return HttpResponse("No system selected.")
    system = System.objects.get(id=system_id)
    success, output = hdbalm_wrapper.list_dus(system.hostname, system.alm_port)
    return HttpResponse(output)

@login_required
@require_POST
def sync_systems_view(request):
    call_command('sync_systems')
    return HttpResponse("Registry synced.")

# --- BACKGROUND TASKS (Django Q2) ---
def run_export_task(task_id):
    task = TaskHistory.objects.get(id=task_id)
    task.status = 'RUNNING'
    task.save()
    try:
        source = task.source_system
        success, result = hdbalm_wrapper.export_du(source.hostname, source.alm_port, task.du_name)
        if success:
            task.filename = result
            diff_text = diff_engine.process_export_and_diff(settings.HDBCLIENT_DIR, result, task.du_name)
            task.diff_text = diff_text
            task.status = 'SUCCESS'
        else:
            task.error_message = result
            task.status = 'FAILURE'
    except Exception as e:
        task.error_message = str(e)
        task.status = 'FAILURE'
    task.save()

def run_import_task(task_id, target_ids):
    task = TaskHistory.objects.get(id=task_id)
    task.status = 'RUNNING'
    task.save()
    results = []
    overall_success = True
    try:
        targets = System.objects.filter(id__in=target_ids)
        for target in targets:
            success, output = hdbalm_wrapper.import_du(target.hostname, target.alm_port, task.filename)
            results.append(f"System: {target.name} - Success: {success} - Output: {output}")
            if not success: overall_success = False
        task.error_message = "\n---\n".join(results)
        task.status = 'SUCCESS' if overall_success else 'FAILURE'
    except Exception as e:
        task.error_message = str(e)
        task.status = 'FAILURE'
    task.save()

# --- HTMX ACTIONS ---
@login_required
@require_POST
def start_export(request):
    system_id = request.POST.get('system_id')
    du_name = request.POST.get('du_name')
    if not system_id: return HttpResponse("<div class='alert alert-danger'>No source selected.</div>")
    system = System.objects.get(id=system_id)
    task = TaskHistory.objects.create(task_type='EXPORT', source_system=system, du_name=du_name, user=request.user)
    async_task(run_export_task, task.id)
    return render(request, 'delivery_units/partials/task_status.html', {'task': task})

@login_required
def task_status_view(request, task_id):
    task = TaskHistory.objects.get(id=task_id)
    return render(request, 'delivery_units/partials/task_status.html', {'task': task})

@login_required
def deploy_fragment(request, task_id):
    task = TaskHistory.objects.get(id=task_id)
    systems = System.objects.all().order_by('name')
    stages = System.STAGE_CHOICES
    return render(request, 'delivery_units/partials/deploy_fragment.html', {
        'task': task, 'systems': systems, 'stages': stages
    })

@login_required
@require_POST
def start_import(request):
    stages = request.POST.getlist('stages')
    specific_id = request.POST.get('specific_id')
    filename = request.POST.get('filename')
    du_name = request.POST.get('du_name')
    source_id = request.POST.get('source_id')
    target_ids = []
    if specific_id: target_ids.append(specific_id)
    else: target_ids = list(System.objects.filter(stage__in=stages).exclude(id=source_id).values_list('id', flat=True))
    if not target_ids: return HttpResponse("<div class='alert alert-danger'>No target systems found.</div>")
    task = TaskHistory.objects.create(task_type='IMPORT', filename=filename, du_name=du_name, user=request.user)
    async_task(run_import_task, task.id, target_ids)
    return render(request, 'delivery_units/partials/task_status.html', {'task': task})

# --- HEADLESS API (HAC Integration) ---
class DirectDeployView(APIView):
    def post(self, request):
        target_sid = request.data.get('sid')
        du_name = request.data.get('du_name')
        if not target_sid or not du_name:
            return Response({'error': 'Missing sid or du_name'}, status=status.HTTP_400_BAD_REQUEST)
        target_system = System.objects.filter(name=target_sid.upper()).first()
        if not target_system:
            return Response({'error': f'System {target_sid} not found'}, status=status.HTTP_404_NOT_FOUND)
        latest_file = hdbalm_wrapper.get_latest_export(du_name)
        if not latest_file:
            return Response({'error': f'No existing export for {du_name}'}, status=status.HTTP_404_NOT_FOUND)
        task = TaskHistory.objects.create(task_type='IMPORT', filename=latest_file, du_name=du_name, user=request.user)
        task.target_systems.add(target_system)
        async_task(run_import_task, task.id, [target_system.id])
        return Response({
            'message': 'Direct Deployment initiated',
            'task_id': task.id,
            'status_url': f'/du-automation/api/v1/task-status/{task.id}/'
        }, status=status.HTTP_202_ACCEPTED)

class TaskStatusAPIView(APIView):
    def get(self, request, pk):
        task = TaskHistory.objects.get(id=pk)
        return Response(TaskHistorySerializer(task).data)
