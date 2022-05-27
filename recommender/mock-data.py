from faker import Faker
import pandas as pd
import os
import sqlite3
os.getcwd()

fake = Faker(locale = "en_GB")

fake_dict = {}
fake_dict["first_name"] = []
fake_dict["last_name"] = []
fake_dict["email_address"] = []
fake_dict["phone_number"] = []


for _ in range(4226):
    name = fake.name().split()
    fake_dict["first_name"].append(name[-1])
    fake_dict["last_name"].append(name[-2])
    fake_dict["email_address"].append(fake.email())
    fake_dict["phone_number"].append(fake.phone_number())

fake_df = pd.DataFrame(fake_dict)
fake_df.head()
fake_df.to_excel("fake_data.xlsx")

customers = pd.read_csv("./recommender/customers.csv",delimiter = ";")
customers.head()

con = sqlite3.connect('./recommender/recommender.db')
customers.to_sql("customers", con=con, if_exists="replace")