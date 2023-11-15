from flask import Flask  # facilitate flask webserving
from flask import render_template  # facilitate jinja templating
from flask import request
from flask import flash
from flask.helpers import make_response  # facilitate form submissio
from flask import session, redirect
from data.users import *
from keys import *
from qb_app.invoicing import run_invoices, get_url
from qb_app.sandbox_bill import invoices_collection
from qb_app.get_rates import get_name_by_id
import pandas
import os
from os.path import join, dirname, realpath
from werkzeug.utils import secure_filename
from answer import get_answer

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
            # error = "Something is in the water"
            error=""
            response = get_answer(request.form.get("query", default=""))
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

@app.route("/upload",methods=["POST"])
def upload_data():
    if not 'email' in session or session['email'] == "":
        return redirect("/login")

    if admin_verification(session['email']) and request.method == "POST":
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
        rates_filepath = os.path.join(app.config['UPLOAD_FOLDER'],f"rates_{unique_name(session['email'])}.csv")
        week_filepath = os.path.join(app.config['UPLOAD_FOLDER'],f"weekly_{unique_name(session['email'])}.csv")
        df_rates = pandas.read_csv(rates_filepath)
        collection = invoices_collection(rates_filepath,week_filepath)
        session["collection"] = collection
        locations = []
        for header in collection.keys():
            locations.append([get_name_by_id(df_rates,header),header])
        # print(collection)
        return render_template("billing_confirmation.html",locations=locations)
    else:
        return redirect("/")

@app.route("/confirm", methods=['GET', 'POST'])
def qb_bill_confirm():
    if not 'email' in session or session['email'] == "":
        return redirect("/login")

    if admin_verification(session['email']) and request.method == "POST":
        session['bill_locations'] = request.form.getlist('location_id')
        rates_filepath = os.path.join(app.config['UPLOAD_FOLDER'],f"rates_{unique_name(session['email'])}.csv")
        df_rates = pandas.read_csv(rates_filepath)
        locations = []
        for location in session['bill_locations']:
            locations.append(get_name_by_id(df_rates,int(location)))

        print(request.form.getlist('location_id'))

        return render_template("bill_out.html",auth_link=get_url(),locations=locations)
    else:
        return redirect("/")

@app.route("/process",methods=['GET','POST'])
def process_invoices():
    if not 'email' in session or session['email'] == "":
        return redirect("/login")
    if admin_verification(session['email']) and request.method == "POST":

        auth_code = request.form.get("auth_code", default="")
        realm_id = request.form.get("realm_id", default="")
        date = request.form.get("start_date").split("-")
        starting_invoice_num = request.form.get("start_invoice")
        print(request.form.get("auth_code", default=""))
        print(request.form.get("realm_id", default=""))
        
        #format of date is yyyy-mm-dd [year,month,date]
        print((date))
        print(starting_invoice_num)
        auth_client.get_bearer_token(auth_code, realm_id=realm_id)
        state = auth_client.state_token
        print(state)
        rates_filepath = os.path.join(app.config['UPLOAD_FOLDER'],f"rates_{unique_name(session['email'])}.csv")
        df_rates = pandas.read_csv(rates_filepath)

        invoices = run_invoices(auth_client,int(date[0]),int(date[1]),int(date[2]),session["collection"],session['bill_locations'],int(starting_invoice_num),df_rates)
        print(invoices)
        return render_template("invoices_billed.html",invoices=invoices)
        #return render_template("bill_out.html",locations=locations)
    else:
        return redirect("/")



@app.route("/preview/invoice/<invoice_id>",methods=["GET"])
def preview_invoice(invoice_id):
    rates_filepath = os.path.join(app.config['UPLOAD_FOLDER'],f"rates_{unique_name(session['email'])}.csv")
    df_rates = pandas.read_csv(rates_filepath)
    print(get_name_by_id(df_rates,int(invoice_id)))
    totals = [0,0]
    for line in session['collection'][invoice_id]:
        totals[0] += float(line["Hours"])
        totals[1] += float(line["Total"])
    return render_template("preview_invoice.html",location=get_name_by_id(df_rates,int(invoice_id)),invoice=session['collection'][invoice_id],totals=totals)


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
