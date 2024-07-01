import json
from webbrowser import get
import sqlalchemy
import psycopg2
import pandas as pd
import io
from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.files.file import File
import os
import re
from datetime import datetime
import naming_functions as nf


def connect1():
    # need to swap password for local var
    cnxn = sqlalchemy.create_engine('mysql+pymysql://bq21582:password_password@127.0.0.1:3306/ukllc')
    return(cnxn)
def connect2():
    # need to swap password for local var
    #cnxn = sqlalchemy.create_engine('mysql+pymysql://***REMOVED***')
    cnxn = sqlalchemy.create_engine('postgresql+psycopg2://***REMOVED***')
    return(cnxn)

def get_teams_doc(target, ctx):
    libraryRoot = ctx.web.get_folder_by_server_relative_path("")
    ctx.load(libraryRoot)
    ctx.execute_query()

    response = File.open_binary(ctx, target)

    return io.BytesIO(response.content)

def get_file2_docs(ctx):
    files = []
    libraryRoot = ctx.web.get_folder_by_server_relative_path("/teams/grp-AndyRobinJazz/Shared Documents/Data Access/Data Team/Data Documentation/File 2 Data Block Documentation/File 2 Documentation - LPS COMPLETED")
    ctx.load(libraryRoot)
    ctx.execute_query()
    print("here")

    # Get main data request files 
    files = libraryRoot.files
    ctx.load(files)
    ctx.execute_query()

    rows = []
    for f in files: 
        print(f.properties['Name'])
        if ".xlsx" in f.properties['Name']:
            content = pd.read_excel(get_teams_doc(f.properties['ServerRelativeUrl'], ctx), engine='openpyxl', skiprows=[0,1,2,3,4,5,7, 8])
        
            source = f.properties['Name'].split(" ")[0]
            table_col = [x for x in content.columns if "Data Block File Name" in x][0]
            table_names = content[table_col]

            long_table_names = "tbc"

            long_desc_col = [x for x in content.columns if "Block Description" in x][0]
            long_descs = content[long_desc_col]

            collection_times_col = [x for x in content.columns if "Timepoint: Data Collected" in x][0]
            collection_times = content[collection_times_col]

            participants_invited_col = [x for x in content.columns if "Participants Invited" in x][0]
            participants_inviteds = content[participants_invited_col]

            participants_included_col = [x for x in content.columns if "Participants Included" in x]
            if len(participants_included_col) > 0:
                print(participants_included_col)
                participants_included_col = participants_included_col[0]
                participants_included = content[participants_included_col]
            else:
                participants_included = ["NaN" for x in range(len(content))]

            links_col = [x for x in content.columns if "Link" in x][0]
            links = content[links_col].astype(str).str.replace("\n", ", ")

            topic_tag_cols = [x for x in content.columns if ("Keywords" in x) or ("Unnamed: 9" in x) or ("Unnamed: 10" in x) or ("Unnamed: 11" in x)  or ("Unnamed: 12" in x) or ("Unnamed: 13" in x) or ("Unnamed: 14" in x)  or ("Unnamed: 15" in x)  or ("Unnamed: 16" in x)]
            content["combined_keywords"] = ""
            for col in topic_tag_cols:
                content["combined_keywords"] = content["combined_keywords"] + ", " + content[col]
            topic_tags = content["combined_keywords"]
            
            source_rows = []
            for index in range(len(table_names)):
                source_rows.append([source, table_names[index], long_table_names, collection_times[index], long_descs[index], participants_inviteds[index], participants_included[index], links[index], topic_tags[index]])
        
            rows += source_rows

    df = pd.DataFrame(rows, columns = ["source", "table_name", "long_table_name", "collection_times", "long_descs", "participants_inviteds", "participants_included", "links", "topic_tags"])
    df = df.dropna(subset=["table_name"])
    df = df.dropna(subset=["participants_inviteds"])
    df = df.dropna(subset=["long_descs"])
    return df

'''
def get_context(): 
    ctx_auth = AuthenticationContext("https://uob.sharepoint.com/teams/grp-AndyRobinJazz/")
    if ctx_auth.acquire_token_for_app(bt.token, bt.secret):
        ctx = ClientContext("https://uob.sharepoint.com/teams/grp-AndyRobinJazz/", ctx_auth)
        return ctx
    else:
        raise Exception("Context error")
'''

def contains_version(name):
    
    pattern = re.compile("v[0-9]{4}")
    match = pattern.match(name)
    if match != None:
        return True
    return False

def contains_date(name):
    date_format = "%Y%m%d"
    date = name[-8:]
    try:
        datetime.strptime(date, date_format)
        return True
    except ValueError:
        pass
    return False


def get_formatted_name(df, col = "table"):
    name = df[col]
    if contains_date(name) or contains_version(name):
        cut_name = "_".join(name.split("_")[0:-1])
        if "_v0" in name:
            cut_name = "_".join(cut_name.split("_")[0:-1])
        return cut_name
    else:
        return name
    
# linked ages 
# geo_location
# group_cohorts

def main():
    cnxn1 = connect1()
    cnxn2 = connect2()
    # Get file 2 doc core metadata
    '''
    ctx = get_context()
    cl
    file2_docs = get_file2_docs(ctx)
    print(file2_docs)
    print(file2_docs.columns)
    file2_docs.to_sql("dataset_file2_metadata", cnxn, if_exists="replace")
    '''
    # Path to the JSON file
    json_file_path = 'metrics_out.json'

    # Load data from JSON file
    with open(json_file_path, 'r') as file:
        data = json.load(file)

    spine = data["spine"]
    block_counts = data["block counts"]
    study_participants = data["study participants"]
    dataset_participants = data["block participants"]
    weighted_dataset_participants = data["weighted participants"]
    block_ages = data["block ages"]
    datasets = data["datasets"]
    cohort_linkage_groups = data["cohort linkage rate"]
    cohort_ages = data["cohort ages"]
    linked_ages = data["linked ages"]
    geo_locations = data["geo_locations"]
    nhs_dataset_linkage = data["group_cohorts"]
    nhs_dataset_extracts = data["groupby"]

    block_counts_df = pd.DataFrame(block_counts.items(), columns = ["source", "dataset_count"] )

    ###

    study_participants_df = pd.DataFrame(study_participants.items(), columns = ["source", "participant_count"] )
    study_participants_df.to_sql("study_participants", cnxn1, if_exists="replace")
    study_participants_df.to_sql("study_participants", cnxn2, if_exists="replace")

    ###

    dataset_participants_df = pd.DataFrame(dataset_participants.items(), columns = ["source", "participant_count"] )
    dataset_participants_df = pd.merge(dataset_participants_df, pd.DataFrame(weighted_dataset_participants.items(), columns = ["source", "weighted_participant_count"]) )
    dataset_participants_df[['source', 'table']] = dataset_participants_df['source'].str.split('.', expand=True)

    ###

    rows = []
    for block in block_ages.keys():
        schema = block.split(".")[0]
        table = block.split(".")[1]
        rows.append([schema, table, block_ages[block]["mean"], block_ages[block]["q1"], block_ages[block]["q2"], block_ages[block]["q3"], block_ages[block]["lf"], block_ages[block]["uf"]])

    block_ages_df = pd.DataFrame(rows, columns = ["source", "table_name", "mean", "q1", "q2", "q3", "lf", "uf"])
    block_ages_df.to_sql("dataset_ages", cnxn1, if_exists="replace")
    block_ages_df.to_sql("dataset_ages", cnxn2, if_exists="replace")

    ###

    cohort_linkage_groups_rows = []
    cohort_linkage_groups_by_group_rows = []
    for cohort in cohort_linkage_groups.keys():

        total = cohort_linkage_groups[cohort]["total"]

        
        cohort_linkage_groups_rows.append([cohort, total])

        group = cohort_linkage_groups[cohort]["groups"]
        group_counts = cohort_linkage_groups[cohort]["counts"]
        for key, item in group.items():
            cohort_linkage_groups_by_group_rows.append([cohort, key, item, group_counts[key]])
    cohort_linkage_df = pd.DataFrame(cohort_linkage_groups_rows, columns = ["cohort",  "total"]).rename(columns={"cohort":"source"})
    cohort_linkage_by_group = pd.DataFrame(cohort_linkage_groups_by_group_rows, columns = ["cohort", "group", "perc", "count"])
    cohort_linkage_by_group.to_sql("cohort_linkage_by_group", cnxn1, if_exists="replace")
    cohort_linkage_by_group.to_sql("cohort_linkage_by_group", cnxn2, if_exists="replace")

    ###
    
    blocks_linkage_rows = []
    blocks_linkage_by_group_rows = []
    for block in datasets.keys():
        schema = block.split(".")[0]
        table = block.split(".")[1]
        total = datasets[block]["total"]
        
        blocks_linkage_rows.append([schema, table,  total])

        group = datasets[block]["groups"]
        group_counts = datasets[block]["counts"]
        for key, item in group.items():
            if schema.lower() != "nhsd":
                blocks_linkage_by_group_rows.append([schema, table, key, item, group_counts[key]])

    block_linkage_df = pd.DataFrame(blocks_linkage_rows, columns = ["source", "table_name",  "total"]).rename(columns={"table_name":"table"})
    block_linkage_by_group = pd.DataFrame(blocks_linkage_by_group_rows, columns = ["source", "table_name", "group", "perc", "count"])
    block_linkage_by_group.to_sql("dataset_linkage_by_group", cnxn1, if_exists="replace")
    block_linkage_by_group.to_sql("dataset_linkage_by_group", cnxn2, if_exists="replace")
    
    ###    
    ###
    linked_ages = data["linked ages"]
    linked_rows = []
    cohort_rows = []
    for ds in linked_ages.keys():
        linked_rows.append([ds, linked_ages[ds]["mean"], linked_ages[ds]["q1"], linked_ages[ds]["q2"], linked_ages[ds]["q3"], linked_ages[ds]["lf"], linked_ages[ds]["uf"]])
        if "demographics" in ds.lower():
            cohort_rows.append([ds, linked_ages[ds]["mean"], linked_ages[ds]["q1"], linked_ages[ds]["q2"], linked_ages[ds]["q3"], linked_ages[ds]["lf"], linked_ages[ds]["uf"]])
    linked_ages_df = pd.DataFrame(linked_rows, columns = ["source", "mean", "q1", "q2", "q3", "lf", "uf"])
    linked_ages_df["source_stem"] = linked_ages_df.apply(nf.get_naming_parts, axis =1, args=("source",))
    linked_ages_df.to_sql("linked_ages", cnxn1, if_exists="replace")
    linked_ages_df.to_sql("linked_ages", cnxn2, if_exists="replace")

    
    for cohort in cohort_ages.keys():
        cohort_rows.append([cohort, cohort_ages[cohort]["mean"], cohort_ages[cohort]["q1"], cohort_ages[cohort]["q2"], cohort_ages[cohort]["q3"], cohort_ages[cohort]["lf"], cohort_ages[cohort]["uf"]])

    cohort_ages_df = pd.DataFrame(cohort_rows, columns = ["source", "mean", "q1", "q2", "q3", "lf", "uf"])
    cohort_ages_df.to_sql("cohort_ages", cnxn1, if_exists="replace")
    cohort_ages_df.to_sql("cohort_ages", cnxn2, if_exists="replace")
   

    ###

    nhs_dataset_rows = []
    for dataset in nhs_dataset_linkage.keys():
        for key, value in nhs_dataset_linkage[dataset].items():
            nhs_dataset_rows.append([dataset, key, value])
    nhsd_dataset_linkage_df = pd.DataFrame(nhs_dataset_rows, columns = ["dataset", "cohort", "count"])
    nhsd_dataset_linkage_df["dataset_stem"] = nhsd_dataset_linkage_df.apply(nf.get_naming_parts, axis =1, args=("dataset",))
    # This is a hack to get versioned name onto nhsd_dataset_linkage_df2
    linked_ages_df = linked_ages_df.rename(columns = {"source_stem" : "dataset_stem", "source":"dataset"})
    nhsd_dataset_linkage_df2 = pd.merge(nhsd_dataset_linkage_df[["dataset_stem", "cohort", "count"]], linked_ages_df[["dataset", "dataset_stem"]], how = "left", on = ["dataset_stem"])
    nhsd_dataset_linkage_df2.to_sql("nhs_dataset_cohort_linkage", cnxn1, if_exists="replace")
    nhsd_dataset_linkage_df2.to_sql("nhs_dataset_cohort_linkage", cnxn2, if_exists="replace")

    ###

    nhs_dataset_extract_rows = []
    for dataset in nhs_dataset_extracts.keys():
        for i in nhs_dataset_extracts[dataset]:
            if type(i["extract_date"]) == str:
                nhs_dataset_extract_rows.append([dataset,i["extract_date"], i["count"]])
    nhsd_dataset_extract_df = pd.DataFrame(nhs_dataset_extract_rows, columns = ["dataset", "date", "count"])
    nhsd_dataset_extract_df.to_sql("nhs_dataset_extracts", cnxn1, if_exists="replace")
    nhsd_dataset_extract_df.to_sql("nhs_dataset_extracts", cnxn2, if_exists="replace")
    
    ###

    geo_locations_row = []
    
    for dataset in geo_locations.keys():
        if len(geo_locations[dataset]) > 2:
            geo_locations_row.append([dataset, geo_locations[dataset]["East of England"], geo_locations[dataset]["South East"], geo_locations[dataset]["North West"], geo_locations[dataset]["East Midlands"], geo_locations[dataset]["West Midlands"], geo_locations[dataset]["South West"], geo_locations[dataset]["London"], geo_locations[dataset]["Yorkshire and The Humber"], geo_locations[dataset]["North East"], geo_locations[dataset]["Wales"], geo_locations[dataset]["Scotland"]])
        else:
            geo_locations_row.append([dataset,None,None,None,None,None,None,None,None,None,None,None])
    geo_locations_df = pd.DataFrame(geo_locations_row, columns = ["source", "East of England", "South East", "North West", "East Midlands", "West Midlands", "South West", "London", "Yorkshire and The Humber", "North East", "Wales", "Scotland"])
    # Northern Ireland override
    geo_locations_df["Northern Ireland"] = 0
    geo_locations_df["source_stem"] = geo_locations_df.apply(nf.get_naming_parts, axis =1, args=("source",))
    '''
    geo_locations_trimmed = nf.select_latest_version(geo_locations_df, "source")
    geo_locations_trimmed = nf.select_latest_date(geo_locations_trimmed, "source" )
    geo_locations_df["latest"] = geo_locations_df["source"].isin(geo_locations_trimmed["source"])
    '''
    geo_locations_df.to_sql("geo_locations", cnxn1, if_exists="replace")
    geo_locations_df.to_sql("geo_locations", cnxn2, if_exists="replace")


    ###
    # core source info 
    source_df = pd.read_excel("all_sources_in.xlsx", sheet_name="Sheet1")
    source_df = source_df.rename(columns = {"source name":"source_name"})
    
    source_df = pd.merge(source_df, block_counts_df, on = ["source"], how = "left")
    source_df = pd.merge(source_df, study_participants_df, on = ["source"], how = "left")
    source_df = pd.merge(source_df, cohort_linkage_df, on = ["source"], how = "left")
    source_df["Themes"] = source_df["Themes"].str.replace("\n", "")
    source_df["Themes"] = source_df["Themes"].str.replace(u"\n", u"")
    source_df["Themes"] = source_df["Themes"].str.replace("  ", " ")
    source_df["Themes"] = source_df["Themes"].str.replace(" ,", ",")
    source_df["Themes"] = source_df["Themes"].str.replace(", ", ",")
    source_df["Themes"] = source_df["Themes"].str.replace(u'\xa0', u'')
    source_df["Themes"] = source_df["Themes"].str.strip()
    source_df.to_sql("source_info", cnxn1, if_exists="replace")
    source_df.to_sql("source_info", cnxn2, if_exists="replace")

    ###
    # dataset
    try:
        dataset_df = pd.read_excel("Database tables.xlsx", sheet_name="Sheet1") # If error here, do clean.py
    except ValueError:
        raise Exception("Error loading Database tables.xlsx because of incorrect sheet name. Run clean.py you lemon.")


    dataset_df = pd.merge(dataset_df, dataset_participants_df, how = "left", on =["source", "table"])
    dataset_df = pd.merge(dataset_df, block_linkage_df, how = "left", on =["source", "table"])
    dataset_df = pd.merge(dataset_df, source_df[["source", "source_name", "Type"]], how = "left", on = ["source"])
    dataset_df["topic_tags"] = dataset_df["topic_tags"].str.replace("\n", "")
    dataset_df["topic_tags"] = dataset_df["topic_tags"].str.replace(u"\n", u"")
    dataset_df["topic_tags"] = dataset_df["topic_tags"].str.replace(u'\xa0', u'')
    dataset_df["topic_tags"] = dataset_df["topic_tags"].str.replace("  ", " ")
    dataset_df["topic_tags"] = dataset_df["topic_tags"].str.replace(" ,", ",")
    dataset_df["topic_tags"] = dataset_df["topic_tags"].str.replace(", ", ",")
    dataset_df["topic_tags"] = dataset_df["topic_tags"].str.strip()
    dataset_df.to_sql("dataset", cnxn1, if_exists="replace")
    dataset_df.to_sql("dataset", cnxn2, if_exists="replace")

    ###
    # search terms
    all_variables = pd.read_csv("metadata\\all_metadata.csv", dtype= str).rename(columns = {"Source":"source","Block Name":"table","Variable Name":"variable_name","Variable Description":"variable_description","Value":"value","Value Description":"value_label"})
    #all_variables = all_variables.fillna("")
    # source_id, dataset_id, source fullname, dataset fullname, dataset long desc, dataset age start, dataset age end, dataset collection start, dataset collection end, variable name, variable desc, value, value_label, source themes, dataset tags
    #merging values
    print("Debug start")
    print(all_variables, "\n")
    all_variables = all_variables.groupby(["source", "table", "variable_name", "variable_description"], as_index=False).agg(list)
    all_variables["value"] = all_variables["value"].fillna("")
    all_variables["value"] = all_variables["value"].str.join(", ")
    all_variables["value_label"] = all_variables["value_label"].fillna("")
    all_variables["value_label"] = all_variables["value_label"].str.join(", ")
    print(all_variables, "\n")
    
    #get dataset full name, long desc, dataset topic tags
    search = pd.merge(all_variables, dataset_df[["source", "table", "table_name", "long_desc", "topic_tags", "collection_start", "collection_end", "Type"]], on  = ["source", "table"], how = "right")
    # Get age upper lowers
    block_ages_df = block_ages_df.rename(columns = {"table_name":"table"})
    search = pd.merge(search, block_ages_df[["source", "table", "lf", "uf", "q2"]], on  = ["source", "table"], how = "left" )
    # Get source fullname, description, themes
    search = pd.merge(search, source_df[["source", "source_name", "Aims", "Themes"]],  on  = ["source"], how = "left")
    search["Themes"] = search["Themes"].str.replace("\n", "")
    #search = search.fillna("")
    #search.to_sql("search", cnxn1, if_exists="replace")
    search.to_sql("search", cnxn2, if_exists="replace")


    
    ### 
    # all individual metadata files
    # load all metadata

    for root, dirs, files in os.walk('metadata'):
        for name in files:
            fpath = os.path.join(root, name)
            data = pd.read_csv(fpath)
            if "all_metadata.csv" in name:
                continue
            tab_name = "metadata_"+root.split('\\')[1].lower() + '_' + name.split('.')[0].lower()
            data.to_sql(tab_name, cnxn1, if_exists = 'replace', index = False)
            data.to_sql(tab_name, cnxn2, if_exists = 'replace', index = False)
    # geo special
    f1 = pd.read_csv("metadata\\geo\\air_pollution_hh.csv")
    f2 = pd.read_csv("metadata\\geo\\air_pollution_pc.csv")
    geo = pd.concat([f1, f2])
    geo.to_sql("metadata_geo_air_pollution", cnxn2, if_exists = 'replace', index = False)


if __name__ == "__main__":
    main()
    


'''
Linked data extension: what do we need to implement?
linkage rate = ammount with linkage permission
participant count, weighted participant count
Obvs linkage graph isn't important.

'''