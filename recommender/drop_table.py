from sqlalchemy import create_engine
import sqlalchemy
from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine(r'sqlite:///C:\\Users\\Fikri\\Desktop\\recommender\\recommender\\recommender.db')
metadata = MetaData(engine, reflect=True)
table = metadata.tables.get("order_items")
base = declarative_base()

base.metadata.drop_all(engine, [table], checkfirst=True)

sqlalchemy.inspect(engine).get_table_names()






