from recommender.orderbp.models import Order,OrderStatus,OrderItem
from recommender.cartbp.models import Cart,CartItem
from flask_login import login_required, current_user
from recommender.userbp.models import Customer
from recommender.sharedbp import db
from recommender.cartbp import cart_service
from sqlalchemy import create_engine
from datetime import datetime


def get_cart():
    cart = Cart.query.filter_by(customer_id = current_user.id).first()
    return cart


def get_cart_total():      

    cart = get_cart()
    cart_total = 0.00

    if cart:
        cart_items = CartItem.query.filter_by(cart_id=cart.id).all()
        for item in cart_items:
            cart_total += item.cart_item_total()
        return cart_total
    else:
        return cart_total

def get_cart_items():      

    #Get the cart
    cart = get_cart()

    if cart:
        return CartItem.query.filter_by(cart_id=cart.id).all()

def place_order(request,session):
    cart = get_cart()
    if cart:
        cart_total = get_cart_total()

        customer = Customer.query.filter_by(id = current_user.id).first()
        order = Order()
        order.order_total = cart_total
        order.order_status = OrderStatus.Submitted
        order.customer_id = current_user.id
        order.customer = customer

        db.session.add(order)
        db.session.commit()

        cart_items = get_cart_items()

        if cart_items:
            for cart_item in cart_items:
                order_item = OrderItem()
                order_item.order_id = order.id
                order_item.quantity = cart_item.quantity
                order_item.price = cart_item.price()
                order_item.product_id = cart_item.product.id
                order_item.order_date = datetime.now()
                order_item.total_price = order_item.total()


                db.session.add(order_item)
                db.session.commit()

        cart_service.clear_cart()
        return True
    else:
        return False









