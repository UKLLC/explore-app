from tabnanny import check
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
import warnings
import os

import stylesheet as ss
import constants

pd.options.mode.chained_assignment = None
warnings.simplefilter(action="ignore",category = FutureWarning)

def quick_table(df, id):
    quick_table = dash_table.DataTable(
            id=id,
            data=df.to_dict('records'),
            columns=[{"name": i, "id": i} for i in df.columns], 
            page_size=25,
            editable=False,
            row_selectable=False,
            row_deletable=False,
            style_cell={'textAlign': 'left','overflow': 'hidden',
            'textOverflow': 'ellipsis',
            'maxWidth': 0},
            )
    return quick_table

def data_doc_table(df, id):
    for kw in constants.keyword_cols:
        df[kw] = df[kw].str.strip()
    df["Keywords"] = df["Keywords"]+", "+df[constants.keyword_cols[1]]+", "+df[constants.keyword_cols[2]]+", "+df[constants.keyword_cols[2]]+", "+df[constants.keyword_cols[3]]+", "+df[constants.keyword_cols[4]]
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
            page_size=25,
            style_header=ss.TABLE_HEADER,
            style_cell=ss.TABLE_CELL,
            style_data_conditional=ss.TABLE_CONDITIONAL
            )
    return table


def metadata_doc_table(df, id):
    for kw in constants.keyword_cols:
        df[kw] = df[kw].str.strip()
    df["Keywords"] = df["Keywords"]+", "+df[constants.keyword_cols[1]]+", "+df[constants.keyword_cols[2]]+", "+df[constants.keyword_cols[2]]+", "+df[constants.keyword_cols[3]]+", "+df[constants.keyword_cols[4]]
    df["Keywords"] = df["Keywords"].str.replace(", ,", "")
    df["Keywords"] = df["Keywords"].str.rstrip(",| ,")

    df=df[["Block Name", "Timepoint: Data Collected","Timepoint: Keyword","Number of Participants Invited (n=)", "Number of Participants Included (n=)", "Inclusion Criteria", "Block Description","Links", "Keywords"]]
    df.rename(columns = {"Block Description":"Description", "Number of Participants Invited (n=)":"Participants Invited", "Number of Participants Included (n=)": "Participants Included"})
    table = dash_table.DataTable(
            id=id,
            data=df.to_dict('records'),
            columns=[{"name": i, "id": i} for i in df.columns], 
            page_size=25,
            editable=False,
            row_selectable=False,
            row_deletable=False,
            style_header=ss.TABLE_HEADER,
            style_cell=ss.TABLE_CELL,
            style_data_conditional=ss.TABLE_CONDITIONAL
            )
    return table


def metadata_table(df, id):
    quick_table = dash_table.DataTable(
            id=id,
            data=df.to_dict('records'),
            columns=[{"name": i, "id": i} for i in df.columns], 
            page_size=25,
            editable=False,
            row_selectable=False,
            row_deletable=False,
            style_header=ss.TABLE_HEADER,
            style_cell=ss.TABLE_CELL,
            style_data_conditional=ss.TABLE_CONDITIONAL,
            )
    return quick_table

def basket_review_table(df):
    table = dash_table.DataTable(
        id="basket_review_table", #id = basket_review_table (passed in app)
        data=df.to_dict('records'),
        columns=[{"name": i, "id": i} for i in df.columns], 
        page_size=25,
        editable=False,
        style_header=ss.TABLE_HEADER,
        style_cell=ss.TABLE_CELL,
        row_deletable=True,
        selected_rows=[i for i in range(len(df))]
        )
    return table


def main_titlebar(app, title_text):
    titlebar = html.Div([
        html.Div([
        
        html.Img(
            src = app.get_asset_url("Logo_LLC.png"),
            style = ss.LOGOS_STYLE
        ),
        html.A(
        href="https://ukllc.ac.uk/",
        children=[
        ]
        ),
        html.A(
            href="https://www.ucl.ac.uk/covid-19-longitudinal-health-wellbeing/",
            
            children=[
                html.Img(
                    src = app.get_asset_url("Logo_NCS.png"),
                    style = ss.LOGOS_STYLE
                )
            ]
        )
        ],
        className = "row_layout"
        ),
    ],
    style = ss.TITLEBAR_DIV_STYLE
    )
    return titlebar

def build_sidebar_list(schema_df, current_basket = [], sch_open =[], tab_open = "None"):
    sidebar_children = []
    # Get data sources
    sources = schema_df["Source"].drop_duplicates()
    # Attribute tables to each study
    for schema in sources:
        tables = schema_df.loc[schema_df["Source"] == schema]["Block Name"]

        # CHECKBOXES
        checkbox_items = []
        checkbox_active = []
        for table in tables:
            checkbox_items += [schema+"-"+table]
            if schema+"-"+table in current_basket:
                checkbox_active += [schema+"-"+table]
        
        checkbox_col = html.Div(
            children= dcc.Checklist(
                checkbox_items,
                value = checkbox_active,
                id= {
                        "type":'shopping_checklist',
                        "index" : schema
                    },
                    className = "shopping_checkbox",
                    style = ss.CHECKBOX_STYLE
                    ), 
            id= {
                    "type":'checkbox_col',
                    "index" : schema
                },
            )

        # SCHEMA AND TABLES
        schema_children = dbc.AccordionItem([
            html.Div(
                [    
                dcc.Tabs(
                    id={
                        'type': 'table_tabs',
                        'index': schema
                    },
                    vertical=True,
                    value=tab_open,#"None" by default, otherwise app_state.table
                    parent_className='custom-tabs',
                    className = "table_tabs_container",
                    children = [
                        
                        dcc.Tab(
                            label = table,
                            value = schema+"-"+table,
                            id={
                                'type': 'sidebar_table_item',
                                'index': schema+"-"+table
                            },
                            className = "table_tab",
                            selected_className='table_tab--selected'
                        )
                        for table in tables
                        ],
                    ),
                checkbox_col  
                ],
                className = "list_and_checkbox_div"
                ),
            ],
            title = schema,
            item_id = schema
            )

        sidebar_children += [schema_children]

    study_list = dbc.Accordion(
        sidebar_children,
        id='schema_accordion',
        class_name= "content_accordion",
        always_open=False,
        key = "0",
        active_item = sch_open)
    return study_list


def make_sidebar_catalogue(df):
    catalogue_div = html.Div(
        build_sidebar_list(df), 
        id = "sidebar_list_div", 
        )
    return catalogue_div
 
def make_sidebar_title():
    sidebar_title = html.Div([
        html.Div(html.H2("Catalogue")),
        html.Div(html.P("TODO: filter status")),
        html.Button("Placeholder", id = "search_button"),
        dcc.Input("placeholder", id ="main_search")
        ], id = "sidebar_title")
    return sidebar_title


def make_sidebar_left(sidebar_title, sidebar_catalogue):
    sidebar_left = html.Div([
        dbc.Collapse(
            [
            sidebar_title,
            sidebar_catalogue
            ]
            ,
            id="sidebar-collapse",
            is_open=True,
            dimension="width",
            )
    ],
    id = "sidebar_left_div")
    return sidebar_left


def make_map_box(title= "Map: [study placeholder]", children = []):
    map_box = html.Div([
        html.Div([
            dl.Map(
                center=[54.5,-3.5], 
                zoom=6, 
                children=[
                    dl.TileLayer(url=constants.MAP_URL, 
                        maxZoom=10, 
                        attribution=constants.MAP_ATTRIBUTION),
                    dl.GeoJSON(data = None, 
                        id = "map_region", 
                        options = dict(weight=1, opacity=1, color='#05B6AC',fillOpacity=0),
                        hoverStyle = arrow_function(dict(weight=2, color='#05B6AC', fillOpacity=0.2, dashArray=''))
                        ),
                ],id="map_object", style = ss.DYNA_MAP_STYLE),
            ], id = "Map", style = ss.MAP_BOX_STYLE)
        ],
        )
    return map_box

def make_documentation_box(title = "Block-Level Metadata: [study placeholder]", children = [None, None]):
    if children == [None, None]:
        d1 = html.Div([html.P("Select a schema for more information...", id = "schema_description_text")], id = "schema_description_div", className="container_box")
        d2 = html.Div([html.P("Select a schema for more information...", id = "table_description_text")], id = "table_description_div")
    else:
        d1 = html.Div(children[0], id = "schema_description_div", className="container_box")
        d2 = html.Div(children[1], id = "table_description_div")
    
    doc_box = html.Div([
        html.Div([
        d1,
        d2,
        ], 
        id = "Documentation", 
        style = ss.DOCUMENTATION_BOX_STYLE
        )
        ],
        )
    return doc_box

def make_metadata_box(title = "Variable-Level Metadata: [study placeholder]", children = [None, None]):
    if children == [None, None]:
        d1 = html.Div([], id = "table_meta_desc_div")
        d2 = html.Div([], id = "table_metadata_div", style = ss.METADATA_TABLE_DIV_STYLE)
    else:
        d1 = html.Div(children[0], id = "table_meta_desc_div")
        d2 = html.Div(children[1], id = "table_metadata_div", style = ss.METADATA_TABLE_DIV_STYLE)

    meta_box = html.Div([
        html.Div([
            d1,
            html.Div([
                html.H2("Metadata variable search"),
                html.P("Use the search bar below to filter variables in this block. You can currently search by variable name, variable description, values and value descriptions."),
                dcc.Input(
                id="metadata_search",
                placeholder="search",
                ),
                dcc.Checklist(
                ["Show values"],
                id="values_toggle",
                inline= True
                ),
            ],
            className="container_box"
            ),
            d2,

        ], id = "Metadata", style = ss.METADATA_BOX_STYLE)
        ],
    )
    return meta_box

def make_landing_box():
    landing_box = html.Div([
        html.Div(
            [
            html.H3("Welcome to the UK LLC Data Discovery Portal"),
            html.P(constants.LANDING_GENERAL_TEXT, className="padding_p")
            ],
            id = "landing_general_div",
        ),
        
        html.Div([ # Instructions
            html.Div(
            [
                html.H3("Explore the data"),
                html.Ul(children = [html.Li(i) for i in constants.LANDING_INSTRUCTION_TEXT1]),
            ],
            id = "landing_instructions_div1",
            ),
            html.Div(
            [
                html.H3("Build a shopping basket"),
                html.Ul(children = [html.Li(i) for i in constants.LANDING_INSTRUCTION_TEXT2]),
            ],
            id = "landing_instructions_div2",
            ),
        ],
        ),

        html.Div([
            html.Div([
                html.H3("Working in the TRE"),
                html.P("There is currently no cost to access data in the TRE.", className="padding_p"),
                html.P("You must be UK-based and an Accredited Researcher (link) – read about the application process in the UK LLC Data Access and Acceptable Use Policy (link).", className="padding_p"),
                html.P("Submit an Expression of Interest through the HDR UK Innovation Gateway (link).", className="padding_p"),
                html.P("Email [link]access@ukllc.ac.uk[/link] if you have any queries.", className="padding_p"),
                html.P("Find out more:", className="padding_p"),
                html.Ul(children = [html.Li(i) for i in constants.WORKING_IN_TRE_TEXT]),
            ],),
        ],
        ),

        html.Div([ # Links
            html.Div(
            [
                html.Iframe(
                src="https://www.youtube.com/embed/QfyaG3zemcs", 
                title="YouTube video player",  
                allow="accelerometer, autoplay, clipboard-write, encrypted-media, gyroscope, picture-in-picture",
                id = "embed_video"
                ),
            ],
            id = "landing_info_div"
            ),
        ],
        className = "container_box2", 
        )
    ], 
    id = "Landing",
    className = "body_box",
    )
        
    return landing_box

def make_basket_review_box():    
    basket_review_box = html.Div([
        html.Div([

            html.Div([
            html.P("Select data blocks by checking tick boxes in the left sidebar."),
            ],
            className="container_box"),
                
            #Main body is a table with Source, block, description, checkbox
            #Clear all button at top of checklist col - far from save
            #Big save button at the bottom
            #Recommend box? bottom or RHS 
            
            # Get list of selected tables & doc as df
            
            html.Div([
                html.Div([
                html.P("There are currently no data blocks in the shopping basket"),
                ], className="container_box"),
                dash_table.DataTable(
                        id="basket_review_table", #id = basket_review_table (passed in app)
                        data=None,#df.to_dict('records'),
                        columns=None,#[{"name": i, "id": i} for i in df.columns], 
                        page_size=20,
                        editable=False,
                        row_selectable=False,
                        row_deletable=True, # TODO test this?
                        style_header=ss.TABLE_HEADER,
                        style_cell=ss.TABLE_CELL,
                        )
                ],
                id = "basket_review_table_div"),
                html.Div([
                dbc.Button(
                    "clear basket",
                    id="clear_basket_button",
                    n_clicks=0,
                    ),
                dbc.Button(
                    "Save",
                    id="save_button",
                    n_clicks=0,
                    ),
                ],
                className = "row_layout")

                ],
                id = "Basket Review", style = ss.LANDING_BOX_STYLE)],
        )
    return basket_review_box

def make_body(sidebar):
    return html.Div([
        sidebar,
        html.Button(">",
            id="sidebar-collapse-button",
            n_clicks=0,),
        html.Div([
            make_landing_box()
            ],
            id = "body_content")
        ], 
        id="body")


def make_variable_div(id_type, data = "None"):
    variable_div = dcc.Store(id = id_type, data = data)
    return variable_div

def make_variable_div_list(id_type, indices):
    divs = []
    for i in indices:
        divs += [html.Div([],key = "0", id = {"type":id_type, "index":str(i)})]
    return divs


def make_app_layout(titlebar, body, account_section, variable_divs):
    app_layout =  html.Div([titlebar, body, account_section] + variable_divs, id="app",style=ss.APP_STYLE) 
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
    body = html.Div([
            make_basket_review_box(),
            make_documentation_box(),
            make_metadata_box(),
            make_map_box()
        ],
        style=ss.HIDDEN_BODY_STYLE,
        id = "hidden_body")
    return body


def make_account_section():
    '''
        dbc.DropdownMenu(
            label = "Account",
            children = [
                dbc.DropdownMenuItem("Load Basket (placeholder)"),
                dbc.DropdownMenuItem("Save Basket (placeholder)"),
                dbc.DropdownMenuItem("Download Basket", id = "dl_button_2", n_clicks=0),
                dbc.DropdownMenuItem("Log Out (placeholder"),
            ],
            id="account_dropdown",
            className = "account_dropdown",
            style = ss.ACCOUNT_DROPDOWN_STYLE 
            ),
            
            dcc.Download(id="sb_download")
        '''
    dropdown = html.Div([
        html.Div([
            dbc.NavItem("About", id = "about"),
            dbc.NavItem("Search",  id = "search"),
            dbc.DropdownMenu(
                label = html.P("Data Description", id = "dropdown_label"),
                children = [
                    dbc.DropdownMenuItem("Load Basket (placeholder)"),
                    dbc.DropdownMenuItem("Save Basket (placeholder)"),
                    dbc.DropdownMenuItem("Download Basket", id = "dl_button_2", n_clicks=0),
                    dbc.DropdownMenuItem("Log Out (placeholder"),
                ],
                id="account_dropdown",
                className = "account_dropdown",
            ),   
            dcc.Download(id="sb_download"),
            dbc.NavItem("Review", id = "review"),
            dbc.NavItem("Account", id = "accout"),
        
        ], id = "title_nav_style"),

        html.Div([
        "account info"
        ])], 
        
        style = ss.ACCOUNT_DROPDOWN_DIV_STYLE)
    return dropdown