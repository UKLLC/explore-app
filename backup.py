### DOCUMENTATION BOX #####################


@app.callback(
    Output('schema_description_div', "children"),
    Input('active_schema','data'),
    prevent_initial_call=True
)
def update_schema_description(schema):
    '''
    When schema updates, update documentation    
    '''        

    print("DEBUG: acting, schema = '{}'".format(schema))
    if schema != None:
        schema_info = study_info_and_links_df.loc[study_info_and_links_df["Study Schema"] == schema]
        if schema == "NHSD":
            schema_info = "Generic info about nhsd (placeholder, in development)"
            return schema_info
        else:      
            return struct.make_schema_description(schema_info)
    else:
        return ["Placeholder schema description, null schema - this should not be possible when contextual tabs is implemented"]


@app.callback(
    Output('table_description_div', "children"),
    Input('active_schema','data'),
    prevent_initial_call=True
)
def update_tables_description(tab, schema):
    '''
    When schema updates
    Replace contents of description box with table information 
    '''

    if schema != None:
        tables = get_study_info(schema)
        if schema == "NHSD": # Expand to linked data branch
            schema_info = "Generic info about nhsd (placeholder, in development)"
            return schema_info
        else: # Study data branch
            return struct.data_doc_table(tables, "table_desc_table")
    else:
        return html.Div([html.P(["Metadata is not currently available for this data block"])], className = "container_box")


### METADATA BOX #####################
@app.callback(
    Output('table_meta_desc_div', "children"),
    Input('active_table', 'data'),
    State('active_schema', 'data'),
    prevent_initial_call=True
)
def update_table_data(table, schema):
    '''
    When table updates
    with current schema
    load table metadata
    '''
    print("CALLBACK: META BOX - updating table description with table {}".format(table))
    #pass until metadata block ready
    if schema != None and table != None:
        if schema in constants.LINKED_SCHEMAS: # Expand to linked data branch
            return html.P("Linked data placeholder (in development)")
        tables = get_study_info(schema)
        tables = tables.loc[tables["Block Name"] == table.split("-")[1]]
        return struct.metadata_doc_table(tables, "table_desc_table")
    else:
        # Default (Section may be hidden in final version)
        return html.Div([html.P("Metadata is not currently available for this data block.")], className="container_box")


@app.callback(
    Output('table_metadata_div', "children"),
    Input("values_toggle", "value"),
    Input("metadata_search", "value"),
    Input('active_table','data'),
    prevent_initial_call=True
)
def update_table_metadata(values_on, search, table_id):
    '''
    When table updates
    When values are toggled
    When metadata is searched
    update metadata display
    '''
    print("CALLBACK: META BOX - updating table metadata with active table {}".format(table_id))
    if table_id== None:
        raise PreventUpdate
    try:
        metadata_df = dataIO.load_study_metadata(table_id)
    except FileNotFoundError: # Study has changed 
        print("Failed to load {}.csv".format(table_id))
        print("Preventing update in Meta box table metadata")
        raise PreventUpdate

    if type(values_on) == list and len(values_on) == 1:
        metadata_df = metadata_df[["Block Name", "Variable Name", "Variable Description", "Value", "Value Description"]]
        if type(search) == str and len(search) > 0:
            metadata_df = metadata_df.loc[
            (metadata_df["Block Name"].str.contains(search, flags=re.IGNORECASE)) | 
            (metadata_df["Variable Name"].str.contains(search, flags=re.IGNORECASE)) | 
            (metadata_df["Variable Description"].str.contains(search, flags=re.IGNORECASE)) |
            (metadata_df["Value"].astype(str).str.contains(search, flags=re.IGNORECASE)) |
            (metadata_df["Value Description"].str.contains(search, flags=re.IGNORECASE))
            ]
    else:
        metadata_df = metadata_df[["Block Name", "Variable Name", "Variable Description"]].drop_duplicates()
        if type(search) == str and len(search) > 0:
            metadata_df = metadata_df.loc[
            (metadata_df["Block Name"].str.contains(search, flags=re.IGNORECASE)) | 
            (metadata_df["Variable Name"].str.contains(search, flags=re.IGNORECASE)) | 
            (metadata_df["Variable Description"].str.contains(search, flags=re.IGNORECASE)) 
            ]
    metadata_table = struct.metadata_table(metadata_df, "metadata_table")
    return metadata_table



### MAP BOX #################

@app.callback(
    Output('map_region', "data"),
    Output('map_object', 'zoom'),
    Input('context_tabs','value'), # Get it to trigger on first load to get past zoom bug
    Input('active_schema','data'),
    prevent_initial_call=True
)
def update_map_content(tab, schema):
    '''
    When schema updates
    Update the map content
    '''
    print("CALLBACK: updating map content")
    if schema != None and tab == "Map":
        map_data = load_or_fetch_map(schema)
        if not map_data:
            return dash.no_update, 6
        return map_data, 6
    else:
        raise PreventUpdate


@app.callback(
    Output('doc_title', "children"),
    Output('metadata_title', "children"),
    Output('map_title', "children"),
    Output('landing_title', 'children'),
    Input('active_schema','data'),
    prevent_initial_call=True
)
def update_headers(schema):
    '''
    When schema updates, update documentation
    '''
    print("CALLBACK: Updating section headers (TODO merge into schema update?)")
    doc_header = struct.make_section_title("Block-Level Metadata: {}".format(schema))
    meta_header = struct.make_section_title("Variable-Level Metadata: {}".format(schema))
    map_header = struct.make_section_title("Coverage: {}".format(schema))
    if schema:
        landing_header = struct.make_section_title("Introduction: Selected source {}".format(schema))
    else:
        landing_header = struct.make_section_title("Introduction: Select data to continue")
    return doc_header, meta_header, map_header, landing_header