import sqlite3
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import datetime as dt
from sklearn.preprocessing import MinMaxScaler
import os
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.float_format', lambda x: '%.5f' % x)

def outlier_thresholds(dataframe, col_name, q1=0.05, q3=0.95):
    quartile1 = dataframe[col_name].quantile(q1)
    quartile3 = dataframe[col_name].quantile(q3)
    interquantile_range = quartile3 - quartile1
    up_limit = quartile3 + 1.5 * interquantile_range
    low_limit = quartile1 - 1.5 * interquantile_range
    return low_limit, up_limit

def remove_outlier(dataframe, col_name):
    low_limit, up_limit = outlier_thresholds(dataframe, col_name)
    df_without_outliers = dataframe[~((dataframe[col_name] < low_limit) | (dataframe[col_name] > up_limit))]
    return df_without_outliers

def outlier_count(dataframe,col,q1=0.05,q3=0.95):
    low_limit, up_limit = outlier_thresholds(dataframe,col,q1=0.05,q3=0.95)
    c = df[((df[col] < low_limit) | (df[col] > up_limit))].shape[0]
    return c

def create_rfm(save_database = False):
    con = sqlite3.connect('recommender.db')
    query = "SELECT order_items.order_date, order_items.order_id, customers.id,order_items.total_price, customers.country from order_items JOIN orders on order_items.order_id = orders.id JOIN customers on customers.id = orders.customer_id"
    df = pd.read_sql(query, con)
    # Data conversions
    df["order_date"] = pd.to_datetime(df["order_date"])
    df["total_price"] = pd.to_numeric(df["total_price"], errors="coerce")
    # Create rfm dataframe
    today_date = dt.datetime.today()
    rfm = df.groupby('id').agg({'order_date': lambda date: (today_date - date.max()).days,
                                'order_id': lambda num: num.nunique(),
                                'total_price': lambda total_price: total_price.sum()})
    rfm.columns = ['recency', 'frequency', 'monetary']
    # Recency
    rfm["recency_score"] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1])
    # Frequency
    rfm["freqeuncy_score"] = pd.qcut(rfm['frequency'].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
    # Monetary
    rfm["monetary_score"] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5])
    rfm["rfm_score"] = (rfm['recency_score'].astype(str) +
                        rfm['freqeuncy_score'].astype(str) +
                        rfm['monetary_score'].astype(str))
    seg_map = {
        r'[1-2][1-2]': 'hibernating',
        r'[1-2][3-4]': 'at_Risk',
        r'[1-2]5': 'cant_loose',
        r'3[1-2]': 'about_to_sleep',
        r'33': 'need_attention',
        r'[3-4][4-5]': 'loyal_customers',
        r'41': 'promising',
        r'51': 'new_customers',
        r'[4-5][2-3]': 'potential_loyalists',
        r'5[4-5]': 'champions'
    }
    rfm['segment'] = rfm['rfm_score'].replace(seg_map, regex=True)
    rfm['segment'] = rfm['segment'].str.replace('\d+', '')
    rfm = rfm.reset_index()
    rfm = rfm.rename(columns={"id": "customer_id"})
    rfm.index = rfm.index.rename("id")
    rfm["created_date"] = dt.datetime.today()
    rfm["modified_date"] = dt.datetime.today()
    rfm["is_deleted"] = 0
    if save_database:
        rfm.to_sql("rfm_segments", con=con, if_exists="replace")
        print("Table succesfully updated")
    return rfm

rfm = create_rfm(True)



