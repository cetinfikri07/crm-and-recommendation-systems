from flask import (Blueprint, request,session, render_template, url_for, redirect,jsonify) 
from datetime import datetime
from recommender.cataloguebp import catalogue_service
from recommender.cartbp import cart_service
from recommender.arlbp import arl_service
from flask_login import LoginManager,login_required, current_user
from recommender.userbp.models import Customer


login_manager = LoginManager() 
login_manager.login_view = "user.login_view"

catalogue = Blueprint('catalogue', __name__, template_folder='templates/cataloguebp')

@login_manager.user_loader
def load_user(user_id):
    return Customer.query.get(int(user_id))

@catalogue.route('/catalogue', methods=['GET','POST'])
@catalogue.route('/catalogue/<category_slug>/<brand_slug>/', methods=['GET','POST'])
@login_required
def catalogue_view(category_slug='all-categories', brand_slug='all-brands'): 

     if request.method == 'POST':

         cart_service.add_to_cart(request, session)

         #Fetching products from the catalogue service
         page_object = catalogue_service.fetch_products(request, category_slug, brand_slug)

         return render_template(
           'catalogue.html',
           title='Product Page',
           year=datetime.now().year,
           page_object= page_object,
           selected_category=category_slug,
           selected_brand=brand_slug,
           name = current_user.username
         )
     else:        
         page_object = catalogue_service.fetch_products(request, category_slug, brand_slug)

         return render_template(
           'catalogue.html',
           title='Product Page',
           year=datetime.now().year,
           page_object= page_object,
           selected_category=category_slug,
           selected_brand=brand_slug,
           name = current_user.id
         )


@catalogue.route('/catalogue/products/<product_slug>/',methods = ["GET","POST"]) 
@login_required
def product_detail_view(product_slug = "pink-cherry-lights"):
    # page_object = catalogue_service.fetch_products(request, category_slug, brand_slug)
    product_details = catalogue_service.product_details(request,product_slug)
    rules_df = arl_service.rules_dataframe()
    recommendation_list_obj = arl_service.arl_recommender(rules_df,product_details.id,3)


    if request.method == "POST":
        cart_service.add_to_cart(request, session)
        return render_template(

                  "product_detail.html",
                   title='Product Page',
                   year=datetime.now().year,
                   product_details = product_details,
                   recommendation_list_obj = recommendation_list_obj
           )

    else:
        return render_template(
                   "product_detail.html",
                   title='Product Page',
                   year=datetime.now().year,
                   product_details = product_details,
                   recommendation_list_obj = recommendation_list_obj
            )








