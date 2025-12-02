import pandas as pd
from prophet import Prophet
from inventory_ai.fetch_data import get_sales_data
from plotly.offline import plot
import plotly.graph_objs as go

def forecast_sales_prophet(product_id=None, periods=7):
    
    df = get_sales_data(product_id=product_id)
    if df.empty:
        return [], ""

    # Prepare data for Prophet
    df_prophet = df.groupby('date')['quantity'].sum().reset_index()
    df_prophet.rename(columns={'date':'ds','quantity':'y'}, inplace=True)

    # Initialize and fit Prophet
    model = Prophet(daily_seasonality=True)
    model.fit(df_prophet)

    # Make future dataframe
    future = model.make_future_dataframe(periods=periods)
    forecast = model.predict(future)

    # Extract forecasted values for next `periods` days
    forecasted = forecast[['ds','yhat','yhat_lower','yhat_upper']].tail(periods)
    forecasted['yhat'] = forecasted['yhat'].apply(lambda x: max(0, round(x)))
    forecasted['yhat_lower'] = forecasted['yhat_lower'].apply(lambda x: max(0, round(x)))
    forecasted['yhat_upper'] = forecasted['yhat_upper'].apply(lambda x: max(0, round(x)))

    # Generate Plotly graph
    trace_yhat = go.Scatter(
        x=forecasted['ds'], y=forecasted['yhat'], mode='lines+markers', name='Forecast'
    )
    trace_lower = go.Scatter(
        x=forecasted['ds'], y=forecasted['yhat_lower'], mode='lines',
        name='Lower Bound', line=dict(dash='dash', color='red')
    )
    trace_upper = go.Scatter(
        x=forecasted['ds'], y=forecasted['yhat_upper'], mode='lines',
        name='Upper Bound', line=dict(dash='dash', color='green')
    )

    fig = go.Figure(data=[trace_yhat, trace_lower, trace_upper])
    fig.update_layout(
        title=f"Next {periods} Days Sales Forecast for Product {product_id}",
        xaxis_title="Date",
        yaxis_title="Quantity"
    )
    plot_div = plot(fig, output_type='div', include_plotlyjs=True)

    # Return forecast list + Plotly div
    forecast_list = list(zip(
        forecasted['ds'], forecasted['yhat'], forecasted['yhat_lower'], forecasted['yhat_upper']
    ))

    return forecast_list, plot_div
