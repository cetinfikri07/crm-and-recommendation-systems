from recommender.arlbp.models import Rules
from recommender.cataloguebp.models import Product
from recommender.sharedbp import db
from sqlalchemy.sql import select
import pandas as pd
import numpy as np

# Fetch from database
def get_rules_table():
    rules = Rules.query.all()
    rules_dict = []
    for rule in rules:
        rules_dict.append(rule.__dict__)    

    return rules_dict

def to_frozenset(x):
    return frozenset(map(int, x.split("{")[1].split("}")[0].split(",")))

def rules_dataframe():
    rules_dict = get_rules_table()
    rules_df = pd.DataFrame(rules_dict)
    #cols = [col for col in rules_df.columns if col not in ["antecedents","consequents","id"]]
    #for col in cols:
        #rules_df[col] = rules_df[col].str.replace(',', '').astype(float)
    rules_df[["antecedents","consequents"]] = rules_df[["antecedents","consequents"]].applymap(to_frozenset)
    return rules_df

def arl_recommender(rules_df, product_id, rec_count=1):
    sorted_rules = rules_df.sort_values("lift", ascending=False)
    recommendation_list_ids = []
    recommendation_list_obj = []

    for i, product in sorted_rules["antecedents"].items():
        for j in list(product):
            if j == product_id:
                recommendation_list_ids.append(list(sorted_rules.iloc[i]["consequents"]))

    recommendation_list_ids = list({item for item_list in recommendation_list_ids for item in item_list})

    for id in recommendation_list_ids:
        obj = Product.query.filter_by(id = id).first()
        recommendation_list_obj.append(obj)

    return recommendation_list_obj[:rec_count]




