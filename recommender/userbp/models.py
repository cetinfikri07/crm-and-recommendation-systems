from sqlalchemy.types import Enum
from datetime import datetime
from recommender.sharedbp import db
import enum
from flask_login import UserMixin


class Base(db.Model):
     __abstract__ = True
     id = db.Column(db.Integer, primary_key=True)
     created_date = db.Column(db.DateTime(), default=datetime.now())
     modified_date = db.Column(db.DateTime(), default=datetime.now(), onupdate=datetime.now())
     is_deleted = db.Column(db.Boolean(), default=False)


class Customer(UserMixin,Base):
    __tablename__ = "customers"
    # id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    email_address  = db.Column(db.String(50))  
    phone_number = db.Column(db.String(20))
    country = db.Column(db.String(20))
    username = db.Column(db.String(15))
    password = db.Column(db.String(80))
    cart = db.relationship("Cart",backref = "unique_card_id",lazy = "select",uselist = False)
    rfm_id = db.Column(db.Integer(),db.ForeignKey("rfm_segments.id"))
    cltvc_id = db.Column(db.Integer(),db.ForeignKey("clv_calculation.id"))
    cltvp_id = db.Column(db.Integer(),db.ForeignKey("clv_pred.id"))





