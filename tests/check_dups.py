import json

def main(path):
    with open(path) as f:
        e = json.loads(f.read())

    checked = []
    repeated = {}

    for l in e:
        str_l = str(l)
        if str_l not in checked:
            checked.append(str_l)
        else:
            _id = l['ration_card_details']['राशनकार्ड संख्या']
            repeated[_id] = repeated.get(_id, 0) + 1
            #print(l['url'])

    print('Times repeated:')
    print(repeated.values())
    print(f'Unique values: {len(checked)}')
    print(f'Extracted values: {len(e)}')


if __name__ == '__main__':
    
    main('parsed/extracted_test.json')
