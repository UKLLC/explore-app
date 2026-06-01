# %%
from numpy import source
import pandas as pd
import json
import os
import requests

# define API key 
API_KEY = os.environ['FASTAPI_KEY']
API_BASE = "https://mms-production-3b476d9d2c44.herokuapp.com/meta/api/"

def get_region_counts():
    url = API_BASE + f"geo-locations/"
    r = requests.get(url, headers={"access-token": API_KEY})
    r.raise_for_status() 
    data = r.json()
    df = pd.DataFrame(data)
    return df

t1 = get_region_counts()
# %%


# DONE
def get_datasets():
    url = API_BASE + "all-datasets/"
    r = requests.get(url, headers={"access-token": API_KEY})
    r.raise_for_status() 
    data = r.json()
    df = pd.DataFrame(data)

    # convert to match old format (temp step)
    cols_to_drop = [
        'dataset_id',
        'data_source_id',
        'earliest_version_date'
    ]
    df = df.drop(columns=[c for c in cols_to_drop if c in df.columns])
    # rename source_type -> Type
    df = df.rename(columns={
        'source_type': 'Type'
    })

    return df


# TODO - SAM TO POPULATE dataset_linkage_rate 
# NEED TO GIVE ALEX NEW API endpoint definition 
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


# THIS DOES NOT APPEAR TO BE USED ANYWHERE - CHECK BEFORE DELETING
# def load_dataset_linkage(cnxn, source = "none", table_name = "none"):
#     rtn = pd.read_sql("SELECT * from dataset_linkage", cnxn)
#     if source == "none" and table_name == "none":
#         return rtn
#     elif source == "none":
#         return rtn.loc[rtn["source"].str.lower() == source.lower()]
#     elif table_name == "none":
#         return rtn.loc[rtn["table_name"].str.contains(table_name)]
#     else:
#         return rtn.loc[(rtn["source"].str.lower() == source.lower()) & (rtn["table_name"].str.contains(table_name))]


# NEW API ENDPOINT - DEFINED AND GIVEN TO ALEX
def load_cohort_linkage_groups(cnxn, source = "none"):
    rtn = pd.read_sql("SELECT * from cohort_linkage_by_group", cnxn)
    if source == "none":
        return rtn
    else:
        return rtn.loc[(rtn["cohort"].str.lower() == source.lower())]

# NEED NEW GRAPH TO PICK THIS UP
def get_source_linkage_rate():
    url = API_BASE + "source-linkage-rate/"
    r = requests.get(url, headers={"access-token": API_KEY})
    r.raise_for_status() 
    data = r.json()
    df = pd.DataFrame(data)
    return df


# DONE 
# def load_cohort_age(cnxn, source = "none"):
#     rtn = pd.read_sql("SELECT * from cohort_ages", cnxn)
#     if source == "none":
#         return rtn
#     else:
#         return rtn.loc[(rtn["source"].str.lower() == source.lower())]
def get_source_age(source):
    url = API_BASE + f"source-age-bw/"
    r = requests.get(url, headers={"access-token": API_KEY})
    r.raise_for_status()
    data = r.json()
    df = pd.DataFrame(data)
    if source == "none":
        return df
    else:
        return df.loc[(df["name"].str.lower() == source.lower())]
    
# DONE
# def load_dataset_age(cnxn, source = "none", table_name = "none"):
#     rtn = pd.read_sql("SELECT * from dataset_ages", cnxn)
#     if source == "none" and table_name == "none":
#         return rtn
#     elif source == "none":
#         return rtn.loc[rtn["source"].str.lower() == source.lower()]
#     elif table_name == "none":
#         return rtn.loc[rtn["table_name"] == table_name]
#     else:
#         return rtn.loc[(rtn["source"].str.lower() == source.lower()) & (rtn["table_name"] == (table_name))]

def get_dataset_age(source_name = "none", dataset_name = "none"):
    url = API_BASE + f"dataset-age-bw/"
    r = requests.get(url, headers={"access-token": API_KEY})
    r.raise_for_status()
    data = r.json()
    df = pd.DataFrame(data)

    if source_name == "none" and dataset_name == "none":
        return df
    elif source_name == "none":
        return df.loc[df["source_name"].str.lower() == source_name.lower()]
    elif dataset_name == "none":
        return df.loc[df["dataset_name"] == dataset_name]
    else:
        return df.loc[(df["source_name"].str.lower() == source_name.lower()) & (df["dataset_name"] == (dataset_name))]


# DONE
def get_sources():
    url = API_BASE + "source/"
    r = requests.get(url, headers={"access-token": API_KEY})
    r.raise_for_status() 
    data = r.json()
    df = pd.DataFrame(data)
    df = df.rename(columns={
        'source_type': 'Type'
    })
    return df

# def load_source_info(cnxn, source = "none"):
#     rtn = pd.read_sql("SELECT * from source_info", cnxn)
#     if source == "none":
#         return rtn
#     else:
#         return rtn.loc[(rtn["cohort"].str.lower() == source.lower())]
    

# THIS DOES NOT APPEAR TO BE USED ANYWHERE - CHECK BEFORE DELETING
# def load_dataset_count(cnxn, source = "none", table_name = "none"):
#     rtn = pd.read_sql("SELECT * from dataset_participants", cnxn)
#     if source == "none" and table_name == "none":
#         return rtn
#     elif source == "none":
#         return rtn.loc[rtn["source"].str.lower() == source.lower()]
#     elif table_name == "none":
#         return rtn.loc[rtn["table_name"].str.contains(table_name)]
#     else:
#         return rtn.loc[(rtn["source"].str.lower() == source.lower()) & (rtn["table_name"].str.contains(table_name))]


# THIS DOES NOT APPEAR TO BE USED ANYWHERE - CHECK BEFORE DELETING
# def load_search(cnxn, source = "none", table_name = "none"):

#     if source == "none" and table_name == "none":
#         return pd.read_sql("SELECT * from search", cnxn)
#     elif source == "none":
#         return pd.read_sql("SELECT * from search where [table] = '{}'".format(source, table_name), cnxn)
#     elif table_name == "none":
#         return pd.read_sql("SELECT * from search where [source] = '{}'".format(source, table_name), cnxn)

#     else:
#         return pd.read_sql("SELECT * from search where [source] = '{}' and [table] = '{}'".format(source, table_name), cnxn)


# THIS DOES NOT APPEAR TO BE USED ANYWHERE - CHECK BEFORE DELETING
# def load_study_request(cnxn):
#     '''
#     Data request form info
#     @depricated: should now use
#     '''
#     sheet_df = pd.read_sql("SELECT * from drf_lps", cnxn)
#     #sheet_df = pd.read_excel(os.path.join("assets", "Data Request Form.xlsx"), sheet_name="Study data requested",skiprows=5, usecols = "D,E,F,G,H,I,J,K,L,M,N,O,P,Q,R")

#     return sheet_df

# THIS DOES NOT APPEAR TO BE USED ANYWHERE - CHECK BEFORE DELETING
# def load_linked_request(cnxn):
#     '''
#     '''
#     # What do we need?
#     # Data Block Name	Data Block Description	Coverage 	Time Period†	Number of Participants Included (n=) (i.e. number of particpants with non-null data, and with UK LLC, and linkage permission)"	Documentation 	Codelist Required	Health Domain Groupings (i.e. covid infection, asthma, smoking, etc.) 	Justification of dataset request

#     #sheet_df = pd.read_excel(os.path.join("assets", "Data Request Form.xlsx"), sheet_name="Linked data requested",skiprows=5, usecols = "A,B,C,D,E,F,G,H")
#     #sheet_df = sheet_df.rename(columns = {"Data Block Name":"Block Name", "Data Block Description":"Block Description", "Time Period†":"Timepoint: Data Collected", "'Health Domain Groupings (i.e. covid infection, asthma, smoking, etc.)":"Keywords"})
#     #sheet_df["Source"] = "NHSD"
#     sheet_df = pd.read_sql("SELECT * from drf_nhs", cnxn)

#     return sheet_df

# THIS DOES NOT APPEAR TO BE USED ANYWHERE - CHECK BEFORE DELETING
# def load_study_info_and_links(cnxn):
#     '''
#     '''
#     #TODO Convert to database
#     #sheet_df = pd.read_excel(os.path.join("assets", "Data Request Form.xlsx"), sheet_name="Study info & links", skiprows=1, usecols = "B,C,D,E,F,G,H,I,J" )
#     sheet_df = pd.read_sql("SELECT * from study_info", cnxn)
#     return sheet_df

# USE EXISTING ENDPOINTS variable-by-dataset 

# def load_study_metadata(cnxn, table_id):
#     '''
#     '''
#     print("DEBUG: Load request for", table_id)
#     study = table_id.split("-")[0]
#     table = table_id.split("-")[1]
#     # TODO change to joined metadata file (requires preprep, splitting all into proper folders)
#     try:
#         q = '''
#         SELECT * FROM metadata_{}
#         ORDER BY "Block Name", "Variable Name"
#         '''.format(study.lower()+"_"+table.lower())
#         values_df = pd.read_sql(q, cnxn)
#     except FileNotFoundError:
#         print("Couldn't find file {}. Skipping (shouldn't be a problem when we have a db...".format(str(study.upper())+table+".csv"))
#         return None

#     return values_df

# DONE
def get_labels(table_id): 
    print("DEBUG: Load request for", table_id)
    study = table_id.split("-")[0]
    table = table_id.split("-")[1]
    url = API_BASE + f"variable-by-dataset/{study}/{table}/"
    r = requests.get(url, headers={"access-token": API_KEY})
    r.raise_for_status() 
    data = r.json()
    df = pd.DataFrame(data)
    # remove ID columns
    cols_to_drop = [
        'index',
        'dataset_version_id',
        'dataset_id',
        'data_source_id'
    ]
    df = df.drop(columns=[c for c in cols_to_drop if c in df.columns])
    # rename to match expected format
    df = df.rename(columns={
        "variable_name": "Variable Name",
        "variable_label": "Variable Description",
        "value": "Value",
        "value_label": "Value Description"
    })
    if "Variable Name" in df.columns:
        df = df.sort_values(by="Variable Name", ignore_index=True)
    else:
        print("WARNING: 'Variable Name' column missing. Columns are:", df.columns)
    return df


def load_map_data(cnxn):
    return pd.read_sql("SELECT * from geo_locations", cnxn)

# AWAITING SAM TO FEED DATA INTO REGION COUNTS TABLE  
def get_region_counts():
    url = API_BASE + f"geo-locations/"
    r = requests.get(url, headers={"access-token": API_KEY})
    r.raise_for_status() 
    data = r.json()
    df = pd.DataFrame(data)
    return df

t1 = 



# AUTO PROVISIONING - DEPRICATED - CHECK BEFORE DELETING
#def load_always_provisioned(cnxn):
#    df = pd.read_sql("SELECT * from always_provisioned", cnxn)
#    return df


def basket_out(basket, datasets_df):

    basket_pd = pd.DataFrame({
        "TABLE_SCHEMA" : [item.split("-")[0] for item in basket],
        "TABLE_NAME" : [item.split("-")[1] for item in basket]
        },
        columns = ["TABLE_SCHEMA", "TABLE_NAME"]
    )

    # SN: added full table name and table type 160925
    basket_pd = basket_pd.merge(
        datasets_df,
        left_on=["TABLE_SCHEMA", "TABLE_NAME"],
        right_on=["source", "table"],
        how="left")[
            ["TABLE_SCHEMA",
             "TABLE_NAME",
             "table_name",
             "Type"]].rename(
                 columns={"table_name": "FULL_TABLE_NAME",
                          "Type": "TABLE_TYPE"})

    basket_pd.to_csv("server_save_basket_[datetime].csv", index=False)
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

def load_geojson():
    with open(os.path.join("assets","map overlays","regions.geojson"), 'r') as f:
        gj = json.load(f)
    return gj

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


# %%
