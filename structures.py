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
            style_header=ss.TABLES_DOC_HEADER,
            style_cell=ss.TABLES_DOC_CELL,
            style_data_conditional=[ss.TABLES_DOC_CONDITIONAL]
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
            style_header=ss.METADATA_DESC_HEADER,
            style_cell=ss.METADATA_DESC_CELL,
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
            style_header=ss.METADATA_TABLE_HEADER,
            style_cell=ss.METADATA_TABLE_CELL,
            style_data_conditional=[ss.METADATA_CONDITIONAL]
            )
    return quick_table


def main_titlebar(title_text):
    titlebar = html.Div([
        html.Div([
            html.A(
                href="https://ukllc.ac.uk/",
                children=[
                    html.Img(
                        src = "assets//logo_LLC.png",
                        style = ss.LOGOS_STYLE
                    )
                ]
            ),
            html.A(
                href="https://www.ucl.ac.uk/covid-19-longitudinal-health-wellbeing/",
                
                children=[
                    html.Img(
                        src = "assets//logo_NCS.png",
                        style = ss.LOGOS_STYLE
                    )
                ]
            )
        ],
        style = ss.LOGOS_DIV_STYLE
        ),
        html.H1(title_text, className="title")
        ],
        style = ss.TITLEBAR_STYLE)
    return titlebar

def build_sidebar_list(df, schema_lookup, table_lookup, current_basket = [], sch_open =[], tab_open = "None"):
    print("SB: ", current_basket)
    sidebar_children = []
    # Get data sources
    schema_df = pd.concat([df[["Study"]].rename(columns = {"Study":"Data Directory"}).drop_duplicates().dropna(), pd.DataFrame([["NHSD"]], columns = ["Data Directory"])])
    
    # Attribute tables to each study
    for _, row in schema_df.iterrows():
        schema = row["Data Directory"]

        tables = df.loc[df["Study"] == schema]["Block Name"]

        # CHECKBOXES
        checkbox_prep = []
        for table in tables:
            checkbox_prep += [html.Div([
                dcc.Checklist([schema+"-"+table],
                value = [schema+"-"+table] if schema+"-"+table in current_basket else [],
                id= {
                    "type":'shopping_checklist',
                    "index" : table_lookup[schema+"-"+table]
                },
                style = ss.CHECKBOX_STYLE
                )
            ],
            #row div style
            style = ss.CHECKBOX_ROW_STYLE,
            )]
        
        checkbox_col = html.Div(
            checkbox_prep, 
            style = ss.CHECKBOX_COL_STYLE
            )

        # SCHEMA AND TABLES
        schema_children = dbc.AccordionItem([
            html.Div(
                [
                checkbox_col, 
                dcc.Tabs(
                    id={
                        'type': 'table_tabs',
                        'index': schema_lookup[schema]
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
                                'index': table_lookup[schema+"-"+table]
                            },
                            className = "table_tab",
                            selected_className='table_tab--selected'
                        )
                        for table in tables
                        ],
                    ), 
                ],
                style = ss.CHECKBOX_LIST_COLS_STYLE
                ),
            ],
            title = schema,
            item_id = schema
            )

        sidebar_children += [schema_children]

    schema_list = dbc.Accordion(sidebar_children,
        id='schema_accordion',
        always_open=True,
        key = "0",

        active_item = sch_open)
    print("MAKING SIDEBAR", sch_open)
    return schema_list


def make_sidebar_catalogue(df, schema_lookup, table_lookup):
    catalogue_div = html.Div(build_sidebar_list(df, schema_lookup, table_lookup), id = "sidebar_list_div", style = ss.SIDEBAR_LIST_DIV_STYLE)
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

def make_sidebar_left(sidebar_title, sidebar_catalogue, sidebar_footer):
    sidebar_left = html.Div([
        sidebar_title,
        sidebar_catalogue,
        sidebar_footer],
        style = ss.SIDEBAR_LEFT_STYLE,
        id = "sidebar_left_div")
    return sidebar_left

def make_context_bar():
    context_bar = html.Div([
        dcc.Tabs(id="context_tabs", value='', children=[
            dcc.Tab(label='Introduction', value="Introduction")
            ]),
        ],
        id = "context_bar_div", 
        style = ss.CONTEXT_BAR_STYLE)
    return context_bar

def make_section_title(title):
    # NOTE: I don't think you can pass styles in Dash - they must be explicit. That might be the same with IDs
    section_title = html.Div(html.H2(title))

    return section_title


def make_map_box(title= "Map: [study placeholder]", children = []):
    title_sction = html.Div([make_section_title(title)], id = "map_title", style = ss.MAP_TITLE_STYLE)
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
    title_sction = html.Div([make_section_title(title)], id = "doc_title", style = ss.DOC_TITLE_STYLE)
    if children == [None, None]:
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
        ], id = "Documentation", style = ss.DOCUMENTATION_BOX_STYLE)
        ],
        style=ss.BOX_STYLE
        )
    return doc_box

def make_metadata_box(title = "Metadata: [study placeholder]", children = [None, None]):
    title_section = html.Div([make_section_title(title)], id = "metadata_title", style = ss.METADATA_TITLE_STYLE)
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
                ]),
                d2,
            ], id = "Metadata", style = ss.METADATA_BOX_STYLE)
            ],
        style=ss.BOX_STYLE
        )
    return meta_box

def make_landing_box():
    title_section = html.Div([make_section_title("Landing Page. Select a study to continue.")], id = "landing_title", style = ss.LANDING_TITLE_STYLE)

    landing_box = html.Div([
        title_section,
        html.Div([
            html.P("Welcome to the UKLLC Data Discoverability Resource."),
            html.P("Use the sidebar on the left to select a data source and data block."),
            html.P("Use the tabs along the top of the page to view information on the selected data source and tables."),
        ]
        , id = "Landing", style = ss.LANDING_BOX_STYLE)])
    return landing_box

def make_body():
    return html.Div([
        make_landing_box()
        ], 
        id="body",
        style = ss.BODY_STYLE )


def make_variable_div(id_type):
    variable_div = dcc.Store(id = id_type )
    return variable_div

def make_variable_div_list(id_type, indices):
    divs = []
    for i in indices:
        divs += [html.Div([],key = "0", id = {"type":id_type, "index":str(i)})]
    return divs


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
    body = html.Div([
            make_documentation_box(),
            make_metadata_box(),
            make_map_box()
        ],
        style=ss.HIDDEN_BODY_STYLE,
        id = "hidden_body")
    return body