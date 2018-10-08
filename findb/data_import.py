import csv
from findb.data_stru import Business
import sqlite3

def importTableFromCSV(bsns_json_path, from_csv_path, target_db_path):
    with open(bsns_json_path, "r", encoding = "utf-8") as f:
        reader = csv.DictReader(f)      # First line of CSV is key
        column = [row for row in reader]


def exportTableToCSV(bsns_json_path, from_csv_path, target_db_path):
    row = ['5', 'hanmeimei', '23', '81']
    
    
    
    
    
    with open(from_csv_path, "w+", newline = "") as f:
        csv_writer = csv.writer(f, dialect = "excel")
        csv_writer.writerow(row)
    
    


