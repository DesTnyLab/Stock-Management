import csv
from django.core.management.base import BaseCommand
from stock.models import Product

class Command(BaseCommand):
    help = 'Import products in bulk from a CSV file with name and HS_code'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']
        count = 0

        try:
            with open(csv_file, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    name = row.get('name')
                    hs_code = row.get('HS_code', '')
                    supplier_code = row.get('supplier_code', '')


                    if not name:
                        self.stdout.write(self.style.WARNING("Skipping row with empty name"))
                        continue

                    product, created = Product.objects.get_or_create(
                        name=name,
                        defaults={'HS_code': hs_code,
                                  'supplier_code': supplier_code}
                    )

                    if not created:
                        product.HS_code = hs_code  # Update HS_code if product exists
                        product.supplier_code = supplier_code  # Update supplier_code if product exists
                        product.save()

                    count += 1

            self.stdout.write(self.style.SUCCESS(f'Successfully imported/updated {count} products.'))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'File {csv_file} not found.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
