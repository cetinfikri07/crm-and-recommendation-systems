from flask import (Blueprint, request,session, render_template, url_for, redirect,flash)
from recommender.userbp.forms import LoginForm, RegisterForm
from recommender.userbp.models import Customer
from recommender.cartbp.models import Cart,CartStatus
from recommender.sharedbp import db
from flask_login import login_user, logout_user, login_required
from recommender.userbp import user_service
from recommender.cartbp import cart_service

user = Blueprint("user",__name__,template_folder = "templates/userbp")


@user.route("/login",methods = ["GET","POST"])
def login_view():

    login_form = LoginForm()

    if request.method == "POST":
        user = Customer.query.filter_by(username = login_form.username.data).first()
        print(type(user.password))
        print(type(login_form.username.data))

        if user:
            if str(user.password) == login_form.password.data:
                login_user(user)
                return redirect(url_for("catalogue.catalogue_view"))


        return "<h1>Invalid username or password</h1>"

        #♣return "<h1>" + login_form.username.data + " " + login_form.password.data + "</h1>"

    else:
        return render_template(
                "login.html",
                form = login_form
                )
@user.route("/register",methods = ["GET","POST"])
def register_view():
    register_form = RegisterForm()

    if request.method == "POST":
        new_user = Customer(first_name = register_form.first_name.data, 
                            last_name = register_form.last_name.data, 
                            email_address = register_form.email.data,
                            phone_number = register_form.phone_number.data,
                            username = register_form.username.data,
                            password = register_form.password.data,
                            )

        db.session.add(new_user)
        db.session.commit()

        new_cart = Cart()
        new_cart.unique_cart_id = user_service._unique_cart_id(session)
        new_cart.cart_status = CartStatus.Open
        new_cart.customer_id = new_user.id
        db.session.add(new_cart)
        db.session.commit()

        session.clear()

        return redirect(url_for('user.login_view'))

    else:
        return render_template(
                "register.html",
                form = register_form
                )

@user.route('/logout')
@login_required
def logout():
    cart_service.clear_cart()
    logout_user()
    return redirect(url_for('user.login_view'))








