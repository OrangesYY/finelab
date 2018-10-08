import json
import sys
import _io
 
class Business:
    row_dict = {}
    formated_dict = {}
    def __init__(self,arg = None):
        if type(arg) == dict:
            self.row_dict=arg
            self.format_bussiness()
        elif type(arg) == _io.TextIOWrapper:
            self.row_dict = json.load(arg)
            self.format_bussiness()
        elif type(arg) == str:
            self.row_dict = json.loads(arg)
            self.format_bussiness()
    def format_bussiness(self,_dict=None):
        if _dict == None:
            #print('no')
            dict_tmp = self.row_dict.copy()
            origin_dict = self.row_dict
        else:
            #print('have')
            dict_tmp = _dict.copy()
            origin_dict = _dict
        for key, val in origin_dict.items():
            #print('typeval,',type(val))
            if type(val) == dict:
                #print('in')
                dict_tmp[key] = self.format_bussiness(val)
                for sub_key, sub_val in dict_tmp[key].items():
                    if sub_key == '$KYNM_bsns':
                        dict_tmp['$$BUK_'+sub_val] = dict_tmp[key]
                    elif sub_key == '$KYNM_indb':
                        dict_tmp['$$DBK_'+sub_val] = dict_tmp[key]
        if _dict == None:
            self.formated_dict = dict_tmp
            return self.formated_dict
        else:
            return dict_tmp
    def loadFromPath(self,f_path):
        f= open(f_path, 'r',encoding='utf-8')
        self.__init__(f)
        f.close()
        return self
    def getFomatdDict(self):
        return self.formated_dict
    def getDmpdJsonStr(self):
        return json.dumps(self.formated_dict,indent=4)


if __name__ == '__main__':

    #f= open(sys.argv[1], 'r')
    Dumped_json_str = Business().loadFromPath(sys.argv[1]).getDmpdJsonStr()
    print(Dumped_json_str)
