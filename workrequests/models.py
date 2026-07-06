from django.db import models
from django.conf import settings


class WorkRequest(models.Model):

    CATEGORY_CHOICES = [
        ('Electrical', 'Electrical'),
        ('Mechanical', 'Mechanical'),
        ('Utilities', 'Utilities'), 
        ('Other', 'Other'),
    ]

    TYPE_CHOICES = [
        ('Sensor Adjustment / Damaged', 'Sensor Adjustment / Damaged'), 
        ('No Power', 'No Power'), 
        ('Unusual Noise / Vibration', 'Unusual Noise / Vibration'), 
        ('HMI / Screen Frozen or Black', 'HMI / Screen Frozen or Black'),
        ('Calibration Due / Out of Tolerance', 'Calibration Due / Out of Tolerance'),
        ('Broken Parts / Belt / Chain', 'Broken Parts / Belt / Chain'),
        ('Fluid Leak / Oil Leak', 'Fluid Leak / Oil Leak'),
        ('Temperature / Pressure Out of Range', 'Temperature / Pressure Out of Range'),
        ('Component Jammed / Stuck', 'Component Jammed / Stuck'),
        ('HVAC / Cleanroom / Utilities', 'HVAC / Cleanroom / Utilities'),
        ('Safety Issue', 'Safety Issue'),
        ('Lighting Issue', 'Lighting Issue'),
        ('New Installation / Setup', 'New Installation / Setup'),
        ('Doors Interlock Issue', 'Doors Interlock Issue'),
        ('Valve Issue', 'Valve Issue'),
        ('Heater Issue', 'Heater Issue'),
        ('Ionizer Issue', 'Ionizer Issue'),
        ('Loss of Sterility', 'Loss of Sterility'),
        ('Printer / Labeler Issue', 'Printer / Labeler Issue'),
        ('Other', 'Other'),
    ]

    type = models.CharField(max_length=200, choices = TYPE_CHOICES)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    asset = models.ForeignKey('assets.Asset', null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"WR#{self.pk or 'new'}: {self.type}"


# ChatMessage model removed — kept earlier but removed now to clean DB schema
