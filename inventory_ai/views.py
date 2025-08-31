from django.shortcuts import render, get_object_or_404
from .models import Product
from .forecasting import forecast_sales_prophet

def product_forecast_ajax(request, product_id):
    forecast_list, plot_div = forecast_sales_prophet(product_id=product_id, periods=7)

    forecast_table = [
        {"ds": f[0].date(), "yhat": f[1], "yhat_lower": f[2], "yhat_upper": f[3]}
        for f in forecast_list
    ]

    product_name = get_object_or_404(Product, id=product_id).name

    # Render only the forecast fragment
    return render(request, "inventory_ai/forecast.html", {
        "plot_div": plot_div,
        "forecast_table": forecast_table,
        "product_name": product_name,
    })
