import json
import pandas as pd


BASE_PATH = 'parsed'

def export_to_csv(obj, path):
    # Convert list of dictionaries to csv file trough pandas
    try:
        df = pd.DataFrame.from_dict(obj)
        df.to_csv (path, index = False, header=True) 
    except:
        pass

def read_json_file(path):
    with open(path, 'r') as f:
        file = f.read()

    return json.loads(file)


def main():
    json_data = read_json_file('parsed/extracted_test.json')
    
    ration_cards = []
    for line in json_data:
        if line.get('ration_card_details'):
            ration_cards.append(line)

        # export table
        else:
            table = json.loads(line['table'])
            categories = line['categories']

            file_name = '_'.join([ _ for _ in categories.values()]).replace(' ','')
            path = f"{BASE_PATH}/tables/{file_name}.csv"

            export_to_csv(table, path)

    # Person parsing
    rcds_formatted = []

    for rc in ration_cards:
        row = rc.get('ration_card_details')
        row.update(categories)
        row.update({
            'family members details': json.loads(rc.get('sub_table', [])),
            'url': rc.get('url'),
        })

        rcds_formatted.append(row)
    
    path = f"{BASE_PATH}/ration_cards_details.csv" 
    export_to_csv(rcds_formatted, path)


if __name__ == '__main__':
    main()