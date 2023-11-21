from answer import get_answer
import json
import datetime

from flask import Flask  # facilitate flask webserving
from flask import render_template  # facilitate jinja templating
from flask import request
from flask import flash
from flask.helpers import make_response  # facilitate form submissio
from flask import session, redirect
from data.users import *
from keys import *
from qb_app.invoicing import run_invoices, get_url
from qb_app.sandbox_bill import invoices_collection, invoice_collection_to_JSON, combine_JSON_collections, collection_keys
from qb_app.get_rates import get_name_by_id
import pandas
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

def retrieve_requests(rates,week0,week1,date):
    collection0 = invoice_collection_to_JSON(invoices_collection(rates,week0),int(date[0]),int(date[1]),int(date[2]))
    if week1:
        date_1 = datetime.date(int(date[0]),int(date[1]),int(date[2])) + datetime.timedelta(days=7)
        collection1 = invoice_collection_to_JSON(invoices_collection(rates,week1),int(date_1.year),int(date_1.month),int(date_1.day))
        return combine_JSON_collections(collection0,collection1)
    else:
        return collection0



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

    if admin_verification(session['email']) or "onsite" in user_type(session['email']):
        if request.method == "GET":
            return render_template("qa_search.html",error="",response="")
        elif request.method == "POST":
            # error = "Something is in the water"
            error=""
            response = get_answer(request.form.get("query", default=""))
            return render_template("qa_search.html",error=error,response=response)
    else:
        return redirect("/")

# First Step: Upload the files
@app.route("/billing",methods=["GET","POST"])
def bill():
    if not 'email' in session or session['email'] == "":
        return redirect("/login")

    if admin_verification(session['email']) or "management" in user_type(session['email']) :
        return render_template("billing_upload.html",error="")
    else:
        return redirect("/")

@app.route("/billing_bi",methods=["GET","POST"])
def bill_bi():
    if not 'email' in session or session['email'] == "":
        return redirect("/login")

    if admin_verification(session['email']) or "management" in user_type(session['email']) :
        return render_template("billing_upload_bi.html",error="")
    else:
        return redirect("/")


#### TODO Utilize the Date that you added within the billing upload files and work off the JSON vs the original payload
#### TODO Change it down the chain
#### TODO Create a copy of this function that works for biweekly billing

# Second Step: Select the locations to bill out for
@app.route("/upload",methods=["POST"])
def upload_data():
    if not 'email' in session or session['email'] == "":
        return redirect("/login")

    if (admin_verification(session['email']) or "management" in user_type(session['email'])  ) and request.method == "POST":
        if "collection" in session:
            print("pop")
            session["collection"] = []
            # session.pop('collection', default=None)

        if 'week' not in request.files:
            return redirect(request.url)
        if 'rates' not in request.files:
            return redirect(request.url)
        
        #format of date is yyyy-mm-dd [year,month,date]
        date = request.form.get("start_date").split("-")
        print(int(date[0]),int(date[1]),int(date[2]))
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

        session["rates_path"] = rates_filepath
        session["week_filepath"] = week_filepath
        session["date"] = date

        df_rates = pandas.read_csv(rates_filepath)
        collection = invoice_collection_to_JSON(invoices_collection(rates_filepath,week_filepath),int(date[0]),int(date[1]),int(date[2]))
        # print(collection)
        collectionbi = []
        if 'week2' in request.files:
            print("SECOND WEEK DETECTED")

            file_week = request.files['week2']
            # If the user does not select a file, the browser submits an
            # empty file without a filename.
            if file_week.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if file_week and allowed_file(file_week.filename):
                filename = f"weekly2_{unique_name(session['email'])}.csv"
                filename = secure_filename(filename)
                file_week.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                week_filepath = os.path.join(app.config['UPLOAD_FOLDER'],f"weekly2_{unique_name(session['email'])}.csv")
                date_1 = datetime.date(int(date[0]),int(date[1]),int(date[2])) + datetime.timedelta(days=7)
                print(int(date[0]),int(date[1]),int(date[2]))
                print(int(date_1.year),int(date_1.month),int(date_1.day))
                session["week_filepath2"] = week_filepath

                collectionbi = invoice_collection_to_JSON(invoices_collection(rates_filepath,week_filepath),int(date_1.year),int(date_1.month),int(date_1.day))
                # print(collectionbi)
                # print(collectionbi)
        if collectionbi:
            print("COMBINING STAGE")
            # session["collection"] = combine_JSON_collections(collection,collectionbi)
            print(collection == collectionbi)

        # print(collection[10])

        # session["collection"] = collection
        # print(json.dumps(session["collection"],indent=2))
        # print(session["collection"][10] == collection[10])
        locations = []
        for header in collection_keys(collection):
            locations.append([get_name_by_id(df_rates,header),header])
        # print(collection)
        return render_template("billing_confirmation.html",locations=locations)
    else:
        return redirect("/")

# Third Step: Input auth id and bill out
@app.route("/confirm", methods=['GET', 'POST'])
def qb_bill_confirm():
    if not 'email' in session or session['email'] == "":
        return redirect("/login")

    if (admin_verification(session['email']) or "management" in user_type(session['email'])) and request.method == "POST":
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

# Fourth Step: Call the API and make invoices -> Return the invoice numbers
@app.route("/process",methods=['GET','POST'])
def process_invoices():
    if not 'email' in session or session['email'] == "":
        return redirect("/login")
    if (admin_verification(session['email']) or "management" in user_type(session['email'])) and request.method == "POST":

        auth_code = request.form.get("auth_code", default="")
        realm_id = request.form.get("realm_id", default="")
        starting_invoice_num = request.form.get("start_invoice")
        print(request.form.get("auth_code", default=""))
        print(request.form.get("realm_id", default=""))
        
        print(starting_invoice_num)
        auth_client.get_bearer_token(auth_code, realm_id=realm_id)
        state = auth_client.state_token
        print(state)
        rates_filepath = os.path.join(app.config['UPLOAD_FOLDER'],f"rates_{unique_name(session['email'])}.csv")
        df_rates = pandas.read_csv(rates_filepath)
        collection_val = retrieve_requests(session["rates_path"],session["week_filepath"],session["week_filepath2"],session["date"])
        invoices = run_invoices(auth_client,collection_val,session['bill_locations'],int(starting_invoice_num),df_rates)
        # print(invoices)
        return render_template("invoices_billed.html",invoices=invoices)
        #return render_template("bill_out.html",locations=locations)
    else:
        return redirect("/")

@app.route("/tester",methods=["GET"])
def testing(test):
    print(request.form.get("something"))
    return test

@app.route("/preview/invoice/<invoice_id>",methods=["GET"])
def preview_invoice(invoice_id):
    rates_filepath = os.path.join(app.config['UPLOAD_FOLDER'],f"rates_{unique_name(session['email'])}.csv")
    df_rates = pandas.read_csv(rates_filepath)
    print(get_name_by_id(df_rates,int(invoice_id)))
    totals = [0,0]
    iterable_target = []
    collection_val = retrieve_requests(session["rates_path"],session["week_filepath"],session["week_filepath2"],session["date"])

    for item in collection_val:
        if int(item["CustomerRef"]["value"]) == int(invoice_id):
            iterable_target = item["Line"]
            # print(iterable_target)

    for line in iterable_target:
        totals[0] += float(line["SalesItemLineDetail"]["Qty"])
        totals[1] += float(line["Amount"])
    print(totals)
    return render_template("preview_invoice.html",location=get_name_by_id(df_rates,int(invoice_id)),invoice=iterable_target,totals=totals)


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
