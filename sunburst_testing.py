import sqlalchemy
import dataIO
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def connect():
    try:
        cnxn = sqlalchemy.create_engine('mysql+pymysql://bq21582:password_password@127.0.0.1:3306/ukllc').connect()
        return cnxn

    except Exception as e:
        print("Connection to database failed, retrying.")
        raise Exception("DB connection failed")



if __name__ == "__main__":


    with connect() as cnxn:
        sources_df = dataIO.load_sources(cnxn)
        datasets = dataIO.load_blocks(cnxn)

        source_counts = dataIO.load_source_count(cnxn)
        dataset_counts = dataIO.load_dataset_count(cnxn)

    labels = ["Linked", "LPS"] + list(source_counts["source"].values) + list(dataset_counts["table_name"].values)
    parents = ["",""]+ ["LPS" for i in source_counts["source"].values] + list(dataset_counts["source"].values)
    vals_sources = list(source_counts["participant_count"].values)
    vals_ds = list(dataset_counts["participant_count"].values)
    weighted_vals_ds = [int(x) for x in list(dataset_counts["weighted_participant_count"].values)]
    values = [100000] + [sum(vals_sources)] + vals_sources + weighted_vals_ds
    hover_values = [100000] + [sum(vals_sources)] + vals_sources + vals_ds
    #print("DEBUG:", [sources_df.loc[sources_df["source_id"]==x]["participants"].values for x in blocks_df["source_id"].values])

    print(len(labels), len(parents), len(values))
    for parent, label, val in zip(parents, labels, values):
        continue
        print(parent, label, val)
    #for x, y, z in zip(parents, labels, values):
    #print(str(x)+ " : "+str(y)+" : "+str(z))
    #print("DEBUG", len(labels), len(parents), len(values))
    fig = go.Figure(go.Sunburst(
            labels=labels,
            parents=parents,
            values=values,
            hovertext = hover_values,
            branchvalues = "total",
            #maxdepth = 2
            ),
    )
    #print("made fig")
    fig.show()

    # TODO! Change the hover values of the tables to the count & 
    # Somehow use hover values to weight the sources and datasets appropriately. 
    # Solution: weight source accurately. weight datasets as ds/sum(ds in source) * count in source. Round to int. 
    
