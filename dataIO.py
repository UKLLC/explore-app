import pandas as pd
import json
import os


def load_blocks(cnxn):
    return pd.read_sql("SELECT * from dataset", cnxn)


def load_dataset_linkage_groups(cnxn, source = "none", table_name = "none"):
    rtn = pd.read_sql("SELECT * from dataset_linkage_by_group", cnxn)
    if source == "none" and table_name == "none":
        return rtn
    elif source == "none":
        return rtn.loc[rtn["source"].str.lower() == source.lower()]
    elif table_name == "none":
        return rtn.loc[rtn["table_name"].str.contains(table_name)]
    else:
        return rtn.loc[(rtn["source"].str.lower() == source.lower()) & (rtn["table_name"].str.contains(table_name))]

def load_dataset_linkage(cnxn, source = "none", table_name = "none"):
    rtn = pd.read_sql("SELECT * from dataset_linkage", cnxn)
    if source == "none" and table_name == "none":
        return rtn
    elif source == "none":
        return rtn.loc[rtn["source"].str.lower() == source.lower()]
    elif table_name == "none":
        return rtn.loc[rtn["table_name"].str.contains(table_name)]
    else:
        return rtn.loc[(rtn["source"].str.lower() == source.lower()) & (rtn["table_name"].str.contains(table_name))]


def load_cohort_linkage_groups(cnxn, source = "none"):
    rtn = pd.read_sql("SELECT * from cohort_linkage_by_group", cnxn)
    if source == "none":
        return rtn
    else:
        return rtn.loc[(rtn["cohort"].str.lower() == source.lower())]

def load_cohort_linkage(cnxn, source = "none"):
    rtn = pd.read_sql("SELECT * from cohort_linkage", cnxn)
    if source == "none":
        return rtn
    else:
        return rtn.loc[(rtn["cohort"].str.lower() == source.lower())]


def load_cohort_age(cnxn, source = "none"):
    rtn = pd.read_sql("SELECT * from cohort_ages", cnxn)
    if source == "none":
        return rtn
    else:
        return rtn.loc[(rtn["source"].str.lower() == source.lower())]

def load_dataset_age(cnxn, source = "none", table_name = "none"):
    rtn = pd.read_sql("SELECT * from dataset_ages", cnxn)
    if source == "none" and table_name == "none":
        return rtn
    elif source == "none":
        return rtn.loc[rtn["source"].str.lower() == source.lower()]
    elif table_name == "none":
        return rtn.loc[rtn["table_name"].str.contains(table_name)]
    else:
        return rtn.loc[(rtn["source"].str.lower() == source.lower()) & (rtn["table_name"].str.contains(table_name))]

def load_source_info(cnxn, source = "none"):
    rtn = pd.read_sql("SELECT * from source_info", cnxn)
    if source == "none":
        return rtn
    else:
        return rtn.loc[(rtn["cohort"].str.lower() == source.lower())]
    
def load_dataset_count(cnxn, source = "none", table_name = "none"):
    rtn = pd.read_sql("SELECT * from dataset_participants", cnxn)
    if source == "none" and table_name == "none":
        return rtn
    elif source == "none":
        return rtn.loc[rtn["source"].str.lower() == source.lower()]
    elif table_name == "none":
        return rtn.loc[rtn["table_name"].str.contains(table_name)]
    else:
        return rtn.loc[(rtn["source"].str.lower() == source.lower()) & (rtn["table_name"].str.contains(table_name))]


def load_study_request(cnxn):
    '''
    Data request form info
    @depricated: should now use 
    '''
    sheet_df = pd.read_sql("SELECT * from drf_lps", cnxn)
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
    sheet_df = pd.read_sql("SELECT * from drf_nhs", cnxn)

    return sheet_df


def load_study_info_and_links(cnxn):
    '''
    '''
    #TODO Convert to database
    #sheet_df = pd.read_excel(os.path.join("assets", "Data Request Form.xlsx"), sheet_name="Study info & links", skiprows=1, usecols = "B,C,D,E,F,G,H,I,J" )
    sheet_df = pd.read_sql("SELECT * from study_info", cnxn)
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
        values_df = pd.read_sql("SELECT * from {}".format(study.lower()+"_"+table.lower()), cnxn) 
    except FileNotFoundError:
        print("Couldn't find file {}. Skipping (shouldn't be a problem when we have a db...".format(str(study.upper())+table+".csv"))
        return None
    
    return values_df

def load_spine(cnxn):
    return pd.read_sql("SELECT * from spine", cnxn)

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

'''
spine: 
Minimum info required for searching. Source & dataset.

dataset_counts:
Source name + number of datasets within 
(made redundant by...)

study_participants
source + participant count

dataset_participants:
source + dataset + participant count

dataset_Ages:
source + dataset + age stats

cohort_linkage:
cohort + col per linked source

cohort_linkage_by_groups:
cohort + col per possible linked source combo

dataset_linkage:
source + dataset + col per linked source

dataset_linkage_by_groups:
source + dataset + col per possible linked source combo

cohort_ages:
source + age stats

nhs_dataset_cohort_linkage:
dataset + cohort + count

nhs_dataset_extracts:
dataset + date + count

source_info:
full info for sources
'''