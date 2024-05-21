import streamlit as st
import pandas as pd
from azure.storage.blob import BlobServiceClient
from azure.data.tables import TableServiceClient
from datetime import datetime

# Azure Storage and Table credentials
connection_string = "DefaultEndpointsProtocol=https;AccountName=515team2;AccountKey=+wc53G0GKd551uGI/gn+ow5YcrqralBanMwl+MqJoxReUPwSHwBE6wu4Eoh3awBwxR4za3qlC0hQ+AStlJ2PmA==;EndpointSuffix=core.windows.net"
table_name = "mile2"
container_name_raw = "mile2raw"

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

# Function to extract date and time from RowKey
def extract_datetime(row_key):
    try:
        date_str, time_str = row_key.split('_')[1].split('-')[:2]
        date = datetime.strptime(date_str, '%Y%m%d').date()
        time = datetime.strptime(time_str, '%H%M%S').time()
        return f"{date} {time}"
    except Exception as e:
        st.error(f"Error extracting datetime from RowKey '{row_key}': {e}")
        return None

# Add DateTime column to the dataframe
df['DateTime'] = df['RowKey'].apply(extract_datetime)

# Reorder columns to move DateTime to the first column
first_column = df.pop('DateTime')
df.insert(0, 'DateTime', first_column)

# Hide specific columns
columns_to_hide = ['RowKey','PartitionKey', 'RawImageName', 'ProcessedImageName']
df = df.drop(columns=columns_to_hide)

# Streamlit app
st.title("🌾FarmBeats Monitor")

# Sidebar for filtering data
with st.sidebar:
    st.write("Filter data")
    option = st.selectbox('Predict status', ('Yes', 'No'))


# Display the dataframe with image preview in the column
st.data_editor(
    df,
    column_config={
        "RawImage": st.column_config.ImageColumn(
            "Preview Image", help="Streamlit app preview screenshots"
        )
    },
    hide_index=True,
)
