import json
import secrets
import time
xp_h=100
xp_l=10
level_up_multi=2.5
min_req_xp=250
def reward(amount,multi,userid,game,win):
  with open(f"database/users/{userid}.json") as f:
    user=json.load(f)
  user['games_played']+=1
  user['balance']-=amount
  if win:
    user['games_won']+=1
    total_result=float(amount)*float(multi)
    user['total_gain']+=total_result-amount
    user['balance']+=total_result
  else:
    user['total_loss']+=amount
  user['total_wager']+=amount
  user['xp']+=secrets.randbelow(xp_h-xp_l)+xp_h
  if user["xp"]>=(level_up_multi*(min_req_xp+user['level'])):
    user["xp"]=0
    user['level']+=1
  user['game_history'].append({"game":game,"won":win,"wager":amount})
  user['current_game']={}
  user['last_active']=time.time()
  with open(f"database/users/{userid}.json","w") as f:
    json.dump(user,f)
  return user