import json
import re
import pandas as pd
from sanity import clean_string, check_sanity
import urllib.parse

BASE_PATH = '../parsed'

def export_to_csv(obj, path):
    # Convert list of dictionaries to csv file trough pandas
    df = pd.DataFrame.from_dict(obj)
    df.to_csv (path, index = False, header=True) 

def read_json_file(path):
    with open(path, 'r') as f:
        file = f.read()

    return json.loads(file)

#Not implemented yet - This is for converting data into a DB
# def get_tree(jd):
#     # get tree from ration card details categories data

#     branches = []
#     only_rcd =  list(filter(lambda x: x.get('ration_card_details'), jd))
#     for rct in only_rcd:
#         branch = rct.get('categories')
#         del branch['PLC_code']
#         del branch['Unique_RC_ID']
#         branches.append(json.dumps(branch))
    
#     branches = set(branches)
#     return [json.loads(_) for _ in branches]

def clean_field(f):
    try:
        f = f.replace('+', ' ')
        f = f.replace('%20', ' ')
        f = re.sub('\s+', ' ', f)
        f = f.strip()
    except Exception as e:
        print(e)

    return f

def clean_decode(obj):
    return {k:urllib.parse.unquote(clean_field(v)) for k,v in obj.items()}


def main():
    json_data = read_json_file(f'{BASE_PATH}/extracted.json')

    #tree = get_tree(json_data)
    
    ration_cards = []
    for line in json_data:
        if line.get('ration_card_details'):
            ration_cards.append(line)

        # export table
        else:
            table = json.loads(line['table'])
            categories = clean_decode(line['categories'])

            names_in_categories =  {k: v for k, v in categories.items() if 'Code' not in k}
            file_name = '_'.join([ _ for _ in names_in_categories.values()]).replace(' ','')
            path = f"{BASE_PATH}/tables/{file_name}.csv"

            export_to_csv(table, path)

    # ration card parsing
    rcds_formatted = []

    for rc in ration_cards:
        row = rc.get('ration_card_details')
        try:
            row['img'] = rc.get('images')[0].get('path')
        except:
            row['img'] = ''
        
        row.update(clean_decode(rc['categories']))
        fmd_table_id = 'FMD' + rc['categories']['PLC_code'] + rc['categories']['Unique_RC_ID']
        row.update({
            'family members details table id': fmd_table_id,
            'url': rc.get('url'),
        })

        # Append ration card data row
        rcds_formatted.append(row)

        # Store family member details tables with unique ID
        fmd_table = json.loads(rc.get('sub_table', []))
        path = f"{BASE_PATH}/family_members_details/{fmd_table_id}.csv"
        export_to_csv(fmd_table, path) 
    
    path = f"{BASE_PATH}/ration_cards_details.csv" 
    export_to_csv(rcds_formatted, path)


if __name__ == '__main__':
    main()