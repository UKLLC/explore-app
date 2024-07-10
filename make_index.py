import os.path
import codecs
import pandas as pd
import sqlalchemy
import time
from datetime import datetime
import json

from elasticsearch import Elasticsearch
from elasticsearch.exceptions import RequestError
from urllib.parse import urlparse


def connect():
    try:
        #cnxn = sqlalchemy.create_engine('mysql+pymysql://bq21582:password_password@127.0.0.1:3306/ukllc').connect()
        cnxn = sqlalchemy.create_engine('postgresql+psycopg2://***REMOVED***')

        return cnxn

    except Exception as e:
        print("Connection to database failed, retrying.")
        raise Exception("DB connection failed")

def searchbox_connect():
    
    url = urlparse("https://paas:***REMOVED***")

    print(url.username, url.password)
    ######## test
    es = Elasticsearch(
        ["https://paas:***REMOVED***"],
        http_auth=(url.username, url.password),
        scheme=url.scheme,
        port=url.port,
    )
    return es

def main():
    '''
    '''
    cnxn = connect()
    data = pd.read_sql("SELECT * from search", cnxn)
    print(data.columns)
    print(len(data))

    data["lf"] = data["lf"].fillna("0")
    data["uf"] = data["uf"].fillna("100")
    data["q2"] = data["q2"].fillna("50")
    data["variable_name"] = data["variable_name"].fillna(" ")
    data["variable_description"] = data["variable_description"].fillna(" ")
    data["value"] = data["value"].fillna(" ")
    data["value_label"] = data["value_label"].fillna(" ")
    data["collection_start"] = data["collection_start"].fillna("01/1900")
    data["collection_end"] = data["collection_end"].fillna(datetime.now().strftime('%m/%Y'))
    data["collection_start"] = data["collection_start"].str.replace("ongoing", datetime.now().strftime('%m/%Y'))
    data["collection_end"] = data["collection_end"].str.replace("ongoing", datetime.now().strftime('%m/%Y'))
    data["source_name"] = data["source_name"].fillna(" ")
    data["Aims"] = data["Aims"].fillna(" ")
    data["Themes"] = data["Themes"].fillna(" ")
    data["table_name"] = data["table_name"].fillna(" ")


    try:
        print("Running Spine")
        spine(data)
    except RequestError as err:
        print("failed to write to spine", err)
    
    try:
        print("Running var")
        variable(data)
    except RequestError as err:
        print("failed to write to variable", err)

    print("Finished")

def variable(data):

    with open("var_index_name.json", "r") as f:
        previous_index_name = json.load(f)["name"]
    print("Previous var name:\n",previous_index_name)

    mapping = {
        "mappings" : {
            "properties" : {
                "source" : {"type" : "keyword"},
                "source_name" : {"type" : "text"},
                "table" : {"type" : "text"},
                "table_name" : {"type" : "text"},
                "variable_name" : {"type" : "keyword"},
                "variable_description" : {"type" : "text"},
                "value" : {"type" : "text"},
                "value_label" : {"type" : "text"},
                #"long_desc" : {"type" : "text"},
                "topic_tags" : {"type" : "keyword"},
                #"Aims" : {"type" : "text"},
                "Themes" : {"type" : "keyword"},
                "Type" : {"type" : "keyword"},
                #"collection_duration" : {"type" : "date_range",  "format" : "MM/yyyy"},
                #"age_range" : {"type" : "float_range"},
                "collection_start" : {"type" : "date", "format" : "MM/YYYY", "null_value": "NULL" },
                "collection_end" : {"type" : "date",  "format" : "MM/YYYY", "null_value": "NULL" },
                "lf" : {"type" : "double"},
                "q2" : {"type" : "double"},
                "uf" : {"type" : "double"},
            }
        }
    }
    index_name = "var_"+datetime.now().strftime("%Y%m%d_%H%M%S")

    es = searchbox_connect()
    es.indices.create(index = index_name, body = mapping)
    for doc in data.loc[~data["variable_name"].isna()].to_dict("records"):
        #doc["collection_duration"] = {"gte" : doc["collection_start"], "lte": doc["collection_end"]}
        #doc["age_range"] = {"gte" : doc["lf"], "lte": doc["uf"]}
        if doc["topic_tags"]:
            doc["topic_tags"] = doc["topic_tags"].split(",")
        if doc["Themes"]:
            doc["Themes"] = doc["Themes"].split(",")
        es.index(index = index_name, body = doc)
    print("Writing to var alias")
    es.indices.put_alias(index = index_name, name = "index_var")
    
    with open("var_index_name.json", "w") as f:
        json.dump({"name":index_name}, f)

    print("Deleting",previous_index_name)
    es.indices.delete(index = previous_index_name)


def spine(data):
    es = searchbox_connect()

    with open("spine_index_name.json", "r") as f:
        previous_index_name = json.load(f)["name"]
    print("Previous spine name:\n",previous_index_name)
    
    mapping = {
        "mappings" : {
            "properties" : {
                "source" : {"type" : "keyword"},
                "source_name" : {"type" : "text"},
                "table" : {"type" : "text"},
                "table_name" : {"type" : "text"},
                "long_desc" : {"type" : "text"},
                "topic_tags" : {"type" : "keyword"},
                "Aims" : {"type" : "text"},
                "Themes" : {"type" : "keyword"},
                "Type" : {"type" : "keyword"},
                #"collection_duration" : {"type" : "date_range",  "format" : "MM/yyyy"},
                #"age_range" : {"type" : "float_range"},
                "collection_start" : {"type" : "date", "format" : "MM/YYYY", "null_value": "NULL" },
                "collection_end" : {"type" : "date",  "format" : "MM/YYYY", "null_value": "NULL" },
                "lf" : {"type" : "double"},
                "q2" : {"type" : "double"},
                "uf" : {"type" : "double"},
            }
        }
    }


    index_name = "spine_"+datetime.now().strftime("%Y%m%d_%H%M%S")
    es.indices.create(index = index_name, body = mapping)
    spine = data[["source", "source_name", "table", "table_name", "long_desc", "topic_tags", "collection_start", "collection_end",  "lf", "q2", "uf", "Aims", "Themes", "Type"]].drop_duplicates(subset = ["source", "table"])
    for doc in spine.to_dict("records"):
        #doc["collection_duration"] = {"gte" : doc["collection_start"], "lte": doc["collection_end"]}
        #doc["age_range"] = {"gte" : float(doc["lf"]), "lte": float(doc["uf"])}
        if doc["topic_tags"]:
            doc["topic_tags"] = doc["topic_tags"].split(",")
        if doc["Themes"]:
            doc["Themes"] = doc["Themes"].split(",")

        es.index(index = index_name, body = doc)
    
    print("Writing to spine alias")
    es.indices.put_alias(index = index_name, name = "index_spine")
    
    with open("spine_index_name.json", "w") as f:
        json.dump({"name":index_name}, f)

    print("Deleting",previous_index_name)
    es.indices.delete(index = previous_index_name)

    




if __name__ == "__main__":
    main()