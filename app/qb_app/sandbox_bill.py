#from invoicing import *
from qb_app.get_rates import *
from qb_app.get_schedule import *
import datetime
import pandas as pd

def invoices_collection(rates_csv,schedule):
    invoice_collection = {}
    rates = pd.read_csv(rates_csv)
    compiled = compiled_days(days(schedule))
    #print(compiled)
    for location in compiled.keys():
        location_invoices : list = compiled[location]
        #print(location_invoices)
        
        id = get_id_by_name(rates, location)
        #print(location, id)
        #print(repr(location))
        if id == "":
            #print("NO ID??")
            continue
        id = int(id)
        if get_billing_type(rates,id=id)!="Rate":
            continue

        invoice_collection[id]  = []
        for invoice in location_invoices:
            #print(details)
            details = invoice
            
            details["RateVal"] = get_rate(rates, id=id,role=details["Role"])[details["Rate"]]
            # if id == 1691:
            #     print("WABAJACK HEHEHEHE")
            #     print(get_rate(rates, id=id,role=details["Role"]))
            #     print(details["Role"])
                
            if type(details["RateVal"]) == str:
                details["RateVal"] = float(details["RateVal"].replace("$",""))
            else:
                details["RateVal"] = float(details["RateVal"])
            details["Total"] = details["RateVal"] * details["Hours"]
            details["Billing"] = get_billing_type(rates, id=id)
            invoice_collection[id].append(details)
        if invoice_collection[id] == []:
            del invoice_collection[id]
    return invoice_collection

#print(invoice_collection)
#print(json.dumps(invoice_collection, indent=4))


def return_date(year: int, month: int, day: int, weekday: str):
    weekdays = {"Saturday": 0,
                "Sunday": 1,
                "Monday":2,
                "Tuesday":3,
                "Wednesday":4,
                "Thursday":5,
                "Friday":6}
    date = datetime.datetime(year, month, day)
    new_date = date + datetime.timedelta(days=weekdays[weekday])
    # if new_date.day < 10:
    #     return f'{new_date.year}/{new_date.month}/0{new_date.day}'
    return f'{new_date.year}/{new_date.month if new_date.month >= 10 else f"0{new_date.month}"}/{new_date.day if new_date.day >= 10 else f"0{new_date.day}"}'


def line_to_format(input_line, year: int, month: int, day: int):
    role_descriptions = {
        "SSM": "Site safety management",
        "FSM": "Fire safety management",
        "QSP":"QSP",
        "Super":"Superintendent",
        "CSM" : "Concrete safety management",
        "Laborer" : "On-site staffing",
        "SSC":"Site safety coordinator",
        "Flagger":"Flagger",
        "Fire Guard" : "Fire Guard"
    }

    rate_descriptions = {
        "RT":"regular time rate",
        "OT":"over time rate",
        "DT":"double time rate"
    }

    service_ids = {
        "SSM": {
            "name": "Site Safety Management",
            "value": 174
        },
        "FSM": {
            "name": "Fire Safety Management",
            "value": 12
        },
        "QSP":{
            "name": "Qualified Safety Person (QSP)",
            "value": 199
        },
        "Super":{
            "name": "Full Time Superintendent",
            "value": 74
        },
        "CSM" : {
            "name": "Concrete Safety Management",
            "value": 66
        },
        "Laborer" : {
            "name": "On-Site Staffing",
            "value": 230
        },
        "SSC" : {
            "name": "Full Time Site & Fire Safety Coverage",
            "value": 26 
        },
        "Flagger" :{
            "name":"N/a",
            "value":26
        },
        "Fire Guard" :{
            "name":"Fire Guard",
            "value":32
        }

    }

    line = {}
    has_all = True
    for item in input_line:
        if pd.isna(input_line[item]):
            print(input_line)
            has_all = False
    
    if has_all:
        line["DetailType"] = "SalesItemLineDetail"
        line["Amount"] = input_line["Total"]
        line["SalesItemLineDetail"] = {"Qty": input_line["Hours"],
                                    "UnitPrice": input_line["RateVal"],
                                    "ServiceDate": return_date(year,month,day,input_line["Date"])} #replace service date with date based on first day
        # replace description with stuff that needs to go there
        #print(input_line)
        line["Description"] = f'{role_descriptions[input_line["Role"]]} work at {rate_descriptions[input_line["Rate"]]}'
        
        line["SalesItemLineDetail"]["ItemRef"] = service_ids[input_line["Role"]]
    return line


def invoice_to_JSON(invoice, id, year: int, month: int, day: int):
    JSON = {"CustomerRef": {"value": id}}
    lines = []

    for line in invoice:
        if line != {} and line_to_format(line,year,month,day) != {}:
            lines.append(line_to_format(line,year,month,day))

    JSON["Line"] = lines

    return JSON


def invoice_collection_to_JSON(invoice_collection: dict, year: int, month: int, day: int):
    total_collection = []
    for invoice in invoice_collection.keys():
        # try:
        if invoice_collection[invoice][0]["Billing"] == "Rate":
            invoice_JSON = invoice_to_JSON(invoice_collection[invoice], invoice,year,month,day)
            total_collection.append(invoice_JSON)
        # except Exception as error:
        #     print(f"problem with invoice {invoice}")
        #     print("An exception occurred:", error) # An exception occurred: division by zero

    
    return total_collection



# year = int(input("What year is the first day on?"))
# month = int(input("What month (number) is the first day on?"))
# day = int(input("What day (number) is the first day on?"))
if __name__ == "__main__":
    year = 2023
    month = 8
    day = 19
    invoice_collection = invoices_collection("temp_rates.csv","temp_schedule.csv")
    invoices_JSON = invoice_collection_to_JSON(invoice_collection,year,month,day)
    print(json.dumps(invoice_collection,indent=4))
    for company in invoice_collection.keys():
        curr_invoice = invoice_collection[company]
        total = 0
        for shift in curr_invoice:
            total += shift["Total"]
        rates_stuffs = pd.read_csv("temp_rates.csv")
        print(f"{get_name_by_id(rates_stuffs,company)} : {total}")
#print(json.dumps(invoice_collection,indent=4))