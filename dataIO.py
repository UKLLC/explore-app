import pandas as pd
import json
import os
import requests

# define API key 
API_KEY = os.environ['FASTAPI_KEY']
API_BASE = "https://mms.ukllc.ac.uk/meta/api/"

def get_sources():
    url = API_BASE + "source/"
    r = requests.get(url, headers={"access-token": API_KEY})
    r.raise_for_status() 
    data = r.json()
    df = pd.DataFrame(data)
    # filter to active sources only
    df = df[df["active"] == 1]
    # convert to match old format (temp step)
    df = df.rename(columns={
        'source_type': 'Type'
    })
    return df

def get_datasets():
    url = API_BASE + "all-datasets/"
    r = requests.get(url, headers={"access-token": API_KEY})
    r.raise_for_status() 
    data = r.json()
    df = pd.DataFrame(data)
    # filter to active datasets only
    df = df[df["is_active"] == True]

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


def get_datasets_es():
    url = API_BASE + "all-datasets/"
    r = requests.get(url, headers={"access-token": API_KEY})
    r.raise_for_status() 
    data = r.json()
    df = pd.DataFrame(data)
    return df


def get_dataset_versions():
    url = API_BASE + "dataset-version/"
    r = requests.get(url, headers={"access-token": API_KEY})
    r.raise_for_status()
    data = r.json()
    df = pd.DataFrame(data)
    # columns to keep
    cols_to_keep = [
        'dataset_version_id',
        'dataset_id',
        'version_date',
        'version_num'
    ]
    df = df[cols_to_keep]
    return df


def get_variables(source = "none", table_name = "none"):
    url = API_BASE + f"variable-by-dataset/{source}/{table_name}"
    r = requests.get(url, headers={"access-token": API_KEY})
    r.raise_for_status() 
    data = r.json()
    df = pd.DataFrame(data)
    return df


def get_dataset_linkage_rate(source = "none", table_name = "none"):
    url = API_BASE + f"dataset-linkage-rate/?source_name={source}&dataset_name={table_name}"
    r = requests.get(url, headers={"access-token": API_KEY})
    r.raise_for_status() 
    data = r.json()
    df = pd.DataFrame(data)

    # drop ID columns
    cols_to_drop = [
        'dataset_id', 
        'source_id',
        'linkage_provider_id'

    ]
    df = df.drop(columns=[c for c in cols_to_drop if c in df.columns])
    # rename to match expected format
    df = df.rename(columns={
        'percentage' : 'perc',
        'dataset_name': 'table_name',
        'source_name': 'source',
        'linkage_provider': 'group'
    })

    return df


def get_source_linkage_rate(source = "none"):
    url = API_BASE + f"source-linkage-rate/?source_name={source}"
    r = requests.get(url, headers={"access-token": API_KEY})
    r.raise_for_status() 
    data = r.json()
    df = pd.DataFrame(data)

    # rename source_type -> Type
    df = df.rename(columns={
        'percentage': 'perc',
        'linkage_provider': 'group',
        'source_name': 'cohort'
    })

    return df

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
    

def get_dataset_age(source_name = "none", dataset_name = "none"):
    url = API_BASE + f"dataset-age-bw/"
    r = requests.get(url, headers={"access-token": API_KEY})
    r.raise_for_status()
    data = r.json()
    df = pd.DataFrame(data)

    # filter to latest version of each dataset
    version = get_dataset_versions()
    # keep latest version for each dataset
    version = version.sort_values(by = ["dataset_id", "version_num"], ascending = [True, False]).drop_duplicates(subset = ["dataset_id"], keep = "first")
    # merge ages with versions to act as filter for latest version
    df = pd.merge(df, version, how = "inner", on = ["dataset_version_id", "dataset_id"])
    # drop version columns
    df = df.drop(columns = ["version_date", "version_num"]) 

    if source_name == "none" and dataset_name == "none":
        return df
    elif source_name == "none":
        return df.loc[df["source_name"].str.lower() == source_name.lower()]
    elif dataset_name == "none":
        return df.loc[df["dataset_name"] == dataset_name]
    else:
        return df.loc[(df["source_name"].str.lower() == source_name.lower()) & (df["dataset_name"] == (dataset_name))]


def get_labels(table_id): 
    print("DEBUG: Load request for", table_id)
    study = table_id.split("-")[0]
    table = table_id.split("-")[1]
    url = API_BASE + f"variable-by-dataset/{study}/{table}/"
    r = requests.get(url, headers={"access-token": API_KEY})
    r.raise_for_status() 
    data = r.json()
    df = pd.DataFrame(data)
    print(df.columns)
    # remove ID columns
    cols_to_drop = [
        'index',
        'dataset_version_id',
        'dataset_id',
        'data_source_id',
        'variable_definition_id',
        'value_definition_id'
    ]
    df = df.drop(columns=[c for c in cols_to_drop if c in df.columns])
    # rename to match expected format
    df = df.rename(columns={
        "variable_name": "Variable Name",
        "variable_label": "Variable Description",
        "value": "Value",
        "value_label": "Value Description"
    })
    print(df.columns)
    if "Variable Name" in df.columns:
        df = df.sort_values(by="Variable Name", ignore_index=True)
    else:
        print("WARNING: 'Variable Name' column missing. Columns are:", df.columns)
    return df


def get_region_counts():
    url = API_BASE + f"geo-locations/"
    r = requests.get(url, headers={"access-token": API_KEY})
    r.raise_for_status() 
    data = r.json()
    df = pd.DataFrame(data)

    cols_to_drop = [
        'index',
        'data_source_id',
        'source_stem',
    ]
    df = df.drop(columns=[c for c in cols_to_drop if c in df.columns])
    # rename source_type -> Type
    df = df.rename(columns={
        'north_west': 'North West',
        'south_east': 'South East',
        'west_midlands': 'West Midlands',
        'london': 'London',
        'north_east': 'North East',
        'scotland': 'Scotland',
        'east_of_england': 'East of England',
        'east_midlands': 'East Midlands',
        'south_west': 'South West',
        'yorkshire_and_the_humber': 'Yorkshire and The Humber',
        'wales': 'Wales',
        'northern_ireland': 'Northern Ireland'
    })
    return df

# Data Request form creation
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

# read from file locations
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

