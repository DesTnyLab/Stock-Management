from itertools import product
from django.http import HttpResponse
from .fetch_data import get_product_data, get_sales_data

from django.shortcuts import render, get_object_or_404
from stock.models import Product
from .forecasting import forecast_sales_prophet






def product_forecast_view(request, product_id):
    df_Sales = get_sales_data(product_id=100)

    # Print the DataFrame
    print(df_Sales)

    # Return as simple text
    return HttpResponse("Forecasting endpoint")


def product_forecast_view(request, product_id):

    """
    Display 7-day sales forecast for a product with graph and table.
    """
    # Call the forecast function
    forecast_list, plot_div = forecast_sales_prophet(product_id=product_id, periods=7)

    # Convert forecast_list to list of dicts for template
    forecast_table = [
        {"ds": f[0].date(), "yhat": f[1], "yhat_lower": f[2], "yhat_upper": f[3]}
        for f in forecast_list
    ]

    # Get product name
    product_name = Product.objects.get(id=product_id).name

    return render(request, "inventory_ai/forecast.html", {
        "plot_div": plot_div,
        "forecast_table": forecast_table,
        "product_name": product_name,
    })



