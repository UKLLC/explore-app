import pandas as pd
from collections import Counter

def flatten_concatenation(matrix):
     flat_list = []
     for row in matrix:
         flat_list += row
     return flat_list


if __name__ == "__main__":
    source_df = pd.read_excel("all_sources_in.xlsx", sheet_name="Sheet1")
    source_themes = list(source_df["Themes"])
    source_themes = [x.replace(" ", "") for x in source_themes]
    source_themes = [x.replace("\n", "") for x in source_themes]
    source_themes = [x.replace(u'\xa0', u'') for x in source_themes]
    source_themes = [x.split(",") for x in source_themes]
    source_themes = flatten_concatenation(source_themes)
    st_count = Counter(source_themes)

    dataset_df = pd.read_excel("Database tables.xlsx", sheet_name="Dataset")
    dataset_themes = list(dataset_df["topic_tags"].fillna(""))

    dataset_themes = [x.replace(" ", "") for x in dataset_themes]
    dataset_themes = [x.replace("\n", "") for x in dataset_themes]
    dataset_themes = [x.replace(u'\xa0', u'') for x in dataset_themes]
    dataset_themes = [x.split(",") for x in dataset_themes]
    dataset_themes = flatten_concatenation(dataset_themes)
    dt_count = Counter(dataset_themes)

    all_themes = source_themes + dataset_themes
    all_count = Counter(all_themes)

    print(st_count)
    print(dt_count)
    print(all_count)
