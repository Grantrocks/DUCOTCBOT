import discord
import os # default module

import time
import json
import uuid
import requests
import headstails
import rewardsmanager
import payments
import dice
duco_ip="http://51.15.127.80/"


with open("config.json") as f:
  config=json.load(f)

bot = discord.Bot()

@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")

@bot.slash_command(name = "signup", description = "Make an account for the new casino. No info needed.")
async def _signup(ctx):
    if os.path.isfile(f"database/users/{str(ctx.author.id)}.json"):
      await ctx.respond("It seems like you already have an account.")
    else:
      user=config['templates']['new_user']
      user['joined']=time.time()
      user['username']=str(ctx.author).split("#")[0]
      user['id']=str(ctx.author.id)
      user['last_active']=time.time()
      with open(f"database/users/{str(ctx.author.id)}.json","w") as f:
        json.dump(user,f)
      await ctx.respond("Account created. Now go fund it and begin playing! :)", ephemeral=True)
      
@bot.slash_command(name="deposit",description="Start a DUCO deposit.")
async def _deposit(ctx):
  if not os.path.isfile(f"database/users/{str(ctx.author.id)}.json"):
    await ctx.respond("Please make sure to signup using. /signup")
  else:
    with open(f"database/users/{str(ctx.author.id)}.json") as f:
      user=json.load(f)
    user['deposit_code']=str(uuid.uuid4().hex)
    with open(f"database/users/{str(ctx.author.id)}.json","w") as f:
      json.dump(user,f)
    await ctx.respond("""
    Send any amount of DUCO to:
  DucoTruccoServices

  Include the following id in the memo:
  {}
    
    """.format(user['deposit_code']), ephemeral=True)
@bot.slash_command(name="checkdeposit",description="Checks the provided transaction hash and funds you if its valid.")
async def _checkdeposit(ctx,tx_hash: discord.commands.Option(str, "Enter your tx hash", required = True)):
  if os.path.isfile(f"database/users/{str(ctx.author.id)}.json"):
    res=requests.get(duco_ip+"transactions/"+tx_hash).json()
    if not res['success']:
      await ctx.respond("Invalid transaction hash!",ephemeral=True)
    else:
      with open(f"database/users/{str(ctx.author.id)}.json") as f:
        user=json.load(f)
      tx_data=res['result']
      dep_code=user['deposit_code']
      if tx_data['memo']==dep_code and tx_data['recipient']=="DucoTruccoServices":
        user['deposit_code']=""
        user['balance']+=tx_data['amount']
        user['deposited']+=tx_data['amount']
        user['last_active']=time.time()
        user['transaction_history'].append({"type":"deposit","data":tx_data})
        with open(f"database/users/{str(ctx.author.id)}.json","w") as f:
          json.dump(user,f)
        await ctx.respond(f"Successfully deposited ᕲ {tx_data['amount']} to your account.\nBalance: ᕲ {user['balance']}",ephemeral=True)
      else:
        await ctx.respond("The transaction either has the wrong deposit code or the recipient is not DucoTruccoServicesVault.\nIf you beleive this is a mistake please open a ticket.",ephemeral=True)
  else:
    await ctx.respond("Please make sure to signup using. /signup", ephemeral=True)
@bot.slash_command(name="headstails",description="Do you think the coin is heads or tails? Its a 50/50 chance.")
async def _headstails(ctx,amount: discord.commands.Option(int,"Amount of ᕲ to wager",required=True)):
  if os.path.isfile(f"database/users/{str(ctx.author.id)}.json"):
    with open(f"database/users/{str(ctx.author.id)}.json") as f:
      user=json.load(f)
    if user['balance']< amount:
      await ctx.respond(f"Balance to low. Balance: ᕲ {user['balance']}",ephemeral=True)
    else:
      class HeadsTailsView(discord.ui.View): # Create a class called MyView that subclasses discord.ui.View
        @discord.ui.button(label="Heads", style=discord.ButtonStyle.primary, emoji="🔺")
        async def heads_callback(self, button, interaction):
            win=headstails.play(1)
            with open(f"database/users/{str(interaction.user.id)}.json") as f:
              user=json.load(f)
            if win:
              res=rewardsmanager.reward(user['current_game']['amount'],config['game_configs']['headstails']['win_multi'],str(interaction.user.id),"Heads Or Tails",win)
              await interaction.response.send_message(f"The coin landed on heads. You win! Balance: {res['balance']}", ephemeral=True)
            else:
              res=rewardsmanager.reward(user['current_game']['amount'],config['game_configs']['headstails']['win_multi'],str(interaction.user.id),"Heads Or Tails",win)
              await interaction.response.send_message(f"The coin landed on tails. You lose! Balance: {res['balance']}", ephemeral=True) # Send a message when the button is clicked
        @discord.ui.button(label="Tails", style=discord.ButtonStyle.primary, emoji="🔻")
        async def tails_callback(self, button, interaction):
            win=headstails.play(0)
            with open(f"database/users/{str(interaction.user.id)}.json") as f:
              user=json.load(f)
            if win:
              res=rewardsmanager.reward(user['current_game']['amount'],config['game_configs']['headstails']['win_multi'],str(interaction.user.id),"Heads Or Tails",win)
              await interaction.response.send_message(f"The coin landed on tails. You win! Balance: {res['balance']}", ephemeral=True)
            else:
              res=rewardsmanager.reward(user['current_game']['amount'],config['game_configs']['headstails']['win_multi'],str(interaction.user.id),"Heads Or Tails",win)
              await interaction.response.send_message(f"The coin landed on heads. You lose! Balance: {res['balance']}", ephemeral=True)
      user['current_game']={"amount":amount}
      with open(f"database/users/{str(ctx.author.id)}.json","w") as f:
        json.dump(user,f)
      await ctx.respond(f"Wager: {amount}\nWin Multi: {config['game_configs']['headstails']['win_multi']}\nHeads or tails?",view=HeadsTailsView(),ephemeral=True)
  else:
    await ctx.respond("Please make sure to signup using. /signup", ephemeral=True)
@bot.slash_command(name="withdraw",description="Withdraw your ᕲ from the casino.",timeout=120)
async def _withdraw(ctx,amount: discord.commands.Option(int,"Amount of ᕲ to withdraw",required=True)):
  if not os.path.isfile(f"database/users/{str(ctx.author.id)}.json"):
    await ctx.respond("Please make sure to signup using. /signup", ephemeral=True)
  else:
    with open(f"database/users/{str(ctx.author.id)}.json") as f:
      user=json.load(f)
    if user['balance']>=amount:
      if user['deposited']>=10:
        if user['total_wager']>=10:
          if user['duco_account']!="":
            print(requests.get("https://server.duinocoin.com/transactions").text)
            res=requests.get("https://server.duinocoin.com/transaction?username=DucoTruccoServices&password="+"I34x4oh17ctGSQGh3bgw"+"&recipient="+user['duco_account']+"&amount="+str(amount)+"&memo=Heres your payment from the Duco Truco Casino.")
            print(res.status_code)
            response=res.json()
            # not working right
            if response['success']:
              with open(f"database/users/{str(user['id'])}.json","w") as f:
                user['balance']-=amount
                user['withdrawn']+=amount
                user['transaction_history'].append({"type":"withdraw","data":response['result']})
                json.dump(user,f)
              await ctx.respond(response['result'],ephemeral=True)
            else:
              await ctx.respond("Withdrawl failed. Please try again later!",ephemeral=True)
          else:
            await ctx.respond("Please use /link to link your Duino Coin address.")
        else:
          await ctx.respond("You must wager at least 10 Duino Coin before you can withdraw.",ephemeral=True)    
      else:
        await ctx.respond("You must deposit at least 10 Duino Coin before you can withdraw.",ephemeral=True)    
    else:
      await ctx.respond("Amount requested is larger than your balance.",ephemeral=True)
@bot.slash_command(name="link",description="Link your duino coin wallet to the casino.")
async def _link(ctx,address:discord.commands.Option(str,"Your duino coin username",required=True)):
  if not os.path.isfile(f"database/users/{str(ctx.author.id)}.json"):
    await ctx.respond("Please make sure to signup using. /signup", ephemeral=True)
  else:
    with open(f"database/users/{str(ctx.author.id)}.json") as f:
      user=json.load(f)
    if "&amount=" in address:
      with open("database/logs/warns.txt","a") as f:
        f.write(f"{str(ctx.author)} attempted a withdrawl exploit!   -   $amount=   -   {str(ctx.author.id)}")
      await ctx.respond("Potential exploit detected! This has been logged.", ephemeral=True)
    else:
      user['duco_account']=address
      with open(f"database/users/{str(ctx.author.id)}.json","w") as f:
        json.dump(user,f)
      await ctx.respond("Successfully linked your duino coin address.", ephemeral=True)
@bot.slash_command(name="dice",description="Roll some dice and win!")
async def _dice(ctx,wager:discord.commands.Option(int,"Amount of ᕲ to wager",required=True),number:discord.commands.Option(int,"Number 0-9999. Must be less than 80% win chance.",required=True)):
  userfile=f"database/users/{str(ctx.author.id)}.json"
  if os.path.isfile(userfile):
    class DiceView(discord.ui.View):
      @discord.ui.select( # the decorator that lets you specify the properties of the select menu
          placeholder = "Higher or Lower?", # the placeholder text that will be displayed if nothing is selected
          min_values = 1, # the minimum number of values that must be selected by the users
          max_values = 1, # the maximum number of values that can be selected by the users
          options = [ # the list of options from which users can choose, a required field
              discord.SelectOption(
                  label="Higher",
                  description="If the dice roll is higher than your wager, you win!"
              ),
              discord.SelectOption(
                  label="Lower",
                  description="If the dice roll is lower than your wager, you win!"
              )
          ]
      )
      async def select_callback(self, select, interaction): # the function called when the user is done selecting options
          with open(f"database/users/{str(interaction.user.id)}.json") as f:
            user=json.load(f)
          user['current_game']['guess']=select.values[0]
          game=user['current_game']
          res=dice.play(game['guess'],game['number'],game['wager'])
          if round(res['chance'])>80:
            await interaction.response.send_message("Win chance to high!\nSmallest number for Lower: 8000\nSmallest number for Higher: 2000\nWe do this so the casino does not run out of funds and can continue running. Thanks for the understanding :)", ephemeral=True)
          else:
            rew=rewardsmanager.reward(game['wager'],res['multi'],str(interaction.user.id),"Dice",res['win'])
            if res['win']:
              await interaction.response.send_message(f"You won!\nWin Chance: {round(res['chance'],2)}%\nRolled Number: {res['number']}\nYour Stats:\nBalance: {rew['balance']}\nLevel: {rew['level']}\nXP: {rew['xp']}", ephemeral=True)
            else:
              await interaction.response.send_message(f"You Lose!\nWin Chance: {round(res['chance'],2)}%\nRolled Number: {res['number']}\nYour Stats:\nBalance: {rew['balance']}\nLevel: {rew['level']}\nXP: {rew['xp']}", ephemeral=True) # Send a message when the button is clicked
        
    with open(userfile) as f:
      user=json.load(f)
    user['current_game']['wager']=wager
    user['current_game']['number']=number
    with open(userfile,"w") as f:
      json.dump(user,f)
    higher_win=round((((9999-number)/9999))*100,2)
    lower_win=round((((0+number)/9999))*100,2)
    higher_multi=round(81/higher_win,2)
    lower_multi=round(81/lower_win,2)
    await ctx.respond(f"The smaller the gap of winning, the more you win!\nMake sure win chance is under 80%.\nChance of Higher Win: {higher_win}% ~ x{higher_multi}\nChance of Lower Win: {lower_win} ~ x{lower_multi}",view=DiceView(), ephemeral=True)
  else:
    await ctx.respond("Please make sure to signup using /signup.", ephemeral=True)    
@bot.slash_command(name="help",description="Need some help?")
async def _help(ctx):
  ctx.respond("Hello there!")
bot.run("MTAzNDU5NjgzMzgwNjI1ODI5Nw.GEGMQu.SHahk3IAKfc0X8x8ReJmTrXxD0kfJD9D7I02R4") # run the bot with the token
