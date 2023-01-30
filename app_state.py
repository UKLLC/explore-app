from plotly import data
import structures as struct
import dataIO

class App_State():
    def __init__(self, schema_df) -> None:
        self.schema = "None"
        self.table = "None"

        self.open_schemas = ["None"]
        self.last_table = "None"
        self.waiting_table = "None"
        

        self.tables_df = None
        self.descs_df = None
        self.vals_df = None
        self.sidebar_clicks = {}

        self.schema_collapse_open = {}
        for schema in schema_df["Data Directory"].values:
            self.schema_collapse_open[schema] = False

        self.map_data = {}

        self.lookup_index_to_sch = dataIO.read_json("study_lookup1.json")
        self.lookup_sch_to_index = dataIO.read_json("study_lookup2.json")
        self.lookup_index_to_tab = dataIO.read_json("table_lookup1.json")
        self.lookup_tab_to_index = dataIO.read_json("table_lookup2.json")

        # TEMP NHSD additions:
        self.lookup_index_to_sch["999"] = "NHSD"
        self.lookup_sch_to_index["NHSD"] = "999"
    

        # DEBUG ######
        self.schema_click_count = 0
        self.table_click_count = 0

        #####################
        
        self.global_activations = 0

        self.sections = { # component dictionaries must share a name with html object id and tab value
            "Map":{
                "activations" : 0,
                "active":False,
                "children":[None, None]
            },
            "Documentation":{
                "activations" : 0,
                "active":False,
                "children":[None, None]
            },
            "Metadata":{
                "activations" : 0,
                "active":False,
                "children":[None, None]
            },
            "Landing":{
                "activations" : 0,
                "active":False,
                "children":[None, None]
            }
        }

        self.schema_doc = "None"
        self.table_doc = "None"

        self.shopping_basket = []

        #####################

    
    def get_tables_df(self):
        return self.tables_df

    def set_tables_df(self, tables_df):
        self.tables_df = tables_df

    def get_descs_df(self):
        return self.descs_df

    def set_descs_df(self, descs_df):
        self.descs_df = descs_df

    def get_vals_df(self):
        return self.vals_df

    def set_vals_df(self, vals_df):
        self.vals_df = vals_df

    def set_sidebar_clicks(self, index, nclick):
        if index not in self.sidebar_clicks:
            self.sidebar_clicks[index] = 0
        else:
            self.sidebar_clicks[index] = nclick

    def get_sidebar_clicks(self, index):
        return self.sidebar_clicks[index]

    def set_active_schema(self, schema):
        self.schema = schema

    def set_active_table(self, table):
        self.table = table

    def get_active_table(self):
        return self.table

    def get_active_schema(self):
        return self.schema

    def get_map_data(self, study):
        if study in self.map_data:
            return self.map_data[study]
        else:
            return False

    def set_map_data(self, study, data):
        self.map_data[study] = data


##############################

    def reset_sidebar_clicks(self):
        for k in self.sidebar_clicks.keys():
            self.sidebar_clicks[k] = 0
            