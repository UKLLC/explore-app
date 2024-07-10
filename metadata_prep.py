import pandas as pd
import os


all_metadata = pd.read_csv("metadata\\all_metadata.csv")

unique_schemas = list(set(all_metadata["Source"].values))

for schema in unique_schemas:
    if schema == "NHSD_STAGE":
        continue

    df = all_metadata.loc[all_metadata["Source"] == schema]

    unique_tables = list(set(df["Block Name"].values))
    for table in unique_tables:
        table_df = df.loc[df["Block Name"] == table]

        # TODO write out to file
        if not os.path.exists(os.path.join("metadata",schema)):
            os.makedirs(os.path.join("metadata",schema))

        table_df.to_csv(os.path.join("metadata",schema,table+".csv"))


# TODO: Requirements for this to work smoothly:
#   In SeRP 'dash_prep.py' program for updating the data request form and getting metadata to file out
#   Metadata out needs to be slightly altered. All_metadata.csv is a good start, but version and schema- need to be removed
#   Consideration: Will we want to show previous versions at some point? Yes. How does this change the brief?