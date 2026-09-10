import pandas as pd
import matplotlib.pyplot as plt
pd.options.display.float_format = '{:,.2f}'.format
from dotenv import load_dotenv
import os
from google import genai
import json

filepath = "/Users/enockasiedu/Documents/ai-data-analyst/data-sample.csv"
df = pd.read_csv(filepath)


def profile_dataset(df):
    result = {}
    
    # df.info()
    #print(df.head())
    # print(df.describe())
    # print(df['category'].unique())
    # print(df['payment_method'].unique())
    print(df.groupby('category')['quantity'].sum().sort_values(ascending=False))

    print(df['category'].nunique())
    print(df['customer_id'].nunique())
    print(df['payment_method'].nunique())

    df['revenue'] = df['quantity'] * df['price']
    skewed_cols = []
    for column in df.select_dtypes(include= 'number'):
        mean = df[column].mean()
        median = df[column].median()
        diff = (mean - median)/mean

        if diff > 0.2:
           skewed_cols.append(column)
           result['skewed_columns'] = skewed_cols

    
    for column in df.select_dtypes(include = 'str'):
        if df[column].nunique() < 50:
            result['revenue' + '_' +'by'+ '_'+ column] = df.groupby(column)['revenue'].sum().sort_values(ascending=False).to_dict()



   
    result['revenue_by_category'] = df.groupby('category')['revenue'].sum().sort_values(ascending= False).to_dict()

    result['shape'] = df.shape
    result['null_count'] = df.isnull().sum().to_dict()
    result['top_category_by_quantity'] = df.groupby('category')['quantity'].sum().sort_values(ascending= False).to_dict()



    return result


def gen_graph(df):
    df.groupby('category')['revenue'].sum().sort_values(ascending= False).plot(kind = 'bar')
    plt.title('Revenue by Category')
    plt.tight_layout()
    plt.savefig('revenue_by_category.png')


# def generate_insights(result):
#     data_summary = json.dumps(result, indent=2)

#     prompt = f"""You are a data analyst. Here are statistics from a dataset:

#     {data_summary}

#     Write a short, plain-English summary of the key findings, and flag anything unusual."""

#     load_dotenv()
#     client = genai.Client()

#     interaction = client.interactions.create(
#     model="gemini-3.7-flash",
#     input= prompt
#     )
#     return interaction.output_text



result=(profile_dataset(df))
print(result)
gen_graph(df)

insights = generate_insights(result)
print(insights)