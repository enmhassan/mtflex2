from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("workorders", "0004_remove_workorder_ai_category_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="workorder",
            name="done",
            field=models.BooleanField(default=False),
        ),
    ]
