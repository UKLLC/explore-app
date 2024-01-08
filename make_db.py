import pandas as pd
import os
import sqlalchemy


def connect():
    # need to swap password for local var
    cnxn = sqlalchemy.create_engine('mysql+pymysql://bq21582:password_password@127.0.0.1:3306/ukllc')
    return(cnxn)


def make_table(src, name):
    cnxn = connect()
    print(pd.read_sql("select * from "+"ukllc."+name.lower(), cnxn))
    result = cnxn.execute("DROP TABLE IF EXISTS ukllc."+name.lower()+";")
    df = pd.read_excel(src, sheet_name=name)
    df.to_sql(name.lower(), con = cnxn)


if __name__ == "__main__":
    make_table("Database tables.xlsx", "Datasource")
    make_table("Database tables.xlsx", "Dataset")
    pass