import pandas as pd
import numpy as np
import math
import urllib.request

import time
import json

def flavordb_entity_url(x):
    return "https://cosylab.iiitd.edu.in/flavordb/entities_json?id=" + str(x)

def get_flavordb_entity(x):
    with urllib.request.urlopen(flavordb_entity_url(x)) as url:
        return json.loads(url.read().decode())
    return None


def flavordb_entity_cols():
    return [
        'entity_id', 'entity_alias_readable', 'entity_alias_synonyms',
        'natural_source_name', 'category_readable', 'molecules'
    ]
    
    
# what we want to rename the JSON object "columns" to
def flavordb_df_cols():
    return [
        'entity id', 'alias', 'synonyms',
        'scientific name', 'category', 'molecules'
    ]



# "subcolumns" in the "molecules" column that we are interested in
def molecules_df_cols():
    return ['pubchem id', 'common name', 'flavor profile']   




def clean_flavordb_dataframes(flavor_df, molecules_df):
    """
    Helps ensure consistent intra-column typing and converts all strings to lowercase.
    """
    strtype = type('')
    settype = type(set())
    
    # ensuring that these columns have type str
    for k in ['alias', 'scientific name', 'category']:
        flavor_df[k] = [
            elem.strip().lower() if isinstance(elem, strtype) else ''
            for elem in flavor_df[k]
        ]
    
    # ensuring that these columns are always a set of str
    def map_to_synonyms_set(elem):
        if isinstance(elem, settype):
            return elem
        elif isinstance(elem, strtype) and len(elem) > 0:
            # if it's a string of a set,
            if elem[0] == '{' and elem[-1] == '}':
                # convert it to a set
                return eval(elem)
            else:
                # else it's probably directly from source
                return set(elem.strip().lower().split(', '))
        else:
            return set()
    
    flavor_df['synonyms'] = [
        map_to_synonyms_set(elem)
        for elem in flavor_df['synonyms']
    ]
    
    molecules_df['flavor profile'] = [
        set([x.strip().lower() for x in elem])
        for elem in molecules_df['flavor profile']
    ]
    
    return [
        flavor_df.groupby('entity id').first().reset_index(),
        molecules_df.groupby('pubchem id').first().reset_index()
    ]


# generate dataframes from some of the JSON objects
def get_flavordb_dataframes(start, end):
    """
    Download JSON data, converts it to DataFrames, and cleans them.
    
    Returns DataFrames for both foods and molecules, as well as missing JSON entries.
    """
    # make intermediate values to make dataframes from
    flavordb_data = []
    molecules_dict = {}
    missing = [] # numbers of the missing JSON files during iteration
    
    flavordb_cols = flavordb_entity_cols()
    
    for i in range(start, end):
        # we use a try-except here because some of the JSON pages are missing
        try:
            # 1: Find the JSON file. Gets the ith food entity, as a JSON dict
            fdbe = get_flavordb_entity(i + 1)

            # get only the relevant fields (columns) of the dict
            flavordb_series = [fdbe[k] for k in flavordb_cols[:-1]]
            flavordb_series.append( # convert the field to a set
                set([m['pubchem_id'] for m in fdbe['molecules']])
            )
            flavordb_data.append(flavordb_series)

            # update the molecules dataframe with the data in 'molecules' field
            for m in fdbe['molecules']:
                if m['pubchem_id'] not in molecules_dict:
                    molecules_dict[m['pubchem_id']] = [
                        m['common_name'],
                        set(m['flavor_profile'].split('@'))
                    ]
        except urllib.error.HTTPError as e:
            if e.code == 404: # if the JSON file is missing
                missing.append(i)
            else:
                raise RuntimeError(
                    'Error while fetching JSON object from ' + flavordb_entity_url(i)
                ) from e
            
    # generate the dataframes
    flavordb_df = pd.DataFrame(
        flavordb_data,
        columns=flavordb_df_cols()
    )
    molecules_df = pd.DataFrame(
        [
            [k, v[0], v[1]]
             for k, v in molecules_dict.items()
        ],
        columns=molecules_df_cols()
    )
    
    # clean up the dataframe columns
    flavordb_df, molecules_df = clean_flavordb_dataframes(flavordb_df, molecules_df)
    
    return [flavordb_df, molecules_df, missing]


# updates & saves the download progress of your dataframes
def update_flavordb_dataframes(df0, df1, ranges):
    """
    Adds more data to the specified DataFrames, and saves them as CSV files.
    
    If successful, returns the specified DataFrames, now updated, and any missing JSON files.
    """
    df0_old = df0
    df1_old = df1
    missing_old = []

    # time how long it took to download the files
    start = time.time()
    
    # for each range in ranges, save your progress.
    # don't continue with the program unless everything succeeds!
    try:
        for a, b in ranges:
            df0_new, df1_new, missing_new = get_flavordb_dataframes(a, b)
            
            df0_old = df0_old.append(df0_new, ignore_index=True)
            df1_old = df1_old.append(df1_new, ignore_index=True)
            missing_old.extend(missing_new)
        
        return df0_old, df1_old, missing_old
    except:
        raise # always throw the error so you know what happened
    finally:
        # even if you throw an error, you'll have saved them as csv files
        df0_old.to_csv('flavordb.csv')
        df1_old.to_csv('molecules.csv')

        end = time.time()
        mins = (end - start) / 60.0
        print('Downloading took: '+ str(mins) + ' minutes')
        



# get the missing entries
def missing_entity_ids(flavor_df):
    """
    Get the IDs of the missing JSON entries for this particular food DataFrame.
    """
    out = []
    entity_id_set = set(flavor_df['entity id'])
    for i in range(1, 1 + max(entity_id_set)):
        if i not in entity_id_set:
            out.append(i)
    return out


# loads the dataframes from csv files
def load_db():
    settype = type(set())
    
    df0 = pd.read_csv('flavours\\datasets\\flavordb.csv')[flavordb_df_cols()]
    df0['synonyms'] = [eval(x) if isinstance(x, settype) else x for x in df0['synonyms']]
    df0['molecules'] = [eval(x) for x in df0['molecules']]
    
    df1 = pd.read_csv('flavours\\datasets\\molecules.csv')[molecules_df_cols()]
    df1['flavor profile'] = [eval(x) for x in df1['flavor profile']]
    
    df0, df1 = clean_flavordb_dataframes(df0, df1)
    return df0, df1, missing_entity_ids(df0)



if __name__ == "__main__":
    df0, df1, missing = load_db()

    d = dict()

    d = dict(zip(df0['alias'], df0['entity id']))
    with open('flavours\\ingredients.json', 'w') as f:
        json.dump(d,f)

    df0 = pd.DataFrame(columns=flavordb_df_cols())
    df1 = pd.DataFrame(columns=molecules_df_cols())

    ranges = [(50 * i, 50 * (i + 1)) for i in range(20)]
    update_flavordb_dataframes(df0, df1, ranges)
    