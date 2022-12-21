# sidebar.py
from os import read
from re import S
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
sidebar_left = struct.make_sidebar_left(sidebar_title, sidebar_catalogue)

# Context bar #########################################################################

context_bar_div = struct.make_context_bar()

# Body ################################################################################
# get base map ########################################################################

app_state.map_box = struct.make_map_box("Coverage: Study Name Placeholder")

app_state.documentation_box = struct.make_documentation_box("Documentation: Study Name Placeholder")

app_state.metadata_box = struct.make_metadata_box("Metadata: Study Name Placeholder")

# Main div template ##################################################################
maindiv = struct.make_body([app_state.map_box, app_state.documentation_box, app_state.metadata_box], ["map_collapse", "doc_collapse", "metadata_collapse"])

schema_record = struct.make_variable_div("active_schema")
table_record = struct.make_variable_div("active_table")

###########################################
### Layout
app.layout = struct.make_app_layout(titlebar, sidebar_left, context_bar_div, maindiv, [schema_record, table_record])

###########################################

###########################################
### Actions


### DOCUMENTATION BOX #####################
@app.callback(
    Output('schema_description_div', "children"),
    Input({'type': 'active_schema', 'content': ALL}, 'key'),
)
def update_schema_description(schema):
    schema = schema[0]
    
    print("Update schema:",schema)
    if schema != "None":
        schema_info = study_info_and_links_df.loc[study_info_and_links_df["Study Schema"] == schema]
        if schema == "NHSD":
            schema_info = "Generic info about nhsd"
            return schema_info
        else:
            return struct.make_schema_description(schema_info)
    else:
        # Default (Section may be hidden in final version)
        return [html.P("Select a schema for more information...")]


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
            return struct.data_doc_table(tables, "table_desc_table")
    else:
        # Default (Section may be hidden in final version)
        return html.P("Select a table for more information...")


### METADATA BOX #####################

@app.callback(
    Output('table_meta_desc_div', "children"),
    Input({'type': 'active_schema', 'content': ALL}, 'key'),
    Input({'type': 'active_table', 'content': ALL}, 'key'),
)
def update_table_metadata(schema, table):
    #pass until metadata block ready
    schema = schema[0]
    if schema != "None":
        tables = get_study_tables(schema)

        tables = tables.loc[tables["Block Name"] == table[0]]
        if schema == "NHSD": # Expand to linked data branch
            return html.P("NHSD placeholder text")
        else: # Study data branch
            return struct.metadata_doc_table(tables, "table_desc_table")
    else:
        # Default (Section may be hidden in final version)
        return html.P("Select a table for more information...")

@app.callback(
    Output('table_metadata_div', "children"),
    Input({'type': 'active_schema', 'content': ALL}, 'key'),
    Input({'type': 'active_table', 'content': ALL}, 'key'),
)
def update_table_metadata(schema, table):
    #pass until metadata block ready
    print(schema, table)
    if table[0] == "None":
        print("Debug, update_table_metadata: Table is none")
        return None

    metadata_df = read_data_request.load_study_metadata(schema[0], table[0])
    return struct.metadata_table(metadata_df, "metadata_table")
    #return html.P("DEMO")
    

@app.callback(
    Output("doc_collapse", "is_open"),
    [Input("doc_button", "n_clicks")],
    [State("doc_collapse", "is_open")],
)
def toggle_collapse(n, is_open):
    print("button toggle {}, {}".format(n, is_open))
    if n:
        return not is_open
    return is_open

@app.callback(
    Output("metadata_collapse", "is_open"),
    [Input("metadata_button", "n_clicks")],
    [State("metadata_collapse", "is_open")],
)
def toggle_collapse(n, is_open):
    print("button toggle {}, {}".format(n, is_open))
    if n:
        return not is_open
    return is_open

@app.callback(
    Output("map_collapse", "is_open"),
    [Input("map_button", "n_clicks")],
    [State("map_collapse", "is_open")],
)
def toggle_collapse(n, is_open):
    print("button toggle {}, {}".format(n, is_open))
    if n:
        return not is_open
    return is_open




@app.callback(
    Output({'type': 'schema_collapse', 'index': ALL}, 'is_open'),
    Output({'type': 'active_schema', 'content': ALL}, 'key'),
    Output({'type': 'active_table', 'content': ALL}, 'key'),
    Output('map_region', "data"),
    Input("sidebar_left_div", 'n_clicks'),
    State("schema_list","children"),
    State({'type': 'active_schema', 'content': ALL}, 'key'),
    State({"type": "schema_collapse", "index" : ALL}, "is_open"),
)
def sidebar_clicks(_,children, active_schema, collapse):
    print("Debug: Reading sidebar click")

    schema_clicks = {}
    table_clicks = {}   

    schema_i = 0

    active_schema = active_schema[0]

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
                    print("Action on index {}, schema {}. Stored {}, current {}".format(schema_i, schema, stored, schema_clicks[schema]))
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
                        print("Action on table {}. Stored {}, current {}".format(table_full, stored, table_clicks[table_full]))
                        # load map
                        map_data = load_or_fetch_map(table_schema)
                        return collapse, [table_schema], [table], map_data
                else:
                    app_state.set_sidebar_clicks(table_full, 0)
                    table_clicks[table_full] = 0


    map_data = load_or_fetch_map(active_schema)
    return collapse, [active_schema],  ["None"], map_data


if __name__ == "__main__":
    app.run_server(port=8888)
