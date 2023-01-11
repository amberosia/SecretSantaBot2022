import discord
import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials 
import asyncio
import random
from keep_alive import keep_alive

scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(os.getenv("SERVICE CREDS")), scope)
client = gspread.authorize(creds)
sheet = client.open("Amber's Secret Santa 2022").worksheet("Gift Reveal")

participants = sheet.row_count - 1
AMBER_ID = 607544531042304010
GIFTER_ID_COL = 4
GIFTEE_ID_COL = 7
PARTNER_COL = 8
ARTWORK_COL = 10
GALLERY_ID = 1031026351391645767

intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)


@client.event
async def on_ready():
  print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
  if message.author == client.user:
    return
  
  #bot recieves dm
  if isinstance(message.channel, discord.DMChannel):

    #amber sends testids command
    if message.content.startswith(">testids") and message.author.id == AMBER_ID:
      msg = ""
      for i in range(participants):
        rowNum = i+2
        
        gifterID = int(sheet.cell(rowNum, GIFTER_ID_COL).value)
        gifter = client.get_user(gifterID)

        if gifter == None:
          amber = client.get_user(AMBER_ID)
          msg = msg + str(rowNum) + " " + str(gifterID) + "\n"
        else:
          amber = client.get_user(AMBER_ID)
          msg = msg + str(rowNum) + " <@" + str(gifterID) + ">\n"

        #avoid quota limit
        if (i + 1) % 30 == 0:
          amber = client.get_user(AMBER_ID)
          await amber.send(msg)
          msg = ""
          await asyncio.sleep(60)
        else:
          sentAll = False

      if not sentAll:
        amber = client.get_user(AMBER_ID)
        await amber.send(msg)

        
    #amber sends sendpartners command
    if message.content.startswith(">sendpartners") and message.author.id == AMBER_ID:
      for i in range(participants):
        rowNum = i+2
        
        #avoid quota limit
        if (i + 1) % 30 == 0:
          await asyncio.sleep(60)
          
        gifterID = int(sheet.cell(rowNum, GIFTER_ID_COL).value)
        gifteeID = int(sheet.cell(rowNum, GIFTEE_ID_COL).value)
  
        gifter = client.get_user(gifterID)
        giftee = client.get_user(gifteeID)
        
        try:
          if gifter == None:
            amber = client.get_user(AMBER_ID)
            await amber.send(str(rowNum) + " Gifter " + str(gifterID) + " not in server")
          elif giftee == None:
            amber = client.get_user(AMBER_ID)
            await amber.send(str(rowNum) + " Giftee " + str(gifteeID) + " not in server")
          else:
            await gifter.send("Hey <@" + str(gifterID) + ">! \n\nYour giftee for Amber's Secret Santa 2022 is " + giftee.name + "#" + giftee.discriminator + "! Don't tell anyone who your giftee is, it's a surprise! To find your giftee's wishlist, search 'in: wishlists from: " + giftee.name + "#" + giftee.discriminator + "' in the server! \n\nPlease dm a sketch of your artwork to your group leader by **December 14th**! Let your group leader know if you need an extension! \n\nWhenever you're ready to submit your finished artwork, dm '>submit' to this bot and attach your file(s) to the message! Please let your group leader know when you've submitted so that we can double check your submission. To change your submission, send the '>submit' command again and attach your updated file(s), this will replace all previous files. The final artwork deadline is **December 23rd**! \n\nHave fun! :D")
            sheet.update_cell(rowNum, PARTNER_COL, "sent")
        except:
          amber = client.get_user(AMBER_ID)
          await amber.send(str(rowNum) + " Unknown error sending giftee " + str(gifteeID) + " to gifter " + str(gifterID))
  
    
    #anyone sends submit command
    if message.content.startswith(">submit"):
      correctFileTypes = True
      senderID = message.author.id

      try:
        if message.attachments:
          allFiles = ""
          confirmMsg = ""
          fileCount = 0
          
          senderCell = sheet.find(str(senderID), in_row = None, in_column = GIFTER_ID_COL)
          
          if senderCell:
            senderRow = senderCell.row
            
            for i in range(len(message.attachments)):
              attachment = message.attachments[i]
              if attachment.content_type in ('image/jpeg', 'image/gif', 'image/png', 'image/heic', 'video/mp4'):
                file = attachment.url
                allFiles = allFiles + file + " "
                fileCount += 1
                confirmMsg = confirmMsg + ":white_check_mark: File " + str(i+1) + " received: " + file + "\n\n"
              else:
                correctFileTypes = False
                confirmMsg = confirmMsg + ":x: Error: File " + str(i+1) + " is not a jpeg, png, gif, heic or mp4 file!\n\n"
  
            await message.channel.send(confirmMsg)
            
            if correctFileTypes:
              try:
                sheet.update_cell(senderRow, ARTWORK_COL, allFiles)
                await message.channel.send(str(fileCount) + " file(s) submitted successfully!")
              except:
                await message.channel.send("Failed to add artwork to database. Please dm amber ASAP!")
            else:
              await message.channel.send("Submission failed. Please double check your file formats and try again!")
                
          else:
            await message.channel.send("No user found. Please dm amber ASAP!")
        else:
          await message.channel.send("No file detected. Please attach your file(s) to your '>submit' message!")
      except:
        await message.channel.send("Unknown error. Please dm amber ASAP!")

        
    #amber sends testsubmit command
    '''if message.content.startswith(">testsubmit") and message.author.id == AMBER_ID:
      confirmMsg = "gottem"
      fileCount = 1
      
      for i in range(participants):
        senderID = i

        try:
          file = "https://cdn.discordapp.com/attachments/1041724795357773957/1045794420781490326/anya_-_angry.png"
          senderCell = sheet.find(str(senderID), in_row = None, in_column = GIFTER_ID_COL)
            
          if senderCell:
            senderRow = senderCell.row
            
            await message.channel.send(confirmMsg)
              
            try:
              sheet.update_cell(senderRow, ARTWORK_COL, file)
              await message.channel.send(str(fileCount) + " file(s) submitted!")
            except:
              await message.channel.send("Failed to submit artwork. Please dm amber!")         
          else:
            await message.channel.send("No user found. Please dm amber!")
        except:
          await message.channel.send("Unknown error. Please dm amber ASAP!")'''

        
    #amber sends serversendart command
    if message.content.startswith(">serversendart") and message.author.id == AMBER_ID:
      allPuns = ["Hold on for deer life, this artwork for @ will blow you away!", "This artwork for @ will make you fall in love at frost sight!", "This artwork for @ is snow amazing!", "This artwork for @ is looking tree-mendous!", "This gift for @ sleighs!", "This artwork for @ is the best thing since sliced (ginger)bread!", "This gorgeous gift for @ graces us with its presents!", "It’s rien-ning gorgeous artwork! This one’s for @!", "Tree-t your eyes to this amazing artwork for @!", "This gift for @ is be-yule-tiful!", "You have no i-deer how dazzling this artwork for @ is!", "This amazing gift for @ will leave you feeling santa-mental!", "This pine art for @ will spruce things up!", "This gift for @ is snow joke!", "This jolly artwork for @ will leave a fa-la-la-la-lasting impression!"]
      
      for i in range(participants):
        rowNum = i+2
        
        #avoid quota limit
        if (i + 1) % 30 == 0:
          await asyncio.sleep(60)
          
        gifteeID = int(sheet.cell(rowNum, GIFTEE_ID_COL).value)
        giftee = client.get_user(gifteeID)
        links = sheet.cell(rowNum, ARTWORK_COL).value

        try:
          if links == None:
            amber = client.get_user(AMBER_ID)
            await amber.send(str(rowNum) + " Giftee <@" + str(gifteeID) + "> no links")
          else:
            pun = random.choice(allPuns)
            allPuns.remove(pun)
            pun = pun.replace("@", "<@" + str(gifteeID) + ">")
            
            galleryChannel = client.get_channel(GALLERY_ID)
            await galleryChannel.send(pun + " " + links)

            if len(allPuns) == 0:
              allPuns = ["Hold on for deer life, this artwork for @ will blow you away!", "This artwork for @ will make you fall in love at frost sight!", "This artwork for @ is snow amazing!", "This artwork for @ is looking tree-mendous!", "This gift for @ sleighs!", "This artwork for @ is the best thing since sliced (ginger)bread!", "This gorgeous gift for @ graces us with its presents!", "It’s rien-ning gorgeous artwork! This one’s for @!", "Tree-t your eyes to this amazing artwork for @!", "This gift for @ is be-yule-tiful!", "You have no i-deer how dazzling this artwork for @ is!", "This amazing gift for @ will leave you feeling santa-mental!", "This pine art for @ will spruce things up!", "This gift for @ is snow joke!", "This jolly artwork for @ will leave a fa-la-la-la-lasting impression!"]
        except:
          amber = client.get_user(AMBER_ID)
          await amber.send(str(rowNum) + "Unknown error for giftee " + str(gifteeID))

          
    #amber sends dmsendart command
    '''if message.content.startswith(">dmsendart") and message.author.id == AMBER_ID:
      for i in range(participants):
        rowNum = i+2
        
        #avoid quota limit
        if (i + 1) % 30 == 0:
          await asyncio.sleep(60)
          
        gifteeID = int(sheet.cell(rowNum, GIFTEE_ID_COL).value)
        giftee = client.get_user(gifteeID)
        links = sheet.cell(rowNum, ARTWORK_COL).value

        try:
          if giftee == None:
            amber = client.get_user(AMBER_ID)
            await amber.send(str(rowNum) + " Giftee " + str(gifteeID) + " not in server")
          elif links == None:
            amber = client.get_user(AMBER_ID)
            await amber.send(str(rowNum) + " Giftee <@" + str(gifteeID) + "> no links")
          else:
            await giftee.send("Hey <@" + str(gifteeID) + ">! Here's the gift you recieved for Amber's Secret Santa 2022! " + links + "\n\nHead over to the #gift-gallery channel in the server to take a look at all the gifts from this event (including what you gifted)! You can also try to guess who your gifter was in the #gifter-guessing channel, the first person to guess correctly will be awarded their own emote in my main discord server, amber's jam jar: <https://discord.gg/hcgwvwApXR>, and everyone who guesses correctly will receive a special role! You have 5 guesses!")
        except:
          amber = client.get_user(AMBER_ID)
          await amber.send(str(rowNum) + " Unknown error for giftee " + str(gifteeID))'''

    if message.content.startswith(">editmsg") and message.author.id == AMBER_ID:
      channel = client.get_channel(GALLERY_ID)
      message = await channel.fetch_message(1056436525002403894)
      await message.edit(content="These artworks for <@1044953902065406003> are the best thing since sliced (ginger)bread! https://cdn.discordapp.com/attachments/1056215594644553779/1056602058272292974/ADBDC920-1386-4DC2-B16A-36855DFBE5D6.jpg https://cdn.discordapp.com/attachments/914323249884708965/1056436177206525952/Untitled_Artwork.png (there were a few complications with your gift, so you got 2!)")


keep_alive()
try:
  client.run(os.getenv("TOKEN"))
except:
  os.system("kill 1")
