import pandas as pd
import matplotlib.pyplot as plt
pd.options.display.float_format = '{:,.2f}'.format
from dotenv import load_dotenv
import os
from google import genai
import json
import streamlit as st
import plotly.express as px

if st.session_state.get("user") is None:
    st.switch_page("auth.py")

with st.sidebar:
    st.write(f"Signed in as {st.session_state.user['email']}")
    if st.button("Sign out"):
        st.session_state.user = None
        st.switch_page('landing.py')


QUANTITY_KEYWORDS = ['quantity', 'qty', 'units', 'sold','sales volume']
PRICE_KEYWORDS = ['price', 'amount', 'cost', 'revenue', 'total','discounted_price','actual_price']
PRODUCT_KEYWORDS = ['product', 'item', 'sku', 'category', 'type']



st.title("Analey")
st.write('Your Business Data Analyst')
st.write('Upload a CSV to get instant stats, charts, and AI-generated insights.')

# makes streamlit accepts csv file on the webapp
uploaded_file = st.file_uploader("Upload your CSV", type="csv")



#takes the csv file and works on it to produce the various metrics and returns result(dict)
def profile_dataset(df,quantity_col, price_col):                 
    result = {}
    
    
    
    skewed_cols = []
    for column in df.select_dtypes(include= 'number'):
        mean = df[column].mean()
        median = df[column].median()
        diff = (mean - median)/mean

        if diff > 0.2:
           skewed_cols.append(column)
           result['skewed_columns'] = skewed_cols


    if quantity_col is not None and price_col is not None:
        df['revenue'] = df[quantity_col] * df[price_col]
        
        result['shape'] = df.shape
        result['null_count'] = df.isnull().sum().to_dict()
        
        for column in df.select_dtypes(include=['str','object']):
            if df[column].nunique() < 1000 and not is_date_column(df, column):
                result[f"revenue_by_{column}"] = df.groupby(column)['revenue'].sum().sort_values(ascending= False).to_dict()

    return result



def generate_insights(result):      #takes the dict(result) and generates the summary from it
    data_summary = json.dumps(result, indent=2)    

    st.subheader('AI-Generated Insights')

    prompt = f"""You are a senior data analyst. Here are statistics from a dataset:

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
        return st.error(f"⚠️AI insights are temporarily unavailable")


# checks whether a column header is in date/time format
def is_date_column(df, column):
    try:
        pd.to_datetime(df[column])
        return True
    except:
        return False


def find_matching_columns(df, keywords):
    matches = []
    for column in df.columns:
        for keyword in keywords:
            if keyword.lower() in column.lower():
                if column not in matches:
                    matches.append(column)
    return matches



# block to make sure app loads even when csv is uploaded yet
if uploaded_file is not None:
    try:
        rows_to_skip = st.number_input("If your file has extra rows before the real headers, how many should be skipped?", min_value=0, value=0, step=1)                                                        # checks if csv file is valid
        encodings_to_try = ['utf-8', 'windows-1252', 'latin-1']
        df = None

        for encoding in encodings_to_try:
            try:
                uploaded_file.seek(0)
                df = pd.read_csv(uploaded_file, encoding=encoding, skiprows= rows_to_skip)
                
                break
            except:
                continue

        if df is None:
            st.error("...")
            st.stop()

        if df.empty:
            st.error("Your CSV file is empty")
            st.stop()
        elif len(df) < 5:
            st.error("CSV file invalid...Your CSV file needs at least 5 rows of data for meaningful analysis.")
            st.stop()
           

    except:
        st.error("An error occured while reading the file. Ensure it's a valid CSV file ")
        st.stop()

    
    quantity_matches = find_matching_columns(df, QUANTITY_KEYWORDS)
    price_matches = find_matching_columns(df, PRICE_KEYWORDS)
    product_matches = find_matching_columns(df, PRODUCT_KEYWORDS)

    if len(quantity_matches) == 1:
        quantity_col = quantity_matches[0]
        if quantity_col is not None:
            try:
                df[quantity_col] = df[quantity_col].str.replace(',', '')
                df[quantity_col] = pd.to_numeric(df[quantity_col])
            except:
                pass

    elif len(quantity_matches) > 1:
        quantity_col = st.selectbox("Which column is quantity?", quantity_matches)
    else:
        quantity_col = None

    if len(price_matches) == 1:
        price_col = price_matches[0]
        if price_col is not None:
            try:
                df[price_col] = df[price_col].str.replace('€', '')
                df[price_col] = df[price_col].str.replace('£', '')
                df[price_col] = df[price_col].str.replace(',', '')
                df[price_col] = df[price_col].str.replace('$', '')
                df[price_col] = df[price_col].str.replace('₹', '')
                df[price_col] = pd.to_numeric(df[price_col])
            except:
                pass


    elif len(price_matches) > 1:
        price_col = st.selectbox("Which column is price?", price_matches)
    else:
        price_col = None


    categorical_cols = df.select_dtypes(include='object').columns.tolist()
    numerical_cols = df.select_dtypes(include='number').columns.tolist()

    if not numerical_cols:
        st.info(
            "We could not find numeric data yet. "
            "Use the header-row setting above to skip the rows before your real column headings."
        )
        st.dataframe(df.head())
        st.stop()

    filtered_categorical_cols = []
    for column in categorical_cols:
        if not is_date_column(df, column):
            filtered_categorical_cols.append(column)

    with st.sidebar:
        select_category = st.selectbox('Groupby',filtered_categorical_cols)
        select_number = st.selectbox('Measure',numerical_cols)


    if select_category is None or select_number is None:
        st.info(
            "Choose a valid category and numeric measure after setting the correct header row."
        )
        st.stop()


    #  to generate the charts 
    chart_data = df.groupby(select_category)[select_number].sum().sort_values(ascending=False)
    total = chart_data.sum()
    

    # Turn the grouped result into a normal two-column dataframe
    chart_data_df = chart_data.reset_index()

    # Build a Plotly bar chart
    fig = px.bar(
        chart_data_df,
        x=select_category,
        y=select_number,
        color=select_category,
        )

    st.plotly_chart(fig, use_container_width=True)
    st.write(f"### {select_number} by {select_category}")
    st.metric(label=f"Total {select_number}", value= total)
    


    result=(profile_dataset(df,quantity_col, price_col))
    breakdown_keys = [key for key in result.keys() if key.startswith("revenue_by_")]
    


    selected_breakdown = st.selectbox("View breakdown", breakdown_keys)
    breakdown_data = result[selected_breakdown]
    breakdown_df = pd.DataFrame(list(breakdown_data.items()), columns=['Category', 'Value'])
    st.dataframe(breakdown_df)

    insights = generate_insights(result)
    st.write(insights) 