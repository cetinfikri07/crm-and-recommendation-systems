from sqlalchemy.types import Enum
from datetime import datetime
from recommender.sharedbp import db
import enum

# Status
class CartStatus(enum.Enum):
    Open=1
    CheckedOut=2

# Base Model
class Base(db.Model):
     __abstract__ = True
     id = db.Column(db.Integer, primary_key=True)
     created_date = db.Column(db.DateTime(), default=datetime.now())
     modified_date = db.Column(db.DateTime(), default=datetime.now(), onupdate=datetime.now())
     is_deleted = db.Column(db.Boolean(), default=False)



# Cart Model
class Cart(Base):
    __tablename__ = 'carts' 
    unique_cart_id = db.Column(db.String(500), unique=False)
    cart_items = db.relationship('CartItem', backref='cart_items', lazy=True)
    cart_status  = db.Column('cart_status', Enum(CartStatus))
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"))


# CartItem Model
class CartItem(Base):
    __tablename__ = 'cart_items'
    quantity = db.Column(db.Integer(), default=1)
    product_id = db.Column(db.Integer(), db.ForeignKey('products.id'), nullable=False)
    product = db.relationship("Product")
    cart_id = db.Column(db.Integer(), db.ForeignKey('carts.id'), nullable=False)
    cart = db.relationship("Cart", backref=db.backref('cart',cascade='all, delete-orphan',lazy=True))
    
    def cart_item_total(self):           
        return self.quantity * self.product.price 
    
    def name(self):           
        return self.product.name  
    
    def price(self):           
        return self.product.price

    def image_url(self):           
        return self.product.image_url
 
    def increase_quantity(self, quantity):           
        self.quantity = self.quantity + int(quantity)
    



