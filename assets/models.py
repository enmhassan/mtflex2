from django.db import models

class Asset(models.Model):
    asset_name = models.CharField(max_length=100)
    asset_code = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.asset_name