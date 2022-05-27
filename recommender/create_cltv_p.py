##############################################################
# BG-NBD ve Gamma-Gamma ile CLTV Prediction
##############################################################

# 1. Verinin Hazırlanması (Data Preperation)
# 2. BG-NBD Modeli ile Expected Sales Forecasting
# 3. Gamma-Gamma Modeli ile Expected Average Profit
# 4. BG-NBD ve Gamma-Gamma Modeli ile CLTV'nin Hesaplanması
# 5. CLTV'ye Göre Segmentlerin Oluşturulması
# 6. Çalışmanın fonksiyonlaştırılması
# 7. Sonuçların Veri Tabanına Gönderilmesi

# Önceki formülü hatırlayalım:
# CLTV = (Customer_Value / Churn_Rate) x Profit_margin.
# Customer_Value = Average_Order_Value * Purchase_Frequency
import sqlite3
import datetime as dt
import json
import numpy as np
import pandas as pd
from lifetimes import BetaGeoFitter
from lifetimes import GammaGammaFitter
from lifetimes.plotting import plot_period_transactions
from sklearn.preprocessing import MinMaxScaler
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 500)
pd.set_option('display.float_format', lambda x: '%.2f' % x)

def create_cltv_p(save_database = False):
    con = sqlite3.connect('recommender.db')
    query = """
            SELECT customers.id, order_items.order_id,order_items.quantity,order_items.total_price, order_items.order_date 
            FROM order_items 
            JOIN orders on orders.id = order_items.order_id 
            JOIN customers 
            ON customers.id = orders.customer_id 
            """
    df = pd.read_sql(query, con)
    df.rename(columns={"id": "customer_id"}, inplace=True)
    df["order_date"] = pd.to_datetime(df["order_date"])
    cltv_df = df.groupby('customer_id').agg({'order_date': [lambda date: (date.max() - date.min()).days,
                                                            lambda date: (dt.datetime.today() - date.min()).days],
                                             'order_id': lambda num: num.nunique(),
                                             'total_price': lambda TotalPrice: TotalPrice.sum()})
    cltv_df.columns = cltv_df.columns.droplevel(0)
    cltv_df.columns = ['recency', 'T', 'frequency', 'monetary']
    # Average profit per transaction
    cltv_df["monetary"] = cltv_df["monetary"] / cltv_df["frequency"]
    # frequency > 1
    cltv_df = cltv_df[(cltv_df["frequency"] > 1)]
    # Weekly recency and T
    cltv_df["recency"] = cltv_df["recency"] / 7
    cltv_df["T"] = cltv_df["T"] / 7
    cltv_df = cltv_df.reset_index()
    if save_database:
        cltv_df.index = cltv_df.index.rename("id")
        cltv_df["created_date"] = dt.datetime.today()
        cltv_df["modified_date"] = dt.datetime.today()
        cltv_df["is_deleted"] = 0
        cltv_df.to_sql("clv_pred", con=con, if_exists="replace")
        print("clv_pred succesfully created")
    return cltv_df

cltv_p = create_cltv_p(save_database=True)

def expected_cltv(months = 1):
    con = sqlite3.connect(r"C:\Users\Fikri\Desktop\recommender\recommender\recommender.db")
    query = """
    SELECT customers.id as customer_id, customers.first_name,customers.last_name, customers.email_address, customers.phone_number, customers.country,clv_pred.recency,clv_pred.T,clv_pred.frequency,clv_pred.monetary
    FROM clv_pred 
    INNER JOIN customers ON clv_pred.customer_id = customers.id
            """
    clv_pred = pd.read_sql(query, con)
    # Expected number of transactions in weeks
    bgf = BetaGeoFitter(penalizer_coef=0.0001)
    bgf.fit(clv_pred["frequency"],
            clv_pred["recency"],
            clv_pred["T"])
    clv_pred["expected_number_of_transactions"] = bgf.conditional_expected_number_of_purchases_up_to_time(months,
                                                                                                              clv_pred["frequency"],
                                                                                                              clv_pred["recency"],
                                                                                                              clv_pred["T"])
    # expected average profit per transaction
    ggf = GammaGammaFitter(penalizer_coef=0.01)
    ggf.fit(clv_pred["frequency"], clv_pred["monetary"])
    clv_pred["expected_average_profit_per_transaction"] = ggf.conditional_expected_average_profit(clv_pred["frequency"],
                                                                                                  clv_pred["monetary"])
    clv_pred["expected_cltv"] = ggf.customer_lifetime_value(bgf,
                                                            clv_pred["frequency"],
                                                            clv_pred["recency"],
                                                            clv_pred["T"],
                                                            clv_pred["monetary"],
                                                            time=months,
                                                            freq="M",
                                                            discount_rate=0.01,
                                                            )
    clv_pred["expected_cltv_net_profit"] = clv_pred["expected_cltv"] * 0.1

    scaler = MinMaxScaler(feature_range=(0, 100))
    scaler.fit(clv_pred[["expected_cltv"]])
    clv_pred["expected_cltv_scaled"] = scaler.transform(clv_pred[["expected_cltv"]])

    return clv_pred


clv_pred = expected_cltv(months=1)
clv_pred[["customer_id","expected_number_of_transactions","expected_average_profit_per_transaction","expected_cltv"]].head().to_excel("cltvp_son.xlsx")

