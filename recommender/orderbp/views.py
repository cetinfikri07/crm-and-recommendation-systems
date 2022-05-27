from flask import (Blueprint, request,session, render_template, url_for, redirect) 
from datetime import datetime
from flask_login import login_required, current_user
from recommender.orderbp import order_service
from recommender.dashboardbp import dashboard_service


order = Blueprint('order', __name__)

@order.route("/order",methods = ["GET","POST"])
@login_required
def place_order():
    if request.method == "POST":
        result = order_service.place_order(request,session)
        if result:
            return redirect(url_for("checkout.receipt_view"))



       








