# sidebar.py
from os import read
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import read_data_request
from dash import Dash, Input, Output, callback, dash_table

app = dash.Dash(external_stylesheets=["https://ukllc.ac.uk/assets/css/bootstrap.min.css?v=1650990372"])


###########################################
### Styles
TITLEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "width": "100%",
    "height": "5rem",
    "padding": "1rem 0.5rem",
    "background-color": "black",
    "color": "white",
    "textAlign":"center",
    "zIndex":1
}
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": "5rem",
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "overflow": "scroll",
}
BOX_STYLE = {
    "width": "45%",
    "height": "20rem",
    "min-width": "25rem",
    "background-color": "#f8f9fa",
    "overflow": "scroll",
    "margin-top": "1rem",
    "margin-bottom":"0rem",
    "margin-left":"1rem",
    "margin-right":"1rem",
    "display":"inline-block",
    "zIndex":0
}
ROW_STYLE = {
    "height": "100%",
}
CONTENT_STYLE = {
    "position": "relative",
    "top": "5rem",
    "margin-left": "15rem",

    "height": "100%",

}
###########################################

###########################################
### Data prep functions
request_form_url = "https://uob.sharepoint.com/:x:/r/teams/grp-UKLLCResourcesforResearchers/Shared%20Documents/General/1.%20Application%20Process/2.%20Data%20Request%20Forms/Data%20Request%20Form.xlsx?d=w01a4efd8327f4092899dbe3fe28793bd&csf=1&web=1&e=reAgWe"
# request url doesn't work just yet
study_df = read_data_request.load_study_request()
linked_df = read_data_request.load_linked_request()
sidebar_df = pd.concat([study_df[["Study"]].rename(columns = {"Study":"Data Directory"}).drop_duplicates().dropna(), pd.DataFrame([["NHSD"]], columns = ["Data Directory"])])

def get_study_tables(schema):
    return study_df.loc[study_df["Study"] == schema]

DATA_DESC_COLS = ["Timepoint: Data Collected","Timepoint: Keyword","Number of Participants Invited (n=)","Number of Participants Included (n=)","Block Description","Links"]


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
            editable=False,
            row_selectable=False,
            row_deletable=False,
            style_cell={'textAlign': 'left','overflow': 'hidden',
            'textOverflow': 'ellipsis',
            'maxWidth': 0},
            )

sidebar = html.Div([
        dash_table.DataTable(
        id='sidebar_table',
        data=sidebar_df.to_dict('records'),
        editable=False,
        column_selectable="single",
        row_selectable=False,
        row_deletable=False,
        style_cell={'textAlign': 'left'},
        
        style_header={
        'textAlign': 'center',
        'fontWeight': 'bold',
        "font-size": 26,
        "padding": "1rem 1rem"},
        ),
        ],
        style=SIDEBAR_STYLE,)

maindiv = html.Center(html.Div(
    id="body",
    children=[
        # first row
        html.Div([
            html.Div([
                html.H2("Tables"),
                html.Hr(),
                html.Div([
                html.P("Table list")
                ], id = "tables_text"),
            ],
            style=BOX_STYLE,
            id="tables_div"
            ),

            html.Div([
                html.H2("Description"),
                html.Hr(),
                html.Div([
                html.P("Select a schema...")
                ], id = "description_text1"),
                html.Div([
                ], id = "description_text2"),
            ],
            style=BOX_STYLE,
            id="description_div"
            ),
        ],
        id = "row1",
        style = ROW_STYLE
        ),

        # second row
        html.Div([
            html.Div([
                html.H2("Variables"),
                html.Hr(),
                html.Div([
                html.P("Variables list...")
                ], id = "variables_text"),
            ],
            style=BOX_STYLE
            ),
            html.Div([
                html.H2("Values"),
                html.Hr(),
                html.Div([
                html.P("Values list...")
                ], id = "values text"),
            ],
            style=BOX_STYLE
            )
            ],
        id = "row2",
        style = ROW_STYLE)
    ],
    style=CONTENT_STYLE
    ))

###########################################

###########################################
### Layout
app.layout = html.Div([titlebar, sidebar, maindiv])
###########################################

###########################################
### Actions
@app.callback(
    Output('tables_text', "children"),
    Input('sidebar_table', "active_cell") # item in sidebar table
)
def update_tables_table(input_value):
    if input_value:
        schema = sidebar_df.iloc[input_value["row"]].values[0]
        if schema == "NHSD":
            schema_info = "TODO table of nhsd"
            return schema_info
        else:

            study_tables = get_study_tables(schema)[["Block Name"]]
            return single_col_table(study_tables, id = "tables_table")
    else:
        return "Select a schema..."
        

@app.callback(
    Output('description_text1', "children"),
    Input('sidebar_table', "active_cell")
)
def update_schema_description(input_value):
    if input_value:
        schema = sidebar_df.iloc[input_value["row"]].values[0]
        if schema == "NHSD":
            schema_info = "Generic info about nhsd"
            return schema_info
        else:
            schema_info = "Generic info about {}".format(schema)
            
            return html.P("TODO find source of general information about {}".format(schema))
    else:
        return "Select a schema or table for more information..."

@app.callback(
    Output('description_text2', "children"),
    Input('sidebar_table', "active_cell"),
    Input('tables_table', "active_cell")
)
def update_table_description(sidebar_in, tables_in):
    if sidebar_in and tables_in:
        schema = sidebar_df.iloc[sidebar_in["row"]].values[0]
        study_tables = get_study_tables(schema)[DATA_DESC_COLS]
        table_row = study_tables.iloc[tables_in["row"]]
        if schema == "NHSD":
            schema_info = "Generic info about nhsd table"
            return schema_info
        else:
            schema_info = "Generic info about {}".format(schema)
            out_text = [html.Hr()]
            for col in DATA_DESC_COLS:
                print(col, table_row[col])
                out_text.append(html.P("{}: {}\n".format(col, table_row[col])))
            return out_text
    else:
        return 


@app.callback(
    Output('variables_text', "children"),
    Input('sidebar_table', "active_cell"),
    Input('tables_table', "active_cell")
)
def update_table_description(sidebar_in, tables_in):
    if sidebar_in and tables_in:
        schema = sidebar_df.iloc[sidebar_in["row"]].values[0]
        table = get_study_tables(schema).iloc[tables_in["row"]].values[0]
        if schema == "NHSD":
            schema_info = "variables for nhsd"
            return schema_info
        else:
            table = get_study_tables(schema).iloc[tables_in["row"]]["Block Name"]
            descs = pd.read_csv("metadata\\{}\\{}_description.csv".format(schema,table))[["variable_name", "variable_label"]]
            return quick_table(descs, "variables_table")
    else:
        return 

###########################################






    



if __name__ == "__main__":
    app.run_server(port=8888)
