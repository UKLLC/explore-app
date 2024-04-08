import os.path
import codecs
import pandas as pd
import sqlalchemy
import time

from whoosh import fields, index
from whoosh.index import create_in
from whoosh.fields import Schema, TEXT, KEYWORD, ID, STORED
from whoosh.analysis import StemmingAnalyzer
from whoosh import qparser
from whoosh.qparser import QueryParser
from whoosh.filedb.filestore import FileStorage


def connect():
    try:
        cnxn = sqlalchemy.create_engine('mysql+pymysql://bq21582:password_password@127.0.0.1:3306/ukllc').connect()
        return cnxn

    except Exception as e:
        print("Connection to database failed, retrying.")
        raise Exception("DB connection failed")

def main():
    '''
    '''
    cnxn = connect()
    data = pd.read_sql("SELECT * from search", cnxn)

    data["lf"] = data["lf"].fillna("-99")
    data["uf"] = data["uf"].fillna("-99")
    data["variable_name"] = data["variable_name"].fillna(" ")
    data["variable_description"] = data["variable_name"].fillna(" ")
    data["value"] = data["value"].fillna(" ")
    data["value_label"] = data["value_label"].fillna(" ")
    data["collection_start"] = data["collection_start"].fillna(" ")
    data["collection_end"] = data["collection_end"].fillna(" ")
    data["LPS_name"] = data["LPS_name"].fillna(" ")
    data["Aims"] = data["Aims"].fillna(" ")
    data["Themes"] = data["Themes"].fillna(" ")
    data["all"] = "1"
    data.to_csv("test.csv")
    
    variable(data)
    spine(data)

def variable(data):
    time0 = time.time()
    #define the search schema
    schema1 = fields.Schema(
        all = fields.ID(stored=True),
        source = fields.ID(stored=True),
        LPS_name = fields.TEXT(stored=True),
        table = fields.ID(stored=True),
        table_name = fields.TEXT(stored=True),
        variable_name = fields.ID(stored=True),
        variable_description = fields.TEXT(stored=True),
        value = fields.KEYWORD(stored=True),
        value_label = fields.KEYWORD(stored=True),
        long_desc = fields.TEXT(stored=True),
        topic_tags = fields.KEYWORD(stored=True),
        collection_start = fields.TEXT(stored=True),
        collection_end = fields.TEXT(stored=True),
        lf = fields.NUMERIC(stored=True),
        uf = fields.NUMERIC(stored=True),
        Aims = fields.TEXT(stored=True),
        Themes = fields.KEYWORD(stored=True),
    )

    # add dataframe rows to the index
    if not os.path.exists("index_var"):
        os.mkdir("index_var")

    ix1 = create_in("index_var", schema1)
    writer= ix1.writer()
    for i, nrows in data.iterrows():
        writer.add_document(
            all = data["all"][i],
            source = data.source[i],
            LPS_name = data["LPS_name"][i],
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
        )
    writer.commit()

    storage = FileStorage("index_var")
    time1 = time.time()

    print("DURATION: {}mins".format(round((time1 - time0)/60, 3)))

def spine(data):
    spine = data[["all", "source", "LPS_name", "table", "table_name", "long_desc", "topic_tags", "collection_start", "collection_end", "lf", "uf", "Aims", "Themes"]].drop_duplicates(subset = ["source", "table"])
    #define the search schema
    schema2 = fields.Schema(
        all = fields.ID(stored=True),
        source = fields.ID(stored=True),
        LPS_name = fields.TEXT(stored=True),
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
    )

    # add dataframe rows to the index
    if not os.path.exists("index_spine"):
        os.mkdir("index_spine")

    print(spine.columns)
    ix2 = create_in("index_spine", schema2)
    writer= ix2.writer()
    for i, nrows in spine.iterrows():
        writer.add_document(
            all = spine["all"][i],
            source = spine.source[i],
            LPS_name = spine["LPS_name"][i],
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
        )
    writer.commit()

if __name__ == "__main__":
    main()