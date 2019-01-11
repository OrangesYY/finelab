import csv, json, operator
from data_stru import Business
import sqlite3
import pandas



def make_dicts(cursor, row):
        return dict((cursor.description[idx][0], value)
                for idx, value in enumerate(row)     )

#将表导出为csv文件
def exportTableToCSV(table_name , from_csv_path , target_db_path):
    db_conn=sqlite3.connect(target_db_path)
   
    #转换默认的查询数据类型为字典类型
    db_conn.row_factory = make_dicts
    cur = db_conn.cursor()
    #实例化一个bsnses对象
    bsnses = Business('data/data_stru.json')

    #得到数据库中表的列名
    cur.execute("SELECT * FROM " + table_name)
    table_col_name_list = [ tuple[0] for tuple in cur.description ]
    

    #得到json文件中表的列名
    json_col_name_list = []
    formatted_dict = bsnses.getFomatdDict(table_name)
    for c_name in formatted_dict['$COLU'].keys():
        json_col_name_list.append(c_name)

    #若json文件中表的结构与实际表中的列不符合，则报错终止导出操作
    flag = True
    #表比json文件中结构多出的列为differ_table_col_name_list
    differ_table_col_name_list = list ( set ( table_col_name_list ).difference ( set ( json_col_name_list ) ) )
    if differ_table_col_name_list != [] :
        print("导出的表结构与json文件中的表结构不符！表中有列是json结构中没有的！列名为：")
        print(differ_table_col_name_list)
        flag = False

    #json文件比表多出的列为differ_json_col_name_list
    differ_json_col_name_list = list ( set ( json_col_name_list ).difference ( set ( table_col_name_list ) ) )
    if differ_json_col_name_list != [] :
        print("导出的表结构与json文件中的表结构不符！json结构中有列是表中没有的！列名为：")
        print(differ_json_col_name_list)
        flag = False

    if flag :
        #对数据库进行查询操作，并将查询结果导出
        query_str = bsnses.createQuerySQL(t_name = table_name, filters_list = [])
        query_result = cur.execute(query_str).fetchall()

        with open(from_csv_path, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile,query_result[0].keys())
            writer.writeheader()
            writer.writerows(query_result)
        print("导出操作已成功！")

    else :
        print("导出操作已终止！")

    
        
    cur.close()
    db_conn.close()
    csvfile.close()



def importTableFromCSV(table_name, from_csv_path, target_db_path):
   
    db_conn=sqlite3.connect(target_db_path)
    cur = db_conn.cursor()
    #判断表是否已在数据库中，若有同名的表先将其重命名，再导入表
    i = cur.execute("select count(*) from sqlite_master where type = 'table' and name ='%s'" %table_name)
    
    if i!= 0:
        old_table_name = table_name + "_old"
        cur.execute("alter table " + table_name + " rename to " + old_table_name)
        print("改名成功！")

    
    #cur.execute("drop table if exists " + table_name)

    #实例化一个bsnses对象，创建新表
    bsnses = Business('data/data_stru.json')
    init_str = bsnses.createTInitSQL(t_name = table_name)
    cur.execute(init_str).fetchall()

    #得到csv文件中表的列名
    csv_col_name_list = []
    with open(from_csv_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for i, row in enumerate(reader) :
            if i==1 :
                csv_col_name_list = list(row)
    #print(csv_col_name_list)            

    

    #得到json文件中表的列名
    json_col_name_list = []
    formatted_dict = bsnses.getFomatdDict(table_name)
    for c_name in formatted_dict['$COLU'].keys():
        json_col_name_list.append(c_name)
    #print(json_col_name_list)    

    #若json文件中表的结构与csv文件中的列不符合，则报错并会按照json文件中的结构导出
    flag = True
    #csv文件比json文件中结构多出的列为differ_csv_col_name_list
    differ_csv_col_name_list = list ( set ( csv_col_name_list ).difference ( set ( json_col_name_list ) ) )
    if differ_csv_col_name_list != [] :
        print("导入的csv文件中的表结构与json文件中的表结构不符！csv文件中有列是json结构中没有的！列名为：")
        print(differ_csv_col_name_list)
        flag = False

    #json文件比csv文件多出的列为differ_json_col_name_list
    differ_json_col_name_list = list ( set ( json_col_name_list ).difference ( set ( csv_col_name_list ) ) )
    if differ_json_col_name_list != [] :
        print("导入的csv文件中的表结构与json文件中的表结构不符！json结构中有列是csv文件中表结构没有的！列名为：")
        print(differ_json_col_name_list)
        flag = False

    if flag :
        #将csv文件中的数据写入表中
        result = []
        with open(from_csv_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
            #print(dict(row))
            #result = list(row)
                result.append(row)
        #print(result)
        insert_str = bsnses.createInsertSQL(t_name = table_name, values_dicts_list = result ,\
        write_auth_role = 'admin') 
        cur.execute(insert_str)
        db_conn.commit()
        print("导入操作成功！")
    else :
        print("导入操作失败！")    



    
    csvfile.close()
    cur.close()
    db_conn.close()




if __name__ == '__main__':
    exportTableToCSV('a_test', 'C:\\\\Users\\lenovo\\Desktop\\csvtest.csv', 'data/finelab.sqlite3.db')
    importTableFromCSV('a_test', 'C:\\\\Users\\lenovo\\Desktop\\csvtest.csv', 'data/finelab.sqlite3.db')
    

