import streamlit as st
import pandas as pd
from azure.data.tables import TableServiceClient
import plotly.express as px

# Function to retrieve data from Azure Table Storage
def fetch_data_from_azure_table(connection_string, table_name):
    service = TableServiceClient.from_connection_string(conn_str=connection_string)
    table_client = service.get_table_client(table_name=table_name)
    
    entities = table_client.list_entities()
    data = []
    for entity in entities:
        data.append(entity)
    return pd.DataFrame(data)

# Azure Table Storage information
connection_string = 'DefaultEndpointsProtocol=https;AccountName=515team2;AccountKey=+wc53G0GKd551uGI/gn+ow5YcrqralBanMwl+MqJoxReUPwSHwBE6wu4Eoh3awBwxR4za3qlC0hQ+AStlJ2PmA==;EndpointSuffix=core.windows.net'
table_name = 'mile3'

# Fetch the data
data_df = fetch_data_from_azure_table(connection_string, table_name)

# Convert the Date column to datetime
data_df['Date'] = pd.to_datetime(data_df['Date'])

# Sidebar for date range selection
st.sidebar.header("Filter by Date Range")
start_date = st.sidebar.date_input("Start Date", value=data_df['Date'].min())
end_date = st.sidebar.date_input("End Date", value=data_df['Date'].max())

# Filter the data based on the selected date range
filtered_df = data_df[(data_df['Date'] >= pd.to_datetime(start_date)) & (data_df['Date'] <= pd.to_datetime(end_date) + pd.DateOffset(days=1) - pd.Timedelta(seconds=1))]

# Set up the Streamlit app layout
st.title("🌾FarmBeats Data Visualization")

# Create individual charts for each parameter
fig_temp = px.line(filtered_df, x='Date', y='TemperatureC', title='Temperature Over Time')
fig_humidity = px.line(filtered_df, x='Date', y='Humidity', title='Humidity Over Time')
fig_pressure = px.line(filtered_df, x='Date', y='Pressure', title='Pressure Over Time')
fig_percentage = px.line(filtered_df, x='Date', y='Percentage', title='Percentage of Yellow Over Time')

# Create a combined chart for Temperature, Humidity, and Percentage
fig_combined = px.line(filtered_df, x='Date', y=['TemperatureC', 'Humidity', 'Percentage'], 
                       title='Temperature, Humidity, and Percentage Over Time',
                       labels={'value': 'Measurement', 'variable': 'Parameter'})

# Display the charts in a single line
st.plotly_chart(fig_temp)

st.plotly_chart(fig_humidity)

st.plotly_chart(fig_pressure)

# Display the Percentage chart and combined chart below
st.plotly_chart(fig_percentage)
st.plotly_chart(fig_combined)