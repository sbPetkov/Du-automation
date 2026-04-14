from rest_framework import serializers
from .models import System, TaskHistory

class SystemSerializer(serializers.ModelSerializer):
    hostname = serializers.ReadOnlyField()
    alm_port = serializers.ReadOnlyField()

    class Meta:
        model = System
        fields = '__all__'

class TaskHistorySerializer(serializers.ModelSerializer):
    source_system_name = serializers.CharField(source='source_system.name', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = TaskHistory
        fields = '__all__'
