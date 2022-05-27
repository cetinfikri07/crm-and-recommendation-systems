# CLTV = (Customer Value / Cburn Rate) * Profit Margin
# Customer Value = Average Order Value * Purchase Frequency
# Average ORder Value = Total Price / Total Transaction
# Pruchase Frequency = Total Transaction / Total Number of Customers
# Churn Rate = 1 - Repeat Rate (Birden fazla alışveriş yapan müşteri sayısı)
import pandas as pd
import sqlite3
from sklearn.preprocessing import MinMaxScaler
import numpy as np
import datetime as dt
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.float_format', lambda x: '%.5f' % x)

def create_cltv_c(save_database = False):
    con = sqlite3.connect('recommender.db')
    query = """
    SELECT customers.id, order_items.order_id,order_items.quantity,order_items.total_price, order_items.order_date from order_items 
    JOIN orders on orders.id = order_items.order_id 
    JOIN customers 
    ON customers.id = orders.customer_id
    """
    df = pd.read_sql(query, con)
    df["order_date"] = pd.to_datetime(df["order_date"])
    df.rename(columns={"id": "customer_id"}, inplace=True)
    before_1y = pd.to_datetime('today').date() - dt.timedelta(days=365)
    df = df[df['order_date'].dt.date > before_1y]
    # cltv dataframe
    cltv_c = df.groupby("customer_id").agg({"order_id": lambda x: x.nunique(),
                                            "quantity": lambda x: x.sum(),
                                            "total_price": lambda x: x.sum()})
    cltv_c.head()
    # Average Order Value average_order_value = total_price / total_transaction
    cltv_c.columns = ["total_transaction", "total_unit", "total_price"]
    cltv_c["average_order_value"] = cltv_c["total_price"] / cltv_c["total_transaction"]
    # Purchase Frequency total_transaction / total_number_of_customers
    cltv_c["purchase_frequency"] = cltv_c["total_transaction"] / cltv_c.shape[0]
    # Repeat Rate & Churn Rate customers shopped more than once
    # 60 days from today
    before_30d = pd.to_datetime('today').date() - dt.timedelta(days=30)
    # filter date col less than 60 days date
    last_month = df[df['order_date'].dt.date > before_30d]
    repeat_rate = last_month["customer_id"].nunique() / df["customer_id"].nunique()
    churn_rate = 1 - repeat_rate
    # Profit Margin
    cltv_c["profit_margin"] = cltv_c["total_price"] * 0.10
    # customer value
    cltv_c["customer_value"] = (cltv_c["average_order_value"] * cltv_c["purchase_frequency"]) / churn_rate
    # Customer Lifetime Value
    cltv_c["customer_lifetime_value"] = cltv_c["customer_value"] * cltv_c["profit_margin"]
    # min max scaler
    scaler = MinMaxScaler(feature_range=(1, 100))
    scaler.fit(cltv_c[["customer_lifetime_value"]])
    cltv_c["scaled_cltv"] = scaler.transform(cltv_c[["customer_lifetime_value"]])
    cltv_c = cltv_c.sort_values(by="scaled_cltv", ascending=False)
    # segmenting
    cltv_c["segment"] = pd.qcut(cltv_c["scaled_cltv"], 4, labels=["D", "C", "B", "A"])
    if save_database:
        cltv_c = cltv_c.reset_index()
        cltv_c.index = cltv_c.index.rename("id")
        cltv_c["created_date"] = dt.datetime.today()
        cltv_c["modified_date"] = dt.datetime.today()
        cltv_c["is_deleted"] = 0
        cltv_c.to_sql("clv_calculation", con=con, if_exists="replace")
        print("clv_calculation succesfully created")
    return cltv_c

cltv_c = create_cltv_c(save_database=True)


