from dash import Dash, Input, Output, callback, dash_table
import pandas as pd
import pandas as pd


df = pd.read_csv("TWINSUK-COPE1_v0001_20211101.csv")

app = Dash(__name__)

app.layout = dash_table.DataTable(df.to_dict('records'), [{"name": i, "id": i} for i in df.columns])



if __name__ == '__main__': 
    app.run_server(debug = True)