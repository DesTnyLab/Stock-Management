import pandas as pd
from prophet import Prophet
from inventory_ai.fetch_data import get_sales_data

def predict_next_days(product, days=7):
    df = get_sales_data(product.id)

    if df.empty:
        return 0  

    df.rename(columns={"date": "ds", "quantity": "y"}, inplace=True)

    
    dashain_tihar = pd.DataFrame({
        "holiday": ["dashain", "dashain", "tihar", "tihar"],
        "ds": pd.to_datetime(["2023-10-01","2024-10-10","2023-11-01","2024-11-01"]),
        "lower_window": -2,
        "upper_window": 3,
    })

    model = Prophet(holidays=dashain_tihar, daily_seasonality=True)
    model.fit(df)

    future = model.make_future_dataframe(periods=days)
    forecast = model.predict(future)

    next_days = forecast.tail(days)["yhat"].sum()
    print(f"Predicted for next {days} days:", next_days)

    return max(0, round(next_days))
