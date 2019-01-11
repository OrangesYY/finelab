"""
This file provides Insert/Delete/Update and Query methods.
For Insert/Delete/Update support, this file provides functions including data flitering and operation commiting.
For Query support, this file provides functions including string replacing, regular Expression replacing,  
This file will also deal with owner authority.
"""
from .data_frame import DataFrame
import sqlite3
class DataHandler:
    def __init__(self, db_path, frame_path):
        self.data_framework = DataFrame(frame_path)
        self.database = sqlite3.connect(db_path)
        pass
    def query(self, t_name, filters_list = []):
        pass
    def insert(self, t_name, values_dicts_list):
        pass
    def delete(self, t_name, filters_list = []):
        pass
    def update(self, t_name, values_dicts_list, filters_list = []):
        pass



    def query_for_display(self):
        pass
    def query_for_selection(self):
        pass
    def close_db(self):
        pass