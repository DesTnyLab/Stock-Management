from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Purchase, Sale, Stock, Product, BillItemProduct, Bill
from django.core.exceptions import ValidationError


@receiver(post_save, sender=Purchase)
def update_stock_on_purchase(sender, instance, created, **kwargs):
    """Update stock when a purchase is made."""
    product = Product.objects.get(name= instance.product)
    
    stock, created_stock = Stock.objects.get_or_create(product=product)
    if created:  # New purchase
        stock.total_purchased += instance.quantity
        stock.total_buying_cost = ((stock.total_buying_cost or 0)) + float((instance.price * instance.quantity))
    
    else:  # Existing purchase updated
        previous_quantity = Purchase.objects.get(id=instance.id)
        stock.total_purchased += (instance.quantity - previous_quantity.quantity)
        stock.total_buying_cost = (stock.total_buying_cost or 0) + (instance.price * instance.quantity)
        
    stock.save()


@receiver(post_save, sender=Sale)
def update_stock_on_sale(sender, instance, created, **kwargs):
    """Update stock when a sale is made."""
   
    stock, created_stock = Stock.objects.get_or_create(product=instance.product)
    if created:  # New sale
        stock.total_sold += instance.quantity
        stock.total_selling_cost = (stock.total_selling_cost or 0) + float(instance.price * instance.quantity)
    else:  # Existing sale updated
        previous_quantity = Sale.objects.get(id=instance.id).quantity
        stock.total_sold += (instance.quantity - previous_quantity)
        stock.total_selling_cost = (stock.total_selling_cost or 0) + float(instance.price * instance.quantity)
    stock.save()



@receiver(post_save, sender=BillItemProduct)
def create_sale_on_bill_item_product(sender, instance, created, **kwargs):
    """Create a new Sale instance whenever a BillItemProduct is created."""
    if created:  # Only create a new Sale when a BillItemProduct is newly created
        product = instance.product
        quantity = instance.quantity

        # Check if there is enough stock available
        try:
            stock = Stock.objects.get(product=product)
        except Stock.DoesNotExist:
            raise ValidationError(f"Stock record for {product.name} does not exist.")

        if stock.remaining_stock < quantity:
            bill = instance.bill_item.bill
            bill.delete()
            raise ValidationError(
                f"Cannot sell {quantity} units of {product.name}. Only {stock.remaining_stock} units available."
            )
           

        Sale.objects.create(
            product=product,
            quantity=quantity,
            price=instance.rate,
            date=instance.bill_item.bill.date
        )
