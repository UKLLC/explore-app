from openpyxl import load_workbook
import pandas as pd


def load_study_request():
    '''
    
    '''
    sheet_df = pd.read_excel("assets\\Data Request Form.xlsx", sheet_name="Study data requested",skiprows=5, usecols = "D,E,F,G,H,I,J,K,L,M,N,O,P,Q,R")
    return sheet_df


def load_linked_request():
    '''
    '''
    sheet_df = pd.read_excel("assets\\Data Request Form.xlsx", sheet_name="Linked data requested",skiprows=5, usecols = "B,C,D,E,F,G,H")
    return sheet_df


def load_study_info_and_links():
    '''
    '''
    sheet_df = pd.read_excel("assets\\Data Request Form.xlsx", sheet_name="Study info & links", skiprows=1, usecols = "B,C,D,E,F,G,H,I,J" )
    return sheet_df

def load_study_metadata(study, table_stem):
    '''
    '''
    # TODO change to joined metadata file (requires preprep, splitting all into proper folders)
    values_df = pd.read_csv("metadata\\"+str(study.upper())+"\\"+table_stem+"_values.csv")

    return values_df
