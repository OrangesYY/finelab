import sys, os, json, copy

pass
pass

class Business:
    raw_dict = {}
    formated_dict = {}
    def __init__(self,arg = None):
        if type(arg) == dict:
            self.raw_dict = arg
            self.format_bussiness()
            
        elif type(arg) == str:
            # Open root json for read
            root_json_path = arg
            fpr = open(root_json_path, 'r')
            # Load dict from root json file
            root_json_dict = json.load(fpr)
            fpr.close()

            # Initiate self.raw_dict
            self.raw_dict = dict()
            for _key in root_json_dict:
                # Get root json directory firstly
                root_json_dir = os.path.dirname(os.path.realpath(arg)).replace("\\", "/")
                # Open the splited json file
                fpr = open(root_json_dir + "/" + root_json_dict[_key], 'r',encoding='utf-8')
                tmpDict = json.load(fpr)
                # Merge dicts
                self.raw_dict[_key] = tmpDict
                fpr.close()
            self.format_bussiness()

    def format_bussiness(self):
        self.formated_dict = copy.deepcopy(self.raw_dict)
        for t_name, t_stru in self.raw_dict.items():
            for c_name, c_stru in t_stru['$COLU'].items():
                # Before loop, set the origin to this column
                origin_t_name = t_name
                origin_c_name = c_name
                origin_c_dict = self.formated_dict[t_name]['$COLU'][c_name].copy()

                # Loop until the real origin is found
                while self.formated_dict[origin_t_name]['$COLU'][origin_c_name]['$TYPE'] == "column_cite":
                    citing_c_dict = self.formated_dict[origin_t_name]['$COLU'][origin_c_name]
                    citing_t_name = origin_t_name
                    citing_c_name = origin_c_name
                    
                    # Get The elder origin, and update the loop variables
                    origin_t_name = citing_c_dict['$STRU_origin_table']
                    origin_c_name = citing_c_dict['$STRU_origin_column']
                    
                    # Temporary storage of origin_c_dict
                    temp_c_dict = origin_c_dict.copy() 
                    origin_c_dict.update(self.formated_dict[origin_t_name]['$COLU'][origin_c_name].copy())
                    # If citing sections has re-defined the parameters, 
                    #     the final param is subject to the parameters defined in the citing section,
                    #     not the cited section.
                    # If you do not want to change a parameters defined in the cited section, 
                    #     please do NOT include this paramrter in your citing section in JSON.
                    origin_c_dict.update(temp_c_dict)  # So the parameters defined in the citing section can flush the cited params.
                if t_name != origin_t_name or c_name != origin_c_name :  # If this column is citing other columns
                    self.formated_dict[t_name]['$COLU'][c_name] = origin_c_dict
                    self.formated_dict[t_name]['$COLU'][c_name]['$STRU_real_origin_table'] = origin_t_name
                    self.formated_dict[t_name]['$COLU'][c_name]['$STRU_real_origin_column'] = origin_c_name
                else: # If this column is not citing other columns
                    if self.formated_dict[t_name]['$COLU'][c_name].get('$ISPK') == True: # is Primary Key
                        self.formated_dict[t_name]['$PMKY'] = c_name
                # Copy column name inside the column dict for easier access
                self.formated_dict[t_name]['$COLU'][c_name]['$CLNM'] = c_name
            # Copy table name inside the table dict for easier access
            self.formated_dict[t_name]['$TBNM'] = t_name
        return self.formated_dict
    
    def loadFromPath(self,f_path):
        self.__init__(f_path)
        return self
    
    def getFomatdDict(self, t_name = None):
        if t_name:
            return self.formated_dict[t_name]
        else:
            return self.formated_dict
        
    def getDmpdJsonStr(self):
        return json.dumps(self.formated_dict,indent = 4)
        
    # Table Init
    def createTInitSQL(self,t_name):
        t_stru = self.formated_dict[t_name]
        if t_stru['$TYPE'] == 'table':
            init_str = "CREATE TABLE {t_name} (\n{columns_str}\n)\n;"
            columns_str = ''
            
            for c_name, c_stru in t_stru['$COLU'].items():
                column_str = '{data_type_str}{constraints_str}'
                data_type_str = ''
                constraints_str = ''
                # if c_stru.get('$CONS_local'):
                #     constraints_str += c_stru.get('$CONS_local')
                if c_stru['$TYPE'] == "column_cite":
                    foreign_key_str = ' FOREIGN KEY REFERENCES {real_origin_table}({real_origin_column})'
                    foreign_key_str = foreign_key_str.format(
                        real_origin_table = c_stru['$STRU_real_origin_table'],
                        real_origin_column = c_stru['$STRU_real_origin_column']
                    )
                    constraints_str += foreign_key_str
                if c_stru.get('$ISPK') == True: # Is primary key
                    if c_stru['$TYPE'] == "column_cite":
                        pass # ![Exception]
                    else:
                        primary_key_str = ' PRIMARY KEY'
                        constraints_str += primary_key_str
                column_str = column_str.format(data_type_str = data_type_str, constraints_str = constraints_str)

                # ADD Column to columns str
                if columns_str == '':
                    columns_str += ('\t' + c_name + column_str)
                else :
                    columns_str += (',\n\t'+ c_name + column_str)
            init_str = init_str.format(t_name = t_name, columns_str = columns_str)
            return init_str
        else:
            pass # ![Exception]

    # View Init
    def createVInitSQL(self,v_name):
        pass
    
    # Only can be used when initializing, for safety reasons (SQL INJECT)
    def createQuerySQL(self, t_name, filters_list = [], read_auth_role = 'tourist', id = None):
        t_stru = self.formated_dict[t_name]
        if t_stru['$TYPE'] == 'table' or  t_stru['$TYPE'] == 'view' :
            query_str = "SELECT \n{columns_str} \nFROM \n\t{t_name} \n{filters_str}\n;"
            columns_str = ''
            filters_str = ''
            # Generate columns string
            for c_name, c_stru in t_stru['$COLU'].items():
                if c_stru['$AUTH_read'][read_auth_role]:
                    if columns_str == '':
                        columns_str += ('\t'+t_name+'.'+c_name )
                    else :
                        columns_str += (' ,\n\t'+t_name+'.'+c_name )
            # Generate filter string
            if id != None:
                # id specified
                filters_str = "WHERE " + t_stru['$PMKY'] + " = " + str(id)
            else:
                # id not specified
                for filter in filters_list:
                    if filters_list != None:
                        if filters_str == '':
                            filters_str += ('WHERE\n\t' + filter['left'] + filter['type'] + filter['right'])
                        else:
                            filters_str += (',\n\tAND ' + filter['left'] + filter['type'] + filter['right'])
            query_str = query_str.format(t_name = t_name, columns_str = columns_str,filters_str = filters_str)
            return query_str
        else:
            pass # ![Exception]
        
    # Only can be used when initializing, for safety reasons
    def createInsertSQL(self,t_name, values_dicts_list, write_auth_role = 'tourist'):
        t_stru = self.formated_dict[t_name]
        if t_stru['$TYPE'] == 'table':
            insert_str = "INSERT INTO {t_name}({columns_str}\n) \nVALUES{rows_str}\n;"
            columns_str = ''
            rows_str = ''
            # Generate columns string
            for c_name, c_stru in t_stru['$COLU'].items():
                if c_stru['$AUTH_write'][write_auth_role]:
                    if columns_str == '' :
                        columns_str += ('\n\t'+c_name )
                    else :
                        columns_str += (' ,\n\t'+c_name )
            # Generate Values Rows Set string
            for key, values_dict in enumerate(values_dicts_list):
                if rows_str == '':
                    row_str = '\n\t({values_str})'
                else:
                    row_str = ',\n\t({values_str})'

                values_str = ''
                for c_name, c_stru in t_stru['$COLU'].items():
                    if c_stru['$AUTH_write'][write_auth_role]:
                        value_str = values_dict.get(c_name) if  values_dict.get(c_name) else ''
                        if values_str == '':
                            values_str += ('\"'+ value_str +'\"')
                        else:
                            values_str += (','+'\"'+value_str+'\"')
                rows_str += row_str.format(values_str = values_str)


            insert_str = insert_str.format(t_name = t_name, columns_str = columns_str, rows_str = rows_str)
            return insert_str
        else:
            pass # ![Exception]
        
    # Only can be used when initializing, for safety reasons
    def createDeleteSQL(self, t_name, filters_list = [], write_auth_role = 'tourist', id = None):
        t_stru = self.formated_dict[t_name]
        if t_stru['$TYPE'] == 'table':
            delete_str = "DELETE FROM {t_name} \n {filters_str}\n;"
            
            # Generate filter string
            if id != None:
                # id specified
                filters_str = "WHERE " + t_stru['$PMKY'] + " = " + str(id)
            else:
                # id not specified
                for filter in filters_list:
                    if filters_list != None:
                        if filters_str == '':
                            filters_str += ('WHERE\n\t' + filter['left'] + filter['type'] + filter['right'])
                        else:
                            filters_str += (',\n\tAND ' + filter['left'] + filter['type'] + filter['right'])
            delete_str = delete_str.format(t_name = t_name,  filters_str = filters_str)
            return delete_str
        else:
            pass # ![Exception]
        
    # Only can be used when initializing, for safety reasons
    def createUpdateSQL(self, t_name, values_dict, filters_list = [], write_auth_role = 'tourist', id = None):
        t_stru = self.formated_dict[t_name]
        if t_stru['$TYPE'] == 'table':
            update_str = "UPDATE {t_name} SET\n {values_str} \n{filters_str}\n;"
            values_str = ''
            filters_str = ''
            # Generate values string
            for key, val in values_dict.items():
                c_stru = t_stru['$COLU'][key]
                if c_stru['$AUTH_write'][write_auth_role]:
                    if values_str == '' :
                        values_str += ('\t'+key + '=' + "\"" + val + "\"")
                    else :
                        values_str += (' ,\n\t'+key + '=' + "\"" + val + "\"")

            # Generate filter string
            if id != None:
                # id specified
                filters_str = "WHERE " + t_stru['$PMKY'] + " = " + str(id)
            else:
                # id not specified
                for filter in filters_list:
                    if filters_list != None:
                        if filters_str == '':
                            filters_str += ('WHERE\n\t' + filter['left'] + filter['type'] + filter['right'])
                        else:
                            filters_str += (',\n\tAND ' + filter['left'] + filter['type'] + filter['right'])
            update_str = update_str.format(t_name = t_name, values_str = values_str, filters_str = filters_str)
            return update_str
        else:
            pass # ![Exception]





# Outer Functions
def createQueryFilterDict(left,condition_type,righ):
    if condition_type == 'equal':
        pass
    










    
# Testing
if __name__ == '__main__':

    # For Dumped JSON String
    Dumped_json_str = Business().loadFromPath(sys.argv[1]).getDmpdJsonStr()
    print('Dumped JSON String:')
    print(Dumped_json_str)

    # # For Creating Table
    # Create_sql_str = Business().loadFromPath(sys.argv[1]).createTInitSQL(sys.argv[2])
    # print('\nCreate Table SQL String:')
    # print(Create_sql_str)

    # # For Query
    # filters_list = [
    #     {
    #         'left':'person_id',
    #         'type':'=',
    #         'right':':person_id'
    #     }
    # ]
    # Query_sql_str = Business().loadFromPath(sys.argv[1]).createQuerySQL(
    #     sys.argv[2],
    #     filters_list = filters_list,
    #     id = 3
    # )
    # print('\nQuery SQL String:')
    # print(Query_sql_str)
    
    # # For Insert
    # values_dicts_list =[
    #     {
    #         "type":"21",
    #         "person_role":"34"
    #     },
    #     {
    #         "type":"45",
    #         "admin_check":"56"
    #     }
    # ]
    # Insert_sql_str = Business().loadFromPath(sys.argv[1]).createInsertSQL(
    #     sys.argv[2],
    #     values_dicts_list = values_dicts_list,
    #     write_auth_role = 'admin'
    # )
    # print('\nInsert SQL String:')
    # print(Insert_sql_str)
    


