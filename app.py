# sidebar.py
import dash
from dash import dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
from dash import Input, Output, State, ALL, MATCH
import warnings
import logging
from dash.exceptions import PreventUpdate
#import dash_auth
from flask import request
import sqlalchemy
import sys
from elasticsearch import Elasticsearch
from urllib.parse import urlparse, parse_qs
import os
import base64


import dataIO
import structures as struct

import time





######################################################################################
app = dash.Dash(
    __name__, 
    external_stylesheets=["custom.css",  dbc.icons.BOOTSTRAP ],
    routing_callback_inputs={
        # The app state is serialised in the URL hash without refreshing the page
        # This URL can be copied and then parsed on page load
        "state": State("main-url", "hash"),
    },
    )
app.title = "UKLLC Explore"
server = app.server

def connect():
    try:
        db_str = os.environ['DATABASE_URL'].replace("postgres", "postgresql+psycopg2", 1)
        cnxn = sqlalchemy.create_engine(db_str).connect()
        print("returning DB connection")
        return cnxn

    except Exception as e:
        print("fatal: Connection to database failed")
        raise Exception("DB connection failed")
    
def searchbox_connect():
    
    url = urlparse(os.environ['SEARCHBOX_URL'])
    ######## test
    es = Elasticsearch(
        [os.environ['SEARCHBOX_URL']],
        http_auth=(url.username, url.password),
        scheme=url.scheme,
        port=url.port,
    )
    return es

######################################################################################
### Data prep functions

es = searchbox_connect()



#########


with connect() as cnxn:
    # Load block info
    datasets_df = dataIO.load_datasets(cnxn)
    dataset_counts = datasets_df[["source", "table", "participant_count", "weighted_participant_count", "Type"]]

    source_info = dataIO.load_source_info(cnxn)
    spine = datasets_df[["source", "table"]].drop_duplicates(subset = ["source", "table"])

    map_data = dataIO.load_map_data(cnxn)

    cnxn.close()

themes = []
for x in list(set(source_info["Themes"])):
    themes += x.split(",")
for y in list(set(datasets_df["topic_tags"].fillna(""))):
    themes += y.split(",")

for  i in range(len(themes)):
    themes[i] = themes[i].replace("\n", "")
    themes[i] = themes[i].strip()
themes = list(set(themes))
themes = sorted(themes, key=str.casefold)
themes.remove("")


gj = dataIO.load_geojson()




def prep_counts(df):
    '''
    apply function
    '''
    if df["count"] == "<10":
        return 10
    elif pd.isna(df["count"]):
        return 0
    return int(df["count"])

def load_or_fetch_map(study):
    df1 = map_data.loc[map_data["source"] == study]
    df1 = df1.drop(["source", "source_stem", "index"], axis=1)
    df2 = pd.DataFrame([[ str(x), y] for x, y in zip(df1.columns, df1.iloc[0].values) ], columns = ["RGN23NM", "count"])
    df2["labels"] = df2["count"]
    df2["labels"].fillna("Not available")
    df2["count"] = df2.apply(prep_counts, axis = 1)
    return df2

######################################################################################

######################################################################################
### page asset templates

# Titlebar ###########################################################################
titlebar = struct.main_titlebar(app, "UK LLC Data Discovery Portal")

# Left Sidebar #######################################################################

sidebar_catalogue = struct.make_sidebar_catalogue(datasets_df)
sidebar_title = struct.make_sidebar_title()
sidebar_left = struct.make_sidebar_left(sidebar_title, sidebar_catalogue)

# Body ################################################################################

maindiv = struct.make_body(sidebar_left, app, spine, themes)

# Main div template ##################################################################

schema_record = struct.make_variable_div("active_source")
table_record = struct.make_variable_div("active_dataset")
current_tab = struct.make_variable_div("current_tab")
selected_tables = struct.make_variable_div("selected_tables")
shopping_basket_op = struct.make_variable_div("shopping_basket", [])
open_schemas = struct.make_variable_div("open_schemas", [])
user = struct.make_variable_div("user", None)
save_clicks = struct.make_variable_div("save_clicks", 0)
placeholder = struct.make_variable_div("placeholder", "placeholder")
account_section = struct.make_account_section()

hidden_body = struct.make_hidden_body(source_info, dataset_counts)

# Variable Divs ####################################################################

###########################################
### Layout
app.layout = struct.make_app_layout(titlebar, maindiv, account_section, [schema_record, table_record, current_tab, shopping_basket_op, open_schemas, hidden_body, user, save_clicks, placeholder], dcc.Location(id='url', refresh=False),)
print("---------------------\nBuilt app layout\n----------------------")
###########################################
### Actions

###########################################

'''
### Login
@app.callback(
    Output('user', "data"),
    Input('account_dropdown','n_clicks'),
    prevent_initial_call=True
)
def login(_):
    print("auth placeholder - do flask or ditch")
'''

### Update titles #########################

#########################

### DOCUMENTATION BOX #####################
'''
efficiency:
approx 995/try all in
'''
@app.callback(
    Output("source_category", "children"), # Source_ type
    Output("study_title", "children"), # Source_name
    Output('source_description_div', "children"), # Aims
    Output("study_summary", "children"), # several variables
    Output("study_table_div", "children"), # list of datasets in source
    Output('source_row', "style"), # style, for hiding/showing body
    Input('active_source','data'),
    #prevent_initial_call = True
)
def update_schema_description(source):
    '''
    When schema updates, update documentation    
    '''        
    
    print("Updating schema page text, schema = '{}'".format(source))
    if source != None and source != "None": 
        
        info = source_info.loc[source_info["source"] == source]
       
        ### title #### 
        source_name = info["source_name"].values[0]
        if info["Type"].values[0] == "Linked":
            title_text1 = "Linked Source"
        else:
            title_text1 = "LPS Source"

        return title_text1, source_name, info["Aims"], struct.make_schema_description(info), struct.make_blocks_table(datasets_df.loc[datasets_df["source"]==source]), {"display": "flex"}
    else:
        
        #print(all_query)
        r = es.search(index="index_spine", body={"query" : {"match_all" : {}}}, size = 1000)

        search_results = []
        for hit in r["hits"]["hits"]:
            search_results.append({key: hit["_source"][key] for key in ["source", "source_name", "Aims"]})
        if len(search_results) >0:
            info = pd.DataFrame(search_results).drop_duplicates(subset=["source"])
            search_results = struct.sources_list(app, info, "main_search")
        else:
            search_results = struct.error_p("No data available")
        return "UK LLC Data Sources", "Browse and select a source for more information", "", "", search_results,  {"display": "none"}


@app.callback(
    Output('Map', "children"), 
    Input("current_tab", "data"),
    Input('active_source','data'),
    prevent_initial_call=True
)
def update_schema_map(current_tab, source):
    '''
    When schema updates, update documentation    
    '''        
    
    print("Updating schema map, schema = '{}'".format(source))
    trigger = dash.ctx.triggered_id

    print(" boxplot trigger {}".format(trigger))
    if source != None and source != "None": 
         ### map #####
        t0 = time.time()
        try:
            data = load_or_fetch_map(source)
            if sum(data["count"]) == 0:
                map = struct.error_p("Coverage is not available for {}".format(source))
            else:
                map = struct.choropleth(data, gj)
        except:
            data = None
            map = struct.error_p("Error loading map")
            print("Error: failed to load map data")
        

        maptime = time.time() - t0
        print("maptime", round(maptime, 3))
        return map
    else:
        return None
    
@app.callback(
    Output('source_linkage_graph', "children"), 
    Input("current_tab", "data"),
    Input('active_source','data'),
    prevent_initial_call=True
)
def update_schema_pie(current_tab, source):
    '''
    When schema updates, update documentation    
    '''        
    
    print("Updating schema pie, schema = '{}'".format(source))
    trigger = dash.ctx.triggered_id

    print(" pie trigger {}".format(trigger))
    if source != None and source != "None": 

        with connect() as cnxn:
            data = dataIO.load_cohort_linkage_groups(cnxn, source)
        ### pie #####
        labels = []
        values = []
        counts = []
        for v, l, d in zip(data["perc"], data["group"], data["count"]):
            if v != 0:
                l = str(l).replace("]","").replace("[","").replace("'","")
                labels.append(l)
                values.append(round(v * 100, 2))
                counts.append(str(d))
        if len(labels) > 0:
            try:
                pie = struct.pie(labels, values, counts)
            except: 
                pie = struct.error_p("Error: unable to make linkage pie")
        else:
            pie = struct.error_p("Linkage statistics are not currently available for {}".format(source))
        
        return pie
    else:
        return ""

@app.callback(
    Output('source_age_graph', "children"), 
    Input("current_tab", "data"),
    Input('active_source','data'),
    prevent_initial_call=True
)
def update_schema_boxplot(current_tab, source):
    '''
    When schema updates, update documentation    
    '''        
    
    print("Updating schema boxplot, schema = '{}'".format(source))
    trigger = dash.ctx.triggered_id

    '''
    if trigger == "active_source" and current_tab != "source":
        print("preventing update of boxplot")
        raise PreventUpdate
    '''
        
    if trigger == None:
        return struct.error_p("Nothing")

    print(" boxplot trigger {}".format(trigger))
    if source != None and source != "None": 

        with connect() as cnxn:
            ages = dataIO.load_cohort_age(cnxn, source)
        ### boxplot #####
        if len(ages["mean"].values) > 0:
            try:
                print("Confirm made boxplot")
                boxplot = struct.boxplot(mean = ages["mean"], median = ages["q2"], q1 = ages["q1"], q3 = ages["q3"], lf = ages["lf"], uf = ages["uf"])
            except Exception as e:
                print(e)
                boxplot = struct.error_p("Error: unable to make age boxplot")
        else:
            boxplot = struct.error_p("Age distribution statistics are not currently available for {}".format(source))
        return boxplot
    else:
        return ""

### Dataset BOX #####################
@app.callback(
    Output('dataset_description_div', "children"), # description text
    Output('dataset_summary', "children"), # variables
    Output('dataset_linkage_graph', "children"),
    Output("dataset_age_graph", "children"),
    Output('dataset_variables_div', "children"),
    Output("dataset_header", "children"),
    Output("dataset_title", "children"),
    Output("dataset_row" , "style"),
    Input('active_dataset', 'data'),
    prevent_initial_update = True
)
def update_table_data(table_id):
    '''
    When table updates
    with current schema
    load table metadata (but not the metadata itself)
    '''
    trigger = dash.ctx.triggered_id

    print("CALLBACK: Dataset BOX - updating table description with table {}, {}".format(table_id, trigger))
    
    #pass until metadata block ready
    if table_id != None and table_id != "None" and trigger:
        table_split = table_id.split("-")
        schema = table_split[0]
        table = table_split[1]
        blocks = datasets_df.loc[(datasets_df["source"] == schema) & (datasets_df["table"] == table)]
        long_desc = blocks["long_desc"].values[0]
        long_name = blocks["table_name"].values[0]


        if blocks["Type"].values[0] == "Linked":
            title_text1 = "Linked Dataset"
        else:
            title_text1 = "LPS Dataset"
        if long_name and len(long_name) > 0:
            title_text2 = str(long_name)
        else:
            title_text2 = str(schema) + " " + str(table)

        blocks = blocks[["table_name", "collection_start", "collection_end", "participants_invited", "participants_included", "topic_tags", "links", ]]
        with connect() as cnxn:
            metadata_df = dataIO.load_study_metadata(cnxn, table_id)[["Variable Name", "Variable Description", "Value","Value Description"]]
            data = dataIO.load_dataset_linkage_groups(cnxn, schema, table)
            ages = dataIO.load_dataset_age(cnxn, schema, table)
            cnxn.close()
        labels = []
        values = []
        counts = []
        for v, l, d in zip(data["perc"], data["group"], data["count"]):
            if v != 0:
                l = str(l).replace("]","").replace("[","").replace("'","")
                labels.append(l)
                values.append(round(v * 100, 2))
                counts.append(str(d))

        if len(labels) > 0:
            pie = struct.pie(labels, values, counts)
        else:
            pie = "Linkage statistics are not currently available for {} {}".format(schema, table)

        
        if len(ages["mean"].values) > 0:
            boxplot = struct.boxplot(mean = ages["mean"], median = ages["q2"], q1 = ages["q1"], q3 = ages["q3"], lf = ages["lf"], uf = ages["uf"])
        else:
            boxplot = "Age distribution statistics are not currently available for {} {}".format(schema, table)
        
        return long_desc, struct.make_block_description(blocks), pie, boxplot, struct.make_table(metadata_df, "block_metadata_table","dataset_info_table"),  title_text1, title_text2, {"display": "flex"}
    else:
        dataset_table = datasets_df[["source", "table", "short_desc"]].rename(columns = {"source":"Source", "table":"Dataset", "short_desc":"Description"})
        search_results_table = struct.make_table(dataset_table, "search_metadata_table", "none_selected")

        return "", "", "", "", search_results_table, "UK LLC Datasets", "Browse and select a source for more information", {"display": "none"}


### BASKET REVIEW #############

@app.callback(
    Output("basket_review_table_div", "children"),
    Output("basket_review_text_div", "children"),
    Output("basket_review_table_div", "style"),
    Output("basket_review_text_div", "style"),
    Input("shopping_basket", "data"),
)
def basket_review(shopping_basket):
    '''
    When the shopping basket updates
    Update the basket review table
    '''
    trigger = dash.ctx.triggered_id
    if trigger == None:
        raise PreventUpdate
    print("CALLBACK: Updating basket review table, trigger {}".format(trigger))
    rows = []
    df = datasets_df
    for table_id in shopping_basket:
        table_split = table_id.split("-")
        source, table = table_split[0], table_split[1]
        
        df1 = df.loc[(df["source"] == source) & (df["table"] == table)]
        try: # NOTE TEMP LINKED OVERRIDE 
            #print(df1.columns)
            row = [source, table, df1["short_desc"].values[0]]
        except IndexError:
            row = [source, table,""]
        rows.append(row)
    df = pd.DataFrame(rows, columns=["source", "table", "long_desc"])
    brtable = struct.basket_review_table(df)
    if len(df) > 0:
        return brtable, "You have {} datasets in your selection".format(len(df)), {"display":"flex"}, {"display":"none"}
    else:
        return brtable, struct.text_block("You currently have no datasets in your selection. Use the checkboxes in the UK LLC Data Catalogue sidebar to add datasets."), {"display":"none"}, {"display":"flex"}


#########################

@app.callback(
    Output("body_content", "children"),
    Output("hidden_body","children"),
    Output("current_tab", "data"),
    #Input("about", "n_clicks"),
    Input("search", "n_clicks"),
    Input("d_overview", "n_clicks"),
    Input("dd_source", "n_clicks"),
    Input("dd_dataset", "n_clicks"),
    Input('source_description_div', "children"), # When the dataset page is updated (means active source has changed and pages have updated)
    Input('dataset_description_div', "children"), # When the dataset page is updated (means active table has changed and pages have updated)
    Input("search2", "n_clicks"),
    Input("overview2", "n_clicks"),
    Input("source2", "n_clicks"),
    Input("dataset2", "n_clicks"),
    Input('url', 'href'),
    State("active_source", "data"),
    State("active_dataset", "data"),
    State("body_content", "children"),
    State("hidden_body","children"),
    State("current_tab", "data"),
    prevent_initial_call=True
)
def body_sections(search, d_overview, dd_source, dd_data_block, _, __, search2, overview2, source2, dataset2, href, schema_change, table_change, active_body, hidden_body, current_state):#, shopping_basket):
    '''
    When the tab changes
    Read the current body
    Read the hidden body
    Update the body
    Update the hidden body
    
    Overhaul 17/10/2023:
    Change the nav bar to a series of drop down menus and buttons
    Body sections listens for all of these buttons
    determine cause by looking at context
    change the body accordingly

    get id of sections. 
    '''
    trigger = dash.ctx.triggered_id

    print("Debug body trigger", trigger, "schema", schema_change, "table", table_change)
    
    if trigger=="url":
        # Parse the URL and extract query parameters
        parsed_url = urlparse(href)
        params = parse_qs(parsed_url.query)
        input_value = params.get('source', [''])
        print(href)
        print("DEBUG input val", input_value)
        if len(input_value) > 0:
            schema_change = input_value
            trigger = "dd_source"
            print("read source from url", input_value)
        else:
            print("No url, preventing update")
            raise PreventUpdate
        print("DEBUG in url branch of body sections")
    

    
    if (schema_change == None or schema_change == "None") and trigger == "source_description_div" : raise PreventUpdate
    if trigger == "source_description_div" and current_state == "source": raise PreventUpdate

    if (table_change == None or table_change == "None") and trigger == "dataset_description_div" : raise PreventUpdate
    print("CALLBACK: body sections, activating", trigger)
    if trigger == "active_source" or trigger == "active_dataset":
        active_tab = active_body[0]["props"]["id"].replace("body_","").replace("dd_", "")

    sections_states = {}
    for section in active_body + hidden_body:
        section_id = section["props"]["id"].replace("body_","").replace("dd_", "")
        sections_states[section_id] = section

    #print(sections_states)
    a_tab_is_active = False
    sections = ["search",
            "overview",
            "source",
            "dataset"]
    active = []
    inactive = []
    for section in sections:
        if section in trigger:
            active.append(section)
            a_tab_is_active = True
        else:
            inactive.append(section)
    # Check: if no tabs are active, run search page
    if not a_tab_is_active:
        print("branch 1")
        return [sections_states["search"], struct.footer(app)],  [sections_states[s_id] for s_id in inactive], "search"
    else:
        print("branch 2")
        return [sections_states[s_id] for s_id in active] + [ struct.footer(app)], [sections_states[s_id] for s_id in inactive], active[0]

@app.callback(
    Output("offcanvas_review", "is_open"),
    Output("modal_background", "style"),
    Output("modal", "is_open"),
    Output("modal_body", "children"),
    Input("review", "n_clicks"),
    Input("modal_background", "n_clicks"),
    Input("FAQ_button", "n_clicks"),
    Input("offcanvas_close", "n_clicks"),
    Input("modal_close", "n_clicks"),
    Input("contact_us", "n_clicks"),
    prevent_initial_call = True
)
def review_right_sidebar(oc_click, bg_click, FAQ_click, oc_close, FAQ_close, cu_clicks):
    if not oc_click and not bg_click and not FAQ_click and not oc_close and not FAQ_close and not cu_clicks:
        raise PreventUpdate
    print("CALLBACK: review", oc_click, dash.ctx.triggered_id)
    trigger = dash.ctx.triggered_id
    if trigger == "modal_background" or trigger == "offcanvas_close" or trigger == "modal_close": # Background, close all
        return False, {"display":"none"}, False, None
    
    if trigger == "review" and oc_click:
        return True, {"display":"flex"}, False, None
    elif trigger == "FAQ_button" and FAQ_click: #modal / FAQs
        return False, {"display":"flex"}, True, struct.FAQ()
    elif trigger == "contact_us" and cu_clicks:
        return False, {"display":"flex"}, True, struct.contact_us()
    else:
        # strange case - after sidebar click, gets past first prevent update. This is second check to make sure not triggered by spawning in.
        raise PreventUpdate



@app.callback(
    Output({'type': 'source_collapse', 'index': MATCH}, 'is_open'),
    Input({'type': 'source_collapse_button', 'index': MATCH}, 'n_clicks'),
    State({'type': 'source_collapse', 'index': MATCH}, 'is_open'),
    prevent_initial_call = True
)
def sidebar_collapse(_, state):
    trigger = dash.ctx.triggered_id
    print("CALLBACK: toggling collapse. Trigger = {}".format(trigger))
    return not state


@app.callback(
    Output('active_source','data'),
    Input({"type": "source_title", "index": ALL}, 'n_clicks'),
    Input({"type": "main_search_source_links", "index": ALL}, 'n_clicks'),
    Input({"type": "source_links", "index": ALL}, 'n_clicks'),
    Input('url', 'href'),
    prevent_initial_call = True
)
def sidebar_schema(open_study_schema, links1, links2, href):
    '''
    When the active item in the accordion is changed
    Read the active schema NOTE with new system, could make active_source redundant
    Read the previous schema
    Read the open schemas.
    '''
    trigger = dash.ctx.triggered_id
    print("CALLBACK: schema change, trigger: {}".format(trigger))# #Trigger:  {}, open_schema = {}, links1 {}, links2 {}".format(trigger, open_study_schema, links1, links2))
    
    
    if trigger=="url":

        # Parse the URL and extract query parameters
        parsed_url = urlparse(href)
        params = parse_qs(parsed_url.query)
        input_value = params.get('source', [''])[0]
        if len(input_value) == 0:
            print("preventing schema update")
            raise PreventUpdate
        return str(input_value)
    else:
    
        real_triggers = [x for x in open_study_schema if (x and x>0)] + [x for x in links1 if (x and x>0)] +[x for x in links2 if (x and x>0)] 
        if len(real_triggers) == 0 :
            raise PreventUpdate

        open_study_schema = trigger["index"]

        return open_study_schema


@app.callback(
    Output('active_dataset','data'),
    Output({"type": "table_tabs", "index": ALL}, 'value'),
    Input({"type": "table_tabs", "index": ALL}, 'value'),
    Input({"type": "search_metadata_table", "index": ALL}, "active_cell"),
    State({"type": "search_metadata_table", "index": ALL}, "data"),
    prevent_initial_call = True
)
def sidebar_table(tables, active_cell, data):
    '''
    When the active table_tab changes
    When the schema changes
    Read the current active table
    Update the active table
    Update the activated table tabs (deactivate previously activated tabs)
    '''
    #print(active_cell)
    #print(data)
    if active_cell and len(active_cell) > 1:
        active_cell = active_cell[1]
        #active_cell_i = active_cell[1]["row"]

        data = data[0]
    if tables == None:
        raise PreventUpdate
    print("\nCALLBACK: sidebar table click, trigger: {},".format(dash.ctx.triggered_id))
    if active_cell and len(active_cell) > 1:
       cell_click = data[active_cell["row"]]["Source"] + "-" + data[active_cell["row"]]["Dataset"]
       print("debug cell click", cell_click)
       return cell_click, ["None" for t in tables]
       
    active = [t for t in tables if (t!= None and t!='None')]
    # if no tables are active
    if len(active) == 0:
        raise PreventUpdate
    # if more than one table is active
    elif len(active) != 1:
        print("Error 12: More than one activated tab:", active)
    
    table = active[0]
    return table, ["None" for t in tables]



@app.callback(
    Output("sidebar_list_div", "children"),
    Output("search_metadata_div", "children"),
    Output("search_text", "children"),
    Output("sidebar_filter", "children"),
    Output("toggle_values", "style"),
    Input("search_button", "n_clicks"),
    Input("main_search", "n_submit"),
    State("main_search", "value"),
    Input("include_dropdown", "value"),
    Input("exclude_dropdown", "value"),
    Input("tags_search", "value"),
    Input("collection_age_slider", "value"),
    Input("collection_time_slider", "value"),
    Input("search_type_radio", "value"),
    Input("include_type_checkbox", "value"),
    Input("toggle_values", "value"),
    State({'type': 'source_collapse', 'index': ALL}, 'id'),
    State({'type': 'source_collapse', 'index': ALL}, 'is_open'),
    State("shopping_basket", "data"),
    State("active_dataset", "data"),
    )
def main_search(click, enter, s, include_dropdown, exclude_dropdown, cl_1, age_slider, time_slider, search_type,include_type, toggle_values, screen_schemas, open_schemas, shopping_basket, table):
    '''
    When the search button is clicked
    read the main search content
    read the include dropdown value
    read the exclude dropdown value 
    read the search_checklist_1 value
    read the collection_age_slider value
    read the collection_time_slider value
    (etc, may be more added later
    Read the current active schema
    Read the current shopping basket
    Read the active table
    Update the sidebar div

    Version 1: search by similar text in schema, table name or keywords. 
    these may be branched into different search functions later, but for now will do the trick
    Do we want it on button click or auto filter?
    Probs on button click, that way we minimise what could be quite complex filtering
    '''
    trigger = dash.ctx.triggered_id

    print("CALLBACK: main search, searching value: {}, trigger {}.".format(s, trigger))
    print("include_type_checklist", include_type)
    #print("     DEBUG search: click {}, {}, {}, {}, {}, {}, {}".format(click, s, include_dropdown, exclude_dropdown, cl_1, age_slider, time_slider))
    # new version 03/1/24 (after a month off so you know its going to be good)
    '''
    Split by table filtering and variable filtering
    table filtering:
        1. Get list of distinct tables
        2. 
    '''
    # Setting up open schemas
    collapse_state = {}
    for sch, open in zip(screen_schemas, open_schemas):
        if open:
            collapse_state[sch["index"]] = True
        else:
            collapse_state[sch["index"]] = False


    #############
    time0 = time.time()

    # 2. include dropdown & type checkboxes
    renamed_include_type = []
    if "Study data" in include_type:
        renamed_include_type.append("LPS")
    if "Linked data" in include_type:
        renamed_include_type.append("Linked")

    if not include_dropdown:
        include_dropdown = spine["source"].drop_duplicates().values
    if not exclude_dropdown:
        exclude_dropdown = []
        must_not = []
    else:
        must_not = [{
                    "bool" : {
                        "should" : [{"term" : { "source" : source}} for source in exclude_dropdown],
                    }
                }
            ]
    
    if len(s) > 0 :
        search = [
            { "regexp": {"table": 
                        {"value" : ".*"+s+".*",
                        "flags" : "ALL",
                        "case_insensitive": "true",
                        "max_determinized_states": 10000,
                    }
                } 
            },
            { "match": {"table_name": s}},
            { "match": {"long_desc": s}},
            { "match": {"topic_tags": s}},
            { "match": {"Aims": s}},
            { "match": {"Themes": s}},
        ]
    else: 
        search = []

    if cl_1 : # Tags:
        tags = [{"term" : { "topic_tags" : tag}} for tag in cl_1] + [{"term" : { "Themes" : tag}} for tag in cl_1]
                
    else:
        tags = []

    collection_times = ["01/1940", "01/1950", "01/1960", "01/1970", "01/1980", "01/1990", "01/2000", "01/2010", "01/2020", "01/2030"]


    # SPINE SEARCH

    all_query = {
        "query": {
            "bool" : {
                "filter":[{
                        "bool" : {
                            "should" : [{"term" : { "source" : source}} for source in include_dropdown] 
                        }
                    },
                    {
                        "bool" : {
                            "should" : tags
                        }
                    },
                ],
                "must_not": must_not,
                
                "must" : [{
                        "bool" : {
                            "should" : search 
                        }
                    },
                    {
                        "bool" : {
                            "should" : [
                                {"range": {
                                    "lf" : {
                                        "gte" :  age_slider[0], # lower range
                                        "lte" :  age_slider[1] # upper range
                                    },
                                }},
                                {"range": {
                                    "q2" : {
                                        "gte" :  age_slider[0], # lower range
                                        "lte" :  age_slider[1] # upper range
                                    },
                                }},
                                {"range": {
                                    "uf" : {
                                        "gte" :  age_slider[0], # lower range
                                        "lte" :  age_slider[1] # upper range
                                    },
                                }},
                            ],
                        }
                    },
                    {
                        "bool" : {
                            "should" : [

                                {"range": {
                                    "collection_start" : {
                                        "gte" : collection_times[time_slider[0]],
                                        "lte" : collection_times[time_slider[1]],
                                        "format" : "MM/YYYY"
                                    }
                                }},
                                {"range": {
                                    "collection_end" : {
                                        "gte" : collection_times[time_slider[0]],
                                        "lte" : collection_times[time_slider[1]],
                                        "format" : "MM/YYYY"
                                    }
                                }},
                    
                            ],
                        }
                    }
                ],

                }
            }
        }

    r1 = es.search(index="index_spine", body=all_query, size = 1000)
    
    sidebar_results = []
    for hit in r1["hits"]["hits"]:
        #print(hit)
        sidebar_results.append({key: hit["_source"][key] for key in ["source", "source_name", "table", "table_name", "Type"]})
    if len(sidebar_results) == len(spine):
        sidebar_text= "Showing full catalogue"
    else:
        sidebar_text = "Hiding {} datasets from search filters".format(len(spine) - len(sidebar_results))

    toggle_values_style = {"display" : "none"}

    # only if searching by source
    if search_type.lower() == "sources":

        search_results = []
        for hit in r1["hits"]["hits"]:
            search_results.append({key: hit["_source"][key] for key in ["source", "source_name", "Aims", "Type"]})
        if len(search_results) != 0:
            info = pd.DataFrame(search_results).drop_duplicates(subset=["source"])
            search_results_table = struct.sources_list(app, info, "main_search")
            search_text = "Showing {} data sources".format(len(set(info["source"])))
        else:
            search_results_table = None
            search_text = "No results"


    elif search_type.lower() == "datasets": 
        # reuse sidebar results
        search_results = []
        for hit in r1["hits"]["hits"]:
            search_results.append({key: hit["_source"][key] for key in ["source", "table"]})
        if len(search_results) != 0:
            info = pd.DataFrame(search_results)
            info = pd.merge(info, datasets_df, how="left", on = ["source", "table"]) 

            info = info[["source", "table", "short_desc"]].rename(columns={"source":"Source", "table": "Dataset", "short_desc": "Description"}) 
            search_results_table = struct.make_table(info, "search_metadata_table", "datasets_search")
            search_text = "Showing {} datasets".format(len(info))
        else:
            search_results_table = None
            search_text = "No results"

    elif search_type.lower() == "variables": # variables
        '''
        TODO 02/07/2024
        This is too slow. I think its the volume of values & desks. 
        1. Test if this is the case. Measure search time & build time separately
        2. Provided search time isn't the major issue, move to memory all_metadata and try to efficiently join return ids on that.
        3. Store current returned response table in memory and immediately provided if the search terms have not changed
            Likely requires storing the search terms as well as the table
        ----
        ok, suddenly its performing well. Suspicious... I'll keep my eye on you
        but point remains, build time is approx .1-.2 seconds. Not great, but not terrible. We can live with that. Main thing is search.
        '''


        if len(s) > 0 :
            search = [{ "term": {"topic_tags": s}},
                { "term": {"Themes": s}},
                {"match" : {"variable_name" : s}},
                { "regexp": {"variable_name": 
                        {"value" : ".*"+s+".*",
                        "flags" : "ALL",
                        "case_insensitive": "true",
                        "max_determinized_states": 10000,
                    }
                } 
            },
                {"match" : {"variable_description" : s}},
                #{"term" : {"value" : s}},
                #{"match" : {"value_label" : s}},
            ]
            
        all_query2 = {
        "query": {
            "bool" : {
                "filter":[{
                        "bool" : {
                            "should" : [{"term" : { "source" : source.lower()}} for source in include_dropdown] 
                        }
                    },
                    {
                        "bool" : {
                            "should" : tags
                        }
                    },
                ],
                "must_not": must_not,
                
                "must" : [{
                        "bool" : {
                            "should" : search,
                            "boost" : 3, 
                        }
                    },
                    {
                        "bool" : {
                            "should" : [
                                {"range": {
                                    "lf" : {
                                        "gte" :  age_slider[0], # lower range
                                        "lte" :  age_slider[1] # upper range
                                    },
                                }},
                                {"range": {
                                    "q2" : {
                                        "gte" :  age_slider[0], # lower range
                                        "lte" :  age_slider[1] # upper range
                                    },
                                }},
                                {"range": {
                                    "uf" : {
                                        "gte" :  age_slider[0], # lower range
                                        "lte" :  age_slider[1] # upper range
                                    },
                                }},
                            ],
                        }
                    },
                    {
                        "bool" : {
                            "should" : [

                                {"range": {
                                    "collection_start" : {
                                        "gte" : collection_times[time_slider[0]],
                                        "lte" : collection_times[time_slider[1]],
                                        "format" : "MM/YYYY"
                                    }
                                }},
                                {"range": {
                                    "collection_end" : {
                                        "gte" : collection_times[time_slider[0]],
                                        "lte" : collection_times[time_slider[1]],
                                        "format" : "MM/YYYY"
                                    }
                                }
                            },
                    
                            ],
                        }
                    }
                ],

                }
            }
        }
        time0 = time.time()
        r2 = es.search(index="index_var", body=all_query2, size = 1000)
        search_time = time.time() - time0
        time1 = time.time()
        search_results = []
        if "Show values" in toggle_values:
            for hit in r2["hits"]["hits"]:
                search_results.append([hit["_source"]["source"], hit["_source"]["table"], hit["_source"]["variable_name"], hit["_source"]["variable_description"], hit["_source"]["value"], hit["_source"]["value_label"]])
        else:
            for hit in r2["hits"]["hits"]:
                search_results.append([hit["_source"]["source"], hit["_source"]["table"], hit["_source"]["variable_name"], hit["_source"]["variable_description"]])

        if len(search_results) != 0:
            if "Show values" in toggle_values: 
                search_results = pd.DataFrame(search_results, columns=["Source", "Table", "Variable Name", "Variable Description", "Value", "Value Label"])
            else:
                search_results = pd.DataFrame(search_results, columns=["Source", "Table", "Variable Name", "Variable Description"])
     
            search_results_table = struct.make_table(search_results, "search_variable_table", "dataset search")
            search_len = len(search_results)
        
            if len(search_results) >= 1000:
                search_text = "Seach limited to the first 1000 variables"
            else:    
                search_text = "Showing {} variables".format(search_len)
        else:
            search_results_table = None
            search_text = "No results"
        build_time = time.time() - time1

        print("search time: {}\nbuild time: {}".format(round(search_time, 3), round(build_time, 3)))

        toggle_values_style = {"display" : "flex"}

    else:
        search_results = "ERROR: 786, this shouldn't be reachable ", search_type 

    if len(sidebar_results) > 0:
        sidebar_results_df = pd.DataFrame(sidebar_results)
        sidebar_results_df = sidebar_results_df[["source", "source_name", "table", "table_name", "Type"]]
    else:
        sidebar_results_df = pd.DataFrame(data = {"source": [], "source_name" :[], "table": [], "table_name": [], "Type":[]})

    print(toggle_values_style)
    return struct.build_sidebar_list(sidebar_results_df, shopping_basket, collapse_state, table), search_results_table, search_text, sidebar_text, toggle_values_style



@app.callback(
    Output('shopping_basket','data'),
    Output('search_button', "n_clicks"),
    Output("selection_count", "children"),
    Input({"type": "shopping_checklist", "index" : ALL}, "value"),
    Input('basket_review_table', 'data'),
    Input("clear_basket_button", "n_clicks"),
    State("shopping_basket", "data"),
    State('search_button', "n_clicks"),
    prevent_initial_call=True
    )
def shopping_cart(selected, current_data, b1_clicks, shopping_basket, clicks):
    '''
    When the value of the shopping checklist changes
    When the basket review table changes
    When the clear all button is clicked
    Read the current shopping basket
    Read the search button clicks
    Update the shopping basket
    Update the number of search button clicks

    Update the shopping cart and update the basket review section if not already active
    '''
    print("CALLBACK: Shopping cart. Trigger: {}".format(dash.ctx.triggered_id))
    if dash.ctx.triggered_id == "basket_review_table":# If triggered by basket review
        if current_data != None:
            keys = []
            for item in current_data:
                keys.append(item["source"] + "-" + item["table"])

            new_shopping_basket = [item for item in shopping_basket if item in keys]

            if new_shopping_basket == shopping_basket:
                raise PreventUpdate
            else:
                if clicks == None:
                    return new_shopping_basket, 1, "("+ str(len(new_shopping_basket))+")"
                else:
                    return new_shopping_basket, clicks+1, "("+ str(len(new_shopping_basket))+")"
        else:
            raise PreventUpdate
    
    elif dash.ctx.triggered_id == "clear_basket_button": # if triggered by clear button
        if b1_clicks > 0:
            #print(b1_clicks, shopping_basket)
            return [], 1, ""
        else:
            raise PreventUpdate

    else: # if triggered by checkboxes
        if len(dash.ctx.triggered_prop_ids) == 1: # if this is triggered by a change in only 1 checkbox group
            # We don't want to update if the callback is triggered by a sidebar refresh
            # Only update if only 1 checkbox has changed
            checked = []
            for i in selected:
                checked += i
            difference1 = list(set(shopping_basket) - set(checked))
            difference2 = list(set(checked) - set(shopping_basket))
            difference = difference1 + difference2
            if len(difference) == 1: # avoid updating unless caused by a click on a checkbox (search could otherwise trigger this)
                new_item = difference[0]
                if new_item in shopping_basket:
                    shopping_basket.remove(new_item)
                else:
                    shopping_basket.append(new_item)
                return shopping_basket, dash.no_update, "("+ str(len(shopping_basket))+")"
            elif len(difference1) > 0 and len(difference2) == 1:# Case: we are in a search (hiding checked boxes) and added a new item
                new_item = difference2[0]
                shopping_basket.append(new_item)
                return shopping_basket, dash.no_update, "("+ str(len(shopping_basket))+")"
            else:
                raise PreventUpdate
        else:
            raise PreventUpdate


@app.callback(
    Output('sb_download','data'),
    Output("save_clicks", "data"),
    Input("save_button", "n_clicks"),
    #Input("dl_button_2", "n_clicks"),
    State("save_clicks", "data"),
    State("shopping_basket", "data"),
    prevent_initial_call=True
    )
def save_shopping_cart(btn1, save_clicks, shopping_basket):
    '''
    When the save button is clicked
    Read the shopping basket
    Download the shopping basket as a csv
    '''
    print("CALLBACK: Save shopping cart. Trigger: {}".format(dash.ctx.triggered_id))
    #print(btn1, save_clicks)
    if btn1 != save_clicks or dash.ctx.triggered_id == "dl_button_2":
        # TODO insert checks to not save if the shopping basket is empty or otherwise invalid
        fileout = dataIO.basket_out(shopping_basket)
        return dcc.send_data_frame(fileout.to_csv, "data_selection.csv"), btn1
    else:
        raise PreventUpdate


@app.callback(
    Output("main_search", "value"),
    Output("include_dropdown", "value"),
    Output("exclude_dropdown", "value"),
    Output("tags_search", "value"),
    Output("collection_age_slider", "value"),
    Output("collection_time_slider", "value"),

    Output("include_type_checkbox", "value"),

    Input("clear_search1", "n_clicks"),
    Input("clear_search2", "n_clicks"),
    prevent_initial_call=True
    )
def rest_filters(btn1, btn2):
    return "", "", "", "", [0, 100], [0, 9], ["Study data", "Linked data"]


'''
@app.callback(
    Output("placeholder","data"),
    Input("app","n_clicks"),
    State("shopping_basket", "data")   
)
def basket_autosave(_, sb):
    path = os.path.join("saves", request.authorization['username'])
    if not os.path.exists(path):
        os.mkdir(path)
    with open(os.path.join(path, "SB"), 'wb') as f:
        pickle.dump(sb, f)
'''    





if __name__ == "__main__":
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    pd.options.mode.chained_assignment = None
    warnings.simplefilter(action="ignore",category = FutureWarning)
    app.run_server(port=8888, debug = False)


'''

------------
TODO

For search have a granularity filter - don't return variables on a DS level

'''

