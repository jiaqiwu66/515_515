import streamlit as st
import pandas as pd
from azure.storage.blob import BlobServiceClient
from azure.data.tables import TableServiceClient
from io import BytesIO
from PIL import Image

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
    image_name = row['RowKey'] + ".jpg"  # Assuming image names are in the format of RowKey.jpg
    image_url = get_image_url(blob_service_client, container_name_raw, image_name)
    image_urls.append(image_url)

df['RawImage'] = image_urls

# Streamlit app
st.title("Azure Table and Blob Images")

# Display the table with images
st.dataframe(df)

# Show images with table data
for index, row in df.iterrows():
    st.write(row.to_dict())
    st.image(row['RawImage'], caption=row['RowKey'])

