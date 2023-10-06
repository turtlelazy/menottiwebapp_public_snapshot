from flask import Flask  # facilitate flask webserving
from flask import render_template  # facilitate jinja templating
from flask import request
from flask.helpers import make_response  # facilitate form submission

#the conventional way:
#from flask import Flask, render_template, request

app = Flask(__name__)  # create Flask object

@app.route("/", methods=['GET', 'POST'])
def home():
    """
    home page
    """
    return "Home page goes here. maybe list all the web app integrations and redirect to login if not logged in"


@app.route("/login", methods=['GET', 'POST'])
def disp_loginpage():
    """
    renders the login page
    """
    return render_template('login.html',error="")
    #brings up the login.html page
    #askes for inputs of a text and to press a submit button

if __name__ == "__main__":  
    """
    false if this file imported as module
    debugging enabled    
    """
    app.debug = True
    app.run()
