
from flask import (Blueprint, request,session, render_template, url_for, redirect) 
from datetime import datetime
from recommender.checkoutbp.forms import CheckoutForm
from recommender.checkoutbp import checkout_service
from flask_login import login_required

checkout = Blueprint('checkout', __name__, template_folder='templates/checkoutbp')


@checkout.route('/checkout', methods=['GET','POST'])
@login_required
def checkout_view():
    if request.method == "POST":
        result  = checkout_service.process_checkout(request,session)
        if result:
           return redirect(url_for('checkout.receipt_view'))
        else:
           return redirect(url_for('checkout.receipt_view'))
    else:
       form = CheckoutForm()

       return render_template(
           'checkout.html',
           title='Checkout Page',
           year=datetime.now().year,
           form = form,
         )

@checkout.route('/checkout/receipt')
@login_required
def receipt_view():

    return render_template(
           'receipt.html',
           title='Receipt Page',
           year=datetime.now().year,
         )


