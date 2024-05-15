import pandas as pd
import sqlalchemy


def connect():
    # need to swap password for local var
    engine = sqlalchemy.create_engine('mysql+pymysql://bq21582:password_password@127.0.0.1:3306/ukllc')
    return(engine)


def make_table(src, name):
    engine = connect()
    print(pd.read_sql("select * from "+name.lower(), engine))
    with engine.connect() as cnxn:
        result = cnxn.execute(sqlalchemy.text("DROP TABLE IF EXISTS "+name.lower()+";"))
    df = pd.read_excel(src, sheet_name=name)
    df.to_sql(name.lower(), con = engine)


if __name__ == "__main__":
    make_table("Database tables.xlsx", "Datasource")
    make_table("Database tables.xlsx", "Dataset")
    pass