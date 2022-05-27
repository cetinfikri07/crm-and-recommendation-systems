import uuid

UNIQUE_CART_ID_SESSION_KEY = 'unique_cart_id'


# get the current user's unique cart id, sets new one if blank session comes from request
def _unique_cart_id(session):
     if UNIQUE_CART_ID_SESSION_KEY not in session:            
         session[UNIQUE_CART_ID_SESSION_KEY] = _generate_unique_id()    
     return session[UNIQUE_CART_ID_SESSION_KEY]


def _generate_unique_id():
    u_id = uuid.uuid1()
    u_id_string = str(u_id)
    return u_id_string

# Gets the cart
def get_cart(session): 
    unique_id =_unique_cart_id(session)
    cart = Cart.query.filter_by(unique_cart_id=unique_id).first() #Return None if cart does not exist
    return cart
