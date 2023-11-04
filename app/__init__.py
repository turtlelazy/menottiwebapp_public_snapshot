from flask import Flask  # facilitate flask webserving
from flask import render_template  # facilitate jinja templating
from flask import request
from flask import flash
from flask.helpers import make_response  # facilitate form submissio
from flask import session, redirect
from data.users import *
from keys import *
from qb_app.invoicing import run_script, get_url
import os
from os.path import join, dirname, realpath
from werkzeug.utils import secure_filename

# from answer.py import get_answer
#the conventional way:
#from flask import Flask, render_template, request

app = Flask(__name__)  # create Flask object
app.secret_key = flask_secret_key # set the secret key
UPLOAD_FOLDER = "temp"
ALLOWED_EXTENSIONS = {'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
basedir = os.path.abspath(os.path.dirname(__file__))

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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
        return render_template("billing_upload.html",error="",auth_link=get_url())
    else:
        return redirect("/")

@app.route("/upload",methods=["GET","POST"])
def upload_data():
    if not 'email' in session or session['email'] == "":
        return redirect("/login")

    if admin_verification(session['email']) and request.method == "POST":
        print(request.form.get("auth_code", default=""))
        print(request.form.get("realm_id", default=""))
        if 'week' not in request.files:
            return redirect(request.url)
        if 'rates' not in request.files:
            return redirect(request.url)

        file_week = request.files['week']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file_week.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file_week and allowed_file(file_week.filename):
            filename = f"weekly_{unique_name(session['email'])}.csv"
            filename = secure_filename(filename)
            file_week.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        
        file_rates = request.files['rates']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file_rates.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file_rates and allowed_file(file_rates.filename):
            filename = f"rates_{unique_name(session['email'])}.csv"
            filename = secure_filename(filename)
            file_rates.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))


        return "UPLOADED!!"
    else:
        return redirect("/")

@app.route("/billing_test",methods=["GET","POST"])
def bill_t():
    # print(get_url())
    # return f'<a href ="{get_url()}" target="_blank">BLAHBLAHBLAH</a>'

    return "BEEP BOOP"

if __name__ == "__main__":  
    """
    false if this file imported as module
    debugging enabled    
    """
    app.debug = True
    app.run()
