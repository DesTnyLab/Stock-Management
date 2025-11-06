from collections import defaultdict
from stock.models import Product, Suppliers
from .models import Order, OrderItem, OrderItemProduct

def group_low_stock_by_supplier(low_products):
    """
    low_products: a list of Product instances that are low in stock
    returns: dictionary {supplier: [list of products]}
    """
    grouped = defaultdict(list)

    for product in low_products:
        try:
            supplier = Suppliers.objects.get(code=product.supplier_code)
            grouped[supplier].append(product)
        except Suppliers.DoesNotExist:
            # Skip products with invalid supplier_code
            continue

    return dict(grouped)


from django.utils import timezone

def create_order_from_email(supplier_id, product_data_list):
    """
    product_data_list = [
        {"product_id": 1, "quantity": 10, "rate": 120},
        {"product_id": 5, "quantity": 4, "rate": 80},
        ...
    ]
    """
    # 1) Create Order
    order = Order.objects.create(
        order_no = Order.objects.count() + 1,
        suppliers_id = supplier_id,
        date = timezone.now().date(),
        status = "PENDING"  # default anyway
    )

    # 2) Create OrderItem (Parent container for product list)
    order_item = OrderItem.objects.create(order=order)

    order_total = 0

    # 3) Create OrderItemProduct rows
    for item in product_data_list:
        product_obj = Product.objects.get(name=item["product"])
        quantity = item["quantity"]
        rate = 0.00

        product_row = OrderItemProduct.objects.create(
            order_item=order_item,
            product=product_obj,
            quantity=quantity,
            rate=rate
        )

        order_total += product_row.get_subtotal()

    # 4) Save totals at parent levels
    order_item.total = order_total
    order_item.save()

    order.total_amount = order_total
    order.save()

    return order




