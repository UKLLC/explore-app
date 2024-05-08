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
        sources_df = dataIO.load_source_info(cnxn)
        datasets = dataIO.load_datasets(cnxn)
        dataset_counts = datasets[["source", "table", "participant_count", "weighted_participant_count", "Type"]]
        source_counts = sources_df


    dataset_counts["weighted_participant_count"] = dataset_counts["weighted_participant_count"].fillna(0)
    dataset_counts["participant_count"] = dataset_counts["participant_count"].fillna(0)
    source_counts["participant_count"] = source_counts["participant_count"].fillna(0)

    linked_source_counts = source_counts.loc[(source_counts["source"] == "nhsd") | (source_counts["source"] == "GEO")]
    lps_source_counts = source_counts.loc[~((source_counts["source"] == "nhsd") | (source_counts["source"] == "GEO"))]
    linked_dataset_counts = dataset_counts.loc[(dataset_counts["source"] == "nhsd") | (dataset_counts["source"] == "GEO")]
    lps_dataset_counts = dataset_counts.loc[~((dataset_counts["source"] == "nhsd") | (dataset_counts["source"] == "GEO"))]


    dataset_counts = dataset_counts.fillna(0)
    labels = ["Linked", "LPS"] + list(linked_source_counts["source"].values) + list(lps_source_counts["source"].values) + list(linked_dataset_counts["table"].values)  + list(lps_dataset_counts["table"].values)
    parents = ["",""]+ ["Linked" for i in linked_source_counts["source"].values] + ["LPS" for i in lps_source_counts["source"].values] + list(linked_dataset_counts["source"].values) + list(lps_dataset_counts["source"].values)
    vals_sources = list(linked_source_counts["participant_count"].values)+ list(lps_source_counts["participant_count"].values)
    weighted_vals_ds = [int(x) for x in list(linked_dataset_counts["weighted_participant_count"].values)] + [int(x) for x in list(lps_dataset_counts["weighted_participant_count"].values)]
    values = [sum(list(linked_source_counts["participant_count"].values))] + [sum(list(lps_source_counts["participant_count"].values))] + vals_sources + weighted_vals_ds
    print("\n\n\nDebug")
    print(len(source_counts), len(linked_source_counts)+len(lps_source_counts))
    print(len(dataset_counts), len(linked_dataset_counts)+len(lps_dataset_counts))
    print(len(labels), len(parents), len(values))
    for parent, label, val in zip(parents, labels, values):
        print(parent, label, val)
    print(sum(list(linked_source_counts["participant_count"].values)), sum(list(linked_source_counts["participant_count"].values)), sum([int(x) for x in list(linked_dataset_counts["weighted_participant_count"].values)]))

    print(sum(list(lps_source_counts["participant_count"].values)), sum(list(lps_source_counts["participant_count"].values)), sum([int(x) for x in list(lps_dataset_counts["weighted_participant_count"].values)]))
    
    print(len(labels), len(parents), len(values))
    lps_sub = 0
    linked_sub = 0  
    for parent, label, val in zip(parents, labels, values):
        if parent == "LPS":
            lps_sub += val
        elif parent == "Linked":
            linked_sub += val
        
        print(parent, label, val)
    print(lps_sub, linked_sub)
    for parent, label in zip(parents, labels):
        continue
        #print(parent, label)

    layout = go.Layout(
        margin=go.layout.Margin(
            l=0, #left margin
            r=0, #right margin
            b=0, #bottom margin
            t=0, #top margin
        )
    )
    fig = go.Figure(go.Sunburst(
            labels=labels,
            parents=parents,
            values=values,
            branchvalues = "total",
            #maxdepth = 2
            
            ),
            layout = layout
    )
    #print("made fig")
    fig.show()

    # TODO! Change the hover values of the tables to the count & 
    # Somehow use hover values to weight the sources and datasets appropriately. 
    # Solution: weight source accurately. weight datasets as ds/sum(ds in source) * count in source. Round to int. 
    
