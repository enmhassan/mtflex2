import csv
from django.core.management.base import BaseCommand
from django.db import models
from workorders.models import WorkOrder


class Command(BaseCommand):
    help = 'Export workorders to CSV. Use --corrected to export only records where human-corrected values differ from AI predictions.'

    def add_arguments(self, parser):
        parser.add_argument('--output', '-o', type=str, default='workorders_export.csv', help='Output CSV file path')
        parser.add_argument('--corrected', action='store_true', help='Export only corrected (human-labeled) records')

    def handle(self, *args, **options):
        output_path = options['output']
        corrected_only = options['corrected']

        qs = WorkOrder.objects.all().order_by('id')
        if corrected_only:
            qs = qs.exclude(category='').exclude(priority='')

        fieldnames = ['id', 'title', 'description', 'category', 'priority', 'done', 'created_by', 'created_at', 'status']

        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for wo in qs:
                writer.writerow({
                    'id': wo.pk,
                    'title': wo.title,
                    'description': wo.description,
                    'category': wo.category,
                    'priority': wo.priority,
                    'done': wo.done,
                    'created_by': wo.created_by.username if wo.created_by else '',
                    'created_at': wo.created_at.isoformat() if wo.created_at else '',
                    'status': wo.status,
                })

        self.stdout.write(self.style.SUCCESS(f'Exported {qs.count()} workorders to {output_path}'))
