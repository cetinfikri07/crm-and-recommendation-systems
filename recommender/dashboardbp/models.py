from datetime import datetime
from recommender.sharedbp import db

# Base Model
class Base(db.Model):
     __abstract__ = True
     id = db.Column(db.Integer, primary_key=True,autoincrement=True)
     created_date = db.Column(db.DateTime(), default=datetime.now())
     modified_date = db.Column(db.DateTime(), default=datetime.now(), onupdate=datetime.now())
     is_deleted = db.Column(db.Boolean(), default=False)


class RfmSegments(Base):
    __tablename__ = "rfm_segments"
    recency = db.Column(db.Integer())
    frequency = db.Column(db.Integer())
    monetary = db.Column(db.Float())
    recency_score = db.Column(db.String())
    freqeuncy_score = db.Column(db.String())
    monetary_score = db.Column(db.String())
    rfm_score = db.Column(db.String())
    segment = db.Column(db.String())
    customer_id = db.Column(db.Integer())
    customer = db.relationship("Customer",backref = "rfm_segments",lazy = "select",uselist = False)


class CLVCalculation(Base):
    __tablename__ = "clv_calculation"
    customer_id = db.Column(db.Integer())
    customer = db.relationship("Customer",backref = "clv_calculation",lazy = "select",uselist = False)
    total_transaction = db.Column(db.Integer())
    total_unit =  db.Column(db.Integer())
    total_price = db.Column(db.Float())
    average_order_value = db.Column(db.Float())
    purchase_frequency = db.Column(db.Float())
    profit_margin = db.Column(db.Float())
    customer_value = db.Column(db.Float())
    customer_lifetime_value = db.Column(db.Float())
    scaled_cltv = db.Column(db.Float())
    segment = db.Column(db.String())


class CLVPred(Base):
    __tablename__ = "clv_pred"
    customer_id = db.Column(db.Integer())
    customer = db.relationship("Customer",backref = "clv_pred",lazy = "select",uselist = False)
    recency = db.Column(db.Float())
    T = db.Column(db.Float())
    frequency = db.Column(db.Integer())
    monetary =  db.Column(db.Float())










