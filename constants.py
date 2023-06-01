DATA_DESC_COLS = ["Timepoint: Data Collected","Timepoint: Keyword","Number of Participants Invited (n=)","Number of Participants Included (n=)","Block Description","Links"]
request_form_url = "https://uob.sharepoint.com/:x:/r/teams/grp-UKLLCResourcesforResearchers/Shared%20Documents/General/1.%20Application%20Process/2.%20Data%20Request%20Forms/Data%20Request%20Form.xlsx?d=w01a4efd8327f4092899dbe3fe28793bd&csf=1&web=1&e=reAgWe"


MAP_URL = 'https://tiles.stadiamaps.com/tiles/alidade_smooth/{z}/{x}/{y}{r}.png'
MAP_ATTRIBUTION = '&copy; <a href="https://stadiamaps.com/">Stadia Maps</a> '

keyword_cols = ["Keywords","Unnamed: 11","Unnamed: 12", "Unnamed: 13", "Unnamed: 14","Unnamed: 15"]
#keyword_cols = ["Keywords", "Unnamed: 8", "Unnamed: 9","Unnamed: 10","Unnamed: 11","Unnamed: 12"]

VALID_USERNAME_PASSWORD_PAIRS = {
    'username': 'password'
}

LINKED_SCHEMAS = ["NHSD"]

LANDING_GENERAL_TEXT = """
Browse the UK LLC Data Discovery Portal to discover data from the 20+ longitudinal population studies that contribute data to the UK LLC Trusted Reasearch Environment (TRE).
The metadata encompass study-collected and linked data blocks, including health, geospatial and non-health routine records.
\n
Use this tool to select data blocks from our catelogue for a new data request or data ammendment.
"""

LANDING_INSTRUCTION_TEXT1 = """
Use the left sidebar to browse studies and data blocks. Filter the catalogue with search options in the top left (in development).
\nSelect data source or a data block and find out more information about them using the tabs that appear along hte top bar.
"""

LANDING_INSTRUCTION_TEXT2 = """
Make a selection of data blocks by checking the boxes in the left sidebar. You can review your selection in the basket review tab. 
\nYou can download your selection as a file or save it on the UK LLC server (in development). 
"""

LANDING_INFO_TEXT = [
    "You must be UK-based.",
    "Submit an Expression of Interest through the [link]HDR UK Innovation Gateway[/link].",
    "Read about the application process in the [link]UK LLC Data Access and Acceptable Use Policy[link].",
    "There is currently no cost associated with accessing the UK LLC TRE.",
    "You must be an Accredited Researcher before being permitted access to the UK LLC TRE.",
    "Email [link]access@ukllc.ac.uk[/link] if you have any queries.",
    "(Dev note: links pending)"
]

WORKING_IN_TRE_TEXT = [
    "[Link]UK LLC User Guides YouTube channel[/link]",
    "[link]UK LLC TRE User Guide[/link]",
    "[link]Summary of the UK LLC Resource[/link]"
]
