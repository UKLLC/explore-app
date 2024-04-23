from datetime import datetime
import re

import pandas as pd
import constants

def is_date(date):
    '''
    Check for non-valid date formats (must be YYYY/MM/DD).
    Inputs:
        data (str): the date
    Returns:
        (Boolean) True if matches format, else False 
    '''
    date_format = '%Y%m%d'
    if len(date) == 8:
        try:
            datetime.strptime(date, date_format)
            return True
        except ValueError:
            pass
    return False
    
def get_date(name):
    '''
    Match date part of the table name.
    Inputs:
        name (str): the table name
    Returns:
        (str) date matching regular expression
    '''
    parts, part_types = break_down_name(name)
    try:
        date = parts[part_types.index("date")]
        return date
    except:
        return None

def is_version(version):
    ''' 
    Look for version of the form v[num]*4.
    Inputs:
        version (str): a part of the name
    Returns:
        (Boolean) True if matches name, else False
    '''
    for i in range(4,-1, -1):
        pattern = re.compile("v[0-9]{"+str(i)+"}")
        match = pattern.match(version)
        if match != None:
            if match.group() == version:
                return True
    return False

def get_version(name):
    '''
    Match version part of the table name.
    Inputs:
        name (str): the table name
    Returns:
        (str) version matching regular expression
    '''
    for i in range(4,0, -1):
        pattern = re.compile("v[0-9]{"+str(i)+"}")
        match = re.search(pattern, name)
        if match != None:
            return match.group()
    return None


def is_label(part):
    '''
    Check if part is "values" or "description".
    Inputs:
        part (str): section of a table name
    Returns:
        (Boolean) True if match, else False
    '''
    if part == "description" or part == "values":
        return True
    return False


def is_subblock_number(part):
    '''
    Check it is a 2 digit number on its own.
    Inputs:
        part (str): section of a table name
    Returns:
        (Boolean) True if match, else False
    '''
    if len(part) <=2 and all(map(str.isdigit, part)):
        return True
    return False

def is_dataset(part):
    '''
    CODELIST: check if part is recognised dataset.
    Inputs:
        part (str): section of a codelist table name
    Returns:
        (Boolean) True if match, else False
    '''
    if part.upper() in constants.DATASETS:
        return True
    return False

def is_codeset(part):
    '''
    CODELIST: check if part is recognised codeset.
    Inputs:
        part (str): section of a codelist table name
    Returns:
        (Boolean) True if match, else False
    '''
    if part.upper() in constants.CODESETS:
        return True
    return False



def identify_part(part):
    '''
    Identifies the type of a section of a table name (data, version, label, subblock number, other).
    Inputs:
        part (str): the part section of a name
    Returns:
        (str) the type label of the part
    '''
    if part == '':
        return "null"
    elif is_date(part):
        return "date"
    elif is_subblock_number(part):
        return "subblock number"
    elif is_version(part):
        return "version"
    elif is_label(part):
        return "label"
    else:
        return "other"

def identify_part_CODELIST(part):
    '''
    Identifies the type of a section of a table name (null, dataset, codeset, other).
    Inputs:
        part (str): the part section of a name
    Returns:
        (str) the type label of the part
    '''
    if part == '':
        return "null"
    elif is_dataset(part):
        return "dataset"
    elif is_codeset(part):
        return "codeset"
    else:
        return "other"

def split_name(name, delimiter = "_"):
    '''
    Split a string into parts around a delimiter character.
    Inputs:
        name (str): a table name with several parts
        delimiter (str): characters to split parts by
    Returns:
        parts (list): the split part names 
    '''
    parts = []
    for part in name:
        parts += part.split(delimiter)
    return parts


def remove_dupes(part_types, tag):
    '''
    Loop through parts from back to front. If several instances of a tag, replace it with other tag and print a warning.
    Inputs:
        part_types (list of str): the part types
        tag (str): type to check for
    '''
    seen = False
    for i in range(len(part_types)-1, -1, -1):
        if part_types[i] == tag:
            if not seen:
                seen = True
            else:
                #print("Warning: identifed two name parts of type {}".format(tag))
                part_types[i] = "other"
                

def break_down_name(name):
    '''
    Split and label parts of a table name.
    Inputs:
        name (str): the name of the target table
    Returns:
        parts (list of str): the table name split
        part_types (list of str): the types of each part
    '''
    parts = split_name(split_name([name], "_"), "-")
    part_types = []
    for part in parts:
        part_types.append(identify_part(part))
    #positioning pass
    for tag_index in range(len(part_types)):
        if part_types[tag_index] == "subblock number":
            if "date" in part_types and "label" in part_types:
                if tag_index == len(part_types)-3:
                    continue
                else:
                    part_types[tag_index] = "other"
            else:
                if tag_index == len(part_types)-2:
                    continue
                else:
                    part_types[tag_index] = "other"
        if part_types[tag_index] == "date":

            if tag_index == len(part_types)-1:
                continue
            else:
                part_types[tag_index] = "other"

    # remove duplicates
    unique_types = ["date", "version", "label", "subblock number"]
    for tag in unique_types:
        remove_dupes(part_types, tag)

    return parts, part_types


def break_down_name_CODELIST(name):
    '''
    Split and label parts of a table name (for codelist tables).
    Inputs:
        name (str): the name of the target table
    Returns:
        parts (list of str): the table name split
        part_types (list of str): the types of each part
    '''
    parts = split_name([name], "_")
    part_types = []
    for part in parts:
        part_types.append(identify_part_CODELIST(part))

    #positioning pass: Expecting name parts to be in the order: other, dataset, codeset
    first_datset = part_types.index("dataset")
    first_codeset = part_types.index("codeset")
    for tag_index in range(len(part_types)):
        if part_types[tag_index] == "other" and (tag_index > first_datset or tag_index > first_codeset):
            raise Exception("Codelist name parsing error: unrecognised part {} in position {}".format(parts[tag_index], tag_index))
        if part_types[tag_index] == "dataset" and tag_index > first_codeset:
            raise Exception("Codelist name error: datset part {} before codeset part {}".format(parts[tag_index], parts[first_codeset]))

    return parts, part_types


def remove_subblock_num(df):
    '''
    Split up the name and remove the part that is the subblock number.
    Inputs:
        df (row of DataFrame): rows containing TABLE_NAME
    Returns:
        (str) recombined name without subblock
    '''
    table_name = df["TABLE_NAME"]
    return remove_subblock_num_single(table_name)


def remove_subblock_num_single(table_name):
    '''
    Split up the name and remove the part that is the subblock number.
    Inputs:
        table_name (str)
    Returns:
        (str) recombined name without subblock
    '''
    split_name, part_types = break_down_name(table_name)
    if "subblock number" in part_types:
        index = part_types.index("subblock number")
        del split_name[index], part_types[index]
    return "_".join(split_name)


def contains_subblock(name):
    '''
    Identifies if a table has a subblock or not.
    Inputs:
        name (str): the table name
    Returns:
        (Boolean) True if contains a subblock number, else False
    '''
    _,name_types = break_down_name(name)
    if "subblock number" in name_types:
        index = name_types.index("subblock number")
        if name_types[index-1] == "version":
            return True
        else:
            return False
    else:
        return False

def contains_subblock_prep(df):
    name = df["TABLE_NAME"]
    return contains_subblock(name)


def remove_part(df, part, col = "table"):
    '''
    Removes [part] sections from table name.
    Inputs:
        df (row of a DataFrame): row containing "TABLE_NAME" column
        part (str): the label of the parts to remove
    Returns:
        (str) recombined table name
    '''
    name = df[col]
    parts, part_types = break_down_name(name)
    if part in part_types:
        index = part_types.index(part)
        del parts[index]
    return "_".join(parts)


def subblocks_to_master(df):
    '''
    Take a DataFrame and remove tables with a subblock number, replacing them with 1 row of the master block.
    Inputs:
        df (DataFrame): table register
    Returns:
        df2 (DataFrame): table register without tables with subblocks
    '''
    df["subblock"] = df.apply(contains_subblock_prep, axis = 1)
    subblocks = df.loc[df["subblock"] == True]
    subblocks["TABLE_NAME"] = subblocks.apply(remove_subblock_num, axis = 1)
    subblocks = subblocks.drop_duplicates(subset=["TABLE_SCHEMA", "TABLE_NAME"])

    df2 = pd.merge(df.loc[df["subblock"] == False], subblocks, how = "outer")
    df2.reset_index()
    df2 = df2.drop(columns = ["subblock"])

    return df2


def master_to_subblocks(df):
    '''
    Take a DataFrame and look for subblock with a similar names.
    Inputs:
        df (DataFrame): table register
    Returns:
        matches (DataFrame): table register with subblocks added
    '''
    register = io.load_table_register("1")[["TABLE_SCHEMA", "TABLE_NAME"]]
    register["FORMATTED_TABLE_NAME"] = register.apply(remove_subblock_num, axis = 1)
    subblocks = register.loc[register["FORMATTED_TABLE_NAME"] != register["TABLE_NAME"]]

    df = df.rename(columns = {"TABLE_NAME":"FORMATTED_TABLE_NAME"})
    matches = pd.merge(df, register, on = ["TABLE_SCHEMA", "FORMATTED_TABLE_NAME"], how = "inner")
    return matches


def get_naming_parts(df, col = "TABLE_NAME", keep = None):
    '''
    apply function
    Take a tablename and return the "name" part of each table name.
    Inputs:
        df (row of DataFrame): a table register 
        col (str): the column name of df to take table names from
        keep (list of str): other column tags to keep
    Returns:
        (str) the name (and [keep] parts of a table name)
    '''
    name = df[col]
    parts, part_types = break_down_name(name)
    if keep:
        # Include tags in keep (like [label, version, etc])
        indices = [i for i, x in enumerate(part_types) if (x == "other" or x in keep)]
    else:
        indices = [i for i, x in enumerate(part_types) if x == "other"]
    name_parts = [parts[i] for i in indices]
    return "_".join(name_parts)


def get_CODELIST_sheet_parts(sheet_name):
    '''
    Take a tablename and return the parts of each CODELIST sheet name.
    Inputs:
        sheet_name (str): name of the codelist sheet (should be [origin]_[dataset]_[codeset])
    Returns:
        schema_parts (str): "_" joined parts marked as "other" (origin/schema)
        dataset_parts (str): "_" joined parts marked as "dataset"
        codeset_parts (str): "_" joined parts marked as "codeset"
     '''
    parts, part_types = break_down_name_CODELIST(sheet_name)

    schema_indices = [i for i, x in enumerate(part_types) if x == "other"]
    schema_parts = "_".join([parts[i] for i in schema_indices])

    dataset_indices = [i for i, x in enumerate(part_types) if x == "dataset"]
    dataset_parts = "_".join([parts[i] for i in dataset_indices])

    codeset_indices = [i for i, x in enumerate(part_types) if x == "codeset"]
    codeset_parts = "_".join([parts[i] for i in codeset_indices])

    return schema_parts, dataset_parts, codeset_parts


def filter_CODELIST_table_codeset(codelist_name):
    '''
    Get codeset part of codelist names if it includes a valid codeset.
    Inputs:
        codelist_name (str): the codelist table name
    Returns:
        codeset (str): the codeset part of the codelist
    '''
    splits = codelist_name.split("_")
    codeset = splits[-2]

    # check against known codesets
    if codeset in constants.CODESETS:
        return codeset
    else:
        raise Exception("Unrecognised Codeset: correct table name or ammend constants")

def remove_label_df(df):
    '''
    pass dataframe into existing remove_label(name) function
    '''
    return remove_label(df["TABLE_NAME"])

def remove_label(name):
    '''
    Take a table name and remove the "values" or "description" (label) part.
    Inputs:
        name (str): the table name
    Returns:
        (str) the table name excluding the label part
    '''
    parts, part_types = break_down_name(name)
    if "label" in part_types:
        index = part_types.index("label")
        del parts[index]
    return "_".join(parts)


def remove_date(name):
    '''
    Take a table name and date part.
    Inputs:
        name (str): the table name
    Returns:
        (str) the table name excluding the date part
    '''
    parts, part_types = break_down_name(name)
    if "date" in part_types:
        index = part_types.index("date")
        del parts[index]
    return "_".join(parts)


def contains_label(df):
    '''
    Check if each table name includes a label name and if so return it.
    Inputs:
        df (row of DataFrame): table register including "TABLE_NAME" column
    Returns:
        parts (list of str): name parts of type label
    '''
    name = df["TABLE_NAME"]
    parts, part_types = break_down_name(name)
    if "label" in part_types:
        return parts[part_types.index("label")] 
    else:
        return None

def datetime_now():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def edit_distance(s1, s2):
    '''
    Manual implementation of Levenshtein distance: calculates the number of operations required to change string 1 to string 2.
    Inputs:
        s1 (str): string 1
        s2 (str): string 2
    Returns:
        distances (int): the number of operations taken to change s1 to s2
    '''
    if len(s1) > len(s2):
        s1, s2 = s2, s1

    distances = range(len(s1)+1)
    for i2, c2 in enumerate(s2):
        distances_ = [i2+1]
        for i1, c1 in enumerate(s1):
            if c1 == c2:
                distances_.append(distances[i1])
            else:
                distances_.append(1 + min((distances[i1], distances[i1 + 1], distances_[-1])))
        distances = distances_
    return distances[-1]


def increment_version(cnxn, schema, table_name, version = None):
    '''
    Increment the version part of a table name until the table is unique in the database.
    Inputs:
        schema (str): the schema name
        table_name (str): the table name
        version (str): the version part of the table name
    Returns:
        table_name (str): original table name with incremented version if necessary
        existing (str): the name of the most recent table exisiting in db
    '''
    if version == None:
        version = get_version(table_name)
    if not cnxn:
        cnxn = dbf.connect()
    old_table_name = None   
    if get_date(table_name):
        like_name = table_name[:-7]
    else:
        like_name = table_name
    while dbf.table_like_check(cnxn, schema, like_name): 
        new_version = "v" + str(int(version[1:]) + 1 )
        new_version = new_version[:1] + "0"*(5-len(new_version)) + new_version[1:]
        old_table_name = table_name
        table_name = table_name.replace(version, new_version)
        if get_date(table_name):
            like_name = table_name[:-7]
        else:
            like_name = table_name
        version = new_version
    
    # Search 10 ahead
    scout_version = version
    scout_table_name = table_name
    for i in range(10):
        new_version = "v" + str(int(scout_version[1:]) + 1 )
        new_version = new_version[:1] + "0"*(5-len(new_version)) + new_version[1:]
        scout_old_table_name = scout_table_name
        scout_table_name = scout_table_name.replace(scout_version, new_version)
        if get_date(scout_table_name):
            like_name = scout_table_name[:-7]
        else:
            like_name = scout_table_name
        scout_version = new_version
        if dbf.table_like_check(cnxn, schema, like_name): 
            table_name = scout_table_name

    return table_name, old_table_name

def set_version(table_name, new_version):
    '''
    '''
    old_version = get_version(table_name)
    new_table_name = table_name.replace(old_version, new_version)
    return new_table_name


def select_global_latest_version(df):
    df = select_latest_version(df)
    version, val = "v0001", 1
    for index, row in df.iterrows():
        try_version = get_version(row["TABLE_NAME"])
        try_val = int(try_version[1:])
        if try_val > val:
            version = try_version
            val = try_val
    return version


def select_latest_version(df, col = "table"):
    '''
    Get the most recent version of each table in the dataframe by version number.
    Inputs:
        df (DataFrame): table register of some sort
    Returns:
        df (DataFrame): table register including only latest versions
    '''
    df["TABLE_NAME_Backup"] = df[col]
    df[col] = df.apply(remove_part, axis = 1, args = ("date", col))
    df["FORMATTED_TABLE_NAME"] = df.apply(remove_part, axis = 1, args = ("version", col))
    
    df["version"] = df[col].apply(get_version)
    # UPDATE 20220207 to include schema in duplicate assessment
    df["TABLE_NAME"] = df["TABLE_NAME_Backup"]
    # UPDATE 20231208 - remove table with no version
    df = df.dropna(subset = ['version'])
    df = df.sort_values('version').drop_duplicates(["FORMATTED_TABLE_NAME"], keep='last')

    df = df.drop(columns = ["FORMATTED_TABLE_NAME", "version", "TABLE_NAME_Backup"])
    return df



def select_latest_date(df, col = "TABLE_NAME"):
    '''
    Get the most recent version of each table in the dataframe by date.
    Inputs:
        df (DataFrame): table register of some sort
    Returns:
        df (DataFrame): table register including only latest versions
    '''
    df["FORMATTED_TABLE_NAME"] = df.apply(remove_part, axis = 1, args = ("date", col))
    df["date"] = df[col].apply(get_date)
    
    df = (df.sort_values("date")).drop_duplicates("FORMATTED_TABLE_NAME", keep='last')

    df = df.drop(columns = ["FORMATTED_TABLE_NAME", "date"])
    return df


def filter_string(input_string, space_action = ""):
    '''
    Removes illegal SQL characters from a string
    Inputs:
        input_string (str): the string to correct
        space_action (str): the character to replace strings with
    Returns:
        a string without sql illegal characters
    '''
    input_string = input_string.replace(" ", space_action)
    illegal_characters = ["'", "-","/","@","%","$","£","!","^","*","~","#","?","|","\\","=","+","{","}","[","]",".",",",":",";","`","¬","<",">"]
    for char in illegal_characters:
        input_string = input_string.replace(char, "")
    return input_string



def variable_df_prep(df):
    '''
    Prepare a set of variables to improve chances of correctly matching linked variables
    inputs:
        variable (str)
    returns
        variable (str): altered
    '''
    variable = df["vars"]
    # force to lower
    variable = variable.lower()
    # remove non-core data variables (llc_id, avail_from_dt, etc)
    if variable in constants.IGNORE_VARS:
        return variable

    # Remove encryption tags from all vars
    variable = variable[:-2] if variable[-2:] == "_e" else variable 

    # Remove excess characters
    for rem_char in constants.REMOVE_CHARS:
        variable = variable.replace(rem_char,"")
    
    return variable


def variable_set_prep(var_set):
    '''
    Prepare a set of variables to improve chances of correctly matching linked variables
    inputs:
        var_set (list)
    returns
        var_set (list): altered
    '''
    # remove Nones (data issue in nhsd that crashes the process otherwise)
    var_set = [str(var) for var in var_set if var != None]

    # force to lower
    var_set = [x.lower() for x in var_set]
    # remove non-core data variables (llc_id, avail_from_dt, etc)
    for variable in constants.IGNORE_VARS:
        if variable in var_set:
            var_set.remove(variable)


    # Remove encryption tags from all vars
    var_set = [x[:-2] if x[-2:] == "_e" else x for x in var_set]

    # Remove excess characters
    for rem_char in constants.REMOVE_CHARS:
        var_set = [x.replace(rem_char,"") for x in var_set]
    
    return var_set



def variable_intersect_left_similarity(set1, set2):
    '''
    Calculate the similarity of two sets of variables by the variables of set1 in set2.
    Inputs:
        set1 (list): usually data table variables
        set2 (list): usually values table variables
    Returns:
        matching score (float): value between 1 and 0 indicating matching similarity (1 = perfect match, 0 = no similarity)
    '''
    #DEBUG
    set1, set2 = variable_set_prep(set1), variable_set_prep(set2)
    
    # calc score
    try:
        return len([x for x in set1 if x in set2]) / len(set1)
    except ZeroDivisionError:
        return 0


def variable_set_similarity(set1, set2):
    '''
    Calculate the similarity of two sets of variables by the intersection over the union.
    Inputs:
        set1 (list): usually data table variables
        set2 (list): usually values table variables
    Returns:
        matching score (float): value between 1 and 0 indicating matching similarity (1 = perfect match, 0 = no similarity)
    '''
    set1, set2 = set(variable_set_prep(set1)), set(variable_set_prep(set2))
    
    # calc score
    return len(set1.intersection(set2)) / len(set1.union(set2))