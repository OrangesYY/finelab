import os, json, copy


class DataFrame:
    raw_dict = {}
    formatted_dict = {}

    def __init__(self, arg=None):
        # Code for testing paths
        # print("__file__=%s" % __file__)
        # print("os.path.realpath(__file__)=%s" % os.path.realpath(__file__))
        # print("os.path.dirname(os.path.realpath(__file__))=%s" % os.path.dirname(os.path.realpath(__file__)))
        # print("os.path.split(os.path.realpath(__file__))=%s" % os.path.split(os.path.realpath(__file__))[0])
        # print("os.path.abspath(__file__)=%s" % os.path.abspath(__file__))
        # print("os.getcwd()=%s" % os.getcwd())
        # print("sys.path[0]=%s" % sys.path[0])
        # print("sys.argv[0]=%s" % sys.argv[0])
        if type(arg) == dict:
            self.raw_dict = arg
            self.format_bussiness()

        elif type(arg) == str:
            # Open root json for read
            root_json_path = arg
            fpr = open(root_json_path, "r")
            # Load dict from root json file
            root_json_dict = json.load(fpr)
            fpr.close()

            # Initiate self.raw_dict
            self.raw_dict = dict()
            for _key in root_json_dict:
                # Get root json directory firstly
                root_json_dir = os.path.dirname(os.path.realpath(arg)).replace(
                    "\\", "/"
                )
                # Open the splited json file
                fpr = open(
                    root_json_dir + "/" + root_json_dict[_key], "r", encoding="utf-8"
                )
                tmpDict = json.load(fpr)
                # Merge dicts
                self.raw_dict[_key] = tmpDict
                fpr.close()
            self.format_bussiness()
        else:
            raise Exception

    def format_bussiness(self):
        
        self.formatted_dict = copy.deepcopy(self.raw_dict)
        
        for t_name, t_stru in self.raw_dict.items():
            self.formatted_dict[t_name]["$SFLD"] = []
            for c_name in t_stru["$COLU"]:

                c_stru = t_stru["$COLU"][c_name]
                # Find origin
                if c_stru["$TYPE"] == "column_cite":

                    # Get Origin
                    origin_t_name = c_stru["$STRU_origin_table"]
                    origin_c_name = c_stru["$STRU_origin_column"]

                    # Temporary storage of Citing dict
                    temp_c_dict = copy.deepcopy(c_stru)
                    self.formatted_dict[t_name]["$COLU"][c_name].update(
                        copy.deepcopy(
                            self.formatted_dict[origin_t_name]["$COLU"][origin_c_name]
                        )
                    )
                    if (
                        self.formatted_dict[t_name]["$COLU"][c_name]["$TYPE"]
                        == "column_cite"
                    ):
                        raise Exception
                    # Attention!
                    # If citing sections has re-defined the parameters,
                    #     the final param is subject to the parameters defined in the citing section,
                    #     not the cited section.
                    # If you do not want to change a parameters defined in the cited section,
                    #     please do NOT include this paramrter in your citing section in JSON.
                    self.formatted_dict[t_name]["$COLU"][c_name].update(
                        temp_c_dict
                    )  # So the parameters defined in the citing section can flush the cited params.
                elif c_stru["$TYPE"] == "cite_display": # Virtual column, cite other columns.
                    # Display only
                    # Cite a column from another table, but will not appear in current table.
                    pass
                else:  # If this column is not citing other columns
                    
                    if self.formatted_dict[t_name]["$COLU"][c_name].get("$ISPK") == True :  # is Primary Key
                        self.formatted_dict[t_name]["$PMKY"] = c_name                       # Primary Key of a table
                    
                    if self.formatted_dict[t_name]["$COLU"][c_name].get("$ISNM") == True :  # is major diaplay name (of a row)
                        self.formatted_dict[t_name]["$DNCL"] = c_name                       # Diaplay name column
                    
                    
                    if self.formatted_dict[t_name]["$COLU"][c_name].get("$ISSF") == True :  # is in search field (of a row)
                        self.formatted_dict[t_name]["$SFLD"].append(c_name)                 # Search Field

                # Copy column name inside the column dict for easier access
                self.formatted_dict[t_name]["$COLU"][c_name]["$CLNM"] = c_name
            # Copy table name inside the table dict for easier access
            self.formatted_dict[t_name]["$TBNM"] = t_name
        return self.formatted_dict

    def getFomatdDict(self, t_name=None):
        if t_name:
            return self.formatted_dict[t_name]
        else:
            return self.formatted_dict

    def getDmpdJsonStr(self):
        return json.dumps(self.formatted_dict, indent=4)

    # Table Init
    def createTInitSQL(self, t_name):
        t_stru = self.formatted_dict[t_name]
        if t_stru["$TYPE"] == "table":
            init_str = "CREATE TABLE {t_name} (\n{columns_str}\n)\n;"
            columns_str = ""

            for c_name, c_stru in t_stru["$COLU"].items():
                column_str = "{data_type_str}{constraints_str}"
                data_type_str = ""
                constraints_str = ""

                if c_stru["$TYPE"] == "column_cite":
                    foreign_key_str = " FOREIGN KEY REFERENCES {real_origin_table}({real_origin_column})"
                    foreign_key_str = foreign_key_str.format(
                        real_origin_table=c_stru["$STRU_real_origin_table"],
                        real_origin_column=c_stru["$STRU_real_origin_column"],
                    )
                    constraints_str += foreign_key_str
                if c_stru.get("$ISPK") == True:  # Is primary key
                    if c_stru["$TYPE"] == "column_cite":
                        raise Exception
                    else:
                        primary_key_str = " PRIMARY KEY"
                        constraints_str += primary_key_str
                column_str = column_str.format(
                    data_type_str=data_type_str, constraints_str=constraints_str
                )

                # ADD Column to columns str
                if columns_str == "":
                    columns_str += "\t" + c_name + column_str
                else:
                    columns_str += ",\n\t" + c_name + column_str
            init_str = init_str.format(t_name=t_name, columns_str=columns_str)
            return init_str
        else:
            pass  # ![Exception]

    # View Init
    def createVInitSQL(self, v_name):
        pass

    # Only can be used when initializing, for safety reasons (SQL INJECT)
    def createQuerySQL(
        self, t_name, filters_list=[], read_auth_role="tourist", id=None
    ):
        if read_auth_role is None:
            read_auth_role = "tourist"
        t_stru = self.formatted_dict[t_name]
        if t_stru["$TYPE"] == "table" or t_stru["$TYPE"] == "view":
            query_str = "SELECT \n{columns_str} \nFROM \n\t{t_name} \n{filters_str}\n;"
            columns_str = ""
            filters_str = ""
            # Generate columns string
            for c_name, c_stru in t_stru["$COLU"].items():
                if c_stru["$AUTH_read"][read_auth_role]:
                    if columns_str == "":
                        columns_str += "\t" + t_name + "." + c_name
                    else:
                        columns_str += " ,\n\t" + t_name + "." + c_name
            # Generate filter string
            if id != None:
                # id specified
                filters_str = "WHERE " + t_stru["$PMKY"] + " = " + str(id)
            else:
                # id not specified
                for filter in filters_list:
                    if filters_list != None:
                        if filters_str == "":
                            filters_str += (
                                "WHERE\n\t"
                                + t_name + "."+ filter["left"] + ' '
                                + filter["type"] + ' '
                                + '\''+ filter["right"]+ '\''
                            )
                        else:
                            filters_str += (
                                "\n\tOR "
                                + t_name + "."+ filter["left"] + ' '
                                + filter["type"] + ' '
                                + '\''+ filter["right"]+ '\''
                            )
            query_str = query_str.format(
                t_name=t_name, columns_str=columns_str, filters_str=filters_str
            )
            return query_str
        else:
            pass  # ![Exception]

    # Only can be used when initializing, for safety reasons
    def createInsertSQL(self, t_name, values_dicts_list, write_auth_role="tourist"):
        if write_auth_role is None:
            write_auth_role = "tourist"
        t_stru = self.formatted_dict[t_name]
        if t_stru["$TYPE"] == "table":
            insert_str = "INSERT INTO {t_name}({columns_str}\n) \nVALUES{rows_str}\n;"
            columns_str = ""
            rows_str = ""
            # Generate columns string
            for c_name, c_stru in t_stru["$COLU"].items():
                if c_stru["$AUTH_write"][write_auth_role]:
                    if columns_str == "":
                        columns_str += "\n\t" + c_name
                    else:
                        columns_str += " ,\n\t" + c_name
            # Generate Values Rows Set string
            for key, values_dict in enumerate(values_dicts_list):
                if rows_str == "":
                    row_str = "\n\t({values_str})"
                else:
                    row_str = ",\n\t({values_str})"

                values_str = ""
                for c_name, c_stru in t_stru["$COLU"].items():
                    if c_stru["$AUTH_write"][write_auth_role]:
                        value_str = (
                            values_dict.get(c_name) if values_dict.get(c_name) else ""
                        )
                        if values_str == "":
                            values_str += '"' + value_str + '"'
                        else:
                            values_str += "," + '"' + value_str + '"'
                rows_str += row_str.format(values_str=values_str)

            insert_str = insert_str.format(
                t_name=t_name, columns_str=columns_str, rows_str=rows_str
            )
            return insert_str
        else:
            pass  # ![Exception]

    # Only can be used when initializing, for safety reasons
    def createDeleteSQL(
        self, t_name, filters_list=[], write_auth_role="tourist", id=None
    ):
        t_stru = self.formatted_dict[t_name]
        if t_stru["$TYPE"] == "table":
            delete_str = "DELETE FROM {t_name} \n {filters_str}\n;"

            # Generate filter string
            if id != None:
                # id specified
                filters_str = "WHERE " + t_stru["$PMKY"] + " = " + str(id)
            else:
                # id not specified
                for filter in filters_list:
                    if filters_list != None:
                        if filters_str == "":
                            filters_str += (
                                "WHERE\n\t"
                                + filter["left"]
                                + filter["type"]
                                + filter["right"]
                            )
                        else:
                            filters_str += (
                                ",\n\tAND "
                                + filter["left"]
                                + filter["type"]
                                + filter["right"]
                            )
            delete_str = delete_str.format(t_name=t_name, filters_str=filters_str)
            return delete_str
        else:
            pass  # ![Exception]

    # Only can be used when initializing, for safety reasons
    def createUpdateSQL(
        self, t_name, values_dict, filters_list=[], write_auth_role="tourist", id=None
    ):
        t_stru = self.formatted_dict[t_name]
        if t_stru["$TYPE"] == "table":
            update_str = "UPDATE {t_name} SET\n {values_str} \n{filters_str}\n;"
            values_str = ""
            filters_str = ""
            # Generate values string
            for key, val in values_dict.items():
                c_stru = t_stru["$COLU"][key]
                if c_stru["$AUTH_write"][write_auth_role]:
                    if values_str == "":
                        values_str += "\t" + key + "=" + '"' + val + '"'
                    else:
                        values_str += " ,\n\t" + key + "=" + '"' + val + '"'

            # Generate filter string
            if id != None:
                # id specified
                filters_str = "WHERE " + t_stru["$PMKY"] + " = " + str(id)
            else:
                # id not specified
                for filter in filters_list:
                    if filters_list != None:
                        if filters_str == "":
                            filters_str += (
                                "WHERE\n\t"
                                + filter["left"]
                                + filter["type"]
                                + filter["right"]
                            )
                        else:
                            filters_str += (
                                ",\n\tAND "
                                + filter["left"]
                                + filter["type"]
                                + filter["right"]
                            )
            update_str = update_str.format(
                t_name=t_name, values_str=values_str, filters_str=filters_str
            )
            return update_str
        else:
            pass  # ![Exception]


