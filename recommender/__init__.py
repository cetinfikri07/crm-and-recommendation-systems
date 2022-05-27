"""
The flask application package.
"""
import os
from flask import Flask,request,session
from flask_admin import Admin
from flask_migrate import Migrate
from recommender.sharedbp import db
from flask_admin.contrib.sqla import ModelView
from recommender.cataloguebp.views import catalogue 
from recommender.cataloguebp.models import Product, Brand, Category
from recommender.userbp.views import user 
from recommender.cartbp.views import cart
from recommender.checkoutbp.views import checkout
from recommender.orderbp.views import order
from recommender.arlbp.views import arl
from recommender.dashboardbp.views import dashboard_blueprint
from recommender.cataloguebp.views import login_manager
from recommender.cartbp import cart_service


basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

# App config
app.config["SECRET_KEY"] = "yRbrs_yoA-2ZkpHBR6C7ZA"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir,"recommender.db")
app.config["SQLALCHEMY_TRACK_MODIFICATION"] = False

# Register Blueprint
app.register_blueprint(catalogue)
app.register_blueprint(user)
app.register_blueprint(cart)
app.register_blueprint(checkout)
app.register_blueprint(order)
app.register_blueprint(arl)
app.register_blueprint(dashboard_blueprint)

# Register Models to Admin
admin = Admin(app)
admin.add_view(ModelView(Product,db.session))
admin.add_view(ModelView(Category,db.session))
admin.add_view(ModelView(Brand,db.session))

#Register LoginManager
login_manager.init_app(app)

db.init_app(app)
migrate = Migrate(app,db,render_as_batch = True)

import recommender.views

@app.context_processor
def inject_context():
    return {
              'cart_item_count': cart_service.cart_items_count(request),
              'cart_total': cart_service.get_cart_total(request),
              'cart_items': cart_service.get_cart_items(request),
        }




