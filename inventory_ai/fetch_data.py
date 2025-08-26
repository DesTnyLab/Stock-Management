import pandas as pd
from stock.models import Sale, Product

def get_sales_data(product_id=None):
    """
    Fetch sales data from the database.
    Returns a pandas DataFrame with columns: 'date', 'product_id', 'quantity', 'price'.
    Optional filters: product_id, start_date, end_date.
    """

    qs = Sale.objects.filter(product=Product.objects.get(id=product_id)).order_by('date')

    df = pd.DataFrame.from_records(qs.values( 'product', 'quantity', 'price', 'date'))

    return df

def get_product_data(product_id=None):
    """
    Fetch product data from the database.
    Returns a pandas DataFrame with columns: 'id', 'name', 'cost_price', 'selling_price', 'HS_code'.
    """
    qs = Product.objects.all()
    print(product_id)
    
    if product_id:
        print(f"Fetching {product_id}")
        qs = Product.objects.filter(id=product_id)

    df = pd.DataFrame.from_records(qs.values('id', 'name', 'cost_price', 'selling_price', 'HS_code'))

    return df


