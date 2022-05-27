from sqlalchemy.types import Enum
from datetime import datetime
from recommender.sharedbp import db
import enum

# Status
class OrderStatus(enum.Enum):
    Canceled=1
    Submitted=2
    Completed=3
    Processing=4

# Base Model
class Base(db.Model):
     __abstract__ = True
     id = db.Column(db.Integer, primary_key=True,autoincrement=True)
     created_date = db.Column(db.DateTime(), default=datetime.now())
     modified_date = db.Column(db.DateTime(), default=datetime.now(), onupdate=datetime.now())
     is_deleted = db.Column(db.Boolean(), default=False)

# Order Model
class Order(Base):
    __tablename__ = 'orders' 
    order_total = db.Column(db.Float())
    order_status  = db.Column('order_status', Enum(OrderStatus))
    customer_id = db.Column(db.Integer(), db.ForeignKey('customers.id'), nullable=False)
    customer = db.relationship("Customer", backref=db.backref('customer',lazy=True))

# Order Item Model
class OrderItem(Base):
    __tablename__ = 'order_items'
    quantity = db.Column(db.Integer(), default=1) 
    product_id = db.Column(db.Integer(), db.ForeignKey('products.id'), nullable=False)
    product = db.relationship("Product")
    price = db.Column(db.Float())
    order_id = db.Column(db.Integer(), db.ForeignKey('orders.id'), nullable=False)
    order_date = db.Column(db.DateTime(),default = datetime.now().replace(microsecond=0))
    total_price = db.Column(db.Float())
    order = db.relationship("Order", backref=db.backref('order',lazy=True))

     
    def total(self):         
        return self.quantity * self.price

    #def sku(self):         
    #     return self.product.sku 

    #def __repr__(self):
    #    return '{} ({})'.format(self.product.name,self.product.sku)
    