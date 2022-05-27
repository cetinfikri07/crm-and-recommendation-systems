from recommender.dashboardbp.models import RfmSegments,CLVCalculation
from recommender.userbp.models import Customer
from recommender.orderbp.models import OrderItem
from recommender.orderbp.models import Order
from recommender.sharedbp import db
from sqlalchemy.sql import func
from sklearn.preprocessing import MinMaxScaler
from lifetimes import BetaGeoFitter
from lifetimes import GammaGammaFitter
import datetime as dt
import pandas as pd
import numpy as np
import sqlite3
import json
import os

basedir = os.path.abspath(os.path.dirname(__file__ + "/../../"))
con_string = os.path.join(basedir,"recommender.db")


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


def scatter_plot_data(dataframe,col,y_axis):
    for i in dataframe.columns:
        dataframe = remove_outlier(dataframe, i)
    x = dataframe[col].values
    y = dataframe[y_axis].values
    scatter_plot_dict = {}
    scatter_plot_dict[col] = {}
    scatter_plot_dict[col]["values"] = []
    for i in range(len(x)):
        d = {"x": float(x[i]), "y": int(y[i])}
        scatter_plot_dict[col]["values"].append(d)
    return scatter_plot_dict

def scatter_plot_rfm_data(dataframe,col,y_axis):
    num_cols = [col for col in dataframe.columns if dataframe[col].dtype in [np.int64, np.float64]]
    cat_cols = [col for col in dataframe.columns if dataframe[col].dtype == "O"]
    for i in num_cols:
        dataframe = remove_outlier(dataframe, i)
    for s in cat_cols:
        segment_list = dataframe[s].unique()
    x = dataframe[col].values
    y = dataframe[y_axis].values
    scatter_plot_dict = {}
    for segment in segment_list:
        scatter_plot_dict[segment] = {}
        scatter_plot_dict[segment][col] = {}
        scatter_plot_dict[segment][col]["values"] = []
        for i in range(len(x)):
            d = {"x": float(x[i]), "y": int(y[i])}
            scatter_plot_dict[segment][col]["values"].append(d)
    return scatter_plot_dict



# for select list 
def fetch_segments():
    segments = db.session.query(RfmSegments.segment).distinct().all()
    l_segments = [s[0] for s in segments]
    return l_segments

def fetch_countries():
    countries = db.session.query(Customer.country).distinct().all()
    l_countries = [s[0] for s in countries]
    return l_countries

def fetch_rfm_onload():
    customer_segment = db.session.query(Customer,RfmSegments).join(RfmSegments).all()
    return customer_segment

def fetch_cltv_onload():
    cltv = db.session.query(Customer,CLVCalculation).join(CLVCalculation).all()
    return cltv


def fetch_customer_segment(request):
    if request.form["segment"] != "all-segments" and request.form["country"] != "all-countries":
        customer_segment = db.session.query(Customer,RfmSegments).join(RfmSegments).filter((RfmSegments.segment == request.form["segment"]) & (Customer.country == request.form["country"])).all()
    elif request.form["segment"] != "all-segments":
        customer_segment = db.session.query(Customer,RfmSegments).join(RfmSegments).filter(RfmSegments.segment == request.form["segment"]).all()
    elif request.form["country"] != "all-countries":
        customer_segment = db.session.query(Customer,RfmSegments).join(RfmSegments).filter(Customer.country == request.form["country"]).all()
    else:
        customer_segment = db.session.query(Customer,RfmSegments).join(RfmSegments).all()

    return customer_segment


def home_kpis():
    # Kpi lists
    kpis = {}

    con = sqlite3.connect(con_string)
    cur = con.cursor()
    before_30d = cur.execute("""
                    SELECT COUNT(DISTINCT id)
                    FROM
    	                (SELECT order_items.order_date, customers.id
    	                FROM order_items
    	                JOIN orders 
    	                ON order_items.order_id = orders.id 
    	                JOIN customers on customers.id = orders.customer_id
    	                )
                        WHERE order_date > DATETIME('now',"-1 month")
                    """).fetchone()[0]
    before_1y = cur.execute("""
                    SELECT COUNT(DISTINCT id)
                    FROM
    	            (SELECT order_items.order_date, customers.id
    	            FROM order_items
    	            JOIN orders 
    	            on order_items.order_id = orders.id 
    	            JOIN customers on customers.id = orders.customer_id
    	            )
                    WHERE order_date > DATETIME('now',"-1 year")
                    """).fetchone()[0]
    repeat_rate = cur.execute("""
                    SELECT (x / COUNT(DISTINCT customers.id))
                    FROM (
	                SELECT COUNT(DISTINCT customer_id) as x
	                FROM
		                (SELECT customers.id as customer_id, order_items.order_id
		                FROM order_items
		                JOIN orders 
		                on order_items.order_id = orders.id 
		                JOIN customers on customers.id = orders.customer_id
		                )
	                    WHERE order_id >= 2
                        ), customers
                    """).fetchone()[0] * 100
    today_orders = cur.execute(""" 
                SELECT COUNT(order_items.id)
                FROM order_items
                WHERE strftime('%Y-%m-%d', order_items.order_date) = date("now")
                """).fetchone()[0]
    # retention rate
    retention_rate = round((before_30d / before_1y * 100),2)
    # churn rate
    churn_rate = round((100 - retention_rate),2)
    retention_rate = "%"+str(retention_rate)
    churn_rate = "%"+str(churn_rate)
    repeat_rate = "%"+str(repeat_rate)
    con.commit()
    con.close()
    kpis["Churn Rate"] = [churn_rate,"bg-primary"]
    kpis["Retention Rate"] = [retention_rate,"bg-warning"]
    kpis["Repeat Rate"] = [repeat_rate,"bg-success"]
    kpis["Orders Today"] = [today_orders,"bg-danger"]
    print(basedir)
    return kpis

def home_charts():
    # Number of orders made by customers
    con = sqlite3.connect(con_string)
    cur = con.cursor()
    most_orders = cur.execute(""" 
                    SELECT customers.id as customer_id, COUNT(DISTINCT order_items.order_id) as number_of_orders
                    FROM order_items
                    JOIN orders 
                    ON order_items.order_id = orders.id 
                    JOIN customers on customers.id = orders.customer_id
                    GROUP BY customer_id ORDER BY number_of_orders DESC LIMIT 6
                """).fetchall()

    best_sellers = cur.execute(""" 
                        SELECT products.id as product_name, COUNT(DISTINCT order_items.order_id) as total_orders
                        FROM order_items,products
                        WHERE order_items.product_id = products.id
                        GROUP BY product_name ORDER BY total_orders DESC LIMIT 6
                """).fetchall()

    print(best_sellers)


    customer_ids = []
    num_orders = []
    for id,num in most_orders:
        customer_ids.append(id)
        num_orders.append(num)

    product_names = []
    num_sales = []
    for name,num in best_sellers:
        product_names.append(name)
        num_sales.append(num)

    # Line Plot 
    order_items = pd.read_sql("SELECT order_date,total_price FROM order_items",con)
    order_items["order_date"] = pd.to_datetime(order_items["order_date"])
    total_sales_by_years = order_items.groupby(order_items.order_date.dt.year)["total_price"].sum()
    years = list(total_sales_by_years.index)
    sales = total_sales_by_years.values

    lineplot_dict = {}
    for year,sale in zip(years,sales):
        lineplot_dict[year] = int(sale)

    # Pie Chart 
    customer_country = pd.read_sql("SELECT id,country FROM customers",con)
    pie_chart = customer_country.groupby("country")["id"].count().sort_values(ascending=False)[0:5]
    country_list = list(pie_chart.index)
    numbers = pie_chart.values
    pie_dict = {}
    for country,number in zip(country_list,numbers):
        pie_dict[country] = int(number)

    return customer_ids,num_orders, product_names, num_sales,lineplot_dict,pie_dict

def rfm_kpis():
    #session.query(func.avg(Rating.field2).label('average')).filter(Rating.url==url_string.netloc)
    avg_rfm = db.session.query(func.avg(RfmSegments.recency),func.avg(RfmSegments.frequency),func.avg(RfmSegments.monetary)).all()
    avg_rfm_list = []
    for r,f,m in avg_rfm:
        avg_rfm_list.append(round(r,2))
        avg_rfm_list.append(round(f,2))
        avg_rfm_list.append(round(m,2))

    avg_rfm_scores = db.session.query(func.avg(RfmSegments.recency_score),func.avg(RfmSegments.freqeuncy_score),func.avg(RfmSegments.monetary_score)).all()
    avg_rfm_scores_list = []
    for r,f,m in avg_rfm_scores:
        avg_rfm_scores_list.append(round(r))
        avg_rfm_scores_list.append(round(f))
        avg_rfm_scores_list.append(round(m))

    return avg_rfm_list,avg_rfm_scores_list


def rfm_charts():
    con = sqlite3.connect(con_string)
    cur = con.cursor()
    segment_count = cur.execute(""" 
                    SELECT rfm_segments.segment as segments, COUNT(DISTINCT rfm_segments.customer_id) as total_customers
                    FROM rfm_segments
                    GROUP BY segments ORDER BY total_customers DESC
                    """).fetchall()

    segment_names = []
    customer_count = []
    for segment,count in segment_count:
        segment_names.append(segment)
        customer_count.append(count)

    # Scatter plots 
    rfm_query = """
                SELECT recency,frequency,monetary,segment
                FROM rfm_segments 
                """  
    rfm_df = pd.read_sql(rfm_query,con)
    scatter_freq_dict = scatter_plot_rfm_data(rfm_df,"frequency","monetary")
    scatter_recency_dict = scatter_plot_rfm_data(rfm_df,"recency","monetary")

    backgroundColor = ["rgb(239, 196, 86)","rgb(54, 162, 235)","rgb(152, 18, 229)","rgb(255, 26, 104)","rgb(242, 121, 0)","rgb(26, 183, 201)","rgb(201, 237, 45)","rgb(53, 140, 59)"]
    datasets_freq = []
    for (key,value),color in zip(scatter_freq_dict.items(),backgroundColor):
        d = {
            "label" : key,
            "backgroundColor" : color,
            "data": scatter_freq_dict[key]["frequency"]["values"]
        }
        datasets_freq.append(d)

    datasets_recency = []
    for (key,value),color in zip(scatter_recency_dict.items(),backgroundColor):
        d = {
            "label" : key,
            "backgroundColor" : color,
            "data": scatter_recency_dict[key]["recency"]["values"]
        }
        datasets_recency.append(d)


    return segment_names,customer_count,scatter_freq_dict,scatter_recency_dict,datasets_freq,datasets_recency


def cltv_kpis():
    con = sqlite3.connect(con_string)
    cur = con.cursor()
    cltv_kpis = cur.execute(""" 
            SELECT avg(clv_calculation.average_order_value), avg(clv_calculation.purchase_frequency),avg(clv_calculation.customer_value),avg(clv_calculation.customer_lifetime_value)
            FROM clv_calculation
                    """).fetchone()
    kpis = {}

    kpis["Average Purchase Value"] = [round(cltv_kpis[0],2),"bg-primary"]
    kpis["Average Purchase Frequency"] = [round(cltv_kpis[1],4),"bg-warning"]
    kpis["Average Customer Value"] = [round(cltv_kpis[2],2),"bg-success"]
    kpis["Average CLTV"] = [round(cltv_kpis[3],2),"bg-danger"]
    
    return kpis


def cltv_bar_chart(request):
    con = sqlite3.connect(con_string)
    cur = con.cursor()

    cltv_table_query = """ 
            SELECT average_order_value,purchase_frequency,customer_lifetime_value
            FROM clv_calculation
    """ 

    cltv_table = pd.read_sql(cltv_table_query,con)

    scatter_plot_dict_freq = scatter_plot_data(cltv_table,"purchase_frequency","customer_lifetime_value")
    scatter_plot_dict_order = scatter_plot_data(cltv_table,"average_order_value","customer_lifetime_value")


    if "bar-chart-value" in request.form:
        value_name = request.form["bar-chart-value"]
        chart_data = cur.execute("""
                    SELECT clv_calculation.customer_id as customer_id , round(clv_calculation.{0},2) as {0}
                    FROM clv_calculation
                    ORDER BY {0} DESC LIMIT 6
                    """.format(request.form["bar-chart-value"])).fetchall()
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
        line_value = "average_cltv"
        for df in df_list:
            year = df["order_date"].dt.year.unique()[0]
            cltv = create_cltv_c(df)
            cltv_dict[str(year)] = ((cltv["total_price"].sum() / cltv["total_transaction"].sum()) * (cltv["total_transaction"].sum() / cltv.shape[0])) * 0.1

    elif "line-chart-value" in request.form:
        value_name = "scaled_cltv"
        chart_data = cur.execute("""
                    SELECT clv_calculation.customer_id as customer_id , round(clv_calculation.scaled_cltv,2) as scaled_cltv
                    FROM clv_calculation
                    ORDER BY scaled_cltv DESC LIMIT 6
                    """).fetchall()
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
        line_value = request.form["line-chart-value"]
        for df in df_list:
            year = df["order_date"].dt.year.unique()[0]
            year = str(year)
            cltv = create_cltv_c(df)
            if request.form["line-chart-value"] == "average_purchase_value":
                cltv_dict[year] =  cltv["total_price"].sum() / cltv["total_transaction"].sum()

            elif request.form["line-chart-value"] == "average_purchase_frequency":
                cltv_dict[year] = cltv["total_transaction"].sum() / cltv.shape[0]

            elif request.form["line-chart-value"] == "average_customer_value":
                cltv_dict[year] = (cltv["total_price"].sum() / cltv["total_transaction"].sum()) * (cltv["total_transaction"].sum() / cltv.shape[0])

            else:
                cltv_dict[year] = ((cltv["total_price"].sum() / cltv["total_transaction"].sum()) * (cltv["total_transaction"].sum() / cltv.shape[0])) * 0.1


    else:
        value_name = "scaled_cltv"
        chart_data = cur.execute("""
                    SELECT clv_calculation.customer_id as customer_id , round(clv_calculation.scaled_cltv,2) as scaled_cltv
                    FROM clv_calculation
                    ORDER BY scaled_cltv DESC LIMIT 6
                    """).fetchall()
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
        line_value = "average_cltv"
        for df in df_list:
            year = df["order_date"].dt.year.unique()[0]
            cltv = create_cltv_c(df)
            cltv_dict[str(year)] = ((cltv["total_price"].sum() / cltv["total_transaction"].sum()) * (cltv["total_transaction"].sum() / cltv.shape[0])) * 0.1

    top_customers_id = []
    top_customers_value = []

    for id,value in chart_data:
        top_customers_id.append(id)
        top_customers_value.append(value)

    return top_customers_id,top_customers_value,value_name,cltv_dict,line_value,scatter_plot_dict_freq,scatter_plot_dict_order

def expected_cltv(months = 1):
    con = sqlite3.connect(con_string)
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


def cltv_prediction_kpis_table(request):
    if "months" in request.form:
        months = int(request.form["months"])
        cltv_pred = expected_cltv(months = months)

        cltvp_kpis_dict = {}

        cltvp_kpis_dict["Expected Total Sales"] = [int(cltv_pred["expected_number_of_transactions"].sum()),"bg-primary",months]
        cltvp_kpis_dict["Expected Average Profit per Transaction "] = ["$"+str(round(cltv_pred["expected_average_profit_per_transaction"].mean(),2)),"bg-warning",months]
        cltvp_kpis_dict["Expected Total Profit (CLTV)"] = ["$"+str(round(cltv_pred["expected_cltv"].sum(),2)),"bg-success",months]
        cltvp_kpis_dict["Expected Total Net Profit"] = ["$"+str(round(cltv_pred["expected_cltv_net_profit"].sum(),2)),"bg-danger",months]



    else:
        cltv_pred = expected_cltv()
        months = 1
        cltvp_kpis_dict = {}

        cltvp_kpis_dict["Expected Total Sales"] = [int(cltv_pred["expected_number_of_transactions"].sum()),"bg-primary",months]
        cltvp_kpis_dict["Expected Average Profit per Transaction "] = ["$"+str(round(cltv_pred["expected_average_profit_per_transaction"].mean(),2)),"bg-warning",months]
        cltvp_kpis_dict["Expected Total Profit (CLTV)"] = ["$"+str(round(cltv_pred["expected_cltv"].sum(),2)),"bg-success",months]
        cltvp_kpis_dict["Expected Total Net Profit"] = ["$"+str(round(cltv_pred["expected_cltv_net_profit"].sum(),2)),"bg-danger",months]


    return cltvp_kpis_dict,cltv_pred,months

def dist_plot_data(dataframe,col):
    values = dataframe[col].values
    max = round(np.quantile(values, 0.99)+0.5)
    step_size = int(max/5)
    bins = np.linspace(0, max, num=21)
    hist, bin_edges = np.histogram(values, bins=bins)
    return hist,bin_edges,step_size



def cltv_prediction_charts(request,cltvp_table):

    # Default Bar Chart Values
    bar_chart_value = "expected_number_of_transactions"
    top_customer_ids = cltvp_table[["customer_id","expected_cltv"]].sort_values(by = "expected_cltv", ascending = False).head(6)["customer_id"].astype(str).values
    top_customer_values = cltvp_table[["customer_id","expected_cltv"]].sort_values(by = "expected_cltv", ascending = False).head(6)["expected_cltv"].astype(int).values
    top_customer_ids = top_customer_ids.tolist()
    top_customer_values = top_customer_values.tolist()

    # Default Line Plot Values
    dist_plot_value = "expected_number_of_transactions"
    hist, bin_edges,step_size = dist_plot_data(cltvp_table, dist_plot_value)
    dist_plot_dict = {}
    dist_plot_dict[dist_plot_value] = {}
    dist_plot_dict[dist_plot_value]["step_size"] = step_size
    dist_plot_dict[dist_plot_value]["values"] = []

    for i in range(len(hist)):
        d = {"x": float(bin_edges[i]), "y": int(hist[i])}
        dist_plot_dict[dist_plot_value]["values"].append(d)

    # Scatter Plot
    df = cltvp_table[["expected_number_of_transactions", "expected_average_profit_per_transaction", "expected_cltv"]]
    scatter_plot_dict_transaction = scatter_plot_data(df,"expected_number_of_transactions","expected_cltv")
    scatter_plot_dict_profit = scatter_plot_data(df,"expected_average_profit_per_transaction","expected_cltv")


    if "bar-chart-value" in request.form:
        bar_chart_value = request.form["bar-chart-value"]

        top_customer_ids = cltvp_table[["customer_id",bar_chart_value]].sort_values(by = bar_chart_value, ascending = False).head(6)["customer_id"].astype(str).values
        top_customer_values = cltvp_table[["customer_id",bar_chart_value]].sort_values(by = bar_chart_value, ascending = False).head(6)[bar_chart_value].astype(int).values
        top_customer_ids = top_customer_ids.tolist()
        top_customer_values = top_customer_values.tolist()

    if "dist-plot-value" in request.form:

        dist_plot_value = request.form["dist-plot-value"]

        hist, bin_edges, step_size = dist_plot_data(cltvp_table, dist_plot_value)
        dist_plot_dict = {}
        dist_plot_dict[dist_plot_value] = {}
        dist_plot_dict[dist_plot_value]["step_size"] = step_size
        dist_plot_dict[dist_plot_value]["values"] = []
        for i in range(len(hist)):
            d = {"x": float(bin_edges[i]), "y": int(hist[i])}
            dist_plot_dict[dist_plot_value]["values"].append(d)

    return top_customer_ids,top_customer_values,bar_chart_value,dist_plot_dict,dist_plot_value,scatter_plot_dict_transaction,scatter_plot_dict_profit
    


  

































        
















