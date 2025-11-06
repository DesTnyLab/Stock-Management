from inventory_ai.predict import predict_next_days
from stock.models import Stock, Suppliers  # adjust app name

def predict_demand(context):
    product = context["product"]
    context["predicted"] = predict_next_days(product, days=7)
    return context

def get_stock(context):
    product = context["product"]
    stock = Stock.objects.get(product=product)
    context["stock"] = stock.remaining_stock
    return context



def compare(context):
    product = context["product"]
    predicted = context["predicted"]
    stock = context["stock"]

    context["low"] = predicted > stock
    if context["low"]:
        print(f"Product {product.name} is low in stock. Predicted: {predicted}, Stock: {stock}")
    return context
