import csv
from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_date
from stock.models import Product, Sale  # adjust if app name differs

class Command(BaseCommand):
    help = "Import sales from sales.csv"

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='rice.csv',
            help='Path to the sales CSV file'
        )

    def handle(self, *args, **options):
        file_path = options['file']

        try:
            with open(file_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                count = 0

                for row in reader:
                    product_name = row['product'].strip()
                    quantity = int(row['quantity'])
                    price = float(row['price'])
                    date = parse_date(row['date'])

                    try:
                        product = Product.objects.get(name=product_name)
                    except Product.DoesNotExist:
                        self.stdout.write(
                            self.style.WARNING(f"⚠️ Skipped: Product '{product_name}' not found.")
                        )
                        continue

                    Sale.objects.create(
                        product=product,
                        quantity=quantity,
                        price=price,
                        date=date
                    )
                    count += 1

                self.stdout.write(
                    self.style.SUCCESS(f"✅ Successfully imported {count} sales from {file_path}")
                )
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"❌ File not found: {file_path}"))
