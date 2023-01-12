class App_State():
    def __init__(self, schema_df) -> None:
        self.schema = "None"
        self.table = "None"

        self.last_table = "None"

        self.tables_df = None
        self.descs_df = None
        self.vals_df = None
        self.sidebar_clicks = {}
        self.button_clicks = [0,0,0]
        self.schema_collapse_open = {}
        for schema in schema_df["Data Directory"].values:
            self.schema_collapse_open[schema] = False
    

        self.map_data = {}

        #####################
        
        self.global_activations = 0

        self.map = {
            "object": None,
            "activations" : 0,
            "active":False
            }
        self.documentation = {
            "object": None,
            "activations" : 0,
            "active":False
            }
        
        self.metadata = {
            "object": None,
            "activations" : 0,
            "active":False
            }

        self.schema_doc = "None"
        self.table_doc = "None"

        self.meta_table_doc = "None"
        self.meta_table = "None"

        self.meta_table_df = "None"


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


    def set_button_clicks(self, lst):
        self.button_clicks = lst

    def get_button_clicks(self):
        return self.button_clicks

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
#   buttons

    def get_global_activations(self):
        return self.global_activations
    def set_global_activations(self, val):
        self.global_activations = val


    def get_sections(self):
        return self.documentation, self.metadata, self.map

##############################

    def reset_sidebar_clicks(self):
        for k in self.sidebar_clicks.keys():
            self.sidebar_clicks[k] = 0
            