import os.path
import codecs
import pandas as pd
import sqlalchemy
import time
from datetime import datetime
import json
import dataIO

from elasticsearch import Elasticsearch
from elasticsearch import helpers
from elasticsearch.exceptions import RequestError
from urllib.parse import urlparse

def searchbox_connect():
    
    url = urlparse(os.environ['SEARCHBOX_URL'])
    ######## test
    es = Elasticsearch(
        [os.environ['SEARCHBOX_URL']],
        http_auth=(url.username, url.password),
    )
    return es

def prep_search_data():
    # get all sources
    sources = dataIO.get_sources()
    sources = sources[["data_source_id", "source", "source_name", "Aims", "Themes"]]
    # match datasets to sources
    datasets = dataIO.get_datasets_es()
    datasets = datasets[["dataset_id", "data_source_id", "table", "table_name", "long_desc", "topic_tags", "collection_start", "collection_end", "source_type"]]
    # match in ages 
    dataset_ages = dataIO.get_dataset_age(source_name = "none", dataset_name = "none")
    dataset_ages = dataset_ages[["lower_fence_age", "upper_fence_age", "q2_age", "dataset_version_id", "dataset_id"]]
    # merge datasets and sources
    merged = pd.merge(datasets, sources, how = "left", on = ["data_source_id"])
    # need version id to get latest for ages
    version = dataIO.get_dataset_versions()
    # keep latest version for each dataset
    version = version.sort_values(by = ["dataset_id", "version_num"], ascending = [True, False]).drop_duplicates(subset = ["dataset_id"], keep = "first")
    # merge ages with versions to act as filter for latest version
    dataset_ages = pd.merge(dataset_ages, version, how = "inner", on = ["dataset_version_id", "dataset_id"])
    # merge ages into merged datasets and sources
    merged = pd.merge(merged, dataset_ages, how = "left", on = ["dataset_id"])
    # build up variable-level data
    variable_dfs = []
    for _, row in merged.iterrows():
        variables = dataIO.get_variables(
            source=row["source"],
            table_name=row["table"]
        )
        # Add dataset information to every variable
        variables = variables.assign(
            dataset_id=row["dataset_id"],
            source=row["source"],
            table_name=row["table"]
        )
        variable_dfs.append(variables)
    # Combine all variables
    variables = pd.concat(variable_dfs, ignore_index=True)
    # merge ages with versions to act as filter for latest version
    variables = pd.merge(variables, version, how = "inner", on = ["dataset_version_id", "dataset_id"])
    variables = variables[["dataset_id", "variable_name", "variable_label", "value", "value_label"]]
    # final merge
    merged = pd.merge(merged, variables, how = "left", on = ["dataset_id"])
    # Rename columns to match target schema
    merged = merged.rename(columns={
        "variable_label": "variable_description",
        "source_type": "Type",
        "lower_fence_age": "lf",
        "upper_fence_age": "uf",
        "q2_age": "q2",
    })
    # Target column order
    target_columns = [
        "source",
        "table",
        "variable_name",
        "variable_description",
        "value",
        "value_label",
        "table_name",
        "long_desc",
        "topic_tags",
        "collection_start",
        "collection_end",
        "Type",
        "lf",
        "uf",
        "q2",
        "source_name",
        "Aims",
        "Themes",
    ]
    # Keep only target columns and order them correctly
    data = merged[target_columns]
    # match the previous pre-processing steps to ensure consistency
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
    return data

def variable(data):

    with open("var_index_name.json", "r") as f:
        previous_index_name = json.load(f)["name"]
    print("Previous var name:\n",previous_index_name)

    mapping = {
        "mappings" : {
            "properties" : {
                "source" : {"type" : "text"},
                "source_name" : {"type" : "text"},
                "table" : {"type" : "text"},
                "table_name" : {"type" : "text"},
                "variable_name" : {"type" : "text"},
                "variable_description" : {"type" : "text"},
                "value" : {"type" : "text"},
                "value_label" : {"type" : "text"},
                #"long_desc" : {"type" : "text"},
                "topic_tags" : {"type" : "text"},
                #"Aims" : {"type" : "text"},
                "Themes" : {"type" : "text"},
                "Type" : {"type" : "text"},
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

    es.indices.put_settings(
        index=index_name,
        body={
            "index": {
                "refresh_interval": "-1"
            }
        }
    )

    filtered = data[data["variable_name"].notna()]

    def generate_docs():
        for doc in filtered.to_dict("records"):
            if doc["topic_tags"]:
                doc["topic_tags"] = doc["topic_tags"].split(",")
            if doc["Themes"]:
                doc["Themes"] = doc["Themes"].split(",")
            yield {
                "_index": index_name,
                "_source": doc
            }

    print(f"Indexing {len(filtered):,} variable records...")

    helpers.bulk(
        es,
        generate_docs(),
        chunk_size=1000,
        request_timeout=120
    )

    # Re-enable refreshes
    es.indices.put_settings(
        index=index_name,
        body={
            "index": {
                "refresh_interval": "1s"
            }
        }
    )

    es.indices.refresh(index=index_name)

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

def main():
    
    data = prep_search_data()

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


if __name__ == "__main__":
    main()