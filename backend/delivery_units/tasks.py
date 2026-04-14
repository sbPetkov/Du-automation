from celery import shared_task
from django.core.management import call_command
from .models import System, TaskHistory
from .services import hdbalm_wrapper, diff_engine
from django.conf import settings
import os

@shared_task
def sync_systems_task():
    call_command('sync_systems')

@shared_task
def export_du_task(task_id):
    task = TaskHistory.objects.get(id=task_id)
    task.status = 'RUNNING'
    task.save()

    try:
        source = task.source_system
        success, result = hdbalm_wrapper.export_du(source.hostname, source.alm_port, task.du_name)
        
        if success:
            task.filename = result
            # Process diff
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

@shared_task
def import_du_task(task_id, target_ids):
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
            if not success:
                overall_success = False
        
        task.error_message = "\n---\n".join(results)
        task.status = 'SUCCESS' if overall_success else 'FAILURE'
    except Exception as e:
        task.error_message = str(e)
        task.status = 'FAILURE'
    
    task.save()
