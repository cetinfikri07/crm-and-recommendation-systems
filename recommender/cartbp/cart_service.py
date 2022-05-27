
from recommender.cataloguebp.models import Product
from recommender.cartbp.models import CartStatus, Cart, CartItem
from recommender.sharedbp import db
from flask_login import current_user

def get_cart():
    if current_user.is_authenticated:
        current_user_id = current_user.id
        cart = Cart.query.filter_by(customer_id = current_user_id).first()
        return cart



def clear_cart():
    cart = get_cart()
    cart_items = CartItem.query.filter_by(cart_id = cart.id).all()
    for item in cart_items:
        db.session.delete(item)
    db.session.commit()


def add_to_cart(request,session):

    product_id = request.form["product_id"]
    product = Product.query.filter_by(id=product_id).first()

    cart = get_cart()

    cart_item = CartItem.query.filter_by(product_id=product_id).first()

    if cart_item:
        cart_item.increase_quantity(1)
        db.session.commit()
    else:
        new_cart_item = CartItem()
        new_cart_item.quantity = 1
        new_cart_item.product = product
        new_cart_item.product_id = product.id
        new_cart_item.cart_id= cart.id
        new_cart_item.cart = cart

        db.session.add(new_cart_item)
        db.session.commit()


# Removes Item from cart
def remove_from_cart(request):
    product_id = request.form['product_id']
    cart_item = CartItem.query.filter_by(product_id=product_id)

    cart_item.delete()
    db.session.commit()


# Return Items From User Cart
def get_cart_items(request):      

    #Get the cart
    cart = get_cart()

    if cart:
        return CartItem.query.filter_by(cart_id=cart.id).all()

# Gets the number of unique items in the User's CArt
def cart_items_count(request):
    items = get_cart_items(request)
    int = 0
    if items:     
       for item in items:
           int +=item.quantity
    return int


# Get the Cart Total
def get_cart_total(request):      

    #Get the cart
    cart = get_cart()
    cart_total = 0.00

    if cart:
        cart_items = CartItem.query.filter_by(cart_id=cart.id).all()
        for item in cart_items:
            cart_total += item.cart_item_total()
        return cart_total
    else:
        return cart_total



