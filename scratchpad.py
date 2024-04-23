import plotly.graph_objects as go
import dataIO 

import sqlalchemy
import pandas as pd
import os
import json



def connect():
    try:
        #cnxn = sqlalchemy.create_engine("mysql+pymysql://***REMOVED***").connect()
        cnxn = sqlalchemy.create_engine('mysql+pymysql://bq21582:password_password@127.0.0.1:3306/ukllc').connect()
        return cnxn

    except Exception as e:
        print("fatal: Connection to database failed")
        raise Exception("DB connection failed")

with open(os.path.join("assets","map overlays","regions.geojson"), 'r') as f:
    gj = json.load(f)

def prep_counts(df):
    '''
    apply function
    '''
    if df["count"] == "<10":
        return 10
    elif pd.isna(df["count"]):
        return 0
    return int(df["count"])

df = dataIO.load_map_data(connect())
df1 = df.loc[df["source"] == "EXCEED"]
df1 = df1.drop(["source", "source_stem", "index"], axis=1)
df2 = pd.DataFrame([[ str(x), y] for x, y in zip(df1.columns, df1.iloc[0].values) ], columns = ["RGN23NM", "count"])
df2["labels"] = df2["count"]
df2["labels"].fillna("Not available")
df2["count"] = df2.apply(prep_counts, axis = 1)


fig = go.Figure(data=go.Choropleth(z=df2["count"],
    geojson = gj, # Spatial coordinates
    locations = df2["RGN23NM"],
    locationmode = 'geojson-id', # set of locations match entries in `locations`
    colorscale = 'Blues',
    colorbar = None,
    )
)
fig.update_layout(  
    geo_scope = "europe",
    coloraxis_showscale=False
)

fig.update_geos(
    visible = False,
    showframe=False,
    fitbounds = "locations"
)

fig.show()