DATA_DESC_COLS = ["Timepoint: Data Collected","Timepoint: Keyword","Number of Participants Invited (n=)","Number of Participants Included (n=)","Block Description","Links"]
request_form_url = "https://uob.sharepoint.com/:x:/r/teams/grp-UKLLCResourcesforResearchers/Shared%20Documents/General/1.%20Application%20Process/2.%20Data%20Request%20Forms/Data%20Request%20Form.xlsx?d=w01a4efd8327f4092899dbe3fe28793bd&csf=1&web=1&e=reAgWe"


MAP_URL = 'https://tiles.stadiamaps.com/tiles/alidade_smooth/{z}/{x}/{y}{r}.png'
MAP_ATTRIBUTION = '&copy; <a href="https://stadiamaps.com/">Stadia Maps</a> '

keyword_cols = ["topic_tags", "Keywords","Unnamed: 11","Unnamed: 12", "Unnamed: 13", "Unnamed: 14","Unnamed: 15"]
#keyword_cols = ["Keywords", "Unnamed: 8", "Unnamed: 9","Unnamed: 10","Unnamed: 11","Unnamed: 12"]

VALID_USERNAME_PASSWORD_PAIRS = {
    'username': 'password'
}

LINKED_SCHEMAS = ["NHSD"]

LANDING_GENERAL_TEXT = """
Browse the UK LLC Data Discovery Portal to discover data from the 20+ longitudinal population studies that contribute data to the UK LLC Trusted Research Environment (TRE).
The metadata encompass study-collected and linked data blocks, including health, geospatial and non-health routine records.
\n
Use this tool to select data blocks from our catalogue for a new data request or data amendment.
"""

LANDING_INSTRUCTION_TEXT1 = [
"Use the left sidebar to browse studies and data blocks.", 
"Filter the catalogue with search options in the top left (in development).",
"Select a data source or a data block and find out more information about them using the tabs that appear along the top bar."
]

LANDING_INSTRUCTION_TEXT2 = [
"Make a selection of data blocks by checking the boxes in the left sidebar.", 
"You can review your selection in the basket review tab.", 
"You can download your selection as a file or save it on the UK LLC server (in development)." 
]

LANDING_INFO_TEXT = """
    There is currently no cost to access data in the TRE.
    You must be UK-based and an Accredited Researcher (link) – read about the application process in the UK LLC Data Access and Acceptable Use Policy (link).
    Submit an Expression of Interest through the HDR UK Innovation Gateway (link).
    Email [link]access@ukllc.ac.uk[/link] if you have any queries.
    Resources:
    """

WORKING_IN_TRE_TEXT = [
    "[Link]UK LLC User Guides YouTube channel[/link]",
    "[link]UK LLC TRE User Guide[/link]",
    "[link]Summary of the UK LLC Resource[/link]"
]

# Dictionaries of columns in the database: field names on the page
#SOURCE_SUMMARY_VARS = {"full_name": "Name", "coverage_summary":"Coverage", "cohort_desc":"Cohort", "duration":"Duration", "participants":"Participants", "no_avail_datasets": "Available Blocks", "topic_tags": "Core Ontologies", "cohort_owner":"Cohort Owner", "website":"Website", "data_documentation":"Data Documentation"}
#BLOCK_SUMMARY_VARS = {"table_id": "Table ID", "table_name":"Table Name", "short_desc": "Description", "collection_time": "Collection Time", "participants_invited":"Participants Invited", "participants_included":"Participants Included", "linkage_rate":"[?] Linkage Rate", "links":"Link", "topic_tags":"Topics", "sensitivity":"Sensitivity"}

SOURCE_SUMMARY_VARS = {"Source_name":"Study Name", "Owner":"Owner", "Study type":"Study type", "Participant pathway": "Participant pathway", "Geographic coverage - Nations": "Geographic coverage - Nations", "Geographic coverage - Regions":"Geographic coverage - Regions",  "Start date":"Start date", "Age at recruitment": "Age at recruitment", "Sex":"Sex", "dataset_count":"Number of datasets", "participant_count":"Participant count", }
BLOCK_SUMMARY_VARS = {"table_id": "Table ID", "table_name":"Table Name", "short_desc": "Description", "collection_time": "Collection Time", "participants_invited":"Participants Invited", "participants_included":"Participants Included", "linkage_rate":"[?] Linkage Rate", "links":"Link", "topic_tags":"Topics", "sensitivity":"Sensitivity"}
