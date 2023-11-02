from flask import Flask  # facilitate flask webserving
from flask import render_template  # facilitate jinja templating
from flask import request
from flask.helpers import make_response  # facilitate form submissio
from flask import session, redirect
from data.users import *
from keys import *

# from answer.py import get_answer
#the conventional way:
#from flask import Flask, render_template, request

app = Flask(__name__)  # create Flask object
app.secret_key = flask_secret_key # set the secret key


@app.route("/", methods=['GET', 'POST'])
def home():
    """
    home page
    """
    if not 'email' in session or session['email'] == "":
        return redirect("/login")
    return render_template("home_page.html",user=session['email'])
    #return "Home page goes here. maybe list all the web app integrations and redirect to login if not logged in"


@app.route("/login", methods=['GET', 'POST'])
def disp_loginpage():
    """
    renders the login page
    """
    if request.method == "GET":
        return render_template('login.html',error="")
    if request.method == "POST":
        email = request.form.get("email", default = "")
        password = request.form.get("password", default="")

    if not user_exists(email):
            error = "Incorrect email or password"
            return render_template('login.html', error=error)
    else:
            if not verify_user(email, password):
                error = "Incorrect email or password"
                return render_template('login.html', error=error)
            else:
                session['email'] = email
                return redirect("/")

    return render_template('login.html',error="")
    #brings up the login.html page
    #askes for inputs of a text and to press a submit button

@app.route("/logout",methods=['GET','POST'])
def logout():
    session['email'] = ""
    return redirect("/login")  
@app.route("/ask",methods=["GET","POST"])
def ask_gpt():
    if not 'email' in session or session['email'] == "":
        return redirect("/login")

    if admin_verification(session['email']):
        if request.method == "GET":
            return render_template("qa_search.html",error="",response="")
        elif request.method == "POST":
            error = "Something is in the water"
            response = request.form.get("query", default="")
            return render_template("qa_search.html",error=error,response=response)
    else:
        return redirect("/")

@app.route("/billing",methods=["GET","POST"])
def bill():
    if not 'email' in session or session['email'] == "":
        return redirect("/login")

    if admin_verification(session['email']):
        return render_template("billing_upload.html",error="")
    else:
        return redirect("/")

if __name__ == "__main__":  
    """
    false if this file imported as module
    debugging enabled    
    """
    app.debug = True
    app.run()
