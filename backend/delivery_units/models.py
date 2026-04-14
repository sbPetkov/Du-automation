from django.db import models

class System(models.Model):
    STAGE_CHOICES = [
        ('D', 'Development'),
        ('Q', 'Quality'),
        ('T', 'Test'),
        ('P', 'Production'),
        ('S', 'Sandbox'),
    ]

    name = models.CharField(max_length=10, help_text="SID")
    stage = models.CharField(max_length=1, choices=STAGE_CHOICES)
    virtual_hostname = models.CharField(max_length=255)
    domain = models.CharField(max_length=255)
    instance_number = models.IntegerField()
    tenant = models.CharField(max_length=10, blank=True, null=True)
    is_rise = models.BooleanField(default=True)
    last_synced = models.DateTimeField(auto_now=True)

    @property
    def hostname(self):
        return f"{self.virtual_hostname}.{self.domain}"

    @property
    def alm_port(self):
        return f"43{str(self.instance_number).zfill(2)}"

    def __str__(self):
        if self.tenant:
            return f"{self.name} ({self.tenant}) - {self.stage}"
        return f"{self.name} - {self.stage}"

class TaskHistory(models.Model):
    TASK_TYPES = [
        ('EXPORT', 'Export'),
        ('IMPORT', 'Import'),
    ]
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('RUNNING', 'Running'),
        ('SUCCESS', 'Success'),
        ('FAILURE', 'Failure'),
    ]

    task_type = models.CharField(max_length=10, choices=TASK_TYPES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    source_system = models.ForeignKey(System, on_delete=models.SET_NULL, null=True, related_name='exports')
    target_systems = models.ManyToManyField(System, related_name='imports')
    du_name = models.CharField(max_length=255)
    filename = models.CharField(max_length=255, blank=True, null=True)
    diff_text = models.TextField(blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.task_type} - {self.du_name} - {self.status}"
