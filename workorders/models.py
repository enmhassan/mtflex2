from django.db import models
from django.conf import settings
from workrequests.models import WorkRequest

class WorkOrder(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('closed', 'Closed'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    CATEGORY_CHOICES = [
        ('Electrical', 'Electrical'),
        ('Mechanical', 'Mechanical'),
        ('Utilities', 'Utilities'), 
        ('Other', 'Other'),
    ]   
    title = models.CharField(max_length=200, choices = WorkRequest.TYPE_CHOICES)
    description = models.TextField(blank=True)
    eng_description = models.TextField(blank=True, verbose_name="Engineering Instructions & Details")
    feedback = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    # (removed) ai prediction fields were previously here

    # final values (can be overridden)
    category = models.CharField(max_length=100, blank=True, choices = CATEGORY_CHOICES)
    priority = models.CharField(max_length=20, blank=True, choices = PRIORITY_CHOICES)
    asset = models.ForeignKey('assets.Asset', null=True, blank=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')

    request_by = models.CharField(max_length=200, null=True, blank=True)
    request_created_at = models.DateTimeField(null=True, blank=True)
    

    work_request = models.OneToOneField(
        'workrequests.WorkRequest', 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL,
        related_name='converted_order'
    )

    def __str__(self):
        return f"WO#{self.pk or 'new'}: {self.title}"


# ChatMessage model removed — kept earlier but removed now to clean DB schema
