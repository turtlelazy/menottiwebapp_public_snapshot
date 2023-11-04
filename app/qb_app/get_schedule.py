# import pandas lib as pd
from cmath import nan
import json
from numpy import NaN
import pandas as pd
from qb_app.get_rates import *

file = "sandbox.csv"

weekdays = ["Saturday","Sunday","Monday","Tuesday","Wednesday","Thursday","Friday"]
weekdays_date = {} #day corresponding to date goes here

for day in weekdays:
    weekdays_date[day] = day

def print_cols(df):
    for col in df.columns:
        print(col)


def convert_to_decimal(hour_entry: str) -> float:
    hour_entry = hour_entry.replace(" ", "")
    hour_entry = hour_entry.replace("\xa0", "")
    index = hour_entry.find(":")
    hours = int(hour_entry[0:index])
    minutes = float(hour_entry[index+1:])
    time = hours + minutes/60.0
    #print(hour_entry +" --> " + str(time))
    return time

# read by default 1st sheet of an excel file
weekendHeader = ["Location", "Client", "Role", "Employee", "Start", "End",
             "OT", "Time Verified", "Labor Costs", "Shift Price", "Profit Per Shift"]

def days(csv_file):

    saturday = pd.read_csv(csv_file,skiprows=2)
    saturday = saturday.drop(columns = saturday.columns[15:], axis=1)
    saturday = saturday.drop(columns=saturday.columns[2:6], axis=1)
    saturday.columns = weekendHeader

    weekendHeader[6] = "DT"

    sunday = pd.read_csv(csv_file, skiprows=2)
    sunday = sunday.drop(columns=sunday.columns[24:], axis=1)
    sunday = sunday.drop(columns=sunday.columns[2:15], axis=1)
    sunday.columns = weekendHeader

    weekdayHeader = ["Location", "Client", "Role", "Employee", "Start", "End", "RT",
                    "OT", "Time Verified", "Labor Costs", "Shift Price", "Profit Per Shift"]

    monday = pd.read_csv(csv_file, skiprows=2)
    monday = monday.drop(columns=monday.columns[34:], axis=1)
    monday = monday.drop(columns=monday.columns[2:24], axis=1)
    monday.columns = weekdayHeader

    tuesday = pd.read_csv(csv_file, skiprows=2)
    tuesday = tuesday.drop(columns=tuesday.columns[44:], axis=1)
    tuesday = tuesday.drop(columns=tuesday.columns[2:34], axis=1)
    tuesday.columns = weekdayHeader

    wednesday = pd.read_csv(csv_file, skiprows=2)
    wednesday = wednesday.drop(columns=wednesday.columns[54:], axis=1)
    wednesday = wednesday.drop(columns=wednesday.columns[2:44], axis=1)
    wednesday.columns = weekdayHeader

    thursday = pd.read_csv(csv_file, skiprows=2)
    thursday = thursday.drop(columns=thursday.columns[64:], axis=1)
    thursday = thursday.drop(columns=thursday.columns[2:54], axis=1)
    thursday.columns = weekdayHeader

    friday = pd.read_csv(csv_file, skiprows=2)
    friday = friday.drop(columns=friday.columns[74:], axis=1)
    friday = friday.drop(columns=friday.columns[2:64], axis=1)
    friday.columns = weekdayHeader

    return [saturday,sunday,monday,tuesday,wednesday,thursday,friday]


# for row in friday["RT"]:

#     if (pd.notnull(row)):
#         row = row.replace(" ","")
#         row = row.replace("\xa0", "")

#         if(row != "0:0"):
#             print(convert_to_decimal(row))

rates = ["RT", "OT", "DT"]
def line_formatted(row):
    location = row["Location"]
    client = row["Client"]
    role = row["Role"]
    rates_hours = {"RT": 0, "OT": 0, "DT": 0}
    subtract = True
    for rate in rates:
        if rate in row:
            rates_hours[rate] = convert_to_decimal(
                row[rate]) if not pd.isnull(row[rate]) else 0.0
            if subtract and rates_hours[rate] > 5:
                subtract = False
                rates_hours[rate] = rates_hours[rate] - 0.5 
    return {"Location":location,"Client":client,"Role":role,"Hours":rates_hours}

def day_values(day_df: pd.DataFrame) -> list:
    return_list = []
    for i in range(len(day_df)):
        row = day_df.iloc[i]
        if not pd.isnull(row["Location"]):
            return_list.append(line_formatted(row))
    return return_list

def compiled_data(libraries: dict):
    existing_companies = []
    company_header = ["Location","Client"]

    compiled = {}

    for day in libraries.keys():
        day_data = libraries[day]
        for line in day_data:
            #print(line["Location"],line["Client"])
            lplusc = line["Location"]

            if pd.isnull(line["Client"]):
                line["Client"] = ""
            else:
                lplusc += " " + line["Client"]
    
            if [line["Location"],line["Client"]] not in existing_companies:
                #print(line["Location"],line["Client"])
                compiled[lplusc] = []
                existing_companies.append([line["Location"], line["Client"]])

            for rate in rates:
                if line["Hours"][rate] != 0:
                    compiled[lplusc].append({
                        "Date":weekdays_date[day],"Role": line["Role"], "Rate": rate, "Hours": line["Hours"][rate]
                    })
    return compiled

def compiled_days(days):
    libraries = {
        "Saturday":day_values(days[0]),
        "Sunday": day_values(days[1]),
        "Monday": day_values(days[2]),
        "Tuesday": day_values(days[3]),
        "Wednesday": day_values(days[4]),
        "Thursday": day_values(days[5]),
        "Friday": day_values(days[6]),
    }
    compiled = compiled_data(libraries)
    return compiled

if __name__ == "__main__":
    compiled = compiled_days(days(file))
    print(json.dumps(compiled, indent=4))
