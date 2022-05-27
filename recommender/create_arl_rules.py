import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules
import sqlite3
import os

def outlier_thresholds(dataframe, variable):
    quartile1 = dataframe[variable].quantile(0.01)
    quartile3 = dataframe[variable].quantile(0.99)
    interquantile_range = quartile3 - quartile1
    up_limit = quartile3 + 1.5 * interquantile_range
    low_limit = quartile1 - 1.5 * interquantile_range
    return low_limit, up_limit

def replace_with_thresholds(dataframe, variable):
    low_limit, up_limit = outlier_thresholds(dataframe, variable)
    dataframe.loc[(dataframe[variable] < low_limit), variable] = low_limit
    dataframe.loc[(dataframe[variable] > up_limit), variable] = up_limit

def retail_data_prep(dataframe):
    dataframe.dropna(inplace=True)
    dataframe = dataframe[~dataframe["Invoice"].str.contains("C", na=False)]
    dataframe = dataframe[dataframe["Quantity"] > 0]
    dataframe = dataframe[dataframe["Price"] > 0]
    replace_with_thresholds(dataframe, "Quantity")
    replace_with_thresholds(dataframe, "Price")
    return dataframe

def check_df(dataframe, head=5):
    print("##################### Shape #####################")
    print(dataframe.shape)
    print("##################### Types #####################")
    print(dataframe.dtypes)
    print("##################### Head #####################")
    print(dataframe.head(head))
    print("##################### Tail #####################")
    print(dataframe.tail(head))
    print("##################### NA #####################")
    print(dataframe.isnull().sum())
    print("##################### Quantiles #####################")
    print(dataframe.quantile([0, 0.05, 0.50, 0.95, 0.99, 1]).T)

def create_invoice_product_df(dataframe, id=False):
    if id:
        return dataframe.groupby(['order_id', "product_id"])['quantity'].sum().unstack().fillna(0). \
            applymap(lambda x: 1 if x > 0 else 0)
    else:
        return dataframe.groupby(['order_id', 'product_id'])['quantity'].sum().unstack().fillna(0). \
            applymap(lambda x: 1 if x > 0 else 0)


def create_rules(dataframe, id=True, country="France"):
    dataframe = dataframe[dataframe['country'] == country]
    dataframe = create_invoice_product_df(dataframe, id)
    frequent_itemsets = apriori(dataframe, min_support=0.01, use_colnames=True)
    rules = association_rules(frequent_itemsets, metric="support", min_threshold=0.01)
    return rules


def arl_recommender(rules_df, product_id, rec_count=1):
    sorted_rules = rules_df.sort_values("lift", ascending=False)
    recommendation_list = []

    for i, product in sorted_rules["antecedents"].items():
        for j in list(product):
            if j == product_id:
                recommendation_list.append(list(sorted_rules.iloc[i]["consequents"]))

    recommendation_list = list({item for item_list in recommendation_list for item in item_list})

    return recommendation_list[:rec_count]

def create_rules(id=True, country="France",save_database = False):
    con = sqlite3.connect('recommender.db')
    query = """
    SELECT order_items.order_id,order_items.product_id,order_items.quantity,customers.country FROM order_items
    JOIN orders on orders.id = order_items.order_id 
    JOIN customers 
    ON customers.id = orders.customer_id
    """
    dataframe = pd.read_sql(query,con)
    dataframe = dataframe[dataframe['country'] == country]
    dataframe = create_invoice_product_df(dataframe, id)
    frequent_itemsets = apriori(dataframe, min_support=0.01, use_colnames=True)
    rules = association_rules(frequent_itemsets, metric="support", min_threshold=0.01)
    if save_database:
        rules[["antecedents", "consequents"]] = rules[["antecedents", "consequents"]].astype(str)
        rules = rules.rename(columns={"antecedent support": "antecedent_support", "consequent support": "consequent_support"})
        rules.index = rules.index.rename("id")
        rules.to_sql("rules",con = con, if_exists="replace")
        print("Rules tables has been succesfully created")
    return rules

rules = create_rules(country="Germany",save_database=False,id = False)
rules.head()

sorted_rules = rules.sort_values("lift", ascending=False)
recommendation_list = []

for i, product in sorted_rules["antecedents"].items():
    for j in list(product):
        if j == product_id:
            recommendation_list.append(list(sorted_rules.iloc[i]["consequents"]))

recommendation_list = list({item for item_list in recommendation_list for item in item_list})

