import pandas as pd
import matplotlib.pyplot as plt
pd.options.display.float_format = '{:,.2f}'.format
from dotenv import load_dotenv
import os
from google import genai
import json
import streamlit as st

st.title("Analey")
st.write('Your AI Data Analyst')
st.write('Upload a CSV to get instant stats, charts, and AI-generated insights.')
# makes streamlit accepts csv file on the webapp
uploaded_file = st.file_uploader("Upload your CSV", type="csv")

    
#takes the csv file and works on it to produce the various metrics and returns result(dict)
def profile_dataset(df):                     
    result = {}
    
    # df.info()
    #print(df.head())
    # print(df.describe())
    # print(df['category'].unique())
    # print(df['payment_method'].unique())
    # st.write(df.groupby(column)['quantity'].sum().sort_values(ascending=False))
    
    
    skewed_cols = []
    for column in df.select_dtypes(include= 'number'):
        mean = df[column].mean()
        median = df[column].median()
        diff = (mean - median)/mean

        if diff > 0.2:
           skewed_cols.append(column)
           result['skewed_columns'] = skewed_cols


    if 'quantity' in df.columns and 'price' in df.columns:
        df['revenue'] = df['quantity'] * df['price']
        result['revenue_by_category'] = df.groupby('category')['revenue'].sum().sort_values(ascending= False).to_dict()

        result['shape'] = df.shape
        result['null_count'] = df.isnull().sum().to_dict()
        result['top_category_by_quantity'] = df.groupby('category')['quantity'].sum().sort_values(ascending= False).to_dict()


        for column in df.select_dtypes(include = 'str'):
            if df[column].nunique() < 50:
                result[f"revenue_by_{column}"] = df.groupby(column)['revenue'].sum().sort_values(ascending= False).to_dict()
            

    return result



def generate_insights(result):      #takes the dict(result) and generates the summary from it
    data_summary = json.dumps(result, indent=2)    

    st.subheader('AI-Generated Insights')

    prompt = f"""You are a data analyst. Here are statistics from a dataset:

    {data_summary}

    Write a short, plain-English summary of the key findings, and flag anything unusual."""

    # block handles the API calls 
    load_dotenv()
    try:
        client = genai.Client()

        interaction = client.interactions.create(
        model="gemini-3.7-flash",
        input= prompt
        )
        return interaction.output_text

    except Exception as e:
        return "⚠️ AI insights are temporarily unavailable (rate limit or API issue). Please try again shortly."


# block to make sure app loads even when csv is uploaded yet
if uploaded_file is not None:
    try:                                                        # checks if csv file is valid
        df = pd.read_csv(uploaded_file)
        if df.empty:
            st.error("Your CSV file is empty")
            st.stop()
        elif len(df) < 5:
            st.error("CSV file invalid...Your CSV file needs at least 5 rows of data for meaningful analysis.")
            st.stop()
           
        
    except:
        st.error("An error occured while reading the file. Ensure it's a valid CSV file ")
        st.stop()

    categorical_cols = df.select_dtypes(include='str').columns.tolist()
    numerical_cols = df.select_dtypes(include='number').columns.tolist()

    filtered_categorical_cols = []
    for column in categorical_cols:
        try:
            pd.to_datetime(df[column])
            continue
        except:
            filtered_categorical_cols.append(column)


    select_category = st.selectbox('Groupby',filtered_categorical_cols)
    select_number = st.selectbox('Measure',numerical_cols)


    #  to generate the charts 
    chart_data = df.groupby(select_category)[select_number].sum().sort_values(ascending=False)
    st.write(f"### {select_number} by {select_category}")
    st.bar_chart(chart_data)


    result=(profile_dataset(df))
    st.json(result)
   

    insights = generate_insights(result)
    st.write(insights)