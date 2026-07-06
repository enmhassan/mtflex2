from django.db import models
from django.contrib.auth.models import AbstractUser


class Permission(models.Model):
    codename = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.codename} ({self.name})"


class Role(models.Model):
    name = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True)
    permissions = models.ManyToManyField(Permission, blank=True, related_name='roles')

    def __str__(self):
        return self.name


class CustomUser(AbstractUser):
    roles = models.ManyToManyField(Role, blank=True, related_name='users')

    def get_all_permissions(self):
        perms = set()
        for role in self.roles.all():
            for p in role.permissions.all():
                perms.add(p.codename)
        return perms

    def has_permission(self, codename: str) -> bool:
        return codename in self.get_all_permissions()
