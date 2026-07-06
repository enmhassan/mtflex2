from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='WorkOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('ai_category', models.CharField(blank=True, max_length=100)),
                ('ai_priority', models.CharField(blank=True, max_length=20)),
                ('ai_confidence', models.FloatField(blank=True, null=True)),
                ('ai_model', models.CharField(blank=True, max_length=200)),
                ('category', models.CharField(blank=True, max_length=100)),
                ('priority', models.CharField(blank=True, max_length=20)),
                ('status', models.CharField(default='open', max_length=20)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
