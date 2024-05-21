import streamlit as st
import pandas as pd
from azure.data.tables import TableServiceClient
from datetime import datetime

# Function to retrieve data from Azure Table Storage
def fetch_data_from_azure_table(connection_string, table_name):
    service = TableServiceClient.from_connection_string(conn_str=connection_string)
    table_client = service.get_table_client(table_name=table_name)
    
    entities = table_client.list_entities()
    data = []
    for entity in entities:
        data.append(entity)
    return pd.DataFrame(data)

# Function to extract date from RowKey
def extract_date(row_key):
    try:
        date_str = row_key.split('_')[1].split('-')[0]
        date = datetime.strptime(date_str, '%Y%m%d').date()
        return date
    except Exception as e:
        st.error(f"Error extracting date from RowKey '{row_key}': {e}")
        return None

# Azure Table Storage information
connection_string = 'DefaultEndpointsProtocol=https;AccountName=515team2;AccountKey=+wc53G0GKd551uGI/gn+ow5YcrqralBanMwl+MqJoxReUPwSHwBE6wu4Eoh3awBwxR4za3qlC0hQ+AStlJ2PmA==;EndpointSuffix=core.windows.net'
table_name = 'mile2'

# Fetch the data
data_df = fetch_data_from_azure_table(connection_string, table_name)

# Extract date from RowKey and add it as a new column
if 'RowKey' in data_df.columns:
    data_df['date'] = data_df['RowKey'].apply(extract_date)
    data_df.dropna(subset=['date'], inplace=True)
    data_df.sort_values('date', inplace=True)
else:
    st.error("The 'RowKey' column is missing in the retrieved data.")

# Streamlit app
st.title('🌾FarmBeats Data Visualization')

# Sidebar for date range selection
st.sidebar.title("Filter")
start_date = st.sidebar.date_input("Start date", data_df['date'].min())
end_date = st.sidebar.date_input("End date", data_df['date'].max())

# Filter data based on the selected date range
filtered_df = data_df[(data_df['date'] >= start_date) & (data_df['date'] <= end_date)]

# Display charts in a row
col1, col2, col3 = st.columns(3)

with col1:
    # Line chart for Temperature
    if 'TemperatureC' in filtered_df.columns:
        st.subheader('Temperature')
        st.line_chart(filtered_df.set_index('date')['TemperatureC'])
    else:
        st.warning("Temperature data is missing.")

with col2:
    # Line chart for Humidity
    if 'Humidity' in filtered_df.columns:
        st.subheader('Humidity')
        st.line_chart(filtered_df.set_index('date')['Humidity'])
    else:
        st.warning("Humidity data is missing.")

with col3:
    # Line chart for Pressure
    if 'Pressure' in filtered_df.columns:
        st.subheader('Pressure')
        st.line_chart(filtered_df.set_index('date')['Pressure'])
    else:
        st.warning("Pressure data is missing.")

# Line chart for Percentage (of yellow)
if 'Percentage' in filtered_df.columns:
    st.subheader('Percentage (of Rust) Over Time')
    st.line_chart(filtered_df.set_index('date')['Percentage'])
else:
    st.warning("Percentage (of yellow) data is missing.")