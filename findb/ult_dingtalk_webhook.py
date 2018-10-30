
import requests
import json

webhook_addr = "https://oapi.dingtalk.com/robot/send?access_token=d2f224fdb78c28fc64d52ec770d7557b90e292a105b67d88da89cbdd40adc60b"

json_dict =  {
      "msgtype": "text",
      "text": {
          "content": "Stupid enough. 22"
      }
 }

r = requests.post(webhook_addr , json=json_dict)