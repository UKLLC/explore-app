from contextvars import copy_context
from dash._callback_context import context_value
from dash._utils import AttributeDict
from dash import dash_table
from os import read
from re import S
import re
import dash
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import pandas as pd
from dash import Dash, Input, Output, State, callback, dash_table, ALL, MATCH
import dash_leaflet as dl
import dash_leaflet.express as dlx
from dash_extensions.javascript import arrow_function
from dash_extensions.javascript import assign
import json
import time
import warnings
import logging
from dash.exceptions import PreventUpdate
from flask_caching import Cache

from app_state import App_State
import dataIO
import stylesheet as ss
import constants 
import structures as struct

# Import the names of callback functions you want to test
from app import update_schema_description, update_table_data, update_table_metadata, update_doc_header, context_tabs, body_sctions, sidebar_schema, sidebar_table, main_search, shopping_cart, save_shopping_cart

'''
Testing Directory:
    Documentation
    1. Update_schema_descriptions: 
        i. schema is study - make schema description
        ii. schema is linkage - make schema description
    Metadata
    1. update_table_data:
        i. schema is study
        ii. schema is linkage
    2. update_table_metadata:
        i. study table, values off, no seach
        ii. study table, values on, no search
        iii. study table, values on, search
    Map 
    1. update_doc_header
        i. test several schemas
    Body
    1. context_tabs
        i. no schema, no table
        ii. schema, no table
        iii. schema, table
    2. body_sections
        i. documentation active
        ii. metadata active
        iii. maps active
        iv. introduction active
        v. none active
    Sidebar
    1. sidebar_schema
        i. test a study schema
        ii. test a linkage schema
    2. sidebar_table
        i. test table activation
    3. main_search
        i. test study search
        ii. test table search
        iii. test keyword search
    Shopping cart
    1. shopping_cart
        i. select a table 
    2. save_shopping_cart
        i. Test save process
'''

### Documentation ###
'''
1. Update_schema_descriptions: 
    i. schema is study - make schema description
    ii. schema is linkage - make schema description
2. update_tables_description:
    i. schema is study
    ii. schema is linkage
'''
def test_update_schema_description_callback():
    output1 = update_schema_description("ALSPAC",)
    assert type(output1) == list

    output2 = update_schema_description("NHSD",)
    assert output2 == "Generic info about nhsd"
    

def test_update_tables_description_callback():
    output1 = update_tables_description("BCS70",)
    assert type(output1) == dash_table.DataTable

    output2 = update_tables_description("NHSD",)
    assert output2 == "Generic info about nhsd"
    
### Metadata ###
'''
1. update_table_data:
    i. schema is study
    ii. schema is linkage
2. update_table_metadata:
    i. study table, values off, no seach
    ii. study table, values on, no search
    iii. study table, values off, search
'''
def test_update_table_data_callback():
    output1 = update_table_data("BIB-CV_W1","BIB")
    assert type(output1) == dash_table.DataTable

    # Doesn't work yet
    #output2 = update_table_data("NHSD", "DEMOGRAPHICS")
    #assert output2 == html.P("NHSD placeholder text")

def test_update_table_metadata_callback():
    output1 = update_table_metadata("ELSA-elsa_covid_w2_eul", [], "")
    assert len(output1.data) > 0
    assert output1.data[0]["Block Name"] == 'elsa_covid_w2_eul'
    assert list(output1.data[0].keys()) == ["Block Name", "Variable Name", "Variable Description"]

    output2 = update_table_metadata("ELSA-elsa_covid_w2_eul", ["values"], "")
    assert len(output2.data) > 0
    assert output2.data[0]["Block Name"] == 'elsa_covid_w2_eul'
    assert list(output2.data[0].keys()) == ["Block Name", "Variable Name", "Variable Description", "Value", "Value Description"]

    output3 = update_table_metadata("ELSA-elsa_covid_w2_eul", [], "study_id_e")
    print(output3.data)
    assert len(output3.data) == 1
    assert output3.data[0]["Block Name"] == 'elsa_covid_w2_eul'
    assert list(output3.data[0].keys()) == ["Block Name", "Variable Name", "Variable Description"]

### Map ###
'''
1. update_doc_header
    i. test several schemas
'''
def test_update_doc_header_callback():
    output1 = update_doc_header("None", "EXCEED")
    assert output1 != None

### Body ###
'''
1. context_tabs
    i. no schema, no table
    ii. schema, no table
    iii. schema, table
2. body_sections
    i. documentation active
    ii. metadata active
    iii. maps active
    iv. introduction active
    v. none active
'''
def test_context_tabs_callback():
    output1 = context_tabs("None", "None")
    assert output1[0].label == "Introduction"

    output1 = context_tabs("EPICN", "None")
    assert output1[0].label == "Introduction"
    assert output1[1].label == "Documentation"
    assert output1[2].label == "Coverage"

    output1 = context_tabs("EPICN", "FU1")
    assert output1[0].label == "Introduction"
    assert output1[1].label == "Documentation"
    assert output1[2].label == "Metadata"
    assert output1[3].label == "Coverage"


def test_body_sections_callback():
    # Can't really test here
    pass

### Sidebar ###
'''
1. sidebar_schema
    i. test a study schema
    ii. test a linkage schema
2. sidebar_table
    i. test table activation
3. main_search
    i. test study search
    ii. test table search
    iii. test keyword search
'''
def test_sidebar_schema_callback(): 
    # No schema selected - select Fenland
    output1 = sidebar_schema(["GLAD"], "None", [] )
    assert output1[0] == "GLAD"
    assert output1[1] == ["GLAD"] 
    
    # Fenland selected - select Fenland again
    output1 = sidebar_schema([], "GLAD", ["GLAD"] )
    assert output1[0] == "GLAD"
    assert output1[1] == [] 

    # Fenland selected - select MCS again
    output1 = sidebar_schema(["MCS", "GLAD"], "GLAD", ["GLAD"] )
    assert output1[0] == "MCS"
    assert sorted(output1[1]) == sorted(["MCS","GLAD"]) 

def test_sidebar_table_callback():
    output1 = sidebar_table(['None', 'None', 'None', 'None', 'None', 'None', 'None', 'MCS-COVID_w1', 'None', 'None', 'None', 'None', 'None', 'None', 'None', 'None', 'None', 'None', 'None'], "None")
    assert output1[0] == "MCS-COVID_w1"
    assert output1[1] == ['None', 'None', 'None', 'None', 'None', 'None', 'None', 'MCS-COVID_w1', 'None', 'None', 'None', 'None', 'None', 'None', 'None', 'None', 'None', 'None', 'None']
    
    output2 = sidebar_table(['None', 'None', 'None', 'None', 'None', 'None', 'None', 'MCS-COVID_w2', 'None', 'None', 'None', 'None', 'None', 'None', 'None', 'None', 'None', 'None', 'None'], "MCS-COVID_w1")
    assert output2[0] == "MCS-COVID_w2"
    assert output2[1] == ['None', 'None', 'None', 'None', 'None', 'None', 'None', 'MCS-COVID_w2', 'None', 'None', 'None', 'None', 'None', 'None', 'None', 'None', 'None', 'None', 'None']

    output3 = sidebar_table(['wave1m', 'None', 'None', 'None', 'None', 'None', 'None', 'MCS-COVID_w2', 'None', 'None', 'None', 'None', 'None', 'None', 'None', 'None', 'None', 'None', 'None'], "MCS-COVID_w2")
    assert output3[0] == "wave1m"
    assert output3[1] == ['wave1m', 'None', 'None', 'None', 'None', 'None', 'None', 'None', 'None', 'None', 'None', 'None', 'None', 'None', 'None', 'None', 'None', 'None', 'None']

def test_main_search_callback():
    # Very hard to test this one
    pass

### Shopping Cart ###
'''
1. shopping_cart
    i. select a table 
2. save_shopping_cart
    i. Test save process
'''
def test_shopping_cart_callback():
    output1 = shopping_cart([[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], ['BIB-CV_W1'], ['BIB-CV_W2'], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], ['EPICN-FU1'], ['EPICN-FU2'], ['EPICN-HLEQ1'], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []], ['BIB-CV_W1', 'EPICN-FU1', 'EPICN-FU2', 'EPICN-HLEQ1'])
    assert output1 == ['BIB-CV_W1', 'BIB-CV_W2', 'EPICN-FU1', 'EPICN-FU2', 'EPICN-HLEQ1']

def test_save_shopping_cart():
    output1 = save_shopping_cart("", ['BIB-CV_W1', 'BIB-CV_W2', 'EPICN-FU1', 'EPICN-FU2', 'EPICN-HLEQ1'])
    assert output1["content"] == ',TABLE_SCHEMA,TABLE_NAME\r\n0,BIB,CV_W1\r\n1,BIB,CV_W2\r\n2,EPICN,FU1\r\n3,EPICN,FU2\r\n4,EPICN,HLEQ1\r\n'