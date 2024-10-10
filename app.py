import streamlit as st
import boto3
import pandas as pd
from io import StringIO

# Set the page config before any other Streamlit commands
st.set_page_config(layout="wide")

# Simple password protection
def password_protect():
    password = st.text_input("Enter password:", type="password")
    if password != "!NewEnglandClamCh0wd@":
        st.warning("Incorrect password. Please try again.")
        st.stop()  # This will stop the execution of the app if the password is incorrect.

password_protect()

# AWS credentials (using secrets)
aws_access_key_id = st.secrets["AWS_ACCESS_KEY_ID"]
aws_secret_access_key = st.secrets["AWS_SECRET_ACCESS_KEY"]

s3_client = boto3.client('s3',
                         aws_access_key_id=aws_access_key_id,
                         aws_secret_access_key=aws_secret_access_key,
                         region_name=st.secrets["AWS_DEFAULT_REGION"])

bucket_name = "5x5-athena-res"
folder_key = "results/"

@st.cache_data
def load_all_data():
    response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=folder_key)
    files = response.get('Contents', [])
    combined_df = pd.DataFrame()
    for file in files:
        file_key = file['Key']
        if file_key.endswith(".csv"):
            response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
            csv_data = response['Body'].read().decode('utf-8')
            df = pd.read_csv(StringIO(csv_data))
            combined_df = pd.concat([combined_df, df], ignore_index=True)
    return combined_df

st.title("AWS S3 Data Viewer")

try:
    data = load_all_data()
    st.write("Here is the combined data from your S3 bucket:")
    st.dataframe(data, use_container_width=True)
except Exception as e:
    st.error(f"Error loading data: {e}")
