import re
import urllib.parse
import logging
import ijson
import sqlite3
from helpers import *

BASE_PATH = 'parsed'

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("logs/parser.log"),
                              logging.StreamHandler()])

def create_sql_db():
    conn = sqlite3.connect(f'{BASE_PATH}/ration_cards.sqlite')
    cursor = conn.cursor()
    cursor.execute('Create Table if not exists ration_card_details (ration_card_number TEXT NOT NULL PRIMARY KEY, card_type Text, img_url Text, know Text, mobile_number Text, fair_price_shopkeeper_name Text, fps_id Text, village_id Text, plc_id Text, unique_rc_id Text, url Text, family_members_table Text)')

    cursor.execute('Create Table if not exists district (id INTEGER NOT NULL PRIMARY KEY, name Text)')
    cursor.execute('Create Table if not exists town (id INTEGER NOT NULL PRIMARY KEY, name Text)')
    cursor.execute('Create Table if not exists village (id TEXT NOT NULL PRIMARY KEY, name Text)')
    cursor.execute('Create Table if not exists fps (id INTEGER NOT NULL PRIMARY KEY, name text)')
    cursor.execute('Create Table if not exists tahsil (id INTEGER NOT NULL PRIMARY KEY, name Text)')
    cursor.execute('Create Table if not exists panchayat (id INTEGER NOT NULL PRIMARY KEY, name Text)')
    
    return conn, cursor

def feed_tree(cursor, cat):
    tw = cat.get('town_wise')
    if tw:
        query = """INSERT OR IGNORE INTO town (id, name) VALUES (?, ?)"""
        insert = (
            1 if tw == 'rural' else 2, 
            tw
        )
        cursor.execute(query, insert)

    if cat.get('District_Code_PMO'):
        query = """INSERT OR IGNORE INTO district (id, name) VALUES (?, ?)"""
        insert = (
           cat.get('District_Code_PMO', ''), 
           cat.get('District_Name_PMO', '') 
        )
        cursor.execute(query, insert)

    if cat.get('FPS_CODE_PMO'):
        query = """INSERT OR IGNORE INTO fps (id, name) VALUES (?, ?)"""
        insert = (
           cat.get('FPS_CODE_PMO', ''), 
           cat.get('FPS_Name_PMO', '') 
        )
        cursor.execute(query, insert)

    if cat.get('Village_Code_PMO'):
        query = """INSERT OR IGNORE INTO village (id, name) VALUES (?, ?)"""
        insert = (
           cat.get('Village_Code_PMO'), 
           cat.get('Village_Name_PMO', '') 
        )
        cursor.execute(query, insert)

    elif cat.get('Village_Name_PMO'):
        query = """INSERT OR IGNORE INTO village (id, name) VALUES (?, ?)"""
        insert = (
           cat.get('Village_Name_PMO'), 
           cat.get('Village_Name_PMO', '') 
        )
        cursor.execute(query, insert)

    if cat.get('Tahsil_Code_PMO'):
        query = """INSERT OR IGNORE INTO tahsil (id, name) VALUES (?, ?)"""
        insert = (
           cat.get('Tahsil_Code_PMO', ''), 
           cat.get('Tahsil_Name_PMO', '') 
        )
        cursor.execute(query, insert)
    
    if cat.get('Panchayat_Code_PMO'):
        query = """INSERT OR IGNORE INTO panchayat (id, name) VALUES (?, ?)"""
        insert = (
           cat.get('Panchayat_Code_PMO', ''), 
           cat.get('Panchayat_Name_PMO', '') 
        )
        cursor.execute(query, insert)


def json_to_sqlite(conn, cursor, paths):
    for path in paths:
        with open(path, 'rb') as f:
            for item in ijson.items(f, "item"):
                
                # Ration card details
                rcd = item.get('ration_card_details')
                if rcd:
                    categories = item.get('categories', {})

                    query = """INSERT OR IGNORE INTO ration_card_details
                          (ration_card_number, card_type, img_url, know, mobile_number, fair_price_shopkeeper_name, fps_id, village_id, plc_id, unique_rc_id, url, family_members_table) 
                           VALUES 
                          (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""

                    insert = (
                        rcd.get('राशनकार्ड संख्या', ''),
                        rcd.get('कार्ड का प्रकार', ''),
                        rcd.get('img', ''),
                        rcd.get('पता', ''),
                        rcd.get('मोबाईल संख्या', ''),
                        rcd.get('उचित मूल्य दुकानदार का नाम', ''),
                        categories.get('FPS_CODE_PMO', ''),
                        categories.get('Village_Code_PMO', ''),
                        categories.get('PLC_code', ''),
                        categories.get('Unique_RC_ID', ''),
                        categories.get('url', ''),
                        item.get('sub_table', '')
                    )

                    cursor.execute(query, insert)
                    feed_tree(cursor, categories)
                    conn.commit() 

    return conn
        
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
    path = f'{BASE_PATH}/extracted/'
    paths = get_json_files_paths(path)
    
    logging.info(f'Dumping results into DB...') 
    conn, cursor = create_sql_db()
    conn = json_to_sqlite(conn, cursor, paths)
    conn.close()


if __name__ == '__main__':
    main()