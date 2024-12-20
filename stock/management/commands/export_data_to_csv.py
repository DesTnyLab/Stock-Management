import csv
import os
from django.core.management.base import BaseCommand
from django.apps import apps

class Command(BaseCommand):
    help = "Export custom app's database data to CSV files"

    def handle(self, *args, **kwargs):
        output_dir = 'exports'  # Directory to store CSV files
        os.makedirs(output_dir, exist_ok=True)

        # Specify your app name here
        app_name = "stock"

        for model in apps.get_models():
            if model._meta.app_label == app_name:  # Check if the model belongs to your app
                model_name = model._meta.model_name
                file_path = os.path.join(output_dir, f"{model_name}.csv")

                with open(file_path, mode="w", newline="", encoding="utf-8") as file:
                    writer = csv.writer(file)
                    fields = [field.name for field in model._meta.fields]
                    writer.writerow(fields)  # Write header row

                    for obj in model.objects.all():
                        row = [getattr(obj, field) for field in fields]
                        writer.writerow(row)

                self.stdout.write(f"Exported {model_name} to {file_path}")

