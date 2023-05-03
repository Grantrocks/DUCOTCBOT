import secrets
def play(guess):
  possible=[0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1]
  num=possible[secrets.randbelow((len(possible)))]
  if guess==num:
    return True
  elif guess!=num:
    return False
