from django.template.loader import get_template
from django.core.mail import EmailMessage
from django.urls import reverse
from stock.models import ProductEmailStatus
from .services import create_order_from_email
from inventory_ai.predict import predict_next_days  # adjust import path if needed
from stock.models import Product
def send_low_stock_email(supplier, product_list):
    """
    supplier: Supplier instance
    product_list: list of Product instances
    """
    # Prepare product data with predicted quantity
    products_data = []
    for product in product_list:
        predicted_quantity = predict_next_days(product, days=30)
        products_data.append({
            "product": product.name,
            "quantity": predicted_quantity
        })

    
    try:
        order = create_order_from_email(supplier.id, products_data)
        # Render email template
        order_link = f"http://192.168.1.70{reverse('edit_order', args=[order.id])}"
        context = {"products": products_data, "supplier_name": supplier.name, "order_link": order_link}
        email_template = get_template("inventory_ai/email.html").render(context)

        subject = "Low Stock Alert - Request for Supply"
        email = EmailMessage(subject, email_template, "", [supplier.email])
        email.content_subtype = "html"

        email.send()

        # ✅ After successful send, save status for each product
        for product in products_data:
            product_obj = Product.objects.get(name=product["product"])
            ProductEmailStatus.objects.create(
                product=product_obj,
                supplier=supplier,
                status="SENT"
            )

        print(f"✅ Email successfully sent to {supplier.name}")

       

    except Exception as e:
        print(f"❌ Email sending failed: {e}")

        # ❗ If email fails, mark status as FAILED
        for product in products_data:
            product_obj = Product.objects.get(name=product["product"])
            ProductEmailStatus.objects.create(
                product=product_obj,
                supplier=supplier,
                status="SENT"
            )
