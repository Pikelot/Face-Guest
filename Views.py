from flask import Flask
from flask import render_template
from Main import app


@app.route('/')
def homepage():
    return render_template('homepage.html')

@app.route('/about')
def about():
    return "sobre o site"