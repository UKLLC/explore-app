import requests
import pandas as pd


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


def main():
    api_url = "https://www.cataloguementalhealth.ac.uk:443/testing/api/v2/"
    # Specify the endpoint you want to access (replace with your specific endpoint)
    endpoint_to_access = "studies"#"-H 'accept: application/json' \ -H 'Range-Unit: items'"

    # Fetch data from the specified endpoint
    result = fetch_data_from_postgrest_api(api_url, endpoint_to_access)
    result = pd.DataFrame(data = result)
    # Process the result (replace this part with your specific data processing logic)
    if result is not None:
        print("Data fetched successfully:")
        print(result.columns)
        data_out = result[["study_id", "title", "aims", "website", "related_themes", "sample_type", "geographic_coverage_nations", "geographic_coverage_regions", "start_date", "sample_size_at_recruitment", "age_at_recruitment", "sex"]]
        data_out.columns = ["MH_study_id", "LPS name", "Aims", "Website", "Themes", "Sample type", "Geographic coverage - Nations", "Geographic coverage - Regions", "Start date", "Sample size at recruitment", "Age at recruitment", "sex"]
        #print(data_out["MH_study_id"])
        
        llc_studies = ["ALSPAC", "AHMS", "BCS", "BiB", "ELSA", "GSSFHS", "LSYPE", "MCS", "NCDS", "NICOLA", "SABRE", "TEDS", "TwinsUK", "UKHLS"]
        data_out = data_out.loc[data_out["MH_study_id"].isin(llc_studies)]

        
        
        data_out.to_csv("mh_catalogue.csv")
    else:
        print("Failed to fetch data.")

    pass


if __name__ == "__main__":
    main()