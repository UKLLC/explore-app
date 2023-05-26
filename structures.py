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
            html.A(
                href="https://ukllc.ac.uk/",
                children=[
                    html.Img(
                        src = app.get_asset_url("Logo_LLC.png"),
                        style = ss.LOGOS_STYLE
                    )
                ]
            ),
            '''
            html.A(
                href="https://www.ucl.ac.uk/covid-19-longitudinal-health-wellbeing/",
                
                children=[
                    html.Img(
                        src = app.get_asset_url("Logo_NCS.png"),
                        style = ss.LOGOS_STYLE
                    )
                ]
            )
            '''
        ],
        style = ss.LOGOS_DIV_STYLE
        ),
        html.Div([
            html.H1(title_text, className="title")],
            style = ss.TITLE_STYLE
            ),
    
        ],
        style = ss.TITLEBAR_DIV_STYLE)
        
    return titlebar

def build_sidebar_list(schema_df, current_basket = [], sch_open =[], tab_open = "None"):
    print("SB: ", current_basket)
    study_sidebar_children = []
    linked_sidebar_children = []
    # Get data sources

    # Attribute tables to each study
    for _, row in schema_df.iterrows():
        schema = row["Source"]
        print("DEBUG: building sidebar schema", schema)
        tables = schema_df.loc[schema_df["Source"] == schema]["Block Name"]

        # CHECKBOXES
        checkbox_prep = []
        for table in tables:
            checkbox_prep += [
                dcc.Checklist([schema+"-"+table],
                value = [schema+"-"+table] if schema+"-"+table in current_basket else [],
                id= {
                    "type":'shopping_checklist',
                    "index" : schema+"-"+table
                },
                className = "shopping_checkbox",
                style = ss.CHECKBOX_STYLE
                )
            ]
        
        checkbox_col = html.Div(children=checkbox_prep, 
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

        if schema != "NHSD": # TODO make this watertight
            study_sidebar_children += [schema_children]
        else:
            linked_sidebar_children += [schema_children]

    study_list = dbc.AccordionItem(
        [dbc.Accordion(study_sidebar_children,
        id='study_schema_accordion',
        class_name= "content_accordion",
        always_open=False,
        key = "0",
        active_item = sch_open)],
        item_id = "study_accordion",
        title = "Study")

    linked_list =  dbc.AccordionItem(
        [dbc.Accordion(linked_sidebar_children,
        id='linked_schema_accordion',
        class_name= "content_accordion",
        always_open=False,
        key = "0",
        active_item = sch_open)],
        item_id = "linked_accordion",
        title = "Linked")
    
    print("MAKING SIDEBAR", sch_open)
    top_level_accordion = dbc.Accordion(
        [study_list, linked_list], 
        always_open = True, 
        active_item = ["study_accordion", "linked_accordion"],
        id= "top_accordion"
        )
    return top_level_accordion


def make_sidebar_catalogue(df):
    catalogue_div = html.Div(
        build_sidebar_list(df), 
        id = "sidebar_list_div", 
        style = ss.SIDEBAR_LIST_DIV_STYLE
        )
    return catalogue_div
 
def make_sidebar_title():
    sidebar_title = html.Div([
        html.Div(html.H2("Data Directory")),
        html.Div([
            dcc.Input(
            id="main_search",
            placeholder="search",
            className= "search_field"
            ),
            dbc.Button(
            "Search",
            id="search_button",
            n_clicks=0,
            class_name="search_button"
            ),
        ])
        ], id = "sidebar_title", style = ss.SIDEBAR_TITLE_STYLE)
    return sidebar_title

def make_sidebar_footer():
    sidebar_footer = html.Div([
        html.H2("Save Shopping Basket"),
        dbc.Button(
            "Save",
            id="save_button",
            n_clicks=0,
            ),
        dcc.Download(id="sb_download")
        ], 
        style = ss.SIDEBAR_FOOTER_STYLE)
    return sidebar_footer

def make_sidebar_left(sidebar_title, sidebar_catalogue):
    sidebar_left = html.Div([
        sidebar_title,
        sidebar_catalogue],
        style = ss.SIDEBAR_LEFT_STYLE,
        id = "sidebar_left_div")
    return sidebar_left

def make_context_bar():
    context_bar = html.Div([
        dcc.Tabs(id="context_tabs", value='Introduction', children=[
            dcc.Tab(label='Introduction', value="Introduction", className='custom-tab', selected_className='custom-tab--selected-ops'),
            dcc.Tab(label='Basket Review', value="Basket Review", className='custom-tab', selected_className='custom-tab--selected-ops'),
            ],
            parent_className='custom-tabs',
            className='custom-tabs-container',
        ),
        ],
        id = "context_bar_div", 
        style = ss.CONTEXT_BAR_STYLE
        )

    return context_bar

def make_section_title(title):
    # NOTE: I don't think you can pass styles in Dash - they must be explicit. That might be the same with IDs
    section_title = html.Div(html.H2(title))

    return section_title

def make_map_box(title= "Map: [study placeholder]", children = []):
    title_sction = html.Div([make_section_title(title)], id = "map_title", className="show_header",  style = ss.MAP_TITLE_STYLE)
    map_box = html.Div([
        title_sction,
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
        style=ss.BOX_STYLE
        )
    return map_box

def make_documentation_box(title = "Documentation: [study placeholder]", children = [None, None]):
    title_sction = html.Div([make_section_title(title)], id = "doc_title",className="doc_header",  style = ss.DOC_TITLE_STYLE)
    if children == [None, None]:
        d1 = html.Div([html.P("Select a schema for more information...", id = "schema_description_text")], id = "schema_description_div", className="container_box")
        d2 = html.Div([html.P("Select a schema for more information...", id = "table_description_text")], id = "table_description_div")
    else:
        d1 = html.Div(children[0], id = "schema_description_div", className="container_box")
        d2 = html.Div(children[1], id = "table_description_div")
    
    doc_box = html.Div([
        title_sction,
        html.Div([
        d1,
        d2,
        ], 
        id = "Documentation", 
        style = ss.DOCUMENTATION_BOX_STYLE
        )
        ],
        style=ss.BOX_STYLE,
        )
    return doc_box

def make_metadata_box(title = "Metadata: [study placeholder]", children = [None, None]):
    title_section = html.Div([make_section_title(title)], id = "metadata_title",className="doc_header",  style = ss.METADATA_TITLE_STYLE)
    if children == [None, None]:
        d1 = html.Div([], id = "table_meta_desc_div")
        d2 = html.Div([], id = "table_metadata_div", style = ss.METADATA_TABLE_DIV_STYLE)
    else:
        d1 = html.Div(children[0], id = "table_meta_desc_div")
        d2 = html.Div(children[1], id = "table_metadata_div", style = ss.METADATA_TABLE_DIV_STYLE)

    meta_box = html.Div([
            title_section,
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
        style=ss.BOX_STYLE
        )
    return meta_box

def make_landing_box():
    title_section = html.Div([make_section_title("Landing Page. Select a study to continue.")], id = "landing_title", className="ops_header", style = ss.LANDING_TITLE_STYLE)

    landing_box = html.Div([
        title_section,
        html.Div([
            html.P("This is a placeholder page. Any design help would be appreciated."),
            html.P("Welcome to the UKLLC Data Discoverability Resource."),
            html.P("Use the sidebar on the left to select a data source and data block."),
            html.P("Use the tabs along the top of the page to view information on the selected data source and tables. The tabs will only appear when a study or data block is selected."),
            html.P("You can selected one data block at a time to see information about it. You can add a data block to the shopping basket by clicking the tick box.")
        
        ]
        , id = "Landing", style = ss.LANDING_BOX_STYLE)])


    return landing_box

def make_basket_review_box():
    title_section = html.Div([make_section_title("Basket Review")], id = "basket_review_title",className="ops_header",  style = ss.LANDING_TITLE_STYLE)
    
    basket_review_box = html.Div([
        title_section,
        html.Div([

            html.P("Insert list of selected tables (add checkboxes to them)."),
            html.P("Insert save, clear, recommend, etc buttons"),
                
            #Main body is a table with Source, block, description, checkbox
            #Clear all button at top of checklist col - far from save
            #Big save button at the bottom
            #Recommend box? bottom or RHS 
            
            # Get list of selected tables & doc as df
            dbc.Button(
                    "clear basket",
                    id="clear_basket_button",
                    n_clicks=0,
                    ),
            html.Div([
                html.P("There are currently no data blocks in the shopping basket"),
                dash_table.DataTable(
                        id="basket_review_table", #id = basket_review_table (passed in app)
                        data=None,#df.to_dict('records'),
                        columns=None,#[{"name": i, "id": i} for i in df.columns], 
                        page_size=25,
                        editable=False,
                        row_selectable=False,
                        row_deletable=True, # TODO test this?
                        style_header=ss.TABLE_HEADER,
                        style_cell=ss.TABLE_CELL,
            
                        )
                ],
                id = "basket_review_table_div"),
                dbc.Button(
                    "Save",
                    id="save_button",
                    n_clicks=0,
                    ),
                dcc.Download(id="sb_download")

                ],
                 id = "Basket Review", style = ss.LANDING_BOX_STYLE)])
    return basket_review_box

def make_body():
    return html.Div([
        make_landing_box()
        ], 
        id="body",
        style = ss.BODY_STYLE )


def make_variable_div(id_type, data = "None"):
    variable_div = dcc.Store(id = id_type, data = data)
    return variable_div

def make_variable_div_list(id_type, indices):
    divs = []
    for i in indices:
        divs += [html.Div([],key = "0", id = {"type":id_type, "index":str(i)})]
    return divs


def make_app_layout(titlebar, sidebar_left, context_bar, body, account_section, variable_divs):
    app_layout =  html.Div([titlebar, sidebar_left, context_bar, body, account_section] + variable_divs, id="app",style=ss.APP_STYLE) 
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
    dropdown = html.Div([
            dbc.DropdownMenu(
                label = "Account",
                children = [
                    dbc.DropdownMenuItem("Load Basket (placeholder)"),
                    dbc.DropdownMenuItem("Save Basket (placeholder)"),
                    dbc.DropdownMenuItem("Download Basket (placeholder)"),
                    dbc.DropdownMenuItem("Log Out (placeholder"),

                ],
                id="account_dropdown",
                className = "account_dropdown",
                style = ss.ACCOUNT_DROPDOWN_STYLE 

                )
            ], 
            style = ss.ACCOUNT_DROPDOWN_DIV_STYLE)
    return dropdown