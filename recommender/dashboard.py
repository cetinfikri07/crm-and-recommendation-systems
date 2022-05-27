import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import datetime as dt
import sqlite3
import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.float_format', lambda x: '%.5f' % x)

con = sqlite3.connect('recommender.db')
# order_items
query = """
        SELECT order_date,total_price
        FROM order_items
        """

order_items = pd.read_sql(query,con)
order_items["order_date"] = pd.to_datetime(order_items["order_date"])
total_sales_by_years = order_items.groupby(order_items.order_date.dt.year)["total_price"].sum()
years = list(total_sales_by_years.index)
sales = total_sales_by_years.values

values_dict = {}
for year,sale in zip(years,sales):
    values_dict[year] = int(sale)

{
    2019: [],
    2020: []
}

# Yıllara gore cltv grafigi hesaplamak icin

def create_cltv_c(df):
    # cltv dataframe
    cltv_c = df.groupby("customer_id").agg({"order_id": lambda x: x.nunique(),
                                            "quantity": lambda x: x.sum(),
                                            "total_price": lambda x: x.sum()})
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
    return cltv_c



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
df_list = [df[df['order_date'].dt.year == y] for y in df['order_date'].dt.year.unique()]

cltv_dict = {}
for df in df_list:
    year = df["order_date"].dt.year.unique()[0]
    cltv = create_cltv_c(df)
    cltv_dict[year] = {"Average Purchase Value:" : cltv["total_price"].sum() / cltv["total_transaction"].sum(),
                       "Average Purchase Frequency" : cltv["total_transaction"].sum() / cltv.shape[0],
                       "Average Customer Value:" : (cltv["total_price"].sum() / cltv["total_transaction"].sum()) * (cltv["total_transaction"].sum() / cltv.shape[0]),
                       "Average CLTV" : ((cltv["total_price"].sum() / cltv["total_transaction"].sum()) * (cltv["total_transaction"].sum() / cltv.shape[0])) * 0.1}



list(cltv_dict.keys())

customer_country = pd.read_sql("SELECT id,country FROM customers",con)
pie_chart = customer_country.groupby("country")["id"].count().sort_values(ascending=False)[0:8]
country_list = list(pie_chart.index)
numbers = pie_chart.values
pie_dict = {}
for country,number in zip(country_list,numbers):
    pie_dict[country] = int(number)


