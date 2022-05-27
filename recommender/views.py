from datetime import datetime
from flask import  url_for, redirect 
from recommender import app

@app.route('/')
@app.route('/home')
def home():
    return redirect(url_for('catalogue.catalogue_view'))
