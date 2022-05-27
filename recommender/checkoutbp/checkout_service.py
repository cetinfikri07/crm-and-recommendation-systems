from recommender.checkoutbp.forms import CheckoutForm


def process_checkout(request,session):
    form = CheckoutForm(request.form)
    print(form.first_name.data)




