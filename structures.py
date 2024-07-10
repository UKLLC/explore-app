import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
import pandas as pd
from dash import dash_table
import warnings
import plotly.graph_objects as go

import stylesheet as ss
import constants

pd.options.mode.chained_assignment = None
warnings.simplefilter(action="ignore",category = FutureWarning)

def make_table(df, id, id2= "default", page_size = 25):
    table = dash_table.DataTable(
            id={
            'type': id,
            'index': id2
            },
            data=df.to_dict('records'),
            columns=[{'id': i, 'name': i, 'presentation': 'markdown'} if "link" in i.lower() else {"name": i, "id": i} for i in df.columns], 
            page_size=page_size,
            editable=False,
            row_selectable=False,
            row_deletable=False,
            style_table=ss.TABLE_STYLE,
            style_header=ss.TABLE_HEADER,
            style_cell=ss.TABLE_CELL,
            style_data_conditional=ss.TABLE_CONDITIONAL
            ),
    return table

def make_table_dict(df , id, page_size = 25, ):
    table = dash_table.DataTable(
            id=id,
            data=df,
            columns=[{'id': i, 'name': i, 'presentation': 'markdown'} if "link" in i.lower() else {"name": i, "id": i} for i in df[0].keys()], 
            page_size=page_size,
            editable=False,
            row_selectable=False,
            row_deletable=False,
            style_table=ss.TABLE_STYLE,
            style_header=ss.TABLE_HEADER,
            style_cell=ss.TABLE_CELL,
            style_data_conditional=ss.TABLE_CONDITIONAL
            ),
    return table


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
                src = app.get_asset_url("explore_lower_full_logo_regular.png"),
                className = "llc_logo",
                id = "llc_logo"
            ),
            html.A(
            href="https://ukllc.ac.uk/",
            children=[
            ]),
        ],
        className = "row_layout"
        ),
    ],
    className = "title_div"
    )
    return titlebar

def build_sidebar_list(blocks_df, current_basket = [], sch_open =[], tab_open = "None"):
    sidebar_children = []
    # Get data sources
    sources = blocks_df["source"].drop_duplicates()
    # Attribute tables to each study
    for schema in sources:
        source_name = blocks_df.loc[blocks_df["source"] == schema]["source_name"].values[0]
        tables = blocks_df.loc[blocks_df["source"] == schema]["table"]
        table_names = blocks_df.loc[blocks_df["source"] == schema]["table_name"]
        table_type = blocks_df.loc[blocks_df["source"] == schema]["Type"].values[0]

        if table_type.lower() == "lps":
            style_classname = "LPS_accordion"
            collapse_style_classname = "LPS_collpase"
        elif table_type.lower() == "linked":
            style_classname = "linked_accordion"
            collapse_style_classname = "linked_collpase"

        collapse_open = False
        if schema in sch_open and sch_open[schema] == True:
            collapse_open = True

        # Tooltip
        source_tooltip = dbc.Tooltip(
            source_name,
            delay = {"show" : 50, "hide":0},
            target= {
                    "type":'button_text',
                    "index" : schema
                },
            placement="right",
        )

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

        # SCHEMA
        source = html.Div([
            html.Div(
                [
                html.Div (
                    [
                    html.Div(
                        [html.Div(
                            schema, 
                            id = {
                            "type":'button_text',
                            "index" : schema},
                            className = "button_text"
                            ),
                            ],
                        id= {
                            "type":'source_title',
                            "index" : schema
                        },
                        className = "source_title",
                        n_clicks = 0
                    ),
                    html.Button(
                        "",
                        id= {
                            "type":'source_collapse_button',
                            "index" : schema
                        },
                        className = "source_collapse_button"
                    )                
                    ],
                    className = "row_layout"
                )
                ],
                className = "collapse-button"
            ),
        ],
        className = style_classname
        )

        # TABLES
        table = dbc.Collapse([
            html.Div(children = [  
                dcc.Tabs(
                id={
                    'type': 'table_tabs',
                    'index': schema
                },
                vertical=True,
                value= "None", #by default, otherwise app_state.table
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
                        selected_className="table_tab--selected"
                    )
                    for table in tables
                    ],
                ),
                checkbox_col  
                ],
                className = "list_and_checkbox_div"
                ),
            ],
            id= {
                "type":'source_collapse',
                "index" : schema
                },
            className = collapse_style_classname,
            is_open = collapse_open
            )

        sidebar_children += [source, source_tooltip, table]

    study_list = html.Div(
        sidebar_children,
        id='schema_accordion',
        className= "content_accordion",
        )
    return study_list


def make_sidebar_catalogue(df):
    catalogue_div = html.Div(
        build_sidebar_list(df), 
        id = "sidebar_list_div", 
        )
    return catalogue_div
 
def make_sidebar_title():
    sidebar_title = html.Div([
        html.Div(html.H2("UK LLC Data Catalogue")),
        html.Div([
                html.Div([
                    html.P("Showing full catalogue"), 
                ], id = "sidebar_filter"),
                dbc.Button("Reset filters", id = "clear_search2", className = "reset_button")
            ], 
            className = "row_layout")
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

def make_about_box(app):
    landing_box = html.Div([
        html.H1("Placeholder for an attention grabbing header"),
        dbc.Accordion(
            [
            dbc.AccordionItem(
                "Browse the UK LLC Data Discovery Portal to discover data from the 20+ longitudinal population studies that contribute data to the UK LLC Trusted Research Environment (TRE). The metadata encompass study-collected and linked datasets, including health, geospatial and non-health routine records. Use this tool to select datasets from our catalogue for a new data request or data amendment.etc",
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
                "select the datasets you want etc",
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

def make_search_box(df, themes):
    '''
    Search box TODO:
        Source type checkboxes - LPS, NHS, Geo, Admin
        Include - takes all possible sources
        Topic Checkboxes - take all recognised topic tags/keywords
        Collection age
        Collections time

        We need to make a table with all of these fields in it for every table:
        type, topics, collection age, collection time

        Ideally we have a search index table, with 1 row per table. If we get a match, we look it up in a info table. 
    '''
    sources = list(df["source"].drop_duplicates().sort_values().values)
    doc_box = html.Div([
        html.Div([
            html.H1("UK LLC Explore"),
            html.Hr(),
            html.Div([
                html.P("Search our catalogue of longitudinal and linked data and build a data request.")
            ]),
            ], 
            className = "text_block" ,
            id = "intro_div"),
        html.Div([
            html.Div([
                dcc.Checklist(
                    ['Study data', 'Linked data'],
                    ['Study data', 'Linked data'],
                    inline=True,
                    id = "include_type_checkbox"
                ),
                html.Div([
                    dcc.Input("", id ="main_search", className="search_field", placeholder = "Search query"),
                    html.Button("search", id = "search_button"),
                ],
                className = "row_layout",
                id = "main_search_row")
            ],
            className = "style_div",
            id = "search_style_div"
            ),
            dbc.Accordion([
                dbc.AccordionItem( 
                    html.Div([
                        dbc.Accordion([
                            dbc.AccordionItem(
                                html.Div([
                                    html.Div([
                                        html.H3("Include"),
                                        dcc.Dropdown(sources, id = "include_dropdown", multi = True),
                                    ],
                                className = "container_div",
                                ),
                                html.Div([
                                    html.H3("Exclude"),
                                    dcc.Dropdown(sources, id = "exclude_dropdown", multi = True)
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
                                    dcc.Dropdown(themes, id = "tags_search", multi = True),
                                ], 
                                className = "container_div"
                                ),
                            title="Topic Checkboxes",
                            className = "search_accordion",
                            id = "topic_accordion"
                            )
                        ]),
                        dbc.Accordion([
                            dbc.AccordionItem(
                                html.Div([
                                    dcc.RangeSlider(min = 0, max = 100, step = 5, value=[0, 100], id='collection_age_slider'),
                                ], 
                                className = "container_div"
                                ),
                            title="Collection Age",
                            className = "search_accordion",
                            id = "collection_age_accordion"
                            )
                        ]),
                        dbc.Accordion([
                            dbc.AccordionItem(
                                html.Div([
                                    dcc.RangeSlider(min = 0,  max = 9, step = 1, value=[0, 9], id='collection_time_slider',
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
                            className = "search_accordion",
                            id = "collection_time_accordion"
                            )
                        ]),
                        
                        dbc.Button("Reset filters", id = "clear_search1", className = "reset_button")
                        ],
                        className = "container_div"
                    ),
                title = "Advanced Options",
                )
                
            ],    
            id = "advanced_options_collapse",
            start_collapsed=True
            ),

            dcc.Tabs(
                id = "search_type_radio",
                value = "Sources",
                children = [
                    dcc.Tab(label = "Sources", value = "Sources"),
                    dcc.Tab(label = "Datasets", value = "Datasets"),
                    dcc.Tab(label = "Variables", value = "Variables")
                ]
                ),
            dcc.Loading(
                children = [
                html.Div([
                    html.Div([], id = "search_text"),
                    html.Div(
                        dcc.Checklist(["Show values"], ["Show values"], id = "toggle_values", className = "button"),
                    ),
                    html.Div([], id = "search_metadata_div")
                ],
                className = "container_div"
                ),
                ],
                id = "search_loading",
                type = "circle",
                parent_className  = "loading",
                className = "loading_spinner"
            )

        ],
        className = "shadow_block"
        )
    ], 
    id = "body_search", 
    className = "body_box"
    )
    return doc_box


def make_d_overview_box(source_counts, dataset_counts):
    d_overview_box = html.Div([
        html.Div([
            html.H1("Overview"),
            html.Hr(),
            html.Div([
                html.H4("The overview sunburst graph shows the complete contents of the UK LLC database scaled by the number of constituent participants. Click a segment of the graph to focus in on it."),
            ]),
        ],
        id = "overview_title",
        className = "text_block"
        ),
        html.Div([
            sunburst(source_counts, dataset_counts)
        ],
        id = "overview_sunburst_div"
        ),
    ],
    id = "body_overview", 
    className = "body_box"
    )
    return d_overview_box


def make_study_box():
    study_box = html.Div([
        html.Div([
            html.H1("Source", id = "source_category"),
            html.Hr(),
            html.Div([
                html.H4("Browse and select a source for more information", id = "study_title"),
            ]),
        ], 
        className = "desc_title",
        ),
        html.Div([
            html.Div([
                html.Div(["Its a description"], id = "source_description_div", className = "text_block"),
                html.Div(["placeholder for summary table"], id = "study_summary", className = "container_div"),
            ], className = "container_line_50"),
            html.Div([
                dcc.Tabs([
                    dcc.Tab(label="Age Distribution", children = [
                        dcc.Loading(children = [
                        html.Div(["placeholder for age table"], id = "source_age_graph", className = "container_div")
                        ], type = "circle",)
                    ]),
                    dcc.Tab(label="Linkage Rates", children =[
                        dcc.Loading(children = [
                        html.Div(["Placeholder for pie char"], id = "source_linkage_graph", className = "container_div")
                        ], type = "circle",)
                    ]),
                    dcc.Tab(label="Coverage", children =[
                        #dbc.Tooltip(
                        #    "Coverage is deduced from NHS England linkage from a participant's most recent interaction with healthcare services. It does not reflect coverage at the time of collection. Information is only available for participants living in England.",
                        #    target="map_tooltip",
                        #),
                        dcc.Loading(children = [
                        html.Div([
                            html.P("Coverage is deduced from NHS England linkage from participants' most recent interaction with healthcare services. It does not reflect coverage at the time of collection. Information is only available for participants living in England.", className = "small_text"),
                            #html.I(className = "bi bi-info-circle", id = "map_tooltip" ),
                            html.Div([
                                
                                ],
                                id = "Map", ),],

                            className = "tab_div"
                            )
                        ], type = "circle",)
                    ])
                ], className = "tab_parent"),
            ], className = "container_line_50" )
            
        ],
        className = "row_layout",
        id = "source_row",
        ),
        html.Div([], id = "study_table_div"),
        ], 
        id = "body_source", 
        className = "body_box"
    )
    return study_box

def make_block_box(children = [None, None]):
    dataset_box = html.Div([
        html.Div([
            html.H1("UK LLC Dataset", id = "dataset_header"),
            html.Hr(),
            html.Div([
                html.P("Browse and select a dataset for more information", id = "dataset_title"),
            ]),
        ], 
        className = "desc_title",
        ),

        html.Div([
            html.Div([
                html.Div(["Placeholder description"], id = "dataset_description_div", className = "text_block"),
                html.Div(["placeholder for summary table"], id = "dataset_summary", className = "container_div"),
            ], className = "container_line_50"),
            html.Div([
                dcc.Tabs([
                    dcc.Tab(label="Age Distribution", children =[
                        html.Div(["placeholder for age table"], id = "dataset_age_graph", className = "container_div")
                    ]),
                    dcc.Tab(label="Linkage Rates", children =[
                        html.Div(["Placeholder for pie char"], id = "dataset_linkage_graph", className = "container_div")
                    ])
                ], className = "tab_parent"),
            ], 
            className = "container_line_50" ),
        ],
        className = "row_layout",
        id = "dataset_row"),
        html.Div(make_table(pd.DataFrame(data = {"col1":["val1"]}), "search_metadata_table"), id = "dataset_variables_div"),
        ], 
        id = "body_dataset", 
        className = "body_box"
    )
    return dataset_box

def make_modal_background():
    return html.Div([], id = "modal_background", className = "modal_background")


def FAQ():
    body = html.Div([
            html.H1("Frequently Asked Questions"),
            html.Hr(className = "center_hr"),
            html.Div([
                html.H2("1. How do I request data from the UK LLC"),
                html.P("Contact access@ukllc.ac.uk who will direct you on the process of starting a project and making a data request.")
            ],
            className = "FAQ_QA"
            ),
            html.Div([
                html.H2("2. Why is your FAQ section so empty?"),
                html.P("We haven't had many questions yet. If you have any, please send them to support@ukllc.ac.uk")
            ],
            className = "FAQ_QA"
            ),
            html.Div([
                html.H2(""),
                html.P("")
            ],
            className = "FAQ_QA"
            ),
            html.Div([
                html.H2(""),
                html.P("")
            ],
            className = "FAQ_QA"
            ),
        ])
    '''
    FAQ ideas:
    1. How do I request data from the UK LLC
    Contact access@ukllc.ac.uk who will direct you on the process of starting a project and making a data request.

    2. Why is your FAQ section so empty?
    We haven't had many questions yet. If you have any, please send them to support@ukllc.ac.uk

    
    '''
    return body

def contact_us():
    body = html.Div([
            html.H1("Contact us"),
            html.Hr(className = "center_hr"),
            html.P("We welcome questions, so please do get in touch. If your query is about:"),
            html.Ul([
                html.Li(
                    html.Div([
                        html.P("The data held in the TRE, please contact:   support@ukllc.ac.uk"),
                    ],
                ),
                className = "FAQ_QA"
                ),
                html.Li(
                    html.Div([
                        html.P("Applying to access the TRE, please contact:   access@ukllc.ac.uk"),
                    ],
                    className = "FAQ_QA"
                    ),
                ),
                html.Li(
                    html.Div([
                        html.P("Your LPS joining the UK LLC, please contact:   info@ukllc.ac.uk"),
                    ],
                    className = "FAQ_QA"
                    ),
                ),
            ])
    ])
    return body


def modal():
    modal = html.Div(
    [
        dbc.Modal(
            [
                dbc.ModalBody([
                    dbc.Button(
                        html.I(className = "bi bi-x-lg", ), id = "modal_close", className="offcanvas_close", n_clicks=0
                    ),
                    html.Div([
                        FAQ()
                    ],
                    className = "modal_body",
                    id = "modal_body"
                    )
                ]
                )

            ],
            id="modal",
            is_open=False,
            className = "modal"
        ),
    ]
    )
    return modal

def make_basket_review_offcanvas():
    offcanvas = html.Div([dbc.Offcanvas(
        
        [
        dbc.Button(html.I(className = "bi bi-x-lg", ), id = "offcanvas_close", n_clicks = 0),
        html.Div([
            text_block("You currently have no datasets in your selection. Use the checkboxes in the UK LLC Data Catalogue sidebar to add datasets.")
        ],
        id = "basket_review_text_div"),
        html.Div([
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
                "clear selection",
                id="clear_basket_button",
                className = "red_button",
                n_clicks=0,
                ),
            dbc.Button(
                "Save",
                id="save_button",
                className = "blue_button",
                n_clicks=0,
                ),
        ],
        className = "row_layout")

        ],
        
        is_open=False, 
        id = "offcanvas_review",
        className = "offcanvas",
        backdrop = True,
        placement = "end"
        ),
        ])
    
    return offcanvas 

def make_basket_review_box():
    # DEPRICATED?    
    basket_review_box = html.Div([
            #Main body is a table with Source, block, description, checkbox
            #Clear all button at top of checklist col - far from save
            #Big save button at the bottom
            #Recommend box? bottom or RHS 
            
            # Get list of selected tables & doc as df
            html.Div([
                text_block("You currently have no datasets in your selection. Use the checkboxes in the UK LLC Data Catalogue sidebar to add datasets.")
            ],
            id = "basket_review_text_div"),
            html.Div([
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
                    "clear selection",
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
    )
    return basket_review_box

def sidebar_collapse_button():
    button = html.Button(
            html.I(className = "bi bi-list", ),
            id="sidebar-collapse-button",
            n_clicks=0,)
    return button

def make_body(sidebar, app, spine, themes):
    return html.Div([
        sidebar,
        sidebar_collapse_button(),
        html.Div([
            make_search_box(spine, themes),
            footer(app),
        ],
        id = "body_content"),

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

def make_hidden_items(hidden_items):
    return html.Div(
        hidden_items,
        className = "Hidden"
    )
    

def make_app_layout(titlebar, body, account_section, variable_divs ):
    app_layout =  html.Div([titlebar, body, account_section, make_modal_background(), make_basket_review_offcanvas(),modal(), ] + variable_divs, id="app") 
    return app_layout

def make_info_box(df):
    out_text = []
    for col in df.columns:
        #row
        if ("website" not in col.lower()) and ("link" not in col.lower()):
            row = html.Div([
                # First column
                html.Div([
                    html.B(col +":")
                ], className = "info_box_left"),

                # Second column
                html.Div([
                    html.P(str(df[col].values[0]).replace("\n", ""))
                ], className = "info_box_right")
            ])
        else:
            row = html.Div([
                # First column
                html.Div([
                    html.B(col)
                ], className = "info_box_left"),

                # Second column
                html.Div([
                    dcc.Markdown(str(df[col].values[0]).replace("\n", ""))
                ], className = "info_box_right")
            ])
            [{'id': x, 'name': x, 'presentation': 'markdown'} if x == 'Link(s)' else {'id': x, 'name': x} for x in df.columns],
        out_text.append(row)
    return html.Div(out_text)

def make_schema_description(schemas):
    # Make the study tab variables
    schemas = schemas[constants.SOURCE_SUMMARY_VARS.keys()].rename(columns = constants.SOURCE_SUMMARY_VARS)
    schemas["Number of datasets"] = schemas["Number of datasets"].astype(int)
    schemas["Participant count"] = schemas["Participant count"].astype(int)
    return make_info_box(schemas)

def make_block_description(blocks):
    # Make the study tab variables
    blocks = blocks[constants.BLOCK_SUMMARY_VARS.keys()].rename(columns = constants.BLOCK_SUMMARY_VARS)
    blocks["Participants Included"] = blocks["Participants Included"].astype(int)
    
    blocks["Collection Duration"] = blocks["Collection Start"] + " - " + blocks["Collection End"]
    blocks = blocks.drop(columns = ["Collection Start", "Collection End"])
    print("DEUBG:", blocks.columns)
    blocks = blocks.fillna( "Not currently available" )
    return make_info_box(blocks)

def make_blocks_table(df):
    df = df[constants.BLOCK_TABLE_VARS.keys()].rename(columns = constants.BLOCK_TABLE_VARS)
    df.insert(loc = 5, column = "Collection Duration", value = df["Collection Start"] + " - " + df["Collection End"])
    df = df.drop(columns = ["Collection Start", "Collection End"])
    table = make_table(df, "tables_desc_table", page_size=5)
    return table


def make_metadata_table(df):
    df = df
    return make_table(df, "metadata_table", page_size= 30)


def make_hidden_body(source_counts, dataset_counts):
    body = html.Div([
            make_d_overview_box(source_counts, dataset_counts),
            make_study_box(),
            make_block_box(),
            
            #make_basket_review_box(),
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
            #dbc.Button("About", className='nav_button', id = "about"),
            dbc.DropdownMenu(
                label = html.P("Explore", className = "nav_button",),
                children = [
                    dbc.DropdownMenuItem("Search", id = "search"),
                    dbc.DropdownMenuItem("Data Overview", id = "d_overview"),
                ],
                id="explore_dropdown",
                className = "nav_button",
            ),   
            dbc.DropdownMenu(
                label = html.P("Data", className = "nav_button",),
                children = [
                    dbc.DropdownMenuItem("Source", id = "dd_source"),
                    dbc.DropdownMenuItem("Dataset", id = "dd_dataset"),
                ],
                id="data_description_dropdown",
                className = "nav_button",
            ),   
            dcc.Download(id="sb_download"),
            html.Div([
                dbc.Button("Selection", className='nav_button', id = "review"),
                html.P("", id = "selection_count")
            ],
            className = "row_layout"
            ),
        ], id = "title_nav_style"),
        ],
        style = ss.ACCOUNT_DROPDOWN_DIV_STYLE)
    '''
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
    '''
    return dropdown


def pie(labels, values, counts):
    # Label correction:
    new_labels = []
    for l in labels:
        l2 = l.replace("NHS_linkage","NHS England")
        l2 = l2.replace("GEO_linkage","Geospatial")
        l2 = l2.replace("None","No linkage")
        new_labels.append(l2)
    labels = new_labels

    # explicit colours
    label_colours = {
        "NHS England" : str(ss.cyan[0]),
        "Geospatial" : str(ss.green[0]),
        "No linkage" : str(ss.peach[0]),
        "NHS England, Geospatial": str(ss.lime[0]),
        }

    colours = [str(label_colours[str(x)]) for x in labels]


    layout = go.Layout(
        margin=go.layout.Margin(
            l=5, #left margin
            r=5, #right margin
            b=5, #bottom margin
            t=5, #top margin
        )
    )
    
    fig = go.Figure(
        data = [go.Pie(
                    labels=labels, 
                    values=values,
                    hovertext = counts,
                    hovertemplate = "%{label}: <br>Count: %{hovertext}",
                    marker = dict(colors=colours)
                ),
            ],
        layout=layout
    )
    return dcc.Graph(figure = fig, className = "tab_div")


def boxplot(mean, median, q1, q3, lf, uf):
    #print(mean, median, q1, median, q3, lf, uf)
    layout = go.Layout(
        margin=go.layout.Margin(
            l=0, #left margin
            r=0, #right margin
            b=0, #bottom margin
            t=0, #top margin
        ),
        xaxis_title = "Age"

    )
    fig = go.Figure(layout = layout)
    fig.add_trace(
        go.Box(
            q1=q1, 
            median=median,   
            q3=q3, 
            mean=mean,
            lowerfence = lf,
            upperfence = uf,
            name="Precompiled Quartiles",
            orientation="h",
            #fillcolor = "#00ABAA"
            ))

    fig.update_traces()
    fig.update_yaxes(showticklabels=False)
    
    return dcc.Graph(figure = fig, className = "tab_div")

def sunburst(source_counts, dataset_counts):
    dataset_counts = dataset_counts.fillna(0)
    dataset_counts["weighted_participant_count"] = dataset_counts["weighted_participant_count"].fillna(0)
    dataset_counts["participant_count"] = dataset_counts["participant_count"].fillna(0)
    source_counts["participant_count"] = source_counts["participant_count"].fillna(0)

    linked_source_counts = source_counts.loc[(source_counts["source"] == "nhsd") | (source_counts["source"] == "GEO")]
    lps_source_counts = source_counts.loc[~((source_counts["source"] == "nhsd") | (source_counts["source"] == "GEO"))]
    linked_dataset_counts = dataset_counts.loc[(dataset_counts["source"] == "nhsd") | (dataset_counts["source"] == "GEO")]
    lps_dataset_counts = dataset_counts.loc[~((dataset_counts["source"] == "nhsd") | (dataset_counts["source"] == "GEO"))]


    dataset_counts = dataset_counts.fillna(0)
    labels = ["Linked", "LPS"] + list(linked_source_counts["source"].values) + list(lps_source_counts["source"].values) + list(linked_dataset_counts["table"].values)  + list(lps_dataset_counts["table"].values)
    parents = ["",""]+ ["Linked" for i in linked_source_counts["source"].values] + ["LPS" for i in lps_source_counts["source"].values] + list(linked_dataset_counts["source"].values) + list(lps_dataset_counts["source"].values)
    vals_sources = list(linked_source_counts["participant_count"].values)+ list(lps_source_counts["participant_count"].values)
    weighted_vals_ds = [int(x) for x in list(linked_dataset_counts["weighted_participant_count"].values)] + [int(x) for x in list(lps_dataset_counts["weighted_participant_count"].values)]
    values = [sum(list(linked_source_counts["participant_count"].values))] + [sum(list(lps_source_counts["participant_count"].values))] + vals_sources + weighted_vals_ds

    layout = go.Layout(
        margin=go.layout.Margin(
            l=0, #left margin
            r=0, #right margin
            b=0, #bottom margin
            t=0, #top margin
        )
    )
    fig = go.Figure(go.Sunburst(
            labels=labels,
            parents=parents,
            values=values,
            branchvalues = "total",
            #maxdepth = 2
            
            ),
            layout = layout
    )
    return dcc.Graph(figure = fig, className = "sunburst")
    '''
    dataset_counts["weighted_participant_count"] = dataset_counts["weighted_participant_count"].fillna(0)
    dataset_counts["participant_count"] = dataset_counts["participant_count"].fillna(0)
    source_counts["participant_count"] = source_counts["participant_count"].fillna(0)

    linked_source_counts = source_counts.loc[(source_counts["source"] == "nhsd") | (source_counts["source"] == "GEO")]
    lps_source_counts = source_counts.loc[~((source_counts["source"] == "nhsd") | (source_counts["source"] == "GEO"))]
    linked_dataset_counts = dataset_counts.loc[(dataset_counts["source"] == "nhsd") | (dataset_counts["source"] == "GEO")]
    lps_dataset_counts = dataset_counts.loc[~((dataset_counts["source"] == "nhsd") | (dataset_counts["source"] == "GEO"))]


    dataset_counts = dataset_counts.fillna(0)
    labels = ["Linked", "LPS"] + list(linked_source_counts["source"].values) + list(lps_source_counts["source"].values) + list(linked_dataset_counts["table"].values)  + list(lps_dataset_counts["table"].values)
    parents = ["",""]+ ["LPS" for i in linked_source_counts["source"].values] + ["LPS" for i in lps_source_counts["source"].values] + list(linked_dataset_counts["source"].values) + list(lps_dataset_counts["source"].values)
    vals_sources = list(linked_source_counts["participant_count"].values)+ list(lps_source_counts["participant_count"].values)
    weighted_vals_ds = [int(x) for x in list(linked_dataset_counts["weighted_participant_count"].values)] + [int(x) for x in list(lps_dataset_counts["weighted_participant_count"].values)]
    values = [sum(list(linked_source_counts["participant_count"].values))] + [sum(list(lps_source_counts["participant_count"].values))] + vals_sources + weighted_vals_ds
    print("\n\n\nDebug")
    print(len(labels), len(parents), len(values))
    for parent, label, val in zip(parents, labels, values):
        print(parent, label, val)
    print(sum(list(linked_source_counts["participant_count"].values)), sum(list(linked_source_counts["participant_count"].values)), sum([int(x) for x in list(linked_dataset_counts["weighted_participant_count"].values)]))

    print(sum(list(lps_source_counts["participant_count"].values)), sum(list(lps_source_counts["participant_count"].values)), sum([int(x) for x in list(lps_dataset_counts["weighted_participant_count"].values)]))
    '''

def choropleth(data, gj):
    layout = go.Layout(
        margin=go.layout.Margin(
            l=0, #left margin
            r=0, #right margin
            b=0, #bottom margin
            t=0, #top margin
        ),
    )

    fig = go.Figure(data=go.Choropleth(z=data["count"],
        geojson = gj, # Spatial coordinates
        locations = data["RGN23NM"],
        locationmode = 'geojson-id', # set of locations match entries in `locations`
        colorscale = 'Blues',
        colorbar = None,
        showscale = False,
        ),
        layout = layout,
    )
    fig.update_layout(  
    geo_scope = "europe",
    coloraxis_showscale=False
    )

    fig.update_geos(
        visible = False,
        showframe=False,
        projection_scale = 5,
        center = {"lat" : 54, "lon" : -2.3}
        #fitbounds = "locations"
    )

    return dcc.Graph(figure = fig, className = "cloropleth")


def footer(app):
    footer = html.Footer(
        [
        html.Div([
            html.Div([
                html.Img(
                    src = app.get_asset_url("Logo_LLC2.png"),

                    className = "llc_logo",
                    id = "footer_logo"
                    ),
                    html.A(
                    href="https://ukllc.ac.uk/",
                    children=[
                    ]
                ),
            ],
            className = "footer_col",
            ),

            html.Div(
                [   html.H2("Address"),
                    html.P("UK Longitudinal Linkage Collaboration"),
                    html.P("University of Bristol"),
                    html.P("Canynge Hall"),
                    html.P("39 Whatley Road"),
                    html.P("Bristol"),
                    html.P("BS8 2PS")
                ],
                className = "footer_col",
                id = "address_col"
            ),
            html.Div(
                [
                    html.H2("Help"),
                   # Help
                    dbc.Button("Contact us", className='footer_button', id = "contact_us"),
                    html.Br(),
                    dbc.Button("FAQs", className = "footer_button", id = "FAQ_button"),
                    html.Br(),
                    html.A(href="https://www.youtube.com/@ukllcollab", children = ["Youtube guides"], className = "footer_button")
                ],
                className = "footer_col",
                id = "help_col"
            ),
            html.Div(
                [   
                    html.H2("Navigation"),
                    dbc.Button("Search", className='footer_button', id = "search2"),
                    html.Br(),
                    dbc.Button("Data Overview", className='footer_button', id = "overview2"),
                    html.Br(),
                    dbc.Button("Source Info", className='footer_button', id = "source2"),
                    html.Br(),
                    dbc.Button("Dataset Info", className='footer_button', id = "dataset2"),

                ],
                className = "footer_col",
                id = "nav_col"
            ),
            
        ],
        className = "row_layout",
        id = "footer_top"
        ),
        html.Div([
            html.Div([
                html.A(
                    href="https://bristol.ac.uk/",
                    children = [
                        html.Img(src = app.get_asset_url("UoB_RGB_24.svg"),),
                    ]
                ),
            ], 
            className = "footer_div"),
            html.Div([
                html.A(
                    href="https://ed.ac.uk/",
                    children = [
                        html.Img(src = app.get_asset_url("UoE_Stacked_Logo_160215.svg"), className = "footer_img" ),
                    ]
                ),
            ], 
            className = "footer_div"),
            html.Div([
                html.A(
                    href="https://ucl.ac.uk/",
                    children = [
                        html.Img(src = app.get_asset_url("University_College_London_logo.png"), className = "footer_img" ),
                    ]
                ),
            ], 
            className = "footer_div"),
            html.Div([
                html.A(
                    href="https://le.ac.uk/",
                    children = [
                        html.Img(src = app.get_asset_url("UoL-Logo-Full-Colour.png"), className = "footer_img" ),
                    ]
                ),
            ], 
            className = "footer_div"),

            html.Div([
                html.A(
                    href="https://swansea.ac.uk/",
                    children = [
                        html.Img( src = app.get_asset_url("swansea-uni-logo.png"), className = "footer_img" ),
                    ]
                ),
                ], 
            className = "footer_div"),
            html.Div([
                html.A(
                    href="https://serp.ac.uk/",
                    children = [
                        html.Img(src = app.get_asset_url("SeRP-UK-Logo-RGB-Navy.png"), className = "footer_img" ),
                    ]
                ),
            ], 
            className = "footer_div"
            )
        ],
        className = "footer",
        ),
        
    ],
    id = "footer"
    )
    return footer


def source_box(app, source_id, source, desc, id_prefix):
    box = html.Div([
        html.Div([
            html.Img(src = app.get_asset_url("logos\\{}.jpg".format(source_id)), className = "inline_img"),
            html.H2(str(source)),
        ],
        n_clicks = 0,
        id={
            'type': id_prefix+'_source_links',
            'index': source_id
        },
        className = "header_row"),
        html.P(desc)
    ],
    className = "source_overview_box")
    return box


def sources_list(app, df, id_prefix):
    source_boxes = []
    for _, row in df.iterrows():
        source_id = row["source"]
        source_name = row["source_name"]
        desc = row["Aims"]
        source_boxes.append(source_box(app, source_id, source_name, desc, id_prefix))
    return html.Div(source_boxes, className = "source_list")


def text_block(txt):
    return html.P(txt, className = "text_block")

def error_p(txt):
    return html.P(txt, className = "error_p")