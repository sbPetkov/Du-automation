from django.urls import path
from . import views

app_name = 'du_automation'

urlpatterns = [
    # UI Views
    path('', views.home, name='home'),
    
    # HTMX partials/actions
    path('hx/list-dus/', views.list_dus, name='list_dus'),
    path('hx/sync-systems/', views.sync_systems_view, name='sync_systems'),
    path('hx/start-export/', views.start_export, name='start_export'),
    path('hx/task-status/<int:task_id>/', views.task_status_view, name='task_status'),
    path('hx/deploy-fragment/<int:task_id>/', views.deploy_fragment, name='deploy_fragment'),
    path('hx/start-import/', views.start_import, name='start_import'),
    
    # External API for HAC
    path('api/v1/direct-deploy/', views.DirectDeployView.as_view(), name='api-direct-deploy'),
    path('api/v1/task-status/<int:pk>/', views.TaskStatusAPIView.as_view(), name='api-task-status'),
]
