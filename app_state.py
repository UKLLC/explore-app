

class App_State():
    def __init__(self) -> None:

        self.map_data = {}    

        self.sections = { # component dictionaries must share a name with html object id and tab value
            #"about":{
            #    "active":False,
            #},
            "search":{
                "active":False,
            },
            "overview":{
                "active":False,
            },
            "study":{
                "active":False,
            },
            "dataset":{
                "active":False,
            },
            "review":{
                "active":False,
            },
        }

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
            