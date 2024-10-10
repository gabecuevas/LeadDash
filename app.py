import streamlit as st
import boto3
import pandas as pd
from io import StringIO

# AWS credentials (using the credentials set up via AWS CLI)
s3_client = boto3.client('s3')

# S3 bucket details
bucket_name = "5x5-athena-res"
folder_key = "results/"

# Read all CSV files from the S3 bucket folder
@st.cache_data
def load_all_data():
    # List all objects in the specified folder
    response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=folder_key)
    files = response.get('Contents', [])
    
    # Initialize an empty DataFrame to store all data
    combined_df = pd.DataFrame()

    # Loop through the files and load the data if the file is a CSV
    for file in files:
        file_key = file['Key']
        if file_key.endswith(".csv"):
            response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
            csv_data = response['Body'].read().decode('utf-8')
            df = pd.read_csv(StringIO(csv_data))
            combined_df = pd.concat([combined_df, df], ignore_index=True)
    
    return combined_df

# Streamlit UI
# Adjust the Streamlit layout for better UX
st.set_page_config(layout="wide")  # Set to "wide" to utilize more screen space

st.title("AWS S3 Data Viewer")

try:
    data = load_all_data()
    st.write("Here is the combined data from your S3 bucket:")
    st.dataframe(data, use_container_width=True)  # Make the table fill the available width
except Exception as e:
    st.error(f"Error loading data: {e}")

