import json
from webbrowser import get
import sqlalchemy
import pandas as pd
import io
from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.files.file import File
import bot_token as bt

def connect():
    # need to swap password for local var
    cnxn = sqlalchemy.create_engine('mysql+pymysql://***REMOVED***')
    cnxn = sqlalchemy.create_engine('mysql+pymysql://bq21582:password_password@127.0.0.1:3306/ukllc')
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


def get_context(): 
    ctx_auth = AuthenticationContext("https://uob.sharepoint.com/teams/grp-AndyRobinJazz/")
    if ctx_auth.acquire_token_for_app(bt.token, bt.secret):
        ctx = ClientContext("https://uob.sharepoint.com/teams/grp-AndyRobinJazz/", ctx_auth)
        return ctx
    else:
        raise Exception("Context error")


def main():
    cnxn = connect()

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
    block_participants = data["block participants"]
    weighted_block_participants = data["weighted participants"]
    block_ages = data["block ages"]
    datasets = data["datasets"]
    cohort_linkage_groups = data["cohort linkage rate"]
    cohort_ages = data["cohort ages"]
    nhs_dataset_linkage = data["group_cohorts"]
    nhs_dataset_extracts = data["groupby"]

    block_counts_df = pd.DataFrame(block_counts.items(), columns = ["source", "dataset_count"] )
    block_counts_df.to_sql("dataset_counts", cnxn, if_exists="replace")

    ###

    study_participants_df = pd.DataFrame(study_participants.items(), columns = ["source", "participant_count"] )
    study_participants_df.to_sql("study_participants", cnxn, if_exists="replace")

    ###

    block_participants_df = pd.DataFrame(block_participants.items(), columns = ["source", "participant_count"] )
    block_participants_df = pd.merge(block_participants_df, pd.DataFrame(weighted_block_participants.items(), columns = ["source", "weighted_participant_count"]) )
    block_participants_df[['source', 'table_name']] = block_participants_df['source'].str.split('.', expand=True)
    block_participants_df.to_sql("dataset_participants", cnxn, if_exists="replace")

    ###

    rows = []
    for block in block_ages.keys():
        schema = block.split(".")[0]
        table = block.split(".")[1]
        rows.append([schema, table, block_ages[block]["mean"], block_ages[block]["std"], block_ages[block]["25%"], block_ages[block]["50%"], block_ages[block]["75%"], block_ages[block]["10%"], block_ages[block]["90%"]])

    block_ages_df = pd.DataFrame(rows, columns = ["source", "table_name", "mean", "std", "q1", "q2", "q3", "lf", "uf"])
    block_ages_df.to_sql("dataset_ages", cnxn, if_exists="replace")


    ###

    cohort_linkage_groups_rows = []
    cohort_linkage_groups_by_group_rows = []
    for cohort in cohort_linkage_groups.keys():

        total = cohort_linkage_groups[cohort]["total"]
        nhs = cohort_linkage_groups[cohort]["nhs"]
        geo = cohort_linkage_groups[cohort]["geo"]
        
        cohort_linkage_groups_rows.append([cohort, nhs, geo, total])

        group = cohort_linkage_groups[cohort]["groups"]
        group_counts = cohort_linkage_groups[cohort]["counts"]
        for key, item in group.items():
            cohort_linkage_groups_by_group_rows.append([cohort, key, item, group_counts[key]])
    cohort_linkage_df = pd.DataFrame(cohort_linkage_groups_rows, columns = ["cohort", "nhs", "geo", "total"])
    cohort_linkage_by_group = pd.DataFrame(cohort_linkage_groups_by_group_rows, columns = ["cohort", "group", "perc", "count"])
    cohort_linkage_df.to_sql("cohort_linkage", cnxn, if_exists="replace")
    cohort_linkage_by_group.to_sql("cohort_linkage_by_group", cnxn, if_exists="replace")

    ###
    
    blocks_linkage_rows = []
    blocks_linkage_by_group_rows = []
    for block in datasets.keys():
        schema = block.split(".")[0]
        table = block.split(".")[1]
        total = datasets[block]["total"]
        nhs = datasets[block]["nhs"]
        geo = datasets[block]["geo"]
        
        blocks_linkage_rows.append([schema, table, nhs, geo, total])

        group = datasets[block]["groups"]
        group_counts = datasets[block]["counts"]
        for key, item in group.items():
            blocks_linkage_by_group_rows.append([schema, table, key, item, group_counts[key]])

    block_linkage_df = pd.DataFrame(blocks_linkage_rows, columns = ["source", "table_name", "nhs", "geo", "total"])
    block_linkage_by_group = pd.DataFrame(blocks_linkage_by_group_rows, columns = ["source", "table_name", "group", "perc", "count"])
    block_linkage_df.to_sql("dataset_linkage", cnxn, if_exists="replace")
    block_linkage_by_group.to_sql("dataset_linkage_by_group", cnxn, if_exists="replace")

    ###

    rows = []
    for cohort in cohort_ages.keys():
        rows.append([cohort, cohort_ages[cohort]["mean"], cohort_ages[cohort]["std"], cohort_ages[cohort]["25%"], cohort_ages[cohort]["50%"], cohort_ages[cohort]["75%"], cohort_ages[cohort]["10%"], cohort_ages[cohort]["90%"]])

    cohort_ages_df = pd.DataFrame(rows, columns = ["source", "mean", "std", "q1", "q2", "q3", "lf", "uf"])
    cohort_ages_df.to_sql("cohort_ages", cnxn, if_exists="replace")

    ###

    nhs_dataset_rows = []
    for dataset in nhs_dataset_linkage.keys():
        for key, value in nhs_dataset_linkage[dataset].items():
            nhs_dataset_rows.append([dataset, key, value])
    nhsd_dataset_linkage_df = pd.DataFrame(nhs_dataset_rows, columns = ["dataset", "cohort", "count"])
    nhsd_dataset_linkage_df.to_sql("nhs_dataset_cohort_linkage", cnxn, if_exists="replace")

    ###

    nhs_dataset_extract_rows = []
    for dataset in nhs_dataset_extracts.keys():
        for i in nhs_dataset_extracts[dataset]:
            if type(i["extract_date"]) != str:
                nhs_dataset_extract_rows.append([dataset,"total", i["count"]])
            else:
                nhs_dataset_extract_rows.append([dataset,i["extract_date"], i["count"]])
    nhsd_dataset_extract_df = pd.DataFrame(nhs_dataset_extract_rows, columns = ["dataset", "date", "count"])
    nhsd_dataset_extract_df.to_sql("nhs_dataset_extracts", cnxn, if_exists="replace")

    ###
    # Search lookup table
    rows = []
    for dataset in spine.keys():
        schema = dataset.split(".")[0]
        table = dataset.split(".")[1]
        age_lf, age_uf = block_ages[dataset]["10%"], block_ages[dataset]["90%"]
        table_type = spine[dataset]

        rows.append([schema, table, table_type, age_lf, age_uf])
    spine_df = pd.DataFrame(rows, columns = ["source", "table", "current_age_lf", "current_age_uf", "table_type"])
    spine_df.to_sql("spine", cnxn, if_exists="replace")

    ###
    # core source info 
    source_df = pd.read_excel("Mental_health_catalogue.xlsx", sheet_name="Sheet1")
    
    source_df = pd.merge(source_df, block_counts_df, on = ["source"])
    source_df = pd.merge(source_df, study_participants_df, on = ["source"])
    
    source_df.to_sql("source_info", cnxn, if_exists="replace")


    ###
    # dataset
    dataset_df = pd.read_excel("Database tables.xlsx", sheet_name="Dataset")
    dataset_df.to_sql("dataset", cnxn, if_exists="replace")


    ###
    # search terms
    all_variables = pd.read_csv("metadata\\all_metadata.csv", dtype= str).rename(columns = {"Source":"source","Block Name":"table","Variable Name":"variable_name","Variable Description":"variable_description","Value":"value","Value Description":"value_label"})
    #all_variables = all_variables.fillna("")
    # source_id, dataset_id, source fullname, dataset fullname, dataset long desc, dataset age start, dataset age end, dataset collection start, dataset collection end, variable name, variable desc, value, value_label, source themes, dataset tags
    #merging values
    all_variables = all_variables.groupby(["source", "table", "variable_name", "variable_description"], as_index=False).agg(list)
    all_variables["value"] = all_variables["value"].str.replace("[|]|'", "")
    all_variables["value_label"] = all_variables["value_label"].str.replace("[|]|", "")
    #get dataset full name, long desc, dataset topic tags
    search = pd.merge(all_variables, dataset_df[["source", "table", "table_name", "long_desc", "topic_tags", "collection_start", "collection_end"]], on  = ["source", "table"] )
    # Get age upper lowers
    block_ages_df = block_ages_df.rename(columns = {"table_name":"table"})
    search = pd.merge(search, block_ages_df[["source", "table", "lf", "uf"]], on  = ["source", "table"] )
    # Get source fullname, description, themes
    search = pd.merge(search, source_df[["source", "LPS name", "Aims", "Themes"]],  on  = ["source"])
    search["Themes"] = search["Themes"].str.replace("\n", "")
    #search = search.fillna("")
    search.to_csv("debug.csv", index=False)
    search = pd.read_csv("debug.csv", index_col=False)
    search.to_sql("search", cnxn, if_exists="replace")
    # TODO collection 
    #print(cohort_linkage_groups_df)

    #print(block_participants)
    #block_participants_df = pd.DataFrame(block_participants.items() )
    
    #print("block ages:\n", block_ages)
    #print("datasets:\n", datasets)
    #print("cohort linkage groups:\n", cohort_linkage_groups)
    #print("cohort ages:\n", cohort_ages)

    '''
    TODO 
    Left to do is build the tables as pandas df
        make cohort linkage numbers (rather than just groups)
        make block ages
        make datasets counts and breakdowns
        make cohort linkage groups
    upload the tables to the database
    '''

    # Adding File 2 Documentation
    


if __name__ == "__main__":
    main()