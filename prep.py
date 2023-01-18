'''
Create JSON files of index to study and index to table (study-table)
'''
import dataIO
import json

request = dataIO.load_study_request().dropna(subset=["Study", "Block Name"])


study_lookup1, study_lookup2 = {}, {}

table_lookup1, table_lookup2 = {}, {}

for index, row in request.iterrows():
    study = row["Study"]
    table = row["Block Name"]

    table_lookup1[index] = study+"-"+table
    table_lookup2[study+"-"+table] = index

study_set = request["Study"].drop_duplicates().values
print(study_set)
for i, schema in zip(range(len(study_set)), study_set):

    study_lookup1[str(i)] = schema
    study_lookup2[schema] = str(i)

dataIO.write_json("study_lookup1.json", study_lookup1)
dataIO.write_json("study_lookup2.json", study_lookup2)
dataIO.write_json("table_lookup1.json", table_lookup1)
dataIO.write_json("table_lookup2.json", table_lookup2)

