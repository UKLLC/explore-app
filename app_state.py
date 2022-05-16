class App_State():
    def __init__(self) -> None:
        self.tables_df = None
        self.descs_df = None
        self.vals_df = None

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