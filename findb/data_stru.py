import json
import sys
import _io

pass
pass

class Business:
    raw_dict = {}
    formated_dict = {}
    def __init__(self,arg = None):
        if type(arg) == dict:
            self.raw_dict = arg
            self.format_bussiness()
        elif type(arg) == _io.TextIOWrapper:
            self.raw_dict = json.load(arg)
            self.format_bussiness()
            
        elif type(arg) == str:
            self.raw_dict = json.loads(arg)
            self.format_bussiness()
    def format_bussiness(self):
        self.formated_dict = self.raw_dict.copy()
        for t_name, t_content in self.raw_dict.items():
            for c_name, c_content in t_content['$COLU'].items():
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
                    origin_c_dict.update(temp_c_dict)  
                if t_name != origin_t_name or c_name != origin_c_name :
                    self.formated_dict[t_name]['$COLU'][c_name] = origin_c_dict
                    self.formated_dict[t_name]['$COLU'][c_name]['$STRU_real_origin_table'] = origin_t_name
                    self.formated_dict[t_name]['$COLU'][c_name]['$STRU_real_origin_column'] = origin_c_name
                self.formated_dict[t_name]['$COLU'][c_name]['$CLNM'] = c_name
                
            self.formated_dict[t_name]['$TBNM'] = t_name
        return self.formated_dict
    def loadFromPath(self,f_path):
        f = open(f_path, 'r',encoding='utf-8')
        self.__init__(f)
        f.close()
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
        t_content = self.formated_dict[t_name]
        if t_content['$TYPE'] == 'table':
            init_str = "CREATE TABLE {t_name} (\n{columns_str}\n)\n;"
            columns_str = ''
            
            for c_name, c_content in t_content['$COLU'].items():
                column_str = '{data_type_str}{constraints_str}'
                data_type_str = ''
                constraints_str = ''
                if c_content.get('$CONS_local'):
                    constraints_str += c_content.get('$CONS_local')
                if c_content['$TYPE'] == "column_cite":
                    foreign_key_str = ' FOREIGN KEY REFERENCES {real_origin_table}({real_origin_column})'
                    foreign_key_str = foreign_key_str.format(
                        real_origin_table = c_content['$STRU_real_origin_table'],
                        real_origin_column = c_content['$STRU_real_origin_column']
                    )
                    constraints_str += foreign_key_str
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
    
    # Only can be used when initializing, for safety reasons
    def createQuerySQL(self, t_name, filters_list = [], read_auth_role = 'tourist', id = None):
        t_content = self.formated_dict[t_name]
        if t_content['$TYPE'] == 'table' or  t_content['$TYPE'] == 'view' :
            query_str = "SELECT \n{columns_str} \nFROM \n\t{t_name} \n{filters_str}\n;"
            columns_str = ''
            filters_str = ''
            # Generate columns string
            for c_name, c_content in t_content['$COLU'].items():
                if c_content['$AUTH_read'][read_auth_role]:
                    if columns_str == '':
                        columns_str += ('\t'+t_name+'.'+c_name )
                    else :
                        columns_str += (' ,\n\t'+t_name+'.'+c_name )
            # Generate film string
            if id != None:
                # id specified
                filters_str = "WHERE rowid = " + str(id)
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
        t_content = self.formated_dict[t_name]
        if t_content['$TYPE'] == 'table':
            insert_str = "INSERT INTO {t_name}({columns_str}\n) \nVALUES{rows_str}\n;"
            columns_str = ''
            rows_str = ''
            # Generate columns string
            for c_name, c_content in t_content['$COLU'].items():
                if c_content['$AUTH_write'][write_auth_role]:
                    if columns_str == '' :
                        columns_str += ('\n\t'+t_name+'.'+c_name )
                    else :
                        columns_str += (' ,\n\t'+t_name+'.'+c_name )
            # Generate Values Rows Set string
            for key, values_dict in enumerate(values_dicts_list):
                if rows_str == '':
                    row_str = '\n\t({values_str})'
                else:
                    row_str = ',\n\t({values_str})'

                values_str = ''
                for c_name, c_content in t_content['$COLU'].items():
                    if c_content['$AUTH_write'][write_auth_role]:
                        value_str = values_dict.get(c_name) if  values_dict.get(c_name) else ''
                        if values_str == '':
                            values_str += (value_str)
                        else:
                            values_str += (','+value_str)
                rows_str += row_str.format(values_str = values_str)


            insert_str = insert_str.format(t_name = t_name, columns_str = columns_str, rows_str = rows_str)
            return insert_str
        else:
            pass # ![Exception]
        
    # Only can be used when initializing, for safety reasons
    def createDeleteSQL(self,t_name):
        pass
        
    # Only can be used when initializing, for safety reasons
    def createUpdateSQL(self,t_name):
        pass





# Outer Functions
def createQueryFilterDict(left,condition_type,righ):
    if condition_type == 'equal':
        pass
    










    
# Testing
if __name__ == '__main__':

    # For Dumped JSON String
    Dumped_json_str = Business().loadFromPath(sys.argv[1]).getDmpdJsonStr()
    #print('Dumped JSON String: \n',Dumped_json_str)


    # For Creating Table
    Create_sql_str = Business().loadFromPath(sys.argv[1]).createTInitSQL(sys.argv[2])
    print('\nCreate Table SQL String:')
    print(Create_sql_str)

    # For Query
    filters_list = [
        {
            'left':'person_id',
            'type':'=',
            'right':':person_id'
        }
    ]
    Query_sql_str = Business().loadFromPath(sys.argv[1]).createQuerySQL(
        sys.argv[2],
        filters_list = filters_list,
        id = 3
    )
    print('\nQuery SQL String:')
    print(Query_sql_str)
    
    # For Insert
    values_dicts_list =[
        {
            "type":"21",
            "person_role":"34"
        },
        {
            "type":"45",
            "admin_check":"56"
        }
    ]
    Insert_sql_str = Business().loadFromPath(sys.argv[1]).createInsertSQL(
        sys.argv[2],
        values_dicts_list = values_dicts_list,
        write_auth_role = 'admin'
    )
    print('\nInsert SQL String:')
    print(Insert_sql_str)
    

