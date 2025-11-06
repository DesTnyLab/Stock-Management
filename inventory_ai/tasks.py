from celery import shared_task
from stock.models import Product, Suppliers, ProductEmailStatus
from inventory_ai.graph.workflow import create_alert_graph
from .email_utils import send_low_stock_email

@shared_task
def run_stock_monitor():
    workflow = create_alert_graph()
    low_products = []

    for product in Product.objects.all():
        last_status = ProductEmailStatus.objects.filter(product=product).order_by('-last_sent').first()
        if last_status and last_status.status == "SENT":
            print(f"Skipping {product.name} - email already sent ✅")
            continue  
        result = workflow.invoke({"product": product})
        if result.get("low"):
            low_products.append(product)

    
    supplier_dict = {}

    for product in low_products:
        supplier = Suppliers.objects.get(code=product.supplier_code)

        supplier_key = supplier.id  # ✅ Safe key

        if supplier_key not in supplier_dict:
            supplier_dict[supplier_key] = {
                "supplier_name": supplier.name,
                "products": []
            }

        supplier_dict[supplier_key]["products"].append(product.name) 

    print("Grouped low stock products by supplier:")
    for supplier_id, info in supplier_dict.items():
        print(info["supplier_name"], info["products"])

    
    for supplier_id, info in supplier_dict.items():
        supplier = Suppliers.objects.get(id=supplier_id)
        product_names = info["products"]  # these are product names
        product_objs = Product.objects.filter(name__in=product_names)
        send_low_stock_email(supplier, product_objs)
    return "Alerts Sent"