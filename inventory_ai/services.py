# from .forecasting import forecast_sales
# from .models import SalesForecast
# from stock.models import Product

# def generate_forecasts(periods=7, save=True):
#     results = {}

#     # Per product forecasts
#     for product in Product.objects.all():
#         forecast = forecast_sales(product.id, periods)
#         results[product.name] = forecast

#         if save:
#             for date, qty in forecast:
#                 SalesForecast.objects.update_or_create(
#                     product=product, forecast_date=date,
#                     defaults={'predicted_quantity': qty}
#                 )

#     # Overall forecast
#     overall = forecast_sales(None, periods)
#     results["Overall"] = overall

#     if save:
#         for date, qty in overall:
#             SalesForecast.objects.update_or_create(
#                 product=None, forecast_date=date,
#                 defaults={'predicted_quantity': qty}
#             )

#     return results
