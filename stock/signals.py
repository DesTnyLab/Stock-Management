from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Purchase, Sale, Stock, Product

@receiver(post_save, sender=Purchase)
def update_stock_on_purchase(sender, instance, created, **kwargs):
    """Update stock when a purchase is made."""
    product = Product.objects.get(name= instance.product)
    
    stock, created_stock = Stock.objects.get_or_create(product=product)
    if created:  # New purchase
        stock.total_purchased += instance.quantity
        stock.total_buying_cost = (stock.total_buying_cost or 0) + (instance.price * instance.quantity)
    
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
        stock.total_selling_cost = (stock.total_selling_cost or 0) + (instance.price * instance.quantity)
    else:  # Existing sale updated
        previous_quantity = Sale.objects.get(id=instance.id).quantity
        stock.total_sold += (instance.quantity - previous_quantity)
        stock.total_selling_cost = (stock.total_selling_cost or 0) + (instance.price * instance.quantity)
    stock.save()


