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
import orjson
import time

from app_state import App_State
import dataIO

###########################################
### Styles
 
app = dash.Dash(external_stylesheets=["https://ukllc.ac.uk/assets/css/bootstrap.min.css?v=1650990372"])
TITLEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "width": "100%",
    "height": "5rem",
    "padding": "1rem 0.5rem",
    "background-color": "white",
    "color": "black",
    "textAlign":"center",
    "zIndex":2
}
SIDEBAR_LEFT_STYLE = {
    "background":"white",
    "position": "fixed",
    "top": "5rem",
    "left": 0,
    "bottom": 0,
    "width":"15%",
    "min-width":"10rem",
    "overflow": "scroll",
    "padding": "0.25rem",
    "zIndex":1,
    "border-right":"solid",
    "border-width":"normal",
}
SCHEMA_LIST_STYLE = {
    "list-style-type":"none",
    "margin-top":"0.25rem",
    "margin-bottom":"0.25rem",
    "padding": 0,
    "border-bottom": "solid",
    "border-width":"thin"
    }
SCHEMA_LIST_ITEM_STYLE = {
    "border-top":"solid",
    "border-width":"thin"}

COLLAPSE_DIV_STYLE = {
    "list-style-type":"none", 
    "margin-left": "0.5rem", 
    "margin-top":"0.25rem",
    "margin-bottom":"0.25rem", 
    "padding": 0,
    "border-top":"solid",
    "border-width":"thin"}
TABLE_LIST_STYLE = {
    "border-top":"solid",
    "border-width":"thin",
    "padding": "0.25rem",
    }
TABLE_LIST_ITEM_STYLE = {
    "border-bottom":"solid",
    "border-width":"thin"
    }
BODY_STYLE = {
    "position": "relative",
    "top": "5.6rem",
    "left":"16%",
    "width":"83%",
    "border":"solid",
    "border-width":"normal",
    "zIndex":0,
}

###########################################

###########################################
### Data prep functions
request_form_url = "https://uob.sharepoint.com/:x:/r/teams/grp-UKLLCResourcesforResearchers/Shared%20Documents/General/1.%20Application%20Process/2.%20Data%20Request%20Forms/Data%20Request%20Form.xlsx?d=w01a4efd8327f4092899dbe3fe28793bd&csf=1&web=1&e=reAgWe"
# request url doesn't work just yet
study_df = dataIO.load_study_request()
linked_df = dataIO.load_linked_request()
schema_df = pd.concat([study_df[["Study"]].rename(columns = {"Study":"Data Directory"}).drop_duplicates().dropna(), pd.DataFrame([["NHSD"]], columns = ["Data Directory"])])
study_info_and_links_df = dataIO.load_study_info_and_links()

def get_study_tables(schema):
    return study_df.loc[study_df["Study"] == schema]

DATA_DESC_COLS = ["Timepoint: Data Collected","Timepoint: Keyword","Number of Participants Invited (n=)","Number of Participants Included (n=)","Block Description","Links"]

start_time = time.time()

app_state = App_State()
##########################################

###########################################
### page asset templates
titlebar = html.Div([html.H1("Data Discoverability Resource", className="title")],style = TITLEBAR_STYLE)

def single_col_table(df, id):
    return dash_table.DataTable(
            id=id,
            data=df.to_dict('records'),
            editable=False,
            
            column_selectable="single",
            row_selectable=False,
            row_deletable=False,
            style_cell={'textAlign': 'left'}
            )

def quick_table(df, id):
    return dash_table.DataTable(
            id=id,
            data=df.to_dict('records'),
            columns=[{"name": i, "id": i} for i in df.columns], 
            editable=False,
            row_selectable=False,
            row_deletable=False,
            style_cell={'textAlign': 'left','overflow': 'hidden',
            'textOverflow': 'ellipsis',
            'maxWidth': 0},
            )

def make_sidebar():
    sidebar_children = []
    schema_df = pd.concat([study_df[["Study"]].rename(columns = {"Study":"Data Directory"}).drop_duplicates().dropna(), pd.DataFrame([["NHSD"]], columns = ["Data Directory"])])
    for i, row in schema_df.iterrows():
        schema = row["Data Directory"]

        tables = get_study_tables(schema)["Block Name"]

        schema_children = dbc.Collapse(dbc.ListGroup(id = schema+"_tables_list",
        children = [
            dbc.ListGroupItem(table, style=TABLE_LIST_ITEM_STYLE,action=True,active=False,key = schema+"-"+table, id={
            'type': 'sidebar_table_item',
            "value":schema+"-"+table
        }) for table in tables],
        style = COLLAPSE_DIV_STYLE,flush=True)
        , id={
            'type': 'schema_collapse',
            'index': i
        },
        style=TABLE_LIST_STYLE,
        is_open=False)

        sidebar_children += [dbc.ListGroupItem(schema, action=True,active=False, id={
            'type': 'schema_item',
            'index': i
        }, key = schema,
        style=SCHEMA_LIST_ITEM_STYLE)] + [schema_children]
    return dbc.ListGroup(sidebar_children, style = SCHEMA_LIST_STYLE, id = "schema_list")

sidebar_left = html.Div([
        make_sidebar()],
        style =SIDEBAR_LEFT_STYLE,
        id = "sidebar_left_div")


maindiv = html.Div(
    [html.H2("Descriptions"),
        html.Hr(),
        html.Div([html.P("Select a schema for more information...", id = "schema_description_text")], id = "schema_description_div"),
        html.Hr(),
        html.Div([html.P("Select a schema for more information...", id = "table_description_text")], id = "table_description_div")],
    id="body",
    style = BODY_STYLE
    )

schema_record = html.Div([],key = "None",id = {"type":"active_schema", "content":"None"})
table_record = html.Div([],key = "None",id = {"type":"active_table", "content":"None"})

###########################################

###########################################
### Layout
app.layout = html.Div([titlebar, sidebar_left, maindiv, schema_record, table_record]) 
###########################################

###########################################
### Actions


@app.callback(
    Output('schema_description_text', "children"),
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
            out_text = []
            for col in schema_info.columns:
                out_text.append(html.B("{}:".format(col)))
                out_text.append(" {}".format(schema_info[col].values[0]))
                out_text.append(html.Br())
            return [html.Hr(), html.P(out_text)]

    else:
        return [html.Hr(), html.P("Select a schema for more information...")]

@app.callback(
    Output('table_description_text', "children"),
    Input({'type': 'active_schema', 'content': ALL}, 'key'),
    Input({'type': 'active_table', 'content': ALL}, 'key'),
)
def update_table_description(schema, table):
    schema = schema[0]
    table = (table[0]).replace(schema+"_","")
    if schema != "None" and table != "None":
        tables = get_study_tables(schema)
        table_row = tables.loc[tables["Block Name"] == table]
        if schema == "NHSD":
            schema_info = "Generic info about nhsd table"
            return schema_info
        else:
            out_text = []
            for col in DATA_DESC_COLS:
                out_text.append(html.B("{}:".format(col)))
                out_text.append(" {}".format(table_row[col].values[0]))
                out_text.append(html.Br())
            return [html.Hr(), html.P(out_text)]
    else:
        return [html.Hr(), html.P("Select a table for more information...")]


@app.callback(
    Output({'type': 'schema_collapse', 'index': ALL}, 'is_open'),
    Output({'type': 'active_schema', 'content': ALL}, 'key'),
    Output({'type': 'active_table', 'content': ALL}, 'key'),
    Input("sidebar_left_div", 'n_clicks'),
    State("schema_list","children"),
    State({'type': 'active_schema', 'content': ALL}, 'key'),
    State({"type": "schema_collapse", "index" : ALL}, "is_open"),
)
def test_callback(_,children,active_schema, collapse):

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
                        return collapse, [table_schema], [table]
                else:
                    app_state.set_sidebar_clicks(table_full, 0)
                    table_clicks[table_full] = 0

    return collapse, [active_schema],  ["None"]


if __name__ == "__main__":
    app.run_server(port=8888)
