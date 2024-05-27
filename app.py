import streamlit as st
import pandas as pd
from azure.storage.blob import BlobServiceClient
from azure.data.tables import TableServiceClient

# Azure Storage and Table credentials
connection_string = "DefaultEndpointsProtocol=https;AccountName=515team2;AccountKey=+wc53G0GKd551uGI/gn+ow5YcrqralBanMwl+MqJoxReUPwSHwBE6wu4Eoh3awBwxR4za3qlC0hQ+AStlJ2PmA==;EndpointSuffix=core.windows.net"
table_name = "mile3"
container_name_raw = "mile3raw"

# Initialize Blob and Table service clients
blob_service_client = BlobServiceClient.from_connection_string(connection_string)
blob_client = blob_service_client.get_container_client(container_name_raw)

table_service_client = TableServiceClient.from_connection_string(connection_string)
table_client = table_service_client.get_table_client(table_name)

# Fetch data from Azure Table
entities = table_client.list_entities()
data = []
for entity in entities:
    data.append(entity)
df = pd.DataFrame(data)

# Convert Date column to datetime
df['Date'] = pd.to_datetime(df['Date'])

# Function to get image URL from Blob Storage
def get_image_url(blob_service_client, container_name, image_name):
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=image_name)
    return blob_client.url

# Add image URLs to the dataframe
image_urls = []
for index, row in df.iterrows():
    image_name = row['RowKey']  # Assuming image names are in the format of RowKey.jpg
    image_url = get_image_url(blob_service_client, container_name_raw, image_name)
    image_urls.append(image_url)

df['RawImage'] = image_urls

# Select and reorder columns
columns_order = ['Date', 'Status', 'Percentage', 'RawImage', 'TemperatureC', 'Humidity', 'Pressure']
df = df[columns_order]

# Rename 'RawImage' to 'Preview Image' for display purposes
df = df.rename(columns={'RawImage': 'Preview Image'})

# Overview section - Get the latest record
latest_record = df.iloc[-1]
previous_record = df.iloc[-2] if len(df) > 1 else latest_record

# Calculating changes for temperature and humidity
temp_change = latest_record['TemperatureC'] - previous_record['TemperatureC']
humidity_change = latest_record['Humidity'] - previous_record['Humidity']


# Streamlit app
st.title("🌾FarmBeats Monitor")

# Sidebar for filtering data
with st.sidebar:
    st.write("Filter data")
    
    # Date range filter
    min_date = df['Date'].min().date()
    max_date = df['Date'].max().date()
    date_range = st.date_input("Date range", [min_date, max_date], min_value=min_date, max_value=max_date)
    
    # Status filter
    status_filter = st.selectbox('Status', ('All', 'Yes', 'No'))
    
    # Percentage filter
    percentage_min, percentage_max = st.slider(
        'Percentage', min_value=int(df['Percentage'].min()), 
        max_value=int(df['Percentage'].max()), 
        value=(int(df['Percentage'].min()), int(df['Percentage'].max())))
    
    # Temperature filter
    temperature_min, temperature_max = st.slider(
        'Temperature (°C)', min_value=int(df['TemperatureC'].min()), 
        max_value=int(df['TemperatureC'].max()), 
        value=(int(df['TemperatureC'].min()), int(df['TemperatureC'].max())))
    
    # Humidity filter
    humidity_min, humidity_max = st.slider(
        'Humidity', min_value=int(df['Humidity'].min()), 
        max_value=int(df['Humidity'].max()), 
        value=(int(df['Humidity'].min()), int(df['Humidity'].max())))

# Apply filters to dataframe
start_date, end_date = pd.to_datetime(date_range)
filtered_df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]


if status_filter != 'All':
    filtered_df = filtered_df[filtered_df['Status'] == status_filter]

filtered_df = filtered_df[(filtered_df['Percentage'] >= percentage_min) & (filtered_df['Percentage'] <= percentage_max)]
filtered_df = filtered_df[(filtered_df['TemperatureC'] >= temperature_min) & (filtered_df['TemperatureC'] <= temperature_max)]
filtered_df = filtered_df[(filtered_df['Humidity'] >= humidity_min) & (filtered_df['Humidity'] <= humidity_max)]

st.subheader("Latest Data")
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    st.image(latest_record['Preview Image'], caption='Latest Image', use_column_width=True)
with col2:
    st.write(f"**Date:** {latest_record['Date']}")
    st.write(f"**Status:** {latest_record['Status']}")
    st.write(f"**Percentage:** {latest_record['Percentage']}%")

with col3:
    st.caption("Temperature")
    st.write(f"{latest_record['TemperatureC']}°C")
    if temp_change > 0:
        st.write(f'<p style="color:red;">↑ {temp_change:.2f}°C Compared to previous</p>', unsafe_allow_html=True)
    else:
        st.write(f'<p style="color:red;">↓ {abs(temp_change):.2f}°C Compared to previous</p>', unsafe_allow_html=True)

    st.caption("Humidity")
    st.write(f"{latest_record['Humidity']}%")
    if humidity_change > 0:
        st.write(f'<p style="color:red;">↑ {humidity_change:.2f}% Compared to previous</p>', unsafe_allow_html=True)
    else:
        st.write(f'<p style="color:red;">↓ {abs(humidity_change):.2f}% Compared to previous</p>', unsafe_allow_html=True)

# Display the dataframe with image preview in the column
st.subheader("Data History")
st.data_editor(
    filtered_df,
    column_config={
        "Preview Image": st.column_config.ImageColumn(
            "Preview Image", help="Streamlit app preview screenshots"
        )
    },
    hide_index=True,
)
