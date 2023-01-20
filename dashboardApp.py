# sidebar.py
from os import read
from re import S
import re
import dash
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import pandas as pd
from dash import Dash, Input, Output, State, callback, dash_table, ALL, MATCH
import dash_leaflet as dl
import dash_leaflet.express as dlx
from dash_extensions.javascript import arrow_function
from dash_extensions.javascript import assign
import json
import time
import warnings
import logging
from dash.exceptions import PreventUpdate

from app_state import App_State
import dataIO
import stylesheet as ss
import constants 
import structures as struct


######################################################################################
app = dash.Dash(__name__, external_stylesheets=["custom.css"])

######################################################################################
### Data prep functions

start_time = time.time()
request_form_url = "https://uob.sharepoint.com/:x:/r/teams/grp-UKLLCResourcesforResearchers/Shared%20Documents/General/1.%20Application%20Process/2.%20Data%20Request%20Forms/Data%20Request%20Form.xlsx?d=w01a4efd8327f4092899dbe3fe28793bd&csf=1&web=1&e=reAgWe"
# request url doesn't work just yet
study_df = dataIO.load_study_request()
linked_df = dataIO.load_linked_request()
schema_df = pd.concat([study_df[["Study"]].rename(columns = {"Study":"Data Directory"}).drop_duplicates().dropna(), pd.DataFrame([["NHSD"]], columns = ["Data Directory"])])
study_info_and_links_df = dataIO.load_study_info_and_links()

app_state = App_State(schema_df)

def load_or_fetch_map(study):
    returned_data = app_state.get_map_data(study)
    if not returned_data: # if no saved map data, returns False
        try:
            with open("assets\\map overlays\\{}.geojson".format(study), 'r') as f:
                returned_data = json.load(f)
        except IOError:
            print("Unable to load map file {}.geojson".format(study))
        app_state.set_map_data(study, returned_data)
    return returned_data
    
def get_study_tables(schema):
    return study_df.loc[study_df["Study"] == schema]
        
######################################################################################

######################################################################################
### page asset templates

# Titlebar ###########################################################################
titlebar = struct.main_titlebar("Data Discoverability Resource")

# Left Sidebar #######################################################################

sidebar_catalogue = struct.make_sidebar_catalogue(study_df, app_state.lookup_sch_to_index, app_state.lookup_tab_to_index)
sidebar_title = struct.make_sidebar_title()
sidebar_footer = struct.make_sidebar_footer()
sidebar_left = struct.make_sidebar_left(sidebar_title, sidebar_catalogue, sidebar_footer)

# Context bar #########################################################################

context_bar_div = struct.make_context_bar()

# Body ################################################################################

# Main div template ##################################################################
maindiv = struct.make_body()
schema_record = struct.make_variable_div("active_schema")
table_record = struct.make_variable_div("active_table")
shopping_basket_op = struct.make_variable_div("shopping_basket_op")
save_output = struct.make_variable_div("save_op") 

hidden_body = struct.make_hidden_body()


# Variable Divs ####################################################################
active_schemas = struct.make_variable_div_list("active_schemas", list(app_state.lookup_index_to_sch.keys()))
active_tables = struct.make_variable_div_list("active_tables", list(app_state.lookup_index_to_tab.keys()))

###########################################
### Layout
app.layout = struct.make_app_layout(titlebar, sidebar_left, context_bar_div, maindiv, [schema_record, table_record, shopping_basket_op, save_output,  hidden_body] + active_schemas + active_tables)
print("Built app layout")
###########################################
### Actions

### DOCUMENTATION BOX #####################
@app.callback(
    Output('schema_description_div', "children"),
    Input('active_schema','key'),
    prevent_initial_call=True
)
def update_schema_description(schema):
    print("CALLBACK: DOC BOX - updating schema description")

    if schema != "None":
        schema_info = study_info_and_links_df.loc[study_info_and_links_df["Study Schema"] == schema]
        if schema == "NHSD":
            schema_info = "Generic info about nhsd"
            return schema_info
        else:      
            return struct.make_schema_description(schema_info)
    else:
        return ["Placeholder schema description, null schema - this should not be possible when contextual tabs is implemented"]


@app.callback(
    Output('table_description_div', "children"),
    Input('active_schema','key'),
    prevent_initial_call=True
)
def update_tables_description(schema):
    '''
    Replace contents of description box with table information 
    '''
    print("CALLBACK: DOC BOX - updating table description")

    if schema != "None":
        tables = get_study_tables(schema)
        if schema == "NHSD": # Expand to linked data branch
            schema_info = "Generic info about nhsd table"
            return schema_info
        else: # Study data branch
            return struct.data_doc_table(tables, "table_desc_table")
    else:
        return ["Placeholder table description, null schema - this should not be possible when contextual tabs is implemented"]


### METADATA BOX #####################

@app.callback(
    Output('table_meta_desc_div', "children"),
    Input('active_table', 'key'),
    prevent_initial_call=True
)
def update_table_data(table):
    print("CALLBACK: META BOX - updating table description")
    #pass until metadata block ready
    schema = app_state.schema
    if schema != "None":
        app_state.last_table = table
        tables = get_study_tables(schema)
        tables = tables.loc[tables["Block Name"] == table.split("-")[1]]
        if schema == "NHSD": # Expand to linked data branch
            return html.P("NHSD placeholder text")
        else: # Study data branch
            return struct.metadata_doc_table(tables, "table_desc_table")
    else:
        # Default (Section may be hidden in final version)
        return ["Placeholder metadata desc, null schema - this should not be possible when contextual tabs is implemented"]



@app.callback(
    Output('table_metadata_div', "children"),
    Input('active_table','key'),
    Input("values_toggle", "value"),
    Input("metadata_search", "value"),
    prevent_initial_call=True
)
def update_table_metadata(table, values_on, search):
    print("CALLBACK: META BOX - updating table metadata")

    table_id = app_state.table
    if table== "None":
        return ["Placeholder table metadata, null table - this should not be possible when contextual tabs is implemented"]
    try:
        metadata_df = dataIO.load_study_metadata(table_id)
    except FileNotFoundError: # Study has changed 
        print("Failed to load {}.csv".format(table_id))
        print("Preventing update in Meta box table metadata")
        raise PreventUpdate

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

    return struct.metadata_table(metadata_df, "metadata_table")

#########################
@app.callback(

    Output("context_tabs","children"),
    Input('active_schema','key'),
    Input('active_table','key'),
    prevent_initial_call=True
)
def context_tabs(_, __):
    if app_state.schema != "None":
        if app_state.table != "None":
            return [dcc.Tab(label='Documentation', value="Documentation"),
            dcc.Tab(label='Metadata', value='Metadata'),
            dcc.Tab(label='Coverage', value='Map')]
        else:
            return [dcc.Tab(label='Documentation', value="Documentation"),
            dcc.Tab(label='Coverage', value='Map')]
    else:
        return [dcc.Tab(label='Introduction', value="Introduction")]


@app.callback(
    Output("body", "children"),
    Output("hidden_body","children"),
    Input("context_tabs", "value"),
    State("body", "children"),
    State("hidden_body","children"),
    prevent_initial_call=True
)
def body_sctions(tab, active_body, hidden_body):
    print("CALLBACK: BODY, activating", tab)
    sections_states = {}
    for section in active_body + hidden_body:
        section_id = section["props"]["children"][1]["props"]["id"]
        print("encountered", section_id)
        sections_states[section_id] = section

    a_tab_is_active = False
    for section in app_state.sections.keys():
        if section in tab:
            app_state.sections[section]["active"] = True
            a_tab_is_active = True
        else:
            app_state.sections[section]["active"] = False

    # Check: if no tabs are active, run landing page
    if not a_tab_is_active:
        print("TODO: landing page:")
        return ["placeholder landing page"],  [sections_states[section_id] for section_id, section_vals in app_state.sections.items() if not section_vals["active"]]

    return [sections_states[section_id] for section_id, section_vals in app_state.sections.items() if section_vals["active"]], [sections_states[section_id] for section_id, section_vals in app_state.sections.items() if not section_vals["active"]]



@app.callback(
    Output({'type': 'schema_collapse', 'index': MATCH}, 'is_open'),
    Output({'type': 'schema_item', 'index': MATCH}, 'key'), # number of triggers, incrementing
    Input({"type": "schema_item", "index": MATCH}, 'n_clicks'),
    State({"type": "schema_collapse", "index" : MATCH}, "is_open"),
    State({"type": "schema_collapse", "index" : MATCH}, "id"),
    State({"type": "schema_item", "index" : MATCH}, "key"),
    prevent_initial_call = True
)# NOTE: is this going to be slow? we are pattern matching all schema. Could we bring it to a higher level? like the list group? Or will match save it
def sidebar_schema(clicks, is_open, id, triggers):
    print("CALLBACK: sidebar schema click")
    app_state.schema_click_count +=1
    print("Schema click count", app_state.schema_click_count)
    ctx = dash.callback_context
    triggered_0 = ctx.triggered[0]
    print("triggered:",triggered_0)
    if str(clicks) == "0":
        print("Aborting sidebar schema click call")
        return False, str(triggers)
    #print(test)
    index = id["index"]
    schema = app_state.lookup_index_to_sch[index]
    if triggers == "None":
        triggers = 0
    else:
        triggers = int(triggers)

    # if schema is active and closed: open, active
    if app_state.schema == schema and not is_open:
        app_state.schema = schema
        return True, str(triggers)

    # if schema is active and open: close, inactive
    elif app_state.schema == schema and is_open:
        app_state.last_schema = app_state.schema
        app_state.schema = schema
        return False, str(triggers)
    # if schema is inactive and closed: open, active
    # if schema is inactive and open: open, active
    elif app_state.schema != schema:
        app_state.last_schema = app_state.schema
        app_state.schema = schema
        return True, str(triggers + 1)

@app.callback(
    Output('active_schema','key'), # Move this out - it is slow!
    Input({'type': 'schema_item', 'index': ALL}, 'key'), # This is slow?
    prevent_initial_call = True
)
def set_schema(_):
    return app_state.schema


# TODO Find a way to get this function working seamlessly... Maybe try linking different items or not using active.
'''
@app.callback(
    Output({"type": "schema_item", "index" : ALL}, "active"),
    Input({'type': 'schema_item', 'index': ALL}, 'key'), # This is slow?
    prevent_initial_call = True
)
def schema_toggle_active(active_schemas):
    print("CALLBACK: schema activation")

    active = [False for s in active_schemas]
    if app_state.schema == "None":
        return active

    active[int(app_state.lookup_sch_to_index[app_state.schema])] = True
    return active
'''

@app.callback(
    Output({'type': 'table_item_container', 'index': MATCH}, 'key'), # number of triggers, incrementing
    Input({"type": "sidebar_table_item", "index": MATCH}, 'n_clicks'),
    State({"type": "sidebar_table_item", "index": MATCH}, 'key'),

    prevent_initial_call = True
)
def sidebar_table(_, table):

    print("CALLBACK: sidebar table click")
    app_state.table_click_count +=1
    print("Table click count", app_state.table_click_count)
    app_state.table = table
    return "trigger"

@app.callback(
    Output('active_table','key'), # Move this out - it is slow!
    Input({'type': 'table_item_container', 'index': ALL}, 'key'), # This is slow?
    prevent_initial_call = True
)
def set_table(_):
    return app_state.table

'''
@app.callback(
    Output({"type": "sidebar_table_item", "index" : ALL}, "active"),

    Input({'type': 'table_item_container', 'index': ALL}, 'key'),
    State({"type": "sidebar_table_item", "index" : ALL}, "active"),
    prevent_initial_call = True
)
def table_toggle_active(table_keys, active):
    print("CALLBACK: Sidebard table active update")
    active = [False for t in table_keys]
    if app_state.table == "None":
        return active

    active[int(app_state.lookup_tab_to_index[app_state.table])] = True

    return active
'''

@app.callback(
    Output("sidebar_list_div", "children"),
    Input("search_button", "n_clicks"),
    Input("main_search", "value")
    )
def main_search(_, search):
    '''
    Version 1: search by similar text in schema, table name or keywords. 
    these may be branched into different search functions later, but for now will do the trick
    Do we want it on button click or auto filter?
    Probs on button click, that way we minimise what could be quite complex filtering
    '''
    print("CALLBACK: main search")

    # Reset sidebar clicks in app state - we are rebuilding it here!
    app_state.reset_sidebar_clicks()

    if type(search)!=str or search == "":
        return struct.build_sidebar_list(study_df, app_state.lookup_sch_to_index, app_state.lookup_tab_to_index, app_state.shopping_basket, app_state.sidebar_clicks)

    sub_list = study_df.loc[
        (study_df["Study"].str.contains(search, flags=re.IGNORECASE)) | 
        (study_df["Block Name"].str.contains(search, flags=re.IGNORECASE)) | 
        (study_df["Keywords"].str.contains(search, flags=re.IGNORECASE)) | 
        (study_df[constants.keyword_cols[1]].str.contains(search, flags=re.IGNORECASE)) |
        (study_df[constants.keyword_cols[2]].str.contains(search, flags=re.IGNORECASE)) |
        (study_df[constants.keyword_cols[3]].str.contains(search, flags=re.IGNORECASE)) |
        (study_df[constants.keyword_cols[4]].str.contains(search, flags=re.IGNORECASE))
        ]

    return struct.build_sidebar_list(sub_list, app_state.lookup_sch_to_index, app_state.lookup_tab_to_index, app_state.shopping_basket, app_state.schema_collapse_open)


@app.callback(
    Output({'type': 'shopping_basket_op', 'content': ALL}, 'key'),
    Input({"type": "shopping_checklist", "value" : ALL}, "value"),
    prevent_initial_call=True
    )
def shopping_cart(selected):
    print("CALLBACK: Shopping cart")
    ctx = dash.callback_context
    triggered_0 = ctx.triggered[0]

    if triggered_0["value"] and triggered_0["value"]!=[]:
        input_id = triggered_0["prop_id"].split(".")[0][38:-2]

        if input_id in app_state.shopping_basket:
            app_state.shopping_basket.remove(input_id)
        else:
            app_state.shopping_basket.append(input_id)

    return ["placeholder"]


@app.callback(
    Output({'type': 'save_op', 'content': ALL}, 'key'),
    Input({"type": "shopping_checklist", "value" : ALL}, "value"),
    prevent_initial_call=True
    )
def save_shopping_cart(shopping_basket):
    '''
    input save button
    Get list of selected checkboxes - how? can just save shopping cart as is, list of ids
    
    '''
    # TODO insert checks to not save if the shopping basket is empty or otherwise invalid
    dataIO.basket_out(app_state.shopping_basket)
    return ["placeholder"]


if __name__ == "__main__":
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    pd.options.mode.chained_assignment = None
    warnings.simplefilter(action="ignore",category = FutureWarning)
    app.run_server(port=8888, debug = True)
    
''''
thoughts on efficiency:
    index throughout
    using match rather than all will be a big improvement.
    tables must be ided by index not key. 
    We currently use key. 
    Thats fine, we can have a dictionary of table key to index setup at the start or even in pre
    Table must always have same index or search will break it.
    can also use index in hidden divs

    This doesn't answer the question of how we efficiently set a list item active and set all others inactive.
    I don't have any ideas for this one just yet. 
    Well. We could make a new callback chain
    Send the old table to a holder
    update - invert active on that index
    update the same callback with the new table
    update - invert active on that index.
    Could work. Bit complex, but its getting that way in general.
    Best wait for the merge at 2:30 though. hour and a half. Go scran. 

    1. Give every table an id (may as well do for study too)
'''