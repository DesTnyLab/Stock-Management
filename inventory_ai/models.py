from django.db import models
from stock.models import Product

class SalesForecast(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    forecast_date = models.DateField()
    predicted_quantity = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['forecast_date']
    
    def __str__(self):
        if self.product:
            return f"Forecast for {self.product.name} on {self.forecast_date}: {self.predicted_quantity}"
        return f"Overall Forecast {self.forecast_date}: {self.predicted_quantity}"
