import os
import pandas as pd

def main():
    source = pd.read_excel("all_sources_in.xlsx", sheet_name = "Sheet1",index_col=False)
    print(source.columns)
    print(source)
    #source = source.drop(columns=["Unnamed: 0"])
    dataset = pd.read_excel("Database tables.xlsx", index_col=False)

    source["Aims"] = source["Aims"].str.replace("<br>", "")
    source["Aims"] = source["Aims"].str.replace("â€™", "'")
    source["Aims"] = source["Aims"].str.replace("ï¬", "f")
    source["Aims"] = source["Aims"].str.replace("â€“", "-")
    source["Aims"] = source["Aims"].str.replace("â€˜", "'")
    source["Aims"] = source["Aims"].str.replace("â€™", "'")


    source["Themes"] = source["Themes"].str.replace("\n", "")
    source["Themes"] = source["Themes"].str.replace(", ", ",")
    source["Themes"] = source["Themes"].str.replace(" ,", ",")
    source["Themes"] = source["Themes"].str.replace(", ", ",")
    source["Themes"] = source["Themes"].str.replace(" ,", ",")
    source["Themes"] = source["Themes"].str.replace(",,", ",")
    
    source['Themes'] = source['Themes'].str.rstrip(',')
    source['Themes'] = source['Themes'].str.rstrip(',')
    source['Themes'] = source['Themes'].str.rstrip(',')
    source['Themes'] = source['Themes'].str.rstrip(',')


    dataset["topic_tags"] = dataset["topic_tags"].str.replace("\n", "")
    dataset["topic_tags"] = dataset["topic_tags"].str.replace(" ", " ")
    dataset["topic_tags"] = dataset["topic_tags"].str.replace(", ", ",")
    dataset["topic_tags"] = dataset["topic_tags"].str.replace(" ,", ",")
    dataset["topic_tags"] = dataset["topic_tags"].str.replace(", ", ",")
    dataset["topic_tags"] = dataset["topic_tags"].str.replace(" ,", ",")
    dataset["topic_tags"] = dataset["topic_tags"].str.replace(", ", ",")
    dataset["topic_tags"] = dataset["topic_tags"].str.replace(" ,", ",")
    dataset["topic_tags"] = dataset["topic_tags"].str.replace(",,", ",")
    
    dataset['topic_tags'] = dataset['topic_tags'].str.rstrip(' ')
    dataset['topic_tags'] = dataset['topic_tags'].str.rstrip(' ')
    dataset['topic_tags'] = dataset['topic_tags'].str.rstrip(',')
    dataset['topic_tags'] = dataset['topic_tags'].str.rstrip(' ')
    dataset['topic_tags'] = dataset['topic_tags'].str.rstrip(',')
    dataset['topic_tags'] = dataset['topic_tags'].str.rstrip(' ')
    dataset['topic_tags'] = dataset['topic_tags'].str.rstrip(',')
    dataset['topic_tags'] = dataset['topic_tags'].str.rstrip(' ')
    dataset['topic_tags'] = dataset['topic_tags'].str.rstrip(',')


    source.to_excel("all_sources_in.xlsx", index = False)
    dataset.to_excel("Database tables.xlsx", index = False)




if __name__ == "__main__":
    main()