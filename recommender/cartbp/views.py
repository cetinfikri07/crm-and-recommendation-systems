from flask import (Blueprint, request, render_template, url_for, redirect) 
from datetime import datetime
from recommender.cartbp import cart_service
from recommender.arlbp import arl_service
from flask_login import LoginManager,login_required, current_user

cart = Blueprint('cart', __name__, template_folder='templates/cartbp')

@cart.route('/cart', methods=['GET','POST'])
@login_required
def cart_detail():
    rules_df = arl_service.rules_dataframe()
    cart_items = cart_service.get_cart_items(request)
    cart_items_id = []
    recommendation_list_obj = []

    for item in cart_items:
        cart_items_id.append(item.product_id)

        print("Cart items id:", cart_items_id)

    for id in cart_items_id:
        recommend = arl_service.arl_recommender(rules_df,id,rec_count= 3)
        print("Recommend list:", recommend)
        if len(recommend) > 0:
            for i in range(len(recommend)):
                recommendation_list_obj.append(recommend[i])

    print("Recommendations:",recommendation_list_obj)

    if request.method == "POST":
        cart_service.remove_from_cart(request)

        return render_template(
           'cart_detail.html',
           title='Product Page',
           year=datetime.now().year,
           recommendation_list_obj = recommendation_list_obj
         )
    else:

        return render_template(
           'cart_detail.html',
           title='Product Page',
           year=datetime.now().year,
           recommendation_list_obj = recommendation_list_obj
         )


