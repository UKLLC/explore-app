from openpyxl import load_workbook
import pandas as pd
import json
import os
import sqlalchemy


def connect():
    # need to swap password for local var
    cnxn = sqlalchemy.create_engine('mysql+pymysql://bq21582:password_password@127.0.0.1:3306/ukllc')
    return(cnxn)


def load_blocks(cnxn):
    return pd.read_sql("SELECT * from ukllc.dataset", cnxn)

def load_sources(cnxn):
    return pd.read_sql("SELECT * from ukllc.datasource", cnxn)


def load_study_request(cnxn):
    '''
    '''
    sheet_df = pd.read_sql("SELECT * from ukllc.drf_lps", cnxn)
    #sheet_df = pd.read_excel(os.path.join("assets", "Data Request Form.xlsx"), sheet_name="Study data requested",skiprows=5, usecols = "D,E,F,G,H,I,J,K,L,M,N,O,P,Q,R")
    
    return sheet_df


def load_linked_request(cnxn):
    '''
    '''
    # What do we need?
    # Data Block Name	Data Block Description	Coverage 	Time Period†	Number of Participants Included (n=) (i.e. number of particpants with non-null data, and with UK LLC, and linkage permission)"	Documentation 	Codelist Required	Health Domain Groupings (i.e. covid infection, asthma, smoking, etc.) 	Justification of dataset request
    
    #sheet_df = pd.read_excel(os.path.join("assets", "Data Request Form.xlsx"), sheet_name="Linked data requested",skiprows=5, usecols = "A,B,C,D,E,F,G,H")
    #sheet_df = sheet_df.rename(columns = {"Data Block Name":"Block Name", "Data Block Description":"Block Description", "Time Period†":"Timepoint: Data Collected", "'Health Domain Groupings (i.e. covid infection, asthma, smoking, etc.)":"Keywords"})
    #sheet_df["Source"] = "NHSD"
    sheet_df = pd.read_sql("SELECT * from ukllc.drf_nhs", cnxn)

    return sheet_df


def load_study_info_and_links(cnxn):
    '''
    '''
    #TODO Convert to database
    #sheet_df = pd.read_excel(os.path.join("assets", "Data Request Form.xlsx"), sheet_name="Study info & links", skiprows=1, usecols = "B,C,D,E,F,G,H,I,J" )
    sheet_df = pd.read_sql("SELECT * from ukllc.study_info", cnxn)
    return sheet_df

def load_study_metadata(cnxn, table_id):
    '''
    '''
    print("DEBUG: Load request for", table_id)
    study = table_id.split("-")[0]
    table = table_id.split("-")[1]
    # TODO change to joined metadata file (requires preprep, splitting all into proper folders)
    try:
        #values_df = pd.read_csv(os.path.join("metadata",str(study.upper()),table+".csv"))
        values_df = pd.read_sql("SELECT * from ukllc.{}".format(study.lower()+"_"+table.lower()), cnxn) 
    except FileNotFoundError:
        print("Couldn't find file {}. Skipping (shouldn't be a problem when we have a db...".format(str(study.upper())+table+".csv"))
        return None
    
    return values_df

def basket_out(basket):
    basket_pd = pd.DataFrame({
        "TABLE_SCHEMA" : [item.split("-")[0] for item in basket],
        "TABLE_NAME" : [item.split("-")[1] for item in basket]
        },
        columns = ["TABLE_SCHEMA", "TABLE_NAME"]
    ) 
    basket_pd.to_csv("server_save_basket_[datetime].csv", index = False)
    return basket_pd
        

def write_json(name, content):
    with open(os.path.join("assets",name), "w") as f:
        json.dump(content, f, ensure_ascii= False)

def read_json(name):
    print("loading ",name)
    with open(os.path.join("assets",name), "r") as f:
        return json.load(f)

def get_map_overlays(study):
    with open(os.path.join("assets","map overlays",study+".geojson"), 'r') as f:
        returned_data = json.load(f)
    return returned_data

