from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Purchase, Sale, Stock

@receiver(post_save, sender=Purchase)
def update_stock_on_purchase(sender, instance, created, **kwargs):
    """Update stock when a purchase is made."""
    stock, created_stock = Stock.objects.get_or_create(product=instance.product)
    if created:  # New purchase
        stock.total_purchased += instance.quantity
    else:  # Existing purchase updated
        previous_quantity = Purchase.objects.get(id=instance.id).quantity
        stock.total_purchased += (instance.quantity - previous_quantity)
    stock.save()


@receiver(post_delete, sender=Purchase)
def update_stock_on_purchase_delete(sender, instance, **kwargs):
    """Update stock when a purchase is deleted."""
    try:
        stock = Stock.objects.get(product=instance.product)
        stock.total_purchased -= instance.quantity
        stock.save()
    except Stock.DoesNotExist:
        pass  # Handle gracefully if Stock doesn't exist


@receiver(post_save, sender=Sale)
def update_stock_on_sale(sender, instance, created, **kwargs):
    """Update stock when a sale is made."""
    stock, created_stock = Stock.objects.get_or_create(product=instance.product)
    if created:  # New sale
        stock.total_sold += instance.quantity
    else:  # Existing sale updated
        previous_quantity = Sale.objects.get(id=instance.id).quantity
        stock.total_sold += (instance.quantity - previous_quantity)
    stock.save()


