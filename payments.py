import requests
import json
import os
import time
def withdraw(user,amount):
  res=requests.get("http://51.15.127.80/transaction?username=DucoTruccoServices&password="+os.environ['casino_acc_pw']+"&recipient="+user['duco_account']+"&amount="+str(amount)+"&memo=Heres your payment from the Duco Truco Casino.")
  time.sleep(5)
  response=json.loads(res.text)
  with open(f"database/users/{str(user['id'])}.json","w") as f:
    user['balance']-=amount
    user['withdrawn']+=amount
    user['transaction_history'].append({"type":"withdraw","data":response['result']})
    json.dump(user,f)
  return res.json()
