from fileinput import filename
import pandas
from quickbooks.objects.customer import Customer
from intuitlib.client import AuthClient
from intuitlib.enums import Scopes
from quickbooks import QuickBooks
from quickbooks.objects import Invoice
import requests
import json
from qb_app.get_rates import get_name_by_id, get_row_by_id, get_email_by_id
from qb_app.sandbox_bill import *
# from qb_app.sandbox_bill import invoices_collection, invoice_collection_to_JSON
from keys import auth_client

def report_log(file_name, message):
    with open(file_name, 'a') as f:
        f.write(message)


def weekly_ids():
    filename = "weekly"

    with open(filename) as file:
        lines = [int(line.rstrip()) for line in file]
        return lines

def invoice(auth_client, JSON):
    base_url = 'https://sandbox-quickbooks.api.intuit.com'

    if(auth_client.environment == "production"):
        base_url = "https://quickbooks.api.intuit.com"
    # url = '{0}/v3/company/{1}/invoice/{1}'.format(
    #     base_url, auth_client.realm_id)

    url = '{0}/v3/company/1236962145/invoice?minorversion=65'.format(
        base_url)

    auth_header = 'Bearer {0}'.format(auth_client.access_token)
    headers = {
        'Authorization': auth_header,
        'Accept': 'application/json'
    }
    response = requests.post(url, headers=headers, json=JSON)
    #(response)
    json_object = json.loads(response.text)
    json_formatted_str = json.dumps(json_object, indent=4)
    #print(json_formatted_str)
    #print(json_formatted_str)
    #print(json_object["Invoice"]["DocNumber"])

    try:
        msg = str(json_object["Invoice"]["DocNumber"]) + " : " + str(json_object["Invoice"]["CustomerRef"]["name"])
        print(msg)
        report_log("invoice_logs.txt", str(JSON["CustomerRef"]["value"]) +  " : " + str(json_formatted_str) + "\n")

        # report_log("invoice_logs.txt",
        #            str(JSON["CustomerRef"]["value"]) + " : " + json_formatted_str + "\n")
        return json_object["Invoice"]["DocNumber"]

    except:
        print("failed")
        report_log("invoice_logs.txt", str(JSON["CustomerRef"]["value"]) +  " : " + str(json_formatted_str) + "\n")
        #print(json_formatted_str)


def get_url():
    return auth_client.get_authorization_url([Scopes.ACCOUNTING])

def set_auth(auth_code,realm_id):
    auth_client.get_bearer_token(auth_code, realm_id=realm_id)

def run_script(auth_code, realm_id,year,month,day,csv_rates,schedule,weekly_id=None):
    starting_invoice_num = 20592
    auth_client.get_bearer_token(auth_code, realm_id=realm_id)
    state = auth_client.state_token

    invoice_collection = invoices_collection(csv_rates,schedule) #collect invoices
    #print(invoice_collection)
    invoices_JSON = invoice_collection_to_JSON( #get the json of the invoices
        invoice_collection, year, month, day)
    
    #print(json.dumps(invoices_JSON, indent=2))
    if not weekly_id:
        weekly_id = weekly_ids()
    
    for invoice_JSON in invoices_JSON:
        
        #print(invoice_JSON)
        # try:
        #     invoice(auth_client,invoice_JSON)
        # except:
        #     print("Something weird happened at this invoice")
        #     print(invoice_JSON)
        #     return
        temp_rates = pandas.read_csv("temp_rates.csv")
        if int(invoice_JSON["CustomerRef"]["value"]) in weekly_id:
            location = get_name_by_id(
                temp_rates, invoice_JSON["CustomerRef"]["value"])
            #proceed = input(f"Would you like to continue with billing for {location} ({invoice_JSON['CustomerRef']['value']})? (enter 'y' to proceed)")
            proceed = "y"
            if proceed == "y":
                #print(invoice_JSON)
                invoice_JSON["DocNumber"] = starting_invoice_num + 1
                invoice_JSON["BillEmail"] = {"Address" : get_email_by_id(temp_rates,invoice_JSON["CustomerRef"]["value"])}
                starting_invoice_num += 1
                invoice(auth_client,invoice_JSON)

        #break

    #print(json_formatted_str)

if __name__ == "__main__":
    url = auth_client.get_authorization_url([Scopes.ACCOUNTING])
    print(url)

    auth_code = input("Auth code")
    realm_id = input("realm id")

    #auth_client.get_bearer_token(auth_code, realm_id=realm_id)
    year = 2022
    month = 1
    day = 1
    state = auth_client.state_token
    # invoice_collection = invoices_collection("sand_rates.csv")
    # invoices_JSON = invoice_collection_to_JSON(
    #     invoice_collection, year, month, day)
    
    # for invoice_JSON in invoices_JSON:
    #     invoice(auth_client,invoice_JSON)

    run_script(auth_code, realm_id, 2023, 10, 21,
               "temp_rates.csv", "temp_schedule.csv")
