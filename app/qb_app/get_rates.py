import pandas as pd
import json


headers = [
    "Location Client Service(Automatic, Do not Edit)", 
    "Location", "Client", "Service", "R", "OT", "DT", 
    "Billing", "ID"]

#print(rates)

def get_row_by_name(df:pd.DataFrame,name) -> pd.Series:
    #return df[(df['Location'] + " " + df['Client']) == name].iloc[0]
    return df[df['Location Client Service(Automatic, Do not Edit)'].str.contains(name)].iloc[0]


def get_row_by_id(df: pd.DataFrame, ID) -> pd.Series:
    return df[df['ID'] == ID].iloc[0]


def get_id_by_name(df,name):
    #return get_row_by_name(df, name)["ID"]
    try:
        if (pd.isna(get_row_by_name(df, name)["ID"])):
            return ""
        return get_row_by_name(df,name)["ID"]
    except:
        return ""


def get_name_by_id(df, name):
    #return get_row_by_name(df, name)["ID"]
    try:
        if (pd.isna(get_row_by_id(df, name)["Location"])):
            return ""
        return get_row_by_id(df, name)["Location"]
    except:
        return ""

rates_header = {"RT","OT","DT"}

def get_billing_type(df,name=None,id=None) -> str:
    row = {}

    if id is not None:
        row = get_row_by_id(df, id)
    elif name is not None:
        row = get_row_by_name(df, name)

    return row["Billing"]



def get_rate(df,name=None,id=None,role=None) -> dict:
    row = {}
    try:
        if id is not None:
            row = df[(df['ID'] == id) & (df['Service'] == role)].iloc[0]
        elif name is not None:
            row = get_row_by_name(df, name)
    except:
        row = df[df['ID'] == id].iloc[0]

    dictionary = {}
    for rate in rates_header:
        dictionary[rate] = row[rate]
    return dictionary

def get_email_by_id(df, name):
    #return get_row_by_name(df, name)["ID"]
    try:
        if (pd.isna(get_row_by_id(df, name)["Email"])):
            return ""
        return get_row_by_id(df, name)["Email"]
    except:
        return ""

# def format_emails(df,ID):
#     emails = get_email_by_id(df,ID)
#     main_emails = ""
#     if emails:
#         emails_list = emails.split(",")
#         for email in emails_list:
#             if len(main_emails) + len(email) <= 80:

#     return []

if __name__ == "__main__":
    rates = pd.read_csv("temp_rates.csv")
    ids_list = [1832, 1691, 1526, 1697, 1540]
    for ID in ids_list:
        x = get_email_by_id(rates,ID)
        if(x):
            print(get_email_by_id(rates,ID))
        else:
            print(f"{ID} has no emails")
#print(get_row_by_name (rates, "asdsadas"))
#print(get_id_by_name(rates, "aaaa"))
# print(get_rates(rates, name="Cool Cars"))
# print(get_rates(rates, id=1))
# print(get_billing_type(rates,name="Cool Cars"))
# print(get_billing_type(rates, id=2))

# def row_to_dict(row) -> dict:
#     return_dict = {}
#     for head in headers:
#         return_dict[head] = row[head]