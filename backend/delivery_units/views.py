from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.core.management import call_command
from .models import System, TaskHistory
from .serializers import SystemSerializer, TaskHistorySerializer
from .services import hdbalm_wrapper
from .tasks import export_du_task, import_du_task
import json

class SystemListView(APIView):
    def get(self, request):
        systems = System.objects.all().order_by('name', 'tenant')
        serializer = SystemSerializer(systems, many=True)
        return Response(serializer.data)

class SyncSystemsView(APIView):
    def post(self, request):
        try:
            call_command('sync_systems')
            return Response({'message': 'Systems synchronized successfully'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ListDUsView(APIView):
    def get(self, request):
        system_id = request.query_params.get('system_id')
        try:
            system = System.objects.get(id=system_id)
            success, output = hdbalm_wrapper.list_dus(system.hostname, system.alm_port)
            return Response({'success': success, 'output': output})
        except System.DoesNotExist:
            return Response({'error': 'System not found'}, status=status.HTTP_404_NOT_FOUND)

class StartExportView(APIView):
    def post(self, request):
        system_id = request.data.get('system_id')
        du_name = request.data.get('du_name')
        
        try:
            system = System.objects.get(id=system_id)
            task = TaskHistory.objects.create(
                task_type='EXPORT',
                source_system=system,
                du_name=du_name,
                user=request.user
            )
            export_du_task.delay(task.id)
            return Response({'task_id': task.id}, status=status.HTTP_201_CREATED)
        except System.DoesNotExist:
            return Response({'error': 'System not found'}, status=status.HTTP_404_NOT_FOUND)

class StartImportView(APIView):
    def post(self, request):
        stages = request.data.get('stages', [])
        specific_id = request.data.get('specific_id')
        filename = request.data.get('filename')
        du_name = request.data.get('du_name')
        source_id = request.data.get('source_id')

        target_ids = []
        if specific_id:
            target_ids.append(specific_id)
        else:
            target_ids = list(System.objects.filter(stage__in=stages).exclude(id=source_id).values_list('id', flat=True))

        if not target_ids:
            return Response({'error': 'No target systems found'}, status=status.HTTP_400_BAD_REQUEST)

        task = TaskHistory.objects.create(
            task_type='IMPORT',
            filename=filename,
            du_name=du_name,
            user=request.user
        )
        import_du_task.delay(task.id, target_ids)
        return Response({'task_id': task.id}, status=status.HTTP_201_CREATED)

class TaskStatusView(APIView):
    def get(self, request, pk):
        try:
            task = TaskHistory.objects.get(id=pk)
            serializer = TaskHistorySerializer(task)
            return Response(serializer.data)
        except TaskHistory.DoesNotExist:
            return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)

class DirectDeployView(APIView):
    """
    Headless API for HAC: Automatically finds the latest export for a DU 
    and deploys it to a specific target SID.
    """
    def post(self, request):
        target_sid = request.data.get('sid')
        du_name = request.data.get('du_name')
        
        if not target_sid or not du_name:
            return Response({'error': 'Missing sid or du_name in request body'}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Find the target system
        try:
            target_system = System.objects.filter(name=target_sid.upper()).first()
            if not target_system:
                return Response({'error': f'System {target_sid} not found in our registry'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # 2. Find the latest export file for this DU
        latest_file = hdbalm_wrapper.get_latest_export(du_name)
        if not latest_file:
            return Response({'error': f'No existing export found for DU: {du_name}'}, status=status.HTTP_404_NOT_FOUND)

        # 3. Create and trigger the Import task
        task = TaskHistory.objects.create(
            task_type='IMPORT',
            filename=latest_file,
            du_name=du_name,
            user=request.user
        )
        task.target_systems.add(target_system)
        
        # We reuse the existing import_du_task
        import_du_task.delay(task.id, [target_system.id])
        
        return Response({
            'message': 'Direct Deployment initiated',
            'task_id': task.id,
            'filename_used': latest_file,
            'status_url': f'/api/v1/du-automation/task-status/{task.id}/'
        }, status=status.HTTP_202_ACCEPTED)
