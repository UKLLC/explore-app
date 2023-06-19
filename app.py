# sidebar.py
import  os
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
import pickle
import time
import warnings
import logging
from dash.exceptions import PreventUpdate
from flask_caching import Cache
#import dash_auth
from flask import request

from app_state import App_State
import dataIO
import stylesheet as ss
import constants 
import structures as struct


######################################################################################
app = dash.Dash(__name__, external_stylesheets=["custom.css"])
server = app.server

######################################################################################
### Data prep functions

request_form_url = "https://uob.sharepoint.com/:x:/r/teams/grp-UKLLCResourcesforResearchers/Shared%20Documents/General/1.%20Application%20Process/2.%20Data%20Request%20Forms/Data%20Request%20Form.xlsx?d=w01a4efd8327f4092899dbe3fe28793bd&csf=1&web=1&e=reAgWe"
# request url doesn't work just yet
study_df = dataIO.load_study_request()
linked_df = dataIO.load_linked_request()
schema_df = pd.merge((study_df.rename(columns = {"Study":"Source"})), (linked_df), how = "outer", on = ["Source", "Block Name", "Block Description"]).drop_duplicates(subset = ["Source", "Block Name"]).dropna(subset = ["Source", "Block Name"])
study_info_and_links_df = dataIO.load_study_info_and_links()

app_state = App_State(schema_df)

def load_or_fetch_map(study):
    returned_data = app_state.get_map_data(study) # memorisation of polygons
    if not returned_data: # if no saved map data, returns False
        try:
            returned_data = dataIO.get_map_overlays(study)
        except IOError:
            print("Unable to load map file {}.geojson".format(study))
        app_state.set_map_data(study, returned_data)
    return returned_data
    
    
def get_study_info(schema):
    return study_df.loc[study_df["Study"] == schema]

def get_source_tables(schema):
    return schema_df.loc[schema_df["Source"] == schema]
        
######################################################################################

######################################################################################
### page asset templates

# Titlebar ###########################################################################
titlebar = struct.main_titlebar(app, "UK LLC Data Discovery Portal")

# Left Sidebar #######################################################################

sidebar_catalogue = struct.make_sidebar_catalogue(schema_df)
sidebar_title = struct.make_sidebar_title()
sidebar_left = struct.make_sidebar_left(sidebar_title, sidebar_catalogue)

# Context bar #########################################################################

context_bar_div = struct.make_context_bar()

# Body ################################################################################

# Main div template ##################################################################
maindiv = struct.make_body()
schema_record = struct.make_variable_div("active_schema")
table_record = struct.make_variable_div("active_table")
shopping_basket_op = struct.make_variable_div("shopping_basket", [])
open_schemas = struct.make_variable_div("open_schemas", [])
user = struct.make_variable_div("user", None)
placeholder = struct.make_variable_div("placeholder", "placeholder")
account_section = struct.make_account_section()

hidden_body = struct.make_hidden_body()

# Variable Divs ####################################################################

###########################################
### Layout
app.layout = struct.make_app_layout(titlebar, sidebar_left, context_bar_div, maindiv, account_section, [schema_record, table_record, shopping_basket_op, open_schemas, hidden_body, user, placeholder])
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

@app.callback(
    Output('doc_title', "children"),
    Output('metadata_title', "children"),
    Output('map_title', "children"),
    Output('landing_title', 'children'),
    Input('active_schema','data'),
    prevent_initial_call=True
)
def update_headers(schema):
    '''
    When schema updates, update documentation
    '''
    doc_header = struct.make_section_title("Block-Level Metadata: {}".format(schema))
    meta_header = struct.make_section_title("Variable-Level Metadata: {}".format(schema))
    map_header = struct.make_section_title("Coverage: {}".format(schema))
    if schema:
        landing_header = struct.make_section_title("Introduction: Selected source {}".format(schema))
    else:
        landing_header = struct.make_section_title("Introduction: Select data to continue")
    return doc_header, meta_header, map_header, landing_header

### DOCUMENTATION BOX #####################


@app.callback(
    Output('schema_description_div', "children"),
    Input('active_schema','data'),
    prevent_initial_call=True
)
def update_schema_description(schema):
    '''
    When schema updates, update documentation    
    '''
    print("CALLBACK: DOC BOX - updating schema description")

    if schema != None:
        schema_info = study_info_and_links_df.loc[study_info_and_links_df["Study Schema"] == schema]
        if schema == "NHSD":
            schema_info = "Generic info about nhsd (placeholder, waiting for database)"
            return schema_info
        else:      
            return struct.make_schema_description(schema_info)
    else:
        return ["Placeholder schema description, null schema - this should not be possible when contextual tabs is implemented"]


@app.callback(
    Output('table_description_div', "children"),
    Input('active_schema','data'),
    prevent_initial_call=True
)
def update_tables_description(schema):
    '''
    When schema updates
    Replace contents of description box with table information 
    '''
    print("CALLBACK: DOC BOX - updating table description")

    if schema != None:
        tables = get_study_info(schema)
        if schema == "NHSD": # Expand to linked data branch
            schema_info = "Generic info about nhsd (placeholder, waiting for database)"
            return schema_info
        else: # Study data branch
            return struct.data_doc_table(tables, "table_desc_table")
    else:
        return html.Div([html.P(["Metadata is not currently available for this data block"])], className = "container_box")

### METADATA BOX #####################
@app.callback(
    Output('table_meta_desc_div', "children"),
    Input('active_table', 'data'),
    State('active_schema', 'data'),
    prevent_initial_call=True
)
def update_table_data(table, schema):
    '''
    When table updates
    with current schema
    load table metadata
    '''
    print("CALLBACK: META BOX - updating table description")
    #pass until metadata block ready
    if schema != None and table != None:
        if schema in constants.LINKED_SCHEMAS: # Expand to linked data branch
            return html.P("Linked data placeholder (in development)")
        tables = get_study_info(schema)
        tables = tables.loc[tables["Block Name"] == table.split("-")[1]]
        return struct.metadata_doc_table(tables, "table_desc_table")
    else:
        # Default (Section may be hidden in final version)
        return html.Div([html.P("Metadata is not currently available for this data block.")], className="container_box")


@app.callback(
    Output('table_metadata_div', "children"),
    Input("values_toggle", "value"),
    Input("metadata_search", "value"),
    Input('active_table','data'),
    prevent_initial_call=True
)
def update_table_metadata(values_on, search, table):
    '''
    When table updates
    When values are toggled
    When metadata is searched
    update metadata display
    '''
    print("CALLBACK: META BOX - updating table metadata")
    table_id = table
    if table== None:
        return  html.Div([html.P(["Metadata is not currently available for this data block"])], className = "container_box")
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
    print("making metadata table")
    metadata_table = struct.metadata_table(metadata_df, "metadata_table")
    return metadata_table


### MAP BOX #################

@app.callback(
    Output('map_region', "data"),
    Output('map_object', 'zoom'),
    Input('context_tabs','value'), # Get it to trigger on first load to get past zoom bug
    Input('active_schema','data'),
    prevent_initial_call=True
)
def update_map_content(tab, schema):
    '''
    When schema updates
    Update the map content
    '''
    if schema != None and tab == "Map":
        map_data = load_or_fetch_map(schema)
        if not map_data:
            return dash.no_update, 6
        return map_data, 6
    else:
        raise PreventUpdate

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
    print("Updating basket review table")
    rows = []
    df = study_df
    for table_id in shopping_basket:
        table_split = table_id.split("-")
        source, table = table_split[0], table_split[1]
        
        df1 = df.loc[(df["Study"] == source) & (df["Block Name"] == table)]
        try: # NOTE TEMP LINKED OVERRIDE 
            row = [source, table, df1["Block Description"].values[0]]
        except IndexError:
            row = [source, table,""]
        rows.append(row)
    df = pd.DataFrame(rows, columns=["Source", "Data Block", "Description"])
    brtable = struct.basket_review_table(df)
    return brtable


#########################
@app.callback(

    Output("context_tabs","children"),
    Input('active_schema','data'),
    Input('active_table','data'),
    prevent_initial_call=True
)
def context_tabs(schema, table):
    '''
    When the schema changes
    When the table changes
    Update the context tabs
    '''
    print("DEBUG, context_tabs {} {}, {} {}".format(schema, type(schema), table, type(table)))
    if schema != None:
        
        if table != None:
            return [dcc.Tab(label='Introduction', value="Introduction", className='custom-tab', selected_className='custom-tab--selected-ops'),
                dcc.Tab(value='Documentation', label="Block-Level Metadata", className='custom-tab', selected_className='custom-tab--selected-doc'),
                dcc.Tab(value='Metadata', label='Variable-Level Metadata', className='custom-tab', selected_className='custom-tab--selected-doc'),
                dcc.Tab(label='Coverage', value='Map', className='custom-tab', selected_className='custom-tab--selected-show'),
                dcc.Tab(label='Basket Review', value="Basket Review", className='custom-tab', selected_className='custom-tab--selected-ops')]

        else:
            return [dcc.Tab(label='Introduction', value="Introduction", className='custom-tab', selected_className='custom-tab--selected-ops'),
                    dcc.Tab(value='Documentation', label="Block-Level Metadata", className='custom-tab', selected_className='custom-tab--selected-doc'),
                    dcc.Tab(label='Coverage', value='Map', className='custom-tab', selected_className='custom-tab--selected-show'),
                    dcc.Tab(label='Basket Review', value="Basket Review", className='custom-tab', selected_className='custom-tab--selected-ops')]

    else:
        return [dcc.Tab(label='Introduction', value="Introduction", className='custom-tab', selected_className='custom-tab--selected-ops'),
                dcc.Tab(label='Basket Review', value="Basket Review", className='custom-tab', selected_className='custom-tab--selected-ops'),
]


@app.callback(
    Output("body", "children"),
    Output("hidden_body","children"),
    #Output("basket_review_table_div", "children"),
    Input("context_tabs", "value"),
    State("body", "children"),
    State("hidden_body","children"),
    #State("shopping_basket", "data"),
    prevent_initial_call=True
)
def body_sctions(tab, active_body, hidden_body):#, shopping_basket):
    '''
    When the tab changes
    Read the current body
    Read the hidden body
    Update the body
    Update the hidden body
    '''
    print("CALLBACK: BODY, activating", tab)
    sections_states = {}
    for section in active_body + hidden_body:
        section_id = section["props"]["children"][1]["props"]["id"]
        sections_states[section_id] = section

    a_tab_is_active = False
    sections = app_state.sections
    active = []
    inactive = []
    for section in sections.keys():
        if section in tab:
            active.append(section)
            a_tab_is_active = True
        else:
            inactive.append(section)

    # Check: if no tabs are active, run landing page
    if not a_tab_is_active:
        return [sections_states["Landing"]],  [sections_states[s_id] for s_id in inactive]
    
    else:
        return [sections_states[s_id] for s_id in active], [sections_states[s_id] for s_id in inactive]


@app.callback(
    Output('context_tabs','value'),
    Input("active_schema", "data"),
    Input("active_table", "data"),
    State("context_tabs", "value"),
    prevent_initial_call = True
)# NOTE: is this going to be slow? we are pattern matching all schema. Could we bring it to a higher level? like the list group? Or will match save it
def force_change_body(schema, table, curr_tab):
    '''
    When the schema changes
    Read the current tab
    Update the current tab
    '''

    if dash.ctx.triggered_id == "active_schema":
        #If schema changes and a table specific section is active, kick them out. 
        
        if schema == None:
            return "Landing"
        elif curr_tab == "Documentation":
            raise PreventUpdate
        elif curr_tab == "Map":
            raise PreventUpdate
        else:
            return "Documentation"
    else:
        if curr_tab == "Map":
            raise PreventUpdate
        elif curr_tab == "Metadata":
            raise PreventUpdate
        else:
            return "Metadata"

@app.callback(
    Output('active_schema','data'),
    Input("study_schema_accordion", "active_item"),
    Input("linked_schema_accordion", "active_item"),
    State("active_schema", "data"),
    prevent_initial_call = True
)
def sidebar_schema(open_study_schema, open_linked_schema, previous_schema):
    '''
    When the active item in the accordion is changed
    Read the active schema NOTE with new system, could make active_schema redundant
    Read the previous schema
    Read the open schemas.
    '''
    print("CALLBACK: sidebar schema click")
    print("DEBUG, sidebar_schema {}, {}, {}".format(open_study_schema, previous_schema, dash.ctx.triggered_id))
    if dash.ctx.triggered_id == "study_schema_accordion":
        if open_linked_schema == previous_schema:
            print("Schema unchanged, preventing update")
            raise PreventUpdate
        else:
            return open_study_schema
    else:
        return open_linked_schema


@app.callback(
    Output('active_table','data'),
    Output({"type": "table_tabs", "index": ALL}, 'value'),
    Input({"type": "table_tabs", "index": ALL}, 'value'),
    Input('active_schema','data'),
    State("active_table", "data"),
    prevent_initial_call = True
)
def sidebar_table(tables, active_schema, previous_table):
    '''
    When the active table_tab changes
    When the schema changes
    Read the current active table
    Update the active table
    Update the activated table tabs (deactivate previously activated tabs)
    '''
    print("CALLBACK: sidebar table click")
    print("DEBUG, sidebar_table {}, {}, {}".format(tables, previous_table, dash.ctx.triggered_id))


    # If triggered by a schema change, clear the current table
    if dash.ctx.triggered_id == "active_schema":
        return None, [None for t in tables]


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
    print(table, previous_table)
    if table == previous_table:
        print("Table unchanged, preventing update")
        raise PreventUpdate

    return table, tables 
    

@app.callback(
    Output("sidebar_list_div", "children"),
    Input("search_button", "n_clicks"),
    Input("main_search", "value"),
    State("active_schema", "data"),
    State("shopping_basket", "data"),
    State("active_table", "data"),
    prevent_initial_call = True
    )
def main_search(_, search, open_schemas, shopping_basket, table):
    '''
    When the search button is clicked
    When the main search content is changed
    Read the current active schema
    Read the current shopping basket
    Read the active table
    Update the sidebar div

    Version 1: search by similar text in schema, table name or keywords. 
    these may be branched into different search functions later, but for now will do the trick
    Do we want it on button click or auto filter?
    Probs on button click, that way we minimise what could be quite complex filtering
    '''
    print("CALLBACK: main search, searching value: {}.".format(search))

    if type(search)!=str or search == "":
        return struct.build_sidebar_list(schema_df, shopping_basket, open_schemas, table)

    sub_list = schema_df.loc[
        (schema_df["Source"].str.contains(search, flags=re.IGNORECASE)) | 
        (schema_df["Block Name"].str.contains(search, flags=re.IGNORECASE)) | 
        (schema_df["Keywords"].str.contains(search, flags=re.IGNORECASE)) | 
        (schema_df[constants.keyword_cols[1]].str.contains(search, flags=re.IGNORECASE)) |
        (schema_df[constants.keyword_cols[2]].str.contains(search, flags=re.IGNORECASE)) |
        (schema_df[constants.keyword_cols[3]].str.contains(search, flags=re.IGNORECASE)) |
        (schema_df[constants.keyword_cols[4]].str.contains(search, flags=re.IGNORECASE))
        ]

    return struct.build_sidebar_list(sub_list, shopping_basket, open_schemas, table)


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
    print("CALLBACK: Shopping cart")
    if dash.ctx.triggered_id == "basket_review_table":# If triggered by basket review
        if current_data is not None:
            keys = []
            for item in current_data:
                keys.append(item["Source"] + "-" + item["Data Block"])

            new_shopping_basket = [item for item in shopping_basket if item in keys]

            if new_shopping_basket == shopping_basket:
                raise PreventUpdate
            else:
                if clicks == None:
                    return new_shopping_basket, clicks+1
                else:
                    return new_shopping_basket, 1
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
        selected = [i[0] for i in selected if i !=[]]
        shopping_basket = selected
        return shopping_basket, dash.no_update


@app.callback(
    Output('sb_download','data'),
    Input("save_button", "n_clicks"),
    Input("dl_button_2", "n_clicks"),
    State("shopping_basket", "data"),
    prevent_initial_call=True
    )
def save_shopping_cart(btn1, btn2, shopping_basket):
    '''
    When the save button is clicked
    Read the shopping basket
    Download the shopping basket as a csv
    '''
    print("CALLBACK: Save shopping cart")
    # TODO insert checks to not save if the shopping basket is empty or otherwise invalid
    fileout = dataIO.basket_out(shopping_basket)
    
    return dcc.send_data_frame(fileout.to_csv, "shopping_basket.csv")

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