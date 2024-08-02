import requests
import pandas as pd
import json


def fetch_data_from_postgrest_api(url, endpoint):
    try:
        # Make a GET request to the API
        response = requests.get(url + endpoint)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the JSON response
            data = response.json()
            return data
        else:
            # Print an error message if the request was not successful
            print(f"Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None


def mental_health_catalogue():
    api_url = "https://www.cataloguementalhealth.ac.uk:443/testing/api/v2/"
    # Specify the endpoint you want to access (replace with your specific endpoint)
    endpoint_to_access = "studies"#"-H 'accept: application/json' \ -H 'Range-Unit: items'"

    # Fetch data from the specified endpoint
    result = fetch_data_from_postgrest_api(api_url, endpoint_to_access)
    result = pd.DataFrame(data = result)
    # Process the result (replace this part with your specific data processing logic)
    if result is not None:
        print("Data fetched successfully:")
        data_out = result[["study_id", "title", "aims", "website", "related_themes", "sample_type", "geographic_coverage_nations", "geographic_coverage_regions", "start_date", "sample_size_at_recruitment", "age_at_recruitment", "sex"]]
        data_out.columns = ["MH_study_id", "LPS name", "Aims", "Website", "Themes", "Sample type", "Geographic coverage - Nations", "Geographic coverage - Regions", "Start date", "Sample size at recruitment", "Age at recruitment", "sex"]
        #print(data_out["MH_study_id"])
        
        llc_studies = ["ALSPAC", "AHMS", "BCS", "BiB", "ELSA", "GSSFHS", "LSYPE", "MCS", "NCDS", "NICOLA", "SABRE", "TEDS", "TwinsUK", "UKHLS"]
        data_out = data_out.loc[data_out["MH_study_id"].isin(llc_studies)]

        
        
        data_out.to_csv("mh_catalogue.csv")
        print("Successfully retrieved mental health data")
    else:
        print("Failed to fetch mental health data")
        

def load_pids():
    '''
    
    Uses json of HDRUK provided persistent ids (dataset level)

    Returns
    -------
    newpids : list
        persistent IDs for all available NHS datasets available via API

    '''
    
    pid_loc = 'datasets_pids_lookup.json'
    with open(pid_loc, "r") as f:
        pids = json.load(f)
    return pids



def gateway(
        
):
    
    '''
    
    Returns
    -------
    metadata : dict
        metdata json/dictionary for target dataset

    '''
    pids = load_pids()
    data_out_df = ""
    for key, val in pids.items():
        # define URL and add persistent ID of target dataset
        url = "https://api.www.healthdatagateway.org/api/v1/datasets/"+key
        # make request 
        response = requests.get(url)
        # get data as text
        data = response.text
        # convert to json and return 
        dataset = json.loads(data)
        data_out = {}
        if val == "ECDS" or val == "COVIDSGSS" or val == "IELISA" or val == "CHESS" or val == "GDPPR" :
            data_out["title"] = [dataset["data"]['datasetfields']['metadataquality']['title']]
        else:
            data_out["title"] = [dataset["data"]['datasetfields']['datautility']['title']]
        data_out["abstract"] = [dataset["data"]['datasetfields']['abstract']]
        data_out["geo_coverage"] = [dataset["data"]['datasetfields']['geographicCoverage'][0]]
        data_out["start_date"] = [dataset["data"]['datasetfields']['datasetStartDate']]
        data_out["age_band"] = [dataset["data"]['datasetfields']['ageBand']]
        if val != "HESAE" and val != "MHSDS":
            data_out["collection_situation"] = [dataset["data"]['datasetv2']['provenance']['origin']['collectionSituation'][0]]
        else:
            if val == "HESAE":
                data_out["collection_situation"] = "A&E"
            else:
                data_out["collection_situation"] = ""
        if val == "MHSDS":
            data_out["purpose"] = ""
            data_out["source"] = ""
        else:
            data_out["purpose"] = [dataset["data"]['datasetv2']['provenance']['origin']['purpose'][0]]
            data_out["source"] = [dataset["data"]['datasetv2']['provenance']['origin']['source'][0]]
        data_out["pathway"] = [dataset["data"]['datasetv2']['coverage']['pathway']]
        if type(data_out_df) == str:
            data_out_df = pd.DataFrame(data = data_out)
        else:
            data_out_row = pd.DataFrame(data = data_out)
            data_out_df = pd.concat([data_out_df, data_out_row]) 

    data_out_df.to_csv("gateway.csv")


def main():
    gateway()
    mental_health_catalogue()


if __name__ == "__main__":
    main()