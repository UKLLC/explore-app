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
from dash import Dash, Input, Output, State, callback, dash_table, ALL
import dash_leaflet as dl
import dash_leaflet.express as dlx
from dash_extensions.javascript import arrow_function
from dash_extensions.javascript import assign
import json
import time
import warnings

from app_state import App_State
import read_data_request
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
study_df = read_data_request.load_study_request()
linked_df = read_data_request.load_linked_request()
schema_df = pd.concat([study_df[["Study"]].rename(columns = {"Study":"Data Directory"}).drop_duplicates().dropna(), pd.DataFrame([["NHSD"]], columns = ["Data Directory"])])
study_info_and_links_df = read_data_request.load_study_info_and_links()

app_state = App_State()

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

sidebar_catalogue = struct.make_sidebar_catalogue(study_df)
sidebar_title = struct.make_sidebar_title()
sidebar_footer = struct.make_sidebar_footer()
sidebar_left = struct.make_sidebar_left(sidebar_title, sidebar_catalogue, sidebar_footer)

# Context bar #########################################################################

context_bar_div = struct.make_context_bar()

# Body ################################################################################
# get base map ########################################################################

app_state.map["object"] = struct.make_map_box("Coverage: Study Name Placeholder")

app_state.documentation["object"] = struct.make_documentation_box("Documentation: Study Name Placeholder")

app_state.metadata["object"] = struct.make_metadata_box("Metadata: Study Name Placeholder")

# Main div template ##################################################################
#maindiv = struct.make_body([app_state.map["object"], app_state.documentation["object"], app_state.metadata["object"]], ["map_collapse", "doc_collapse", "metadata_collapse"])
maindiv = struct.make_body([], [])

schema_record = struct.make_variable_div("active_schema")
table_record = struct.make_variable_div("active_table")
demo = struct.make_variable_div("demo")

hidden_body = struct.make_hidden_body()

###########################################
### Layout
app.layout = struct.make_app_layout(titlebar, sidebar_left, context_bar_div, maindiv, [schema_record, table_record, demo,  hidden_body])

###########################################
### Actions

### DOCUMENTATION BOX #####################
@app.callback(
    Output('schema_description_div', "children"),
    Input({'type': 'active_schema', 'content': ALL}, 'key'),
)
def update_schema_description(schema):
    print("CALLBACK: updating schema description")

    schema = schema[0]

    if schema != "None":
        schema_info = study_info_and_links_df.loc[study_info_and_links_df["Study Schema"] == schema]
        if schema == "NHSD":
            schema_info = "Generic info about nhsd"
            return schema_info
        else:
            app_state.schema_doc = struct.make_schema_description(schema_info)
            return app_state.schema_doc
    else:
        return app_state.schema_doc


@app.callback(
    Output('table_description_div', "children"),
    Input({'type': 'active_schema', 'content': ALL}, 'key'),
)
def update_tables_description(schema):
    '''
    Replace contents of description box with table information 
    '''
    schema = schema[0]
    if schema != "None":
        tables = get_study_tables(schema)
        if schema == "NHSD": # Expand to linked data branch
            schema_info = "Generic info about nhsd table"
            return schema_info
        else: # Study data branch
            app_state.table_doc = struct.data_doc_table(tables, "table_desc_table")
            return app_state.table_doc
    else:
        return [html.P("Select a table for more information...")]


### METADATA BOX #####################

@app.callback(
    Output('table_meta_desc_div', "children"),
    Input({'type': 'active_schema', 'content': ALL}, 'key'),
    Input({'type': 'active_table', 'content': ALL}, 'key'),
)
def update_table_data(schema, table):
    #pass until metadata block ready
    schema = schema[0]
    if schema != "None":
        tables = get_study_tables(schema)

        tables = tables.loc[tables["Block Name"] == table[0]]
        if schema == "NHSD": # Expand to linked data branch
            return html.P("NHSD placeholder text")
        else: # Study data branch
            app_state.meta_table_doc = struct.metadata_doc_table(tables, "table_desc_table")
            return app_state.meta_table_doc
    else:
        # Default (Section may be hidden in final version)
        return html.P("Select a table for more information...")


@app.callback(
    Output('table_metadata_div', "children"),
    Input({'type': 'active_schema', 'content': ALL}, 'key'),
    Input({'type': 'active_table', 'content': ALL}, 'key'),
    Input("values_toggle", "value"),
    Input("metadata_search", "value"),
)
def update_table_metadata(schema, table, values_on, search):
    #pass until metadata block ready
    if table[0] == "None":
        return None

    metadata_df = read_data_request.load_study_metadata(schema[0], table[0])
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

    app_state.meta_table = struct.metadata_table(metadata_df, "metadata_table")
    return app_state.meta_table



@app.callback(
    Output("body", "children"),
    Output("hidden_body","children"),
    Input("doc_button", "n_clicks"),
    Input("metadata_button", "n_clicks"),
    Input("map_button", "n_clicks")
)
def body_sctions(doc_n, metadata_n, map_n):
    app_state.set_global_activations(app_state.get_global_activations() + 1)
    click_state = app_state.get_button_clicks()
    app_state.set_button_clicks([doc_n, metadata_n, map_n])

    # Update sections with current state
    app_state.documentation["object"] = struct.make_documentation_box("Documentation: Study Name Placeholder", [app_state.schema_doc, app_state.table_doc])
    app_state.metadata["object"] = struct.make_metadata_box("Metadata: Study Name Placeholder", [app_state.meta_table_doc, app_state.meta_table])

    sections = app_state.get_sections()

    # determine which button was clicked:
    if click_state[0] != doc_n:
        section = app_state.documentation
    elif click_state[1] != metadata_n:
        section = app_state.metadata
    elif click_state[2] != map_n:
        section = app_state.map
    else:
        return [html.P("Landing page placeholder")], [s["object"] for s in sections] # TODO make tutorial

    # update state
    section["activations"] = app_state.get_global_activations() # incrementing count of global clicks on and off
    if section["active"]:
        section["active"] = False
    else:
        section["active"] = True

    # show state
    active_sections =  [i for i in sections if i["active"] == True]
    ordered_sections = sorted(active_sections, key=lambda d: d["activations"])

    return [s["object"] for s in ordered_sections], [s["object"] for s in sections if s not in ordered_sections]


@app.callback(
    Output({'type': 'schema_collapse', 'index': ALL}, 'is_open'),
    Output({'type': 'active_schema', 'content': ALL}, 'key'),
    Output({'type': 'active_table', 'content': ALL}, 'key'),
    Output('map_region', "data"),
    Input("sidebar_left_div", 'n_clicks'),
    State("schema_list","children"),
    State({'type': 'active_schema', 'content': ALL}, 'key'),
    State({'type': 'active_table', 'content': ALL}, 'key'),
    State({"type": "schema_collapse", "index" : ALL}, "is_open"),
)
def sidebar_clicks(_,children, active_schema, active_table, collapse):
    #print("Debug: Reading sidebar click")
    schema_clicks = {}
    table_clicks = {}   

    schema_i = 0
    active_schema = active_schema[0]
    active_table = active_table[0]

    for schema_root in children:
        if "key" in schema_root["props"]:
            schema = schema_root["props"]["key"]
            if "n_clicks" in schema_root["props"]:
                schema_clicks[schema] = schema_root["props"]["n_clicks"]
                stored = app_state.get_sidebar_clicks(schema)
                if stored != schema_clicks[schema]:
                    collapse[schema_i] = not collapse[schema_i]
                    if collapse[schema_i]:
                        active_schema = schema_df["Data Directory"].iloc[schema_i]
                    #print("Action on index {}, schema {}. Stored {}, current {}".format(schema_i, schema, stored, schema_clicks[schema]))
                app_state.set_sidebar_clicks(schema, schema_clicks[schema])
            else:
                app_state.set_sidebar_clicks(schema, 0)
                schema_clicks[schema] = 0
            schema_i += 1

        else:
            for table_root in schema_root["props"]["children"]["props"]["children"]:
                table_full = table_root["props"]["key"]
                table_schema = table_full.split("-")[0]
                table = table_full.split("-")[1:][0]
                if "n_clicks" in table_root["props"]:
                    table_clicks[table_full] = table_root["props"]["n_clicks"]
                    stored = app_state.get_sidebar_clicks(table_full)
                    app_state.set_sidebar_clicks(table_full, table_clicks[table_full])
                    if stored != table_clicks[table_full]:
                        #print("Action on table {}. Stored {}, current {}".format(table_full, stored, table_clicks[table_full]))
                        # load map
                        map_data = load_or_fetch_map(table_schema)
                        return collapse, [table_schema], [table], map_data
                else:
                    app_state.set_sidebar_clicks(table_full, 0)
                    table_clicks[table_full] = 0

    map_data = load_or_fetch_map(active_schema)
    return collapse, [active_schema],  [active_table], map_data

@app.callback(
    Output("sidebar_list_div", "children"),
    Input("search_button", "n_clicks"),
    Input("main_search", "value")
    )
def main_search(click, search):
    '''
    Version 1: search by similar text in schema, table name or keywords. 
    these may be branched into different search functions later, but for now will do the trick
    Do we want it on button click or auto filter?
    Probs on button click, that way we minimise what could be quite complex filtering
    '''
    print("CALLBACK: main search")
    if type(search)!=str or search == "":
        return struct.build_sidebar_list(study_df)

    sub_list = study_df.loc[
        (study_df["Study"].str.contains(search, flags=re.IGNORECASE)) | 
        (study_df["Block Name"].str.contains(search, flags=re.IGNORECASE)) | 
        (study_df["Keywords"].str.contains(search, flags=re.IGNORECASE)) | 
        (study_df["Unnamed: 11"].str.contains(search, flags=re.IGNORECASE)) |
        (study_df["Unnamed: 12"].str.contains(search, flags=re.IGNORECASE)) |
        (study_df["Unnamed: 13"].str.contains(search, flags=re.IGNORECASE)) |
        (study_df["Unnamed: 14"].str.contains(search, flags=re.IGNORECASE))
        ]

    return struct.build_sidebar_list(sub_list)


'''
Todo: Checklist. 
This is quite a hard problem. 
We need to put a checkbox in every table, preserve its clicked status during searches when the directory is remade.
1. Create checked list in table sections
2. Create dictionary of dictionaries on startup of every possible table and its clicked status for each study. 
3. Callback which takes all checkboxes as input, identifies which table caused the callback, and flips the bit on the dictionary
4. When creating the sidebar, check the dictionary for each schema and make the checkboxes ticked or not as appropriate

Now action
How do we identify the specific table from a dynamic callback?
We can replicate the process for schema collapses.
'''


@app.callback(
    Output({'type': 'demo', 'content': ALL}, 'key'),
    Input({"type": "shopping_checklist", "value" : ALL}, "value")
)
def shopping_cart(checked):
    print("CALLBACK: Shopping cart")
    selected = [t for t in checked if t != None and t != []]
    print(selected)
    return ["1"]


def save_shopping_cart():
    pass


if __name__ == "__main__":
    app.run_server(port=8888)
    pd.options.mode.chained_assignment = None
    warnings.simplefilter(action="ignore",category = FutureWarning)
