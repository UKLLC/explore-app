# sidebar.py
import re
import dash
from dash import dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
from dash import Input, Output, State, ALL
import warnings
import logging
from dash.exceptions import PreventUpdate
#import dash_auth
from flask import request
import plotly.express as px
import plotly.graph_objects as go
import sqlalchemy
import whoosh
from whoosh import fields, index
from whoosh.fields import Schema, TEXT, KEYWORD, ID, STORED
from whoosh.analysis import StemmingAnalyzer
from whoosh import qparser
from whoosh.qparser import QueryParser
from whoosh.filedb.filestore import FileStorage



from app_state import App_State
import dataIO
import constants 
import structures as struct

import time


######################################################################################
app = dash.Dash(__name__, external_stylesheets=["custom.css",  dbc.icons.BOOTSTRAP ])
server = app.server

def connect():
    try:
        cnxn = sqlalchemy.create_engine('mysql+pymysql://bq21582:password_password@127.0.0.1:3306/ukllc').connect()
        return cnxn

    except Exception as e:
        print("Connection to database failed, retrying.")
        raise Exception("DB connection failed")

######################################################################################
### Data prep functions

request_form_url = "https://uob.sharepoint.com/:x:/r/teams/grp-UKLLCResourcesforResearchers/Shared%20Documents/General/1.%20Application%20Process/2.%20Data%20Request%20Forms/Data%20Request%20Form.xlsx?d=w01a4efd8327f4092899dbe3fe28793bd&csf=1&web=1&e=reAgWe"
# request url doesn't work just yet
with connect() as cnxn:
    # Load block info
    datasets_df = dataIO.load_datasets(cnxn)
    dataset_counts = datasets_df[["source", "table", "participant_count", "weighted_participant_count" ]]
    spine = datasets_df[["source", "table"]].drop_duplicates()
    source_info = dataIO.load_source_info(cnxn)

    cnxn.close()

app_state = App_State()


def load_or_fetch_map(study):
    returned_data = app_state.get_map_data(study) # memorisation of polygons
    if not returned_data: # if no saved map data, returns False
        try:
            returned_data = dataIO.get_map_overlays(study)
        except IOError:
            print("Unable to load map file {}.geojson".format(study))
        app_state.set_map_data(study, returned_data)
    return returned_data

######################################################################################
### index
storage_var = FileStorage("index_var")
storage_var.open_index()

storage_spine = FileStorage("index_spine")
storage_spine.open_index()

ix_var = whoosh.index.open_dir('index_var')
ix_spine = whoosh.index.open_dir('index_spine')
searcher_var = ix_var.searcher()
searcher_spine = ix_spine.searcher()

######################################################################################
### page asset templates

# Titlebar ###########################################################################
titlebar = struct.main_titlebar(app, "UK LLC Data Discovery Portal")

# Left Sidebar #######################################################################

sidebar_catalogue = struct.make_sidebar_catalogue(datasets_df)
sidebar_title = struct.make_sidebar_title()
sidebar_left = struct.make_sidebar_left(sidebar_title, sidebar_catalogue)

# Body ################################################################################

maindiv = struct.make_body(sidebar_left, app, spine)

# Main div template ##################################################################

schema_record = struct.make_variable_div("active_schema")
table_record = struct.make_variable_div("active_table")
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
app.layout = struct.make_app_layout(titlebar, maindiv, account_section, [schema_record, table_record, shopping_basket_op, open_schemas, hidden_body, user, save_clicks, placeholder])
print("Built app layout")
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

@app.callback(
    Output("study_title", "children"),
    Output('study_description_div', "children"),
    Output("study_summary", "children"),
    Output("study_table_div", "children"),
    Output("source_linkage_graph", "children"),
    Output("source_age_graph", "children"),
    Output('map_region', "data"),
    Output('map_object', 'zoom'),
    Output('source_row', "style"),
    Input('active_schema','data'),
)
def update_schema_description(source):
    '''
    When schema updates, update documentation    
    '''        
    print("Updating schema page, schema = '{}'".format(source))
    if source != None and source != "None": 
        
        info = source_info.loc[source_info["source"] == source]

        with connect() as cnxn:
            data = dataIO.load_cohort_linkage_groups(cnxn, source)
            ages = dataIO.load_cohort_age(cnxn, source)
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

        pie = struct.pie(labels, values, counts)

        if ages["mean"].values[0]:
            boxplot = struct.boxplot(mean = ages["mean"], median = ages["q2"], q1 = ages["q1"], q3 = ages["q3"], sd = ages["std"], lf = ages["lf"], uf = ages["uf"])
        else:
            boxplot = "Age distribution is not available for this cohort"

        map_data = load_or_fetch_map(source)
        return "Study Information - "+source, info["Aims"], struct.make_schema_description(info), struct.make_blocks_table(blocks), pie, boxplot, map_data, 6, {"display": "flex"}
    else:
        # If a study is not selected (or if its NHSD), list instructions for using the left sidebar to select a study.
        
        qp = qparser.QueryParser("all", ix_spine.schema)
        q = qp.parse("1")

        r = searcher_spine.search(q, collapse = "source", collapse_limit = 1, limit = None)
        search_results = []
        for hit in r:
            search_results.append({key: hit[key] for key in ["source", "LPS_name", "Aims"]})
        info = pd.DataFrame(search_results)
        search_results = struct.sources_list(app, info, "main_search")
        return "UK LLC Data Sources", "", "", search_results, "", "",None, 6, {"display": "none"}


### Dataset BOX #####################
@app.callback(
    Output('dataset_description_div', "children"),
    Output('dataset_summary', "children"),
    Output('dataset_linkage_graph', "children"),
    Output("dataset_age_graph", "children"),
    Output('dataset_variables_div', "children"),
    Input('active_table', 'data'),
    State('active_schema', 'data'),
    prevent_initial_call=True
)
def update_table_data(table_id, schema):
    '''
    When table updates
    with current schema
    load table metadata (but not the metadata itself)
    '''
    print("CALLBACK: Dataset BOX - updating table description with table {}".format(table_id))
    #pass until metadata block ready
    if schema != None and table_id != None:
        table_split = table_id.split("-")
        table = table_split[1]
        blocks = datasets_df.loc[(datasets_df["source"] == schema) & (datasets_df["table"] == table)]
        long_desc = blocks["long_desc"]

        blocks = blocks[["table_name", "collection_start", "collection_end", "participants_included", "topic_tags", "links", ]]
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

        pie = struct.pie(labels, values, counts)

        
        if ages["mean"].values[0]:
            boxplot = struct.boxplot(mean = ages["mean"], median = ages["q2"], q1 = ages["q1"], q3 = ages["q3"], sd = ages["std"], lf = ages["lf"], uf = ages["uf"])
        else:
            boxplot = "Age distribution is not available for this cohort"

        return long_desc, struct.make_block_description(blocks), pie, boxplot, struct.make_table(metadata_df, "block_metadata_table")
    else:
        # Default (Section may be hidden in final version)
        return "Select a dataset for more information...", "", "", "", ""

'''
@app.callback(
    Output('table_metadata_div', "children"),
    Input("values_toggle", "value"),
    Input("metadata_search", "value"),
    Input('active_table','data'),
    prevent_initial_call=True
)
def update_table_metadata(values_on, search, table_id):
    
    When table updates
    When values are toggled
    When metadata is searched
    update metadata display
    
    print("CALLBACK: META BOX - updating table metadata with active table {}".format(table_id))
    if table_id == None:
        raise PreventUpdate
    try:
        metadata_df = dataIO.load_study_metadata(table_id)
    except FileNotFoundError: # Study has changed 
        print("Failed to load {}.csv. ".format(table_id))
        return html.Div([html.P("No metadata available for {}.".format(table_id)),],className="container_box"),

    if type(values_on) == list and len(values_on) == 1:
        metadata_df = metadata_df[["Block Name", "Variable Name", "Variable Description", "Value", "Value Description"]]
        if type(search) == str and len(search) > 0:
            metadata_df = metadata_df.loc[
            (metadata_df["Block Name"].str.contains(search, flags=re.IGNORECASE)) | 
            (metadata_df["Variable Name"].str.contains(search, flags=re.IGNORECASE)) | 
            (metadata_df["Variable Description"].str.contains(search, flags=re.IGNORECASE)) |
            (metadata_df["Value"].astype(str).str.contains(search, flags=re.IGNORECASE)) |
            (metadata_df["Value Description"].str.contains(search, flags=re.IGNORECASE))
            ]
    else:
        metadata_df = metadata_df[["Block Name", "Variable Name", "Variable Description"]].drop_duplicates()
        if type(search) == str and len(search) > 0:
            metadata_df = metadata_df.loc[
            (metadata_df["Block Name"].str.contains(search, flags=re.IGNORECASE)) | 
            (metadata_df["Variable Name"].str.contains(search, flags=re.IGNORECASE)) | 
            (metadata_df["Variable Description"].str.contains(search, flags=re.IGNORECASE)) 
            ]
    print("DEBUG: reached end of bottom metadata")
    metadata_table = struct.metadata_table(metadata_df, "metadata_table")
    return metadata_table
'''




### BASKET REVIEW #############

@app.callback(
    Output("basket_review_table_div", "children"),
    Input("shopping_basket", "data"),
    prevent_initial_call=True
)
def basket_review(shopping_basket):
    '''
    When the shopping basket updates
    Update the basket review table
    '''
    trigger = dash.ctx.triggered_id
    print("CALLBACK: Updating basket review table, trigger {}".format(trigger))
    rows = []
    df = datasets_df
    for table_id in shopping_basket:
        table_split = table_id.split("-")
        source, table = table_split[0], table_split[1]
        
        df1 = df.loc[(df["source"] == source) & (df["table"] == table)]
        try: # NOTE TEMP LINKED OVERRIDE 
            print(df1.columns)
            row = [source, table, df1["short_desc"].values[0]]
        except IndexError:
            row = [source, table,""]
        rows.append(row)
    df = pd.DataFrame(rows, columns=["source", "table", "long_desc"])
    brtable = struct.basket_review_table(df)
    return brtable


#########################

@app.callback(
    Output("body_content", "children"),
    Output("hidden_body","children"),
    #Input("about", "n_clicks"),
    Input("search", "n_clicks"),
    Input("d_overview", "n_clicks"),
    Input("dd_study", "n_clicks"),
    Input("dd_dataset", "n_clicks"),
    Input("review", "n_clicks"),
    Input('study_description_div', "children"), # When the dataset page is updates (means active source has changed and pages have updated)
    Input('dataset_description_div', "children"), # When the dataset page is updates (means active table has changed and pages have updated)
    State("active_schema", "data"),
    State("active_table", "data"),
    State("body_content", "children"),
    State("hidden_body","children"),
    prevent_initial_call=True
)
def body_sections(search, d_overview, dd_study, dd_data_block, review, _, __, schema_change, table_change, active_body, hidden_body):#, shopping_basket):
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

        
    print("CALLBACK: body sections, activating", trigger)
    if (schema_change == None or schema_change == "None") and trigger == "study_description_div" : raise PreventUpdate
    #if (table_change == None or table_change == "None") and trigger == "dataset_description_div" : raise PreventUpdate
    if trigger == "active_schema" or trigger == "active_table":
        active_tab = active_body[0]["props"]["id"].replace("body_","").replace("dd_", "")

        #TODO Should there be some toggle or condition to stop force change?
        if trigger == "active_schema":# and schema_change != current_id:
            trigger = "dd_study"
        elif trigger == "active_table":
            trigger = "dd_dataset"
        else:
            raise PreventUpdate

    sections_states = {}
    for section in active_body + hidden_body:
        section_id = section["props"]["id"].replace("body_","").replace("dd_", "")
        sections_states[section_id] = section

    #print(sections_states)
    a_tab_is_active = False
    sections = app_state.sections
    active = []
    inactive = []
    for section in sections.keys():
        if section in trigger:
            active.append(section)
            a_tab_is_active = True
        else:
            inactive.append(section)
    # Check: if no tabs are active, run search page
    if not a_tab_is_active:
        return [sections_states["search"], struct.footer(app)],  [sections_states[s_id] for s_id in inactive]
    else:
        return [sections_states[s_id] for s_id in active] + [ struct.footer(app)], [sections_states[s_id] for s_id in inactive]


@app.callback(
    Output('active_schema','data'),
    Input("schema_accordion", "active_item"),
    Input({"type": "main_search_source_links", "index": ALL}, 'n_clicks'),
    Input({"type": "source_links", "index": ALL}, 'n_clicks'),
    State("active_schema", "data"),
    prevent_initial_call = True
)
def sidebar_schema(open_study_schema, links1, links2, previous_schema):
    '''
    When the active item in the accordion is changed
    Read the active schema NOTE with new system, could make active_schema redundant
    Read the previous schema
    Read the open schemas.
    '''
    trigger = dash.ctx.triggered_id
    
    print("CALLBACK: sidebar schema click. Trigger:  {}, open_schema = {}".format(trigger, open_study_schema))

    if len( dash.callback_context.triggered) > 1: raise PreventUpdate
    #print("DEBUG, sidebar_schema {}, {}, {}".format(open_study_schema, previous_schema, dash.ctx.triggered_id))
    if type(trigger) == dash._utils.AttributeDict:
        print("Source updated by search click")
        open_study_schema = trigger["index"]
    if open_study_schema == previous_schema:
        print("Schema unchanged, preventing update")
        raise PreventUpdate
    else:
        return open_study_schema


@app.callback(
    Output('active_table','data'),
    Output({"type": "table_tabs", "index": ALL}, 'value'),
    Input({"type": "table_tabs", "index": ALL}, 'value'),
    State("active_table", "data"),
    prevent_initial_call = True
)
def sidebar_table(tables, previous_table):
    '''
    When the active table_tab changes
    When the schema changes
    Read the current active table
    Update the active table
    Update the activated table tabs (deactivate previously activated tabs)
    '''
    print("CALLBACK: sidebar table click, trigger: {}".format(dash.ctx.triggered_id))
    #print("DEBUG, sidebar_table {}, {}, {}".format(tables, previous_table, dash.ctx.triggered_id))

    active = [t for t in tables if t!= None]
    # if no tables are active
    if len(active) == 0:
        if previous_table == None:
            raise PreventUpdate
        return None, tables
    # if more than one table is active
    elif len(active) != 1:
        active = [t for t in active if t != previous_table ]
        if len(active) == 0:
            raise PreventUpdate
        tables = [(t if t in active else None) for t in tables]
        if len(active) != 1:
            print("Error 12: More than one activated tab:", active)
    
    table = active[0]
    if table == previous_table:
        print("Table unchanged, preventing update")
        raise PreventUpdate

    return table, tables 
    

@app.callback(
    Output("sidebar_list_div", "children"),
    Output("search_metadata_div", "children"),
    Input("search_button", "n_clicks"),
    State("main_search", "value"),
    State("include_dropdown", "value"),
    State("exclude_dropdown", "value"),
    State("search_checklist_1", "value"),
    State("collection_age_slider", "value"),
    State("collection_time_slider", "value"),
    Input("search_type_radio", "value"),
    State("active_schema", "data"),
    State("shopping_basket", "data"),
    State("active_table", "data"),
    )
def main_search(_, s, include_dropdown, exclude_dropdown, cl_1, age_slider, time_slider, search_type,  open_schemas, shopping_basket, table):
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
    print("CALLBACK: main search, searching value: {}, trigger {}.".format(s, dash.ctx.triggered_id))
    print("     DEBUG search: {}, {}, {}, {}, {}, {}".format(s, include_dropdown, exclude_dropdown, cl_1, age_slider, time_slider))

    # new version 03/1/24 (after a month off so you know its going to be good)
    '''
    Split by table filtering and variable filtering
    table filtering:
        1. Get list of distinct tables
        2. 
    '''

    # new version 25/03/24 (indexing )
    '''
    Possible fields: 
    source
    LPS_name 
    table
    table_name
    variable_name 
    variable_description
    value
    value_label
    long_desc 
    topic_tags 
    collection_start
    collection_end 
    lf 
    uf 
    Aims 
    Themes 
    '''
    # 1. general search 
    # source, LPS_name, table, table_name, variable_name, variable_description, long_desc, topic_tags, Aims, Themes


    time0 = time.time()

    # 2. include dropdown
    if include_dropdown:
        print("INCLUDE (TEMP LOCKED TO FIRST FOR DEBUG)")
        allow_q = whoosh.query.Or([whoosh.query.Term("source", i) for i in include_dropdown])  # TODO EXPAND TO MORE THAN ONE
        #allow_q = whoosh.query.Term("source", include_dropdown[0]) 
    else:
        print("No include")
        allow_q = None
    # 3. exclude dropdown
    if exclude_dropdown:
        print("EXCLUDe (TEMP LOCKED TO FIRST FOR DEBUG)")
        restict_q =  whoosh.query.Or([whoosh.query.Term("source", i) for i in exclude_dropdown]) # TODO EXPAND TO MORE THAN ONE
        #restict_q = whoosh.query.Term("source", exclude_dropdown[0])
    else:
        print("No exclude")
        restict_q = None
    # Age slider TODO

    #time slider TODO

    ####
    # if no search query, return all, potentially filtered by allow_q, restrict_q etc

    # Always do dataset level (for sidebar):
    if len(s) == 0:
        print("DEUBG: no query")
        qp = qparser.QueryParser("all", ix_spine.schema)
        q = qp.parse("1")
    else:
        print("DEUBG: query = {}".format(s))
        qp = qparser.MultifieldParser(["source", "LPS_name", "table", "table_name", "long_desc", "topic_tags", "Aims", "Themes"], ix_spine.schema, group=qparser.OrGroup)
        qp.add_plugin(qparser.FuzzyTermPlugin())
        q = qp.parse(str(s)+str("~1/3"))

    r = searcher_spine.search(q, filter = allow_q, mask = restict_q, collapse = "table", limit = None)
    sidebar_results = []
    for hit in r:
        sidebar_results.append({key: hit[key] for key in ["source", "table"]})

    # only if searching by source
    if search_type.lower() == "sources":
        if len(s) == 0:
            qp = qparser.QueryParser("all", ix_spine.schema)
            q = qp.parse("1")
        else:
            qp = qparser.MultifieldParser(["source", "LPS_name", "table", "table_name", "long_desc", "topic_tags", "Aims", "Themes"], ix_spine.schema, group=qparser.OrGroup)
            qp.add_plugin(qparser.FuzzyTermPlugin())
            q = qp.parse(str(s)+str("~1/3"))
    
        r = searcher_spine.search(q, filter = allow_q, mask = restict_q, collapse = "source", limit = None)
        search_results = []
        for hit in r:
            search_results.append({key: hit[key] for key in ["source", "LPS_name", "Aims"]})

        info = pd.DataFrame(search_results).drop_duplicates(subset=["source"])
        search_results_table = struct.sources_list(app, info, "main_search")
        #TODO HELLO THIS IS CONFUSING AND WEIRD. Why??

    elif search_type.lower() == "datasets": 
        # reuse sidebar results
        search_results = sidebar_results
        search_results_table = struct.make_table_dict(search_results, "search_metadata_table")


    elif search_type.lower() == "variables": # variables
        time1 = time.time()
        if len(s) == 0: # TODO and other terms
            qp = qparser.QueryParser("all", ix_var.schema)
            q = qp.parse("1")
        else:
            qp = qparser.MultifieldParser(["source", "table", "variable_name", "variable_description", "value", "value_label", "topic_tags"], ix_var.schema, group=qparser.OrGroup)
            qp.add_plugin(qparser.FuzzyTermPlugin())
            q = qp.parse(str(s)+str("~1/3"))
        r = searcher_var.search(q, filter = allow_q, mask = restict_q, limit = 10000)
        search_results = []
        for hit in r:
            search_results.append({key: hit[key] for key in ["source", "table", "variable_name", "variable_description", "value", "value_label"]})
        time2 = time.time()
        print("DEBUG: time to run search function: {} seconds".format(round(time2-time1, 3)))

        search_results_table = struct.make_table_dict(search_results, "search_metadata_table")

    else:
        search_results = "ERROR: 786, this shouldn't be reachable ", search_type 

    sidebar_results_df = pd.DataFrame(sidebar_results)
    sidebar_results_df = sidebar_results_df[["source", "table"]]

    timex = time.time()
    print("DEBUG: time to run search function: {} seconds".format(round(timex-time0, 3)))

    return struct.build_sidebar_list(sidebar_results_df, shopping_basket, open_schemas, table), search_results_table



@app.callback(
    Output('shopping_basket','data'),
    Output('search_button', "n_clicks"),
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
                    return new_shopping_basket, 1
                else:
                    return new_shopping_basket, clicks+1
        else:
            raise PreventUpdate
    
    elif dash.ctx.triggered_id == "clear_basket_button": # if triggered by clear button
        if b1_clicks > 0:
            print(b1_clicks, shopping_basket)
            if clicks == None:
                return [], clicks+1
            else:
                return [], 1
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
                return shopping_basket, dash.no_update
            elif len(difference1) > 0 and len(difference2) == 1:# Case: we are in a search (hiding checked boxes) and added a new item
                new_item = difference2[0]
                shopping_basket.append(new_item)
                return shopping_basket, dash.no_update
            else:
                raise PreventUpdate
        else:
            raise PreventUpdate


@app.callback(
    Output('sb_download','data'),
    Output("save_clicks", "data"),
    Input("save_button", "n_clicks"),
    Input("dl_button_2", "n_clicks"),
    State("save_clicks", "data"),
    State("shopping_basket", "data"),
    prevent_initial_call=True
    )
def save_shopping_cart(btn1, btn2, save_clicks, shopping_basket):
    '''
    When the save button is clicked
    Read the shopping basket
    Download the shopping basket as a csv
    '''
    print("CALLBACK: Save shopping cart. Trigger: {}".format(dash.ctx.triggered_id))
    print(btn1, save_clicks)
    if btn1 != save_clicks or dash.ctx.triggered_id == "dl_button_2":
        # TODO insert checks to not save if the shopping basket is empty or otherwise invalid
        fileout = dataIO.basket_out(shopping_basket)
        print("DOWNLOAD")
        return dcc.send_data_frame(fileout.to_csv, "shopping_basket.csv"), btn1
    else:
        raise PreventUpdate

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

@app.callback(
    Output("sidebar-collapse", "is_open"),
    [Input("sidebar-collapse-button", "n_clicks")],
    [State("sidebar-collapse", "is_open")],
    prevent_initial_call=True
)
def toggle_collapse(n, is_open):
    print("Toggling sidebar")
    if n:
        return not is_open
    return is_open


if __name__ == "__main__":
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    pd.options.mode.chained_assignment = None
    warnings.simplefilter(action="ignore",category = FutureWarning)
    app.run_server(port=8888, debug = True)


'''
TODO 27/02/2024
- Left sidebar collapse styling 
- Left sidebar arrow styling
- Left sidebar search filter status

- Search page, fix page dimensions

- Data overview, design & style the window
- Capture the data by unique participant at the inner layer.
- Split NHS, Geo, ... & LPS
-   Think of variants and options:
-       There is no sense filtering the graph - that does it itself
-       Instead, just make sure the counts at each level are of unique participants
-       Add (collapsible) tooltip for tutorial
- look into zooming on the canvas

- Linked data alternative page

- Style the basket review page

- Build in account login
- Add autosave

- hover tooltips on sidebar with full source and dataset name.

- add link to pages in tables etc (click sociodemo in source view, goto dataset view)
- show source in dataset view

- Make mental health style listing when no study is selected

- Add footer with 1 row. UOB, UOE, collaborators. 


28/02/24 tasks:
1. Get study linkage breakdown graph in (make generic graph function). -------------
    Means we have to make a sub tabs section ------------
2. Remove about page. ------------
3. Make linkage breakdown graphs scale appropriately.

08/03/24 afternoon tasks:
Add footer with requested images.

12/3/24 Tiny last half hour:
Get the collapse button looking better
cont. tomorrow

18/03/24 afternoon:
Get the study list callback to doc page work
Put the study list in unslected doc page
Filter the study list by search terms

19/03/24 afternoon:
well done on study lists - looks great
Now repeat process for tables, but with a different style (compact table, either manual or dashtable)
That will do for now...
What to do next? Searching? Probs should be priority. The next focus is getting searching and content workind across the board. Also cleanup dataIO
TODO setup IO to load only important tables

21/03/24:
Man Marika Hackman was amazing
Today we are to fully hook up searching.
1. Add description & dataset tags to "spine"
2. Hook up age searches
3. Consider how to do tags
4. Look into elastic searching
---
ok, elasticsearch is nogo. Try whoosh. New objective, index a full search dataset.

working on woosh
Its partially integrated. We still have to hook up collection date and age
More pressingly, we have to re-sort out the documentation tabs 
figure out the inputs: if we are using index, do we need the study tabs? We certainly don't need the metadata tables.
Clean out the db?

replace the header with logo + full study name
or logo + full dataset name 


Future major tasks:
1. Hook up all search options
2. Implement linked branch
3. Implement None selected branch
4. update content.
5. Callback cleanup
'''
'''
Closer notes (if any)
Can we get out variable value frequencies?
Help page / tooltips
Closer search syntax? If not elastic search
Aida says pdfs are king
Aida doesn’t like explore, browse, navigate etc all used in the same system.
We will never be as good as closer without access to the questionnaire pdfs. It is likely worth referencing closer when possible. 
'''