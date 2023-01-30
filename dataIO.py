from openpyxl import load_workbook
import pandas as pd
import json


def load_study_request():
    '''
    
    '''
    sheet_df = pd.read_excel("assets\\Data Request Form.xlsx", sheet_name="Study data requested",skiprows=5, usecols = "D,E,F,G,H,I,J,K,L,M,N,O,P,Q,R")
    return sheet_df


def load_linked_request():
    '''
    '''
    sheet_df = pd.read_excel("assets\\Data Request Form.xlsx", sheet_name="Linked data requested",skiprows=5, usecols = "B,C,D,E,F,G,H")
    return sheet_df


def load_study_info_and_links():
    '''
    '''
    sheet_df = pd.read_excel("assets\\Data Request Form.xlsx", sheet_name="Study info & links", skiprows=1, usecols = "B,C,D,E,F,G,H,I,J" )
    return sheet_df

def load_study_metadata(table_id):
    '''
    '''
    study = table_id.split("-")[0]
    table = table_id.split("-")[1]
    # TODO change to joined metadata file (requires preprep, splitting all into proper folders)
    values_df = pd.read_csv("metadata\\"+str(study.upper())+"\\"+table+".csv")

    return values_df

def basket_out(basket):
    basket_pd = pd.DataFrame({
        "TABLE_SCHEMA" : [item.split("-")[0] for item in basket],
        "TABLE_NAME" : [item.split("-")[1] for item in basket]
        },
        columns = ["TABLE_SCHEMA", "TABLE_NAME"]
    ) 
    basket_pd.to_csv("server_save_basket_[datetime].csv")
    return basket_pd
        

def write_json(name, content):
    with open("assets/"+name, "w") as f:
        json.dump(content, f, ensure_ascii= False)

def read_json(name):
    print("loading ",name)
    with open("assets/"+name, "r") as f:
        return json.load(f)
