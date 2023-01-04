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

import stylesheet as ss
import constants

def quick_table(df, id):
    quick_table = dash_table.DataTable(
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
    return quick_table

def data_doc_table(df, id):
    keyword_cols = ["Keywords", "Unnamed: 11", "Unnamed: 12","Unnamed: 13","Unnamed: 14","Unnamed: 15"]
    for kw in keyword_cols:
        df[kw] = df[kw].str.strip()
    df["Keywords"] = df["Keywords"]+", "+df["Unnamed: 11"]+", "+df["Unnamed: 12"]+", "+df["Unnamed: 13"]+", "+df["Unnamed: 14"]+", "+df["Unnamed: 15"]
    df["Keywords"] = df["Keywords"].str.replace(", ,", "")
    df["Keywords"] = df["Keywords"].str.rstrip(",| ,")

    df=df[["Block Name", "Timepoint: Data Collected","Timepoint: Keyword","Number of Participants Invited (n=)", "Number of Participants Included (n=)", "Inclusion Criteria", "Block Description","Links", "Keywords"]]
    df.rename(columns = {"Block Description":"Description", "Number of Participants Invited (n=)":"Participants Invited", "Number of Participants Included (n=)": "Participants Included"})
    table = dash_table.DataTable(
            id=id,
            data=df.to_dict('records'),
            columns=[{"name": i, "id": i} for i in df.columns], 
            editable=False,
            row_selectable=False,
            row_deletable=False,
            style_header=ss.TABLES_DOC_HEADER,
            style_cell=ss.TABLES_DOC_CELL,
            style_data_conditional=[ss.TABLES_DOC_CONDITIONAL]
            )
    return table


def metadata_doc_table(df, id):
    keyword_cols = ["Keywords", "Unnamed: 11", "Unnamed: 12","Unnamed: 13","Unnamed: 14","Unnamed: 15"]
    for kw in keyword_cols:
        df[kw] = df[kw].str.strip()
    df["Keywords"] = df["Keywords"]+", "+df["Unnamed: 11"]+", "+df["Unnamed: 12"]+", "+df["Unnamed: 13"]+", "+df["Unnamed: 14"]+", "+df["Unnamed: 15"]
    df["Keywords"] = df["Keywords"].str.replace(", ,", "")
    df["Keywords"] = df["Keywords"].str.rstrip(",| ,")

    df=df[["Block Name", "Timepoint: Data Collected","Timepoint: Keyword","Number of Participants Invited (n=)", "Number of Participants Included (n=)", "Inclusion Criteria", "Block Description","Links", "Keywords"]]
    df.rename(columns = {"Block Description":"Description", "Number of Participants Invited (n=)":"Participants Invited", "Number of Participants Included (n=)": "Participants Included"})
    table = dash_table.DataTable(
            id=id,
            data=df.to_dict('records'),
            columns=[{"name": i, "id": i} for i in df.columns], 
            editable=False,
            row_selectable=False,
            row_deletable=False,
            style_header=ss.METADATA_DESC_HEADER,
            style_cell=ss.METADATA_DESC_CELL,
            )
    return table


def metadata_table(df, id):
    df = df[["Block Name", "Variable Name", "Variable Description", "Value", "Value Description"]]
    quick_table = dash_table.DataTable(
            id=id,
            data=df.to_dict('records'),
            columns=[{"name": i, "id": i} for i in df.columns], 
            editable=False,
            row_selectable=False,
            row_deletable=False,
            style_header=ss.METADATA_TABLE_HEADER,
            style_cell=ss.METADATA_TABLE_CELL,
            style_data_conditional=[ss.METADATA_CONDITIONAL]
            )
    return quick_table


def main_titlebar(title_text):
    titlebar = html.Div([html.H1(title_text, className="title")],style = ss.TITLEBAR_STYLE)
    return titlebar

def build_sidebar_list(df):
    sidebar_children = []
    # Get data sources
    schema_df = pd.concat([df[["Study"]].rename(columns = {"Study":"Data Directory"}).drop_duplicates().dropna(), pd.DataFrame([["NHSD"]], columns = ["Data Directory"])])
    
    # Attribute tables to each study
    for i, row in schema_df.iterrows():
        schema = row["Data Directory"]

        tables = df.loc[df["Study"] == schema]["Block Name"]

        schema_children = dbc.Collapse(dbc.ListGroup(id = schema+"_tables_list",
        children = [
            dbc.ListGroupItem(table, style=ss.TABLE_LIST_ITEM_STYLE,
                action=True,active=False,key = schema+"-"+table,
                id={
                    'type': 'sidebar_table_item',
                    "value":schema+"-"+table
                }) for table in tables],
            style = ss.COLLAPSE_DIV_STYLE,flush=True)
            , id={
                'type': 'schema_collapse',
                'index': i
        },
        style=ss.TABLE_LIST_STYLE,
        is_open=False)

        sidebar_children += [dbc.ListGroupItem(schema, action=True,active=False, id={
            'type': 'schema_item',
            'index': i
        }, key = schema,
        style=ss.SCHEMA_LIST_ITEM_STYLE)] + [schema_children]
    return [dbc.ListGroup(sidebar_children, style = ss.SCHEMA_LIST_STYLE, id = "schema_list")]


def make_sidebar_catalogue(df):
    catalogue_div = html.Div(build_sidebar_list(df), id = "sidebar_list_div", style = ss.SIDEBAR_LIST_DIV_STYLE)
    return catalogue_div

def make_sidebar_title():
    sidebar_title = html.Div([
        html.Div(html.H2("Data Directory")),
        html.Div([
            dcc.Input(
            id="main_search",
            placeholder="search",
            ),
            dbc.Button(
            "Search",
            id="search_button",
            n_clicks=0,
            ),
        ])
        ], id = "sidebar_title", style = ss.SIDEBAR_TITLE_STYLE)
    return sidebar_title

def make_sidebar_left(sidebar_title, sidebar_catalogue):
    sidebar_left = html.Div([
        sidebar_title,
        sidebar_catalogue],
        style = ss.SIDEBAR_LEFT_STYLE,
        id = "sidebar_left_div")
    return sidebar_left

def make_context_bar():
    context_bar = html.Div([

        dbc.Collapse(
            dbc.Button(
                "Documentation",
                id="doc_button",
                n_clicks=0,
            ),
            id = "doc_button_collapse",
            is_open= True,
            style = ss.BUTTON_STYLE
        ),

        dbc.Collapse(
            dbc.Button(
                "Metadata",
                id="metadata_button",
                n_clicks=0,
            ),
            id = "metadata_button_collapse",
            is_open= True,
            style = ss.BUTTON_STYLE
        ),

        dbc.Collapse(
            dbc.Button(
                "Coverage",
                id="map_button",
                n_clicks=0,
            ),
            id = "map_button_collapse",
            is_open= True,
            style = ss.BUTTON_STYLE
        )

    ], 
        id = "context_bar_div", 
        style = ss.CONTEXT_BAR_STYLE)
    return context_bar

def make_section_title(title):
    # NOTE: I don't think you can pass styles in Dash - they must be explicit. That might be the same with IDs
    section_title = html.Div(html.H2(title))

    return section_title


def make_map_box(title):
    title_sction = html.Div([make_section_title(title)], id = "map_title", style = ss.MAP_TITLE_STYLE)
    map_box = html.Div([
        title_sction,
        dl.Map(
            center=[54.5,-3.5], zoom=5, scrollWheelZoom=False,
            children=[
            dl.TileLayer(url=constants.MAP_URL, maxZoom=20, attribution=constants.MAP_ATTRIBUTION),
            dl.GeoJSON(data = None, id = "map_region", options = dict(weight=1, opacity=1, color='#05B6AC',fillOpacity=0)
            ,hoverStyle = arrow_function(dict(weight=2, color='#05B6AC', fillOpacity=0.2, dashArray=''))),
            ],id="map", style = ss.DYNA_MAP_STYLE),
        ], id = "map_div", style = ss.MAP_DIV_STYLE)
    return map_box

def make_documentation_box(title, children = "None"):
    title_sction = html.Div([make_section_title(title)], id = "doc_title", style = ss.DOC_TITLE_STYLE)
    if children == "None":
        d1 = html.Div([html.P("Select a schema for more information...", id = "schema_description_text")], id = "schema_description_div")
        d2 = html.Div([html.P("Select a schema for more information...", id = "table_description_text")], id = "table_description_div")
    else:
        d1 = html.Div(children[0], id = "schema_description_div")
        d2 = html.Div(children[1], id = "table_description_div")
    
    doc_box = html.Div([
        title_sction,
        html.Div([
        d1,
        d2,
        ], id = "doc_box", style = ss.DOCUMENTATION_BOX_STYLE)])
    return doc_box

def make_metadata_box(title, children = "None"):
    title_section = html.Div([make_section_title(title)], id = "metadata_title", style = ss.METADATA_TITLE_STYLE)
    if children == "None":
        d1 = html.Div([], id = "table_meta_desc_div")
        d2 = html.Div([], id = "table_metadata_div", style = ss.METADATA_TABLE_DIV_STYLE)
    else:
        d1 = html.Div(children[0], id = "table_meta_desc_div")
        d2 = html.Div(children[1], id = "table_metadata_div", style = ss.METADATA_TABLE_DIV_STYLE)

    meta_box = html.Div([
            title_section,
            html.Div([
            d1,
            d2,
            ], id = "meta_box", style = ss.METADATA_BOX_STYLE)])
    return meta_box

def make_body(sections, ids):
    collapse_sections = []
    for section, s_id in zip(sections, ids):
        collapse_sections.append(dbc.Collapse(section, id = s_id, is_open=True))
    body = html.Div((collapse_sections),id="body",style = ss.BODY_STYLE )
    return body

def make_variable_div(id_type):
    variable_div = html.Div([],key = "None",id = {"type":id_type, "content":"None"})
    return variable_div

def make_app_layout(titlebar, sidebar_left, context_bar, body, variable_divs):
    app_layout =  html.Div([titlebar, sidebar_left, context_bar, body] + variable_divs, id="app",style=ss.APP_STYLE) 
    return app_layout

def make_schema_description(schemas):
    out_text = []
    for col in schemas.columns:
        out_text.append(html.B("{}: ".format(col)))
        out_text.append(" {}".format(schemas[col].values[0]))
        out_text.append(html.Br())
    return [html.P(out_text)]


def make_table_doc(tables):
    table = html.Div([data_doc_table(tables, "table_desc_table")], style = ss.TABLE_DOC_DIV)
    return table


def make_hidden_body():
    body = html.Div([],style=ss.HIDDEN_BODY_STYLE, id = "hidden_body")
    return body