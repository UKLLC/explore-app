import os.path
import codecs
import pandas as pd
import sqlalchemy
import time
from datetime import datetime

from elasticsearch import Elasticsearch
from elasticsearch.exceptions import RequestError
from urllib.parse import urlparse


def connect():
    try:
        cnxn = sqlalchemy.create_engine('mysql+pymysql://bq21582:password_password@127.0.0.1:3306/ukllc').connect()
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
        spine2(data)
    except RequestError as err:
        print("failed to write to spine", err)
        pass
 
    try:
        variable2(data)
    except RequestError as err:
        print("failed to write to variable", err)

        pass

def variable2(data):
    mapping = {
        "mappings" : {
            "properties" : {
                "source" : {"type" : "keyword"},
                "source_name" : {"type" : "text"},
                "table" : {"type" : "text"},
                "table_name" : {"type" : "text"},
                "variable_name" : {"type" : "keyword"},
                "variable_description" : {"type" : "text"},
                "value" : {"type" : "keyword"},
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
    es = searchbox_connect()
    es.indices.create(index = "index_var", body = mapping)
    for doc in data.loc[~data["variable_name"].isna()].to_dict("records"):
        #doc["collection_duration"] = {"gte" : doc["collection_start"], "lte": doc["collection_end"]}
        #doc["age_range"] = {"gte" : doc["lf"], "lte": doc["uf"]}
        if doc["topic_tags"]:
            doc["topic_tags"] = doc["topic_tags"].split(",")
        if doc["Themes"]:
            doc["Themes"] = doc["Themes"].split(",")
        es.index(index = "index_var", body = doc)


def variable(data):
    time0 = time.time()
    #define the search schema
    schema1 = fields.Schema(
        all = fields.ID(stored=True),
        source_name = fields.TEXT(stored=True),
        table = fields.ID(stored=True),
        table_name = fields.TEXT(stored=True),
        variable_name = fields.ID(stored=True),
        variable_description = fields.TEXT(stored=True),
        value = fields.KEYWORD(stored=True),
        value_label = fields.KEYWORD(stored=True),
        topic_tags = fields.KEYWORD(stored=True),
        collection_start = fields.TEXT(stored=True),
        collection_end = fields.TEXT(stored=True),
        lf = fields.NUMERIC(stored=True),
        uf = fields.NUMERIC(stored=True),
        Themes = fields.KEYWORD(stored=True),
        Type = fields.KEYWORD(stored=True)
    )

    # add dataframe rows to the index
    if not os.path.exists("index_var"):
        os.mkdir("index_var")

    ix1 = create_in("index_var", schema1)
    writer= ix1.writer()
    for i, nrows in data.loc[~data["variable_name"].isna()].iterrows():
        writer.add_document(
            all = data["all"][i],
            source = data.source[i],
            source_name = data["source_name"][i],
            table = data.table[i],
            table_name = data.table_name[i],
            variable_name = data.variable_name[i],
            variable_description = data.variable_description[i],
            value = data.value[i],
            value_label = data.value_label[i],
            long_desc = data.long_desc[i],
            topic_tags = data.topic_tags[i],
            collection_start = data.collection_start[i],
            collection_end = data.collection_end[i],
            lf = data.lf[i],
            uf = data.uf[i],
            Aims = data.Aims[i],
            Themes = data.Themes[i],
            Type = data.Type[i]
        )
    writer.commit()

    storage = FileStorage("index_var")
    time1 = time.time()

    print("DURATION: {}mins".format(round((time1 - time0)/60, 3)))

def spine2(data):
    es = searchbox_connect()

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

    es.indices.create(index = "index_spine", body = mapping)
    spine = data[["source", "source_name", "table", "table_name", "long_desc", "topic_tags", "collection_start", "collection_end",  "lf", "q2", "uf", "Aims", "Themes", "Type"]].drop_duplicates(subset = ["source", "table"])
    for doc in spine.to_dict("records"):
        #doc["collection_duration"] = {"gte" : doc["collection_start"], "lte": doc["collection_end"]}
        #doc["age_range"] = {"gte" : float(doc["lf"]), "lte": float(doc["uf"])}
        if doc["topic_tags"]:
            doc["topic_tags"] = doc["topic_tags"].split(",")
        if doc["Themes"]:
            doc["Themes"] = doc["Themes"].split(",")

        es.index(index = "index_spine", body = doc)




def spine(data):
    spine = data[["all", "source", "source_name", "table", "table_name", "long_desc", "topic_tags", "collection_start", "collection_end", "lf", "q2", "uf", "Aims", "Themes", "Type"]].drop_duplicates(subset = ["source", "table"])
    #define the search schema
    schema2 = fields.Schema(
        all = fields.ID(stored=True),
        source = fields.ID(stored=True),
        source_name = fields.TEXT(stored=True),
        table = fields.ID(stored=True),
        table_name = fields.TEXT(stored=True),
        long_desc = fields.TEXT(stored=True),
        topic_tags = fields.KEYWORD(stored=True),
        collection_start = fields.TEXT(stored=True),
        collection_end = fields.TEXT(stored=True),
        lf = fields.NUMERIC(stored=True),
        uf = fields.NUMERIC(stored=True),
        Aims = fields.TEXT(stored=True),
        Themes = fields.KEYWORD(stored=True),
        Type = fields.KEYWORD(stored=True)
    )

    # add dataframe rows to the index
    if not os.path.exists("index_spine"):
        os.mkdir("index_spine")

    ix2 = create_in("index_spine", schema2)
    writer= ix2.writer()
    for i, nrows in spine.iterrows():
        writer.add_document(
            all = spine["all"][i],
            source = spine.source[i],
            source_name = spine["source_name"][i],
            table = spine.table[i],
            table_name = spine.table_name[i],
            long_desc = spine.long_desc[i],
            topic_tags = spine.topic_tags[i],
            collection_start = spine.collection_start[i],
            collection_end = spine.collection_end[i],
            lf = spine.lf[i],
            uf = spine.uf[i],
            Aims = spine.Aims[i],
            Themes = spine.Themes[i],
            Type = spine["Type"][i]
        )
    writer.commit()

if __name__ == "__main__":
    main()