import streamlit as st
import pandas as pd
from azure.storage.blob import BlobServiceClient
from azure.data.tables import TableServiceClient
from datetime import datetime

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

# # Function to extract date and time from RowKey
# def extract_datetime(row_key):
#     try:
#         date_str, time_str = row_key.split('_')[1].split('-')[:2]
#         date = datetime.strptime(date_str, '%Y%m%d').date()
#         time = datetime.strptime(time_str, '%H%M%S').time()
#         return f"{date} {time}"
#     except Exception as e:
#         st.error(f"Error extracting datetime from RowKey '{row_key}': {e}")
#         return None

# # Add DateTime column to the dataframe
# df['DateTime'] = df['RowKey'].apply(extract_datetime)

# # Reorder columns to move DateTime to the first column
# first_column = df.pop('DateTime')
# df.insert(0, 'DateTime', first_column)

# Hide specific columns
columns_to_hide = ['RowKey', 'PartitionKey', 'RawImageName', 'ProcessedImageName']
df = df.drop(columns=columns_to_hide)

# Streamlit app
st.title("🌾FarmBeats Monitor")

# Sidebar for filtering data
with st.sidebar:
    st.write("Filter data")
    option = st.selectbox('Predict status', ('Yes', 'No'))

# Pagination settings
items_per_page = 10
total_items = len(df)
total_pages = (total_items // items_per_page) + (1 if total_items % items_per_page > 0 else 0)

# Get current page number from Streamlit session state
if 'current_page' not in st.session_state:
    st.session_state.current_page = 1

# Calculate the start and end indices of the dataframe slice for the current page
start_idx = (st.session_state.current_page - 1) * items_per_page
end_idx = start_idx + items_per_page

# Display the dataframe slice with image preview in the column
st.data_editor(
    df.iloc[start_idx:end_idx],
    column_config={
        "RawImage": st.column_config.ImageColumn(
            "Preview Image", help="Streamlit app preview screenshots"
        )
    },
    hide_index=True,
)

# Display pagination controls below the table
st.write(f"Page {st.session_state.current_page} of {total_pages}")
col1, col2, col3 = st.columns([1, 2, 1])
with col1:
    if st.button("Previous"):
        if st.session_state.current_page > 1:
            st.session_state.current_page -= 1
with col3:
    if st.button("Next"):
        if st.session_state.current_page < total_pages:
            st.session_state.current_page += 1
