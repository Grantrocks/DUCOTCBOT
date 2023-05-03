import secrets
max_num=9999
min_num=0
max_mult=81
def play(guess, number, bet):
  if guess=="Higher":
    chance=(((max_num-number)/max_num))*100
    multi=round(max_mult/chance,2)
  elif guess=="Lower":
    chance=(((min_num+number)/max_num))*100
    multi=round(max_mult/chance,2)
    print(chance)
  num=secrets.randbelow(max_num+1)
  
  if guess=="Higher":
    if num>number:
      return {"win":True,"multi":multi,"chance":chance,"number":num}
    else:
      return {"win":False,"chance":chance,"number":num,"multi":multi}
  elif guess=="Lower":
    if num<number:
      return {"win":True,"chance":chance,"multi":multi,"number":num}
    else:
      return {"win":False,"chance":chance,"number":num,"multi":multi}
