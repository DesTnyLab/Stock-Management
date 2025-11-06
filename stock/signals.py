from django.db.models.signals import post_save, post_delete, pre_delete
from django.dispatch import receiver
from .models import *
from django.core.exceptions import ValidationError
from django.shortcuts import  get_object_or_404

@receiver(post_save, sender=Purchase)
def update_stock_on_purchase(sender, instance, created, **kwargs):
    """Update stock when a purchase is made."""
    
    stock, created_stock = Stock.objects.get_or_create(product=instance.product)
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





@receiver(post_delete, sender=Sale)
def reduce_stock_on_sale_delete(sender, instance, **kwargs):
    """Reduce stock when a sale is deleted."""

    try:
        stock = Stock.objects.get(product=instance.product)
        stock.total_sold -= instance.quantity
        stock.total_selling_cost = (stock.total_selling_cost or 0) - float(instance.price * instance.quantity)
        
        # Ensure totals do not go negative
        if stock.total_sold < 0:
            stock.total_sold = 0
        if stock.total_selling_cost < 0:
            stock.total_selling_cost = 0
        
        stock.save()
    except Stock.DoesNotExist:
        pass  # No stock record exists for this product







@receiver(post_delete, sender=BillItemProduct)
def delete_sale_on_bill_item_product(instance, **kwargs):
    """
    Deletes the most recent Sale object associated with the deleted BillItem's product
    and matching quantity.
    """
    # Retrieve the most recent Sale matching the product and quantity
    sale = Sale.objects.filter(product=instance.product, quantity=instance.quantity).order_by('-id').first()

    # Delete the Sale object if it exists
    if sale:
        sale.delete()




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



@receiver(post_save, sender=Bill)
def update_payment_on_bill_save(sender, instance, created, **kwargs):
        customer = get_object_or_404(Customer, id=instance.customer.id)

        if instance.payment_type == 'CREDIT':
            credit, created = Credit.objects.get_or_create(customer=customer, bill=instance)
            credit.amount = instance.total_amount
            credit.save()
           
        elif instance.payment_type == 'CASH':
            cash, created = BillOnCash.objects.get_or_create(customer=customer, bill=instance)
            cash.amount = instance.total_amount
            print(cash.amount)
            cash.save()
           


@receiver(post_save, sender=Order)
def update_payment_on_bill_save(sender, instance, created, **kwargs):
        supplier = get_object_or_404(Suppliers, id=instance.suppliers.id)

        if instance.payment_type == 'CREDIT':
            credit, created = Suppliers_credit.objects.get_or_create(suppliers=supplier, order=instance)
            credit.amount = instance.total_amount
            credit.save()
          
        elif instance.payment_type == 'CASH':
            cash, created = OrderOnCash.objects.get_or_create(suppliers=supplier, order=instance)
            cash.amount = instance.total_amount
            print(cash.amount)
            cash.save()
           



@receiver(post_save, sender=Investment)
def update_investment(sender, instance, created, **kwargs):
    finance, _ = ActualFinance.objects.get_or_create(id=1)
    if created:
        finance.investment += instance.amount
    else:
        previous_investment = sender.objects.filter(id=instance.id).first().amount
        finance.investment += instance.amount - previous_investment

    finance.save()


@receiver(pre_delete, sender=Investment)
def remove_investment(sender, instance, **kwargs):
    finance, _ = ActualFinance.objects.get_or_create(id=1)
    finance.investment -= instance.amount
    
    finance.save()

@receiver(post_save, sender=OtherRevenue)
def update_revenue(sender, instance, created, **kwargs):
    finance, _ = ActualFinance.objects.get_or_create(id=1)
    if created:
        finance.revenue += instance.amount
        finance.profit += instance.amount
    else:
        previous_revenue = sender.objects.filter(id=instance.id).first().amount
        finance.revenue += instance.amount - previous_revenue

        previous_revenue = sender.objects.filter(id=instance.id).first().amount
        finance.profit += instance.amount - previous_revenue
    finance.save()

@receiver(pre_delete, sender=OtherRevenue)
def remove_revenue(sender, instance, **kwargs):
    finance, _ = ActualFinance.objects.get_or_create(pk=1)
    finance.revenue -= instance.amount
    finance.profit -= instance.amount
    finance.save()



@receiver(post_save, sender=Purchase)
def update_investment(sender, instance, created, **kwargs):
    finance, _ = ActualFinance.objects.get_or_create(id=1)
   
    finance.investment += instance.get_total_cost
    finance.save()
  
@receiver(pre_delete, sender=Purchase)
def remove_investment(sender, instance, **kwargs):
    finance, _ = ActualFinance.objects.get_or_create(id=1)
    finance.investment -= instance.get_total_cost
    finance.save()


@receiver(post_save, sender=Sale)
def update_revenue(sender, instance, created, **kwargs):
    finance, _ = ActualFinance.objects.get_or_create(id=1)
    if created:
        finance.revenue += instance.get_total_cost
        finance.profit += instance.profit
    else:
        previous_revenue = sender.objects.filter(id=instance.id).first().get_total_cost
        finance.revenue += instance.get_total_cost - previous_revenue
    finance.save()


@receiver(pre_delete, sender=Sale)
def remove_revenue(sender, instance, **kwargs):
    finance, _ = ActualFinance.objects.get_or_create(id=1)
    finance.revenue -= instance.get_total_cost
    finance.profit -= instance.profit
    finance.save()



