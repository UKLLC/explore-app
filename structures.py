from pydoc import classname
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
        className= "content_accordion",
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
        html.Div(html.P("TODO: filter status"))
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

def make_about_box():
    landing_box = html.Div([
        html.H1("Placeholder for an attention grabbing header"),
        dbc.Accordion(
            [
            dbc.AccordionItem(
                "Browse the UK LLC Data Discovery Portal to discover data from the 20+ longitudinal population studies that contribute data to the UK LLC Trusted Research Environment (TRE). The metadata encompass study-collected and linked data blocks, including health, geospatial and non-health routine records. Use this tool to select data blocks from our catalogue for a new data request or data amendment.etc",
                title="What is the UK LLC (placeholder)",
                className = "body_accordion",
                id = "about_collapse1"
            ),
            dbc.AccordionItem(
                "Placeholder text",
                title="Understanding the UK LLC data catalogue",
                className = "body_accordion",
                id = "about_collapse2"
            ),
            dbc.AccordionItem(
                "We have data. Its probably worth your time to take a look at it.",
                title="Explore the data",
                className = "body_accordion",
                id = "about_collapse3"
            ),
            dbc.AccordionItem(
                "select the data blocks you want etc",
                title="Build a shopping basket",
                className = "body_accordion",
                id = "about_collapse4"
            ),
            dbc.AccordionItem(
                html.Iframe(
                        src="https://www.youtube.com/embed/QfyaG3zemcs", 
                        title="YouTube video player",  
                        allow="accelerometer, autoplay, clipboard-write, encrypted-media, gyroscope, picture-in-picture",
                        id = "embed_video"
                    ),
                title="User guide etc",
                className = "about_accordion_item",
                id = "about_collapse5"
            ),
            dbc.AccordionItem(
                "More things, please let me know",
                title="Some other heading about the app/crucial information we need to share",
                className = "body_accordion",
                id = "about_collapse6"
            ),
            
            ],
        always_open=True,
        className = "about_accordion"
        ),
        html.Div(
            [
            html.P("Placeholder for bottom stuff like logos or what have you", className="padding_p"),

            ],
            id = "about_content_div7",
        ), 
    ], 
    id = "body_about",
    className = "body_box",
    )
        
    return landing_box

def make_search_box():
    doc_box = html.Div([
        html.P("Placeholder paragraph talking about how this is a search tab for looking through data blocks"),
        html.P("Follow on paragraph reminding what a data block is"),
        html.H2("Master Search"),
        html.Div([
            dcc.Checklist(
                ['Study data', 'NHS data', 'Geo data', 'Admin data'],
                [],
                inline=True
            ),
            dcc.Input("", id ="main_search", className="search_field", placeholder = "search"),
            html.Button("search", id = "search_button"),
            html.Button("Advanced Options", id = "advanced_options_button")
        ],
        className = "style_div",
        id = "search_style_div"
        ),
        dbc.Collapse(
            html.Div([
                dbc.Accordion([
                    dbc.AccordionItem(
                        html.Div([
                            html.Div([
                                html.H3("Include"),
                                dcc.Dropdown(["PH1", "PH2", "PH3"], id = "include_dropdown", multi = True),
                            ],
                            className = "container_div",
                            ),
                            html.Div([
                                html.H3("Exclude"),
                                dcc.Dropdown(["PH1", "PH2", "PH3"], id = "exclude_dropdown", multi = True)
                            ],
                            className = "container_div"
                            ),
                        ], 
                        className = "row_layout"
                        ),
                    title="Data Source",
                    className = "search_accordion",
                    id = "data_source_accordion"
                    )
                ]),
                dbc.Accordion([
                    dbc.AccordionItem(
                        html.Div([
                            html.Div([
                                dcc.Checklist(
                                    ["item 1", "item 2", "item 3", "item 4", "item 5"],
                                    labelStyle = {"display": "flex", "align-items": "center"},
                                    id = "search_checklist_1"
                                )
                            ],
                            className = "container_div",
                            ),
                            html.Div([
                                dcc.Checklist(
                                    ["item 6", "item 7", "item 8", "item 9", "item 10"],
                                    labelStyle = {"display": "flex", "align-items": "center"},
                                )
                            ],
                            className = "container_div"
                            ),
                            html.Div([
                                dcc.Checklist(
                                    ["item 11", "item 12", "item 13", "item 14", "item 15"],
                                    labelStyle = {"display": "flex", "align-items": "center"},
                                )
                            ],
                            className = "container_div",
                            ),
                            html.Div([
                                dcc.Checklist(
                                    ["item 16", "item 17", "item 18", "item 19", "item 20"],
                                    labelStyle = {"display": "flex", "align-items": "center"},
                                )
                            ],
                            className = "container_div"
                            ),
                        ], 
                        className = "row_layout"
                        ),
                    title="Topic Checkboxes",
                    className = "search_accordion",
                    id = "topic_accordion"
                    )
                ]),
                dbc.Accordion([
                    dbc.AccordionItem(
                        html.Div([
                            dcc.RangeSlider(min = 0, max = 100, step = 5, value=[20, 40], id='collection_age_slider'),
                        ], 
                        className = "container_div"
                        ),
                    title="Collection Age",
                    className = "collection_age_accordion",
                    id = "collection_age_accordion"
                    )
                ]),
                dbc.Accordion([
                    dbc.AccordionItem(
                        html.Div([
                            dcc.RangeSlider(min = 0,  max = 9, step = 1, value=[5, 7], id='collection_time_slider',
                            marks={
                                0: '1940',
                                1: "1950",
                                2: '1960',
                                3: "1970",
                                4: "1980",
                                5: "1990",
                                6: "2000",
                                7: "2010",
                                8: "2020",
                                9: "2030"}
                                ,
                            )
                        ], 
                        className = "container_div"
                        ),
                    title="Collection Time",
                    className = "collection_time_accordion",
                    id = "collection_time_accordion"
                    )
                ]),
                ],
                className = "container_div"
            ),
            id = "advanced_options_collapse",
            is_open = False
        ),
        html.Div(
            html.Div([
            ],id = "search_metadata_div"
        )
       )
    ], 
    id = "body_search", 
    className = "body_box"
    )
    return doc_box

def make_study_box(children = [None, None]):
    if children == [None, None]:
        d1 = html.Div([html.P("Select a schema for more information...", id = "schema_description_text")], id = "schema_description_div", className="container_box")
        d2 = html.Div([html.P("Select a schema for more information...", id = "table_description_text")], id = "table_description_div")
    else:
        d1 = html.Div(children[0], id = "schema_description_div", className="container_box")
        d2 = html.Div(children[1], id = "table_description_div")
    
    doc_box = html.Div([
        d1,
        d2,
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
            ],
            id = "Map", 
            style = ss.MAP_BOX_STYLE
            )
        ], 
        id = "body_study", 
        className = "body_box"
    )

    return doc_box

def make_block_box(children = [None, None]):
    if children == [None, None]:
        d1 = html.Div([], id = "table_meta_desc_div")
        d2 = html.Div([], id = "table_metadata_div", style = ss.METADATA_TABLE_DIV_STYLE)
    else:
        d1 = html.Div(children[0], id = "table_meta_desc_div")
        d2 = html.Div(children[1], id = "table_metadata_div", style = ss.METADATA_TABLE_DIV_STYLE)

    meta_box = html.Div([
        d1,

        d2,
    ], 
    id = "body_block", 
    className = "body_box",
    style = ss.METADATA_BOX_STYLE
    )
       
    return meta_box

def make_basket_review_box():    
    basket_review_box = html.Div([

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
    id = "body_review", 
    className = "body_box",
    style = ss.LANDING_BOX_STYLE)
    return basket_review_box

def make_body(sidebar):
    return html.Div([
        sidebar,
        html.Button(">",
            id="sidebar-collapse-button",
            n_clicks=0,),
        html.Div([
            make_about_box()
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
            make_search_box(),
            make_study_box(),
            make_block_box(),
            make_basket_review_box(),
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
            dbc.Button("About", className='nav_button', id = "about"),
            dbc.Button("Search",  className='nav_button', id = "search"),
            dbc.DropdownMenu(
                label = html.P("Data Description", className = "nav_button",),
                children = [
                    dbc.DropdownMenuItem("Study", id = "dd_study"),
                    dbc.DropdownMenuItem("Data Block", id = "dd_data_block"),
                    dbc.DropdownMenuItem("Linked?", id = "dd_linked"),
                ],
                id="data_description_dropdown",
                className = "nav_button",
            ),   
            dcc.Download(id="sb_download"),
            dbc.Button("Review", className='nav_button', id = "review"),
            dbc.DropdownMenu(
                label = html.P("Account",  className = "nav_button",),
                children = [
                    dbc.DropdownMenuItem("Load Basket (placeholder)", id = "a_load"),
                    dbc.DropdownMenuItem("Save Basket (placeholder)", id = "a_save"),
                    dbc.DropdownMenuItem("Download Basket", id = "dl_button_2", n_clicks=0),
                    dbc.DropdownMenuItem("Log Out (placeholder", id = "a_log_out"),
                ],
                id="account_dropdown",
                className = "nav_button",
            ),   
        ], id = "title_nav_style"),

        html.Div([
        "account info"
        ])], 
        
        style = ss.ACCOUNT_DROPDOWN_DIV_STYLE)
    return dropdown