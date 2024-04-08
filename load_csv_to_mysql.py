###################################################
# purpose: load all metadata to MySQL db
# author: rich thomas
# date: 30/10/2023
##################################################

import pandas as pd
import os
import sys

import dataIO as io
from sqlalchemy import create_engine
import pymysql
import glob

# connection
def connect():
    # need to swap password for local var
    cnxn = create_engine('mysql+pymysql://bq21582:password_password@127.0.0.1:3306/ukllc')
    return(cnxn)

# make table
def make_table(df, table_name):
    # make table
    df.to_sql(table_name, cnxn, if_exists = 'replace', index = False)

# test connection
cnxn = connect()
#t2 = pd.read_sql('select * from t1', cnxn)

# 
os.chdir('L:\\Data\\Dev\\programs\\web app')

# data request form load 
study_drf = io.load_study_request()
# and create table
make_table(study_drf, 'drf_lps')

# data request form load 
nhs_drf = io.load_linked_request()
# need to adjust/trim columns names
nhs_drf = nhs_drf.rename (columns={
    'Number of Participants Included (n=) \n(i.e. number of particpants with non-null data, and with UK LLC, and linkage permission)': 'Number of Participants Included',
    'Health Domain Groupings (i.e. covid infection, asthma, smoking, etc.) ' : 'Health Domain Groupings'
    })
# and strip whitespace
nhs_drf = nhs_drf.rename(columns = lambda x: x.strip())
# get rid of any NULL block names
nhs_drf = nhs_drf.dropna(subset = ['Block Name'])
# and create table
make_table(nhs_drf, 'drf_nhs')

# study info and links
study_info = io.load_study_info_and_links()
make_table(study_info, 'study_info')

# load all metadata
all_files = glob.glob('L:\\Data\\Dev\\programs\\web app')

for root, dirs, files in os.walk('metadata'):
    for name in files:
        fpath = os.path.join(root, name)
        data = pd.read_csv(fpath)
        tab_name = "metadata_"+root.split('\\')[1].lower() + '_' + name.split('.')[0].lower()
        make_table(data, tab_name)



    
