import streamlit as st
import pandas as pd
from azure.storage.blob import BlobServiceClient
from azure.data.tables import TableServiceClient
from io import BytesIO
from PIL import Image
from st_aggrid import GridOptionsBuilder, JsCode, AgGrid

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

options_builder = GridOptionsBuilder.from_dataframe(df)

image_nation = JsCode("""
        class ThumbnailRenderer {
            init(params) {

            this.eGui = document.createElement('img');
            this.eGui.setAttribute('src', params.value);
            this.eGui.setAttribute('width', '200');
            this.eGui.setAttribute('height', '200');
            }
                getGui() {
                console.log(this.eGui);

                return this.eGui;
            }
        }
""")
options_builder.configure_column('RawImage', cellRenderer=image_nation)

grid_options = options_builder.build()

# Streamlit app
st.title("🌾FarmBeats Monitor")

grid_return = AgGrid(df,
                     grid_options,
                     theme="streamlit",
                     allow_unsafe_jscode=True,
                     )


# Display the table with images
# st.dataframe(df)
with st.sidebar:
    option = st.selectbox('Predict ststus',('Yes', 'No'))

    st.page_link("app.py", label="Realtime Image", icon="📷")
    st.page_link("app2.py", label="Realtime Image", icon="📷")
# Show images with table data
for index, row in df.iterrows():
    st.write(row.to_dict())
    st.image(row['RawImage'], caption=row['RowKey'])
