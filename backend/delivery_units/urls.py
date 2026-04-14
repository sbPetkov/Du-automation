from django.urls import path
from . import views

app_name = 'du_automation'

urlpatterns = [
    path('systems/', views.SystemListView.as_view(), name='system-list'),
    path('sync-systems/', views.SyncSystemsView.as_view(), name='sync-systems'),
    path('list-dus/', views.ListDUsView.as_view(), name='list-dus'),
    path('start-export/', views.StartExportView.as_view(), name='start-export'),
    path('start-import/', views.StartImportView.as_view(), name='start-import'),
    path('task-status/<int:pk>/', views.TaskStatusView.as_view(), name='task-status'),
    path('direct-deploy/', views.DirectDeployView.as_view(), name='direct-deploy'),
]
