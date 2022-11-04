import pandas as pd
import logging
import os
import ijson

def export_to_csv(obj, path):
    # Convert list of dictionaries to csv file trough pandas
    df = pd.DataFrame.from_dict(obj)
    df.to_csv (path, index = False, header=True) 

def get_json_files_paths(path):
    result = []

    for j in os.listdir(path):
        if j.endswith('.json'):
            result.append(path + j)

    return result

#Not implemented yet - This is for converting data into a DB
def get_tree(item, tree):
    # get tree from ration card details categories data

    b = item.get('categories')
    try:
        tree.setdefault(b['District_Name_PMO'], {})
        tree[b['District_Name_PMO']].setdefault(b['town_wise'], {})
        # Rural
        #if b['town_wise'] == 'rural':
        tree[b['District_Name_PMO']][b['town_wise']].setdefault(b['Tahsil_Name_PMO'], {})
        tree[b['District_Name_PMO']][b['town_wise']][b['Tahsil_Name_PMO']].setdefault(b['Panchayat_Name_PMO'], {}) 
        tree[b['District_Name_PMO']][b['town_wise']][b['Tahsil_Name_PMO']][b['Panchayat_Name_PMO']].setdefault(b['Village_Name_PMO'], {}) 
        tree[b['District_Name_PMO']][b['town_wise']][b['Tahsil_Name_PMO']][b['Panchayat_Name_PMO']][b['Village_Name_PMO']].update({
            b['PLC_code'] + b['Unique_RC_ID']: ''
        })
    except:
        try:
            tree[b['District_Name_PMO']].setdefault(b['town_wise'], {})
            tree[b['District_Name_PMO']][b['town_wise']].setdefault(b['Village_Name_PMO'], {})
            tree[b['District_Name_PMO']][b['town_wise']][b['Village_Name_PMO']].setdefault(b['FPS_Name_PMO'], {}) 
            tree[b['District_Name_PMO']][b['town_wise']][b['Village_Name_PMO']][b['FPS_Name_PMO']].update({
               b['PLC_code'] + b['Unique_RC_ID']: '' 
            })
        except:
            logging.error(f'Tree broken check: {b}')

    return tree