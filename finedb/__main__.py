from .data_stru import Business
import sys, os


# Outer Functions
def createQueryFilterDict(left, condition_type, righ):
    if condition_type == "equal":
        pass


# Testing
if __name__ == "__main__":

    # For Dumped JSON String
    Dumped_json_str = Business(sys.argv[1]).getDmpdJsonStr()
    print("Dumped JSON String:")
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
