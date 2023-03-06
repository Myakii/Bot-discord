import discord
from discord.ext import commands
from discord_buttons_plugin import *
import nest_asyncio
nest_asyncio.apply()
import time
from datetime import datetime
import asyncio
import random
import youtube_dl
import math
import requests
import json

bot = commands.Bot(command_prefix='!', case_insensitive=True, intents=discord.Intents.all())
buttons = ButtonsClient(bot) 
bot.remove_command('help')
bot.point = 0
bot.POINTSMAX = 10
bot.jeu = False
bot.is_score = False
bot.salle1, bot.salle2, bot.salle3, bot.salle4, bot.salle5 = False, False, False, False, False
bot.salle1_indice1, bot.salle1_indice2, bot.salle1_indice3 = False, False, False
bot.magic_ball = ["N'y compte pas.", "Désolé, non.", "Oui, définitivement.", "Ça en a pas l'air.", "Je ne pense pas.", "C'est flou, réesayer.", "Mes sources me disent non.", "Les perspectives ne sont pas très bonnes.", "Je me concentre, redemandez-moi à nouveau", "Mieux vaut ne pas vous le dire maintenant.", "Absolument pas.", "Oui !", "C'est certain.", "Tous les signes indiquent que oui.", "Comme je le vois, oui.", "Redemande plus tard.", "Ma réponse est non.", "La perspective semble bonne.", "Impossible de prédire pour l'instant.", "Le plus probable.", "Très incertain.",]
bot.liste_couleurs = [0xffffff,0x878787, 0x543535, 0x000000, 0x520b3f,0xfc5bb4,0xb80093,0xff8a8a,0xb50000,0xff0000,0xff9c5e,0xf8ffba,0xffff00, 0xd1ff75, 0x8affa7,0x00b524,0x195263,0x00c7a9,0x75b8ff,0x014791,0x192e63,0x333aff,0x000287,0x56029c,0x7a75ff, 0xba75ffB]
bot.gagnant = ""
bot.point_morpion = 0
bot.guessthenumbertime = 0
bot.QCMscore = 0
bot.VFscore = 0
bot.shifumiscore = 0

# music
ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {'options': '-vn'}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = ""

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            data = data['entries'][0] # take first item from a playlist
        filename = data['title'] if stream else ytdl.prepare_filename(data)
        return filename

@bot.command(name='join', help='Pour dire au bot de rejoindre le vocal')
async def join(ctx):
    if not ctx.message.author.voice:
        embed=discord.Embed(description=f"{ctx.message.author.name} n'est pas connecté à un salon vocal.", color=0xfcba03)
        embed.set_author(name=bot.user.name, icon_url=bot.user.avatar)
        await ctx.reply(embed=embed)
        return
    else:
        channel = ctx.message.author.voice.channel
    await channel.connect()
    embed=discord.Embed(description=f"{bot.user.name} a rejoint le salon vocal !", color=0xfcba03)
    embed.set_author(name=bot.user.name, icon_url=bot.user.avatar)
    await ctx.reply(embed=embed)

@bot.command(name='leave', help='Pour que le bot quitte le salon vocal')
async def leave(ctx):
    voice_client = ctx.message.guild.voice_client
    # if voice_client.is_connected():
    if voice_client != None:
        await voice_client.disconnect()        
        embed=discord.Embed(description=f"{bot.user.name} s'est déconnecté du salon vocal.", color=0xfcba03)
        embed.set_author(name=bot.user.name, icon_url=bot.user.avatar)
        await ctx.reply(embed=embed)
    else:
        embed=discord.Embed(description=f"{bot.user.name} n'est pas connecté à un salon vocal.", color=0xfcba03)
        embed.set_author(name=bot.user.name, icon_url=bot.user.avatar)
        await ctx.reply(embed=embed)

@bot.command(name='play', help='Pour jouer une musique')
async def play(ctx, url):
    try :
      server = ctx.message.guild
      voice_channel = server.voice_client

      async with ctx.typing():
        filename = await YTDLSource.from_url(url, loop=bot.loop)
        voice_channel.play(discord.FFmpegPCMAudio(source=filename))
        nom_musique = filename.split('.')[0] # pour récupéré le titre sans l'extension
        video_id = nom_musique[-11:] # pour recuperer l'ID de la vidéo youtube
        nom_musique = nom_musique[:-12] # pour afficher le titre de la vidéo sans l'ID de la vidéo
        nom_musique = nom_musique.replace("_", " ")

        # recupère la miniature de la vidéo
        thumb = 'https://i.ytimg.com/vi/' + video_id + '/hqdefault.jpg?sqp=-oaymwEcCOADEI4CSFXyq4qpAw4IARUAAIhCGAFwAcABBg==&rs=AOn4CLD5uL4xKN-IUfez6KIW_j5y70mlig'
      embed=discord.Embed(title="Joue actuellement", description=f"[{nom_musique}]({url})", color=0xfcba03)
      embed.set_author(name=bot.user.name, icon_url=bot.user.avatar)
      embed.set_thumbnail(url=f'{thumb}')    
      embed.set_footer(text=f"Requête de {ctx.message.author.name}", icon_url=ctx.message.author.avatar)
      await ctx.send(embed=embed)
    except:
      embed=discord.Embed(description=f"{ctx.message.author.name} n'est pas connecté à un salon vocal.", color=0xfcba03)
      embed.set_author(name=bot.user.name, icon_url=bot.user.avatar)
      await ctx.reply(embed=embed)

@bot.command(name='pause', help='Pour mettre la musique en pause')
async def pause(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await voice_client.pause()        
        embed=discord.Embed(description=f"{ctx.message.author.name} a mis en pause la musique.", color=0xfcba03)
        embed.set_author(name=bot.user.name, icon_url=bot.user.avatar)
        await ctx.reply(embed=embed)
    else:
        embed=discord.Embed(description=f"{bot.user.name} ne joue pas de musique pour le moment.", color=0xfcba03)
        embed.set_author(name=bot.user.name, icon_url=bot.user.avatar)
        await ctx.reply(embed=embed)

@bot.command(name='resume', help='Reprend la musique')
async def resume(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_paused():
        await voice_client.resume()      
        embed=discord.Embed(description=f"{ctx.message.author.name} a relancer la musique.", color=0xfcba03)
        embed.set_author(name=bot.user.name, icon_url=bot.user.avatar)
        await ctx.reply(embed=embed)
    else:
        embed=discord.Embed(description=f"{bot.user.name} n'était pas entrain de jouer de la musique ou n'était pas en pause. Utiliser la commande `!play`.", color=0xfcba03)
        embed.set_author(name=bot.user.name, icon_url=bot.user.avatar)
        await ctx.reply(embed=embed)
    
@bot.command(name='stop', help='Arrête la musique')
async def stop(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await voice_client.stop()
    else:
        embed=discord.Embed(description=f"{bot.user.name} ne joue pas de musique pour le moment.", color=0xfcba03)
        embed.set_author(name=bot.user.name, icon_url=bot.user.avatar)
        await ctx.reply(embed=embed)
# fin music

@bot.event
async def on_ready():
    channel = bot.get_channel(id_channel) 
    print("Le bot est prêt !")
    embed=discord.Embed(title="✨ Bienvenue dans le Monde des étoiles ! ✨", description="Cher aventurier, vous vous trouvez actuellement dans le Monde des étoiles, n'hésitez pas à utiliser \"!help\" sur votre téléphone pour demander mon aide.",color=0xfcba03)
    embed.set_image(url='https://media.tenor.com/Ar0TxNJSFSgAAAAC/line.gif')
    embed.set_footer(text='Taper !help pour voir les commandes.')
    await channel.send(embed=embed)

@bot.command(name='magicball', aliases=['8ball', 'mb'], help='Pour prédire l\'avenir et répondre à n\'importe quelle de vos questions')
async def magicball(ctx):
  couleur = random.choice(bot.liste_couleurs)
  con = ctx.message.content.lower().split(" ") # on coupe le message de l'utilisateur
  
  # si il y a que la commande dans le message, il n'y a pas de phrase donc on renvoit une erreur
  if len(con) < 2:
    embed=discord.Embed(description=f'🎱 | Mettez une question avec la commande !', color=couleur)
    embed.set_author(name=bot.user.name, icon_url=bot.user.avatar)
    await ctx.send(embed=embed)
    return

  message = random.choice(bot.magic_ball)
  embed=discord.Embed(description=f'🎱 | {message}', color=couleur)
  embed.set_author(name=bot.user.name, icon_url=bot.user.avatar)
  await ctx.send(embed=embed)

@bot.command(name='gtn', aliases=['guessthenumber'], help='Deviner à quel nombre pense le bot')
async def gtn(ctx):

  start_time = time.time()
  number = random.randint(0, 100)
  guess = -1

  embed=discord.Embed(color=0x014791)
  embed.set_author(name=bot.user.name, icon_url=bot.user.avatar)
  embed.add_field(name= "Guess the number", value=f'Devinez un nombre entre 0 et 100 !', inline=False)
  await ctx.send(embed=embed)
  
  while number != guess:
      response = await bot.wait_for('message')
      answer = str(response.content)
      # print(response.content)
      if answer.isdigit():
        guess = int(response.content)
        if guess < 0 or guess > 100:
          embed=discord.Embed(color=0xc70d00)
          embed.set_author(name=bot.user.name, icon_url=bot.user.avatar)
          embed.add_field(name= "Guess the number", value="Mettez un nombre qui soit compris entre 0 et 100 !", inline=False)
          await ctx.send(embed=embed)
        elif guess > number:
          embed=discord.Embed(color=0xc70d00)
          embed.set_author(name=bot.user.name, icon_url=bot.user.avatar)
          embed.add_field(name= "Guess the number", value="Plus petit ! Réesayer !", inline=False)
          await ctx.send(embed=embed)
        elif guess < number:
          embed=discord.Embed(color=0xc70d00)
          embed.set_author(name=bot.user.name, icon_url=bot.user.avatar)
          embed.add_field(name= "Guess the number", value="Plus grand ! Réesayer !", inline=False)
          await ctx.send(embed=embed)
      else:
          embed=discord.Embed(color=0xc70d00)
          embed.set_author(name=bot.user.name, icon_url=bot.user.avatar)
          embed.add_field(name= "Guess the number", value="Ce n'est pas un nombre ! Mettez un nombre qui soit compris entre 0 et 100 !", inline=False)
          await ctx.send(embed=embed)

  embed=discord.Embed(color=0x01911e)
  embed.set_author(name=bot.user.name, icon_url=bot.user.avatar)
  bot.guessthenumbertime = (time.time() - start_time)
  embed.add_field(name= "Guess the number", value=f'Bravo, le nombre était bien {number}.\nCela vous a pris {math.floor(bot.guessthenumbertime//60)} min {math.floor(bot.guessthenumbertime%60)} sec pour trouver le nombre.', inline=False)
  await ctx.send(embed=embed)

@bot.command()
async def help(ctx) :
    help=discord.Embed(color=0xfcba03)
    help.set_author(name=bot.user.name, icon_url=bot.user.avatar)
    help.add_field(name= "Commandes", value="Si vous souhaitez débuter votre aventure dans le Monde des Etoiles, utilisez la commande `!start`, je vous y attends !\n\n- `!avatar` : pour afficher votre avatar en grand\n- `!cat` `!chat` : J'ai une belle galerie de chat à vous montrer, voulez-vous les voir ?\n- `!dog` `!chien` : J'ai pu me documenter sur les chiens récemment, voulez-vous les voir ?\n- `!greet` : pour me dire bonjour !\n- `!gtn` `!guessthenumber` : pour deviner le chiffre !\n- `!indice` : pour avoir des indices durant le jeu !\n- `!invite` : n'hésitez pas à me proposer à vos amis avec la commande\n- `!magicball votre question` `8ball votre question` `mb votre question`: si vous avez des questions sur votre avenir\n- `!morpion` `!tictactoe` `!ttt` `!mp` : pour jouer au tic tac toe contre moi !", inline=False)
    help.set_image(url='https://media.tenor.com/Ar0TxNJSFSgAAAAC/line.gif')
    

    help2=discord.Embed(color=0xfcba03)
    help2.set_author(name=bot.user.name, icon_url=bot.user.avatar)
    help2.add_field(name= "suite des commandes", value="- `!poll \"votre question\"` Vous avez besoin de l'avis d'autre utilisateur\n- `!qcm` : si vous avez envie de jouer !\n- `!slap <mention d'une personne>` `!s <mention d'une personne>`: si vous avez une envie de frapper quelqu'un\n- `!tag` `!spam` `!t` `!sp` : pour spammer les gens !\n- `!shifumi` `!sfm` `!pfc` `!pierrefeuilleciseaux` : pour jouer au pierre-feuille-ciseaux contre moi !\n- `!vf` : si vous voulez jouer au vrai ou faux !\n- `!weather \"nom de ville\"` `!w \"nom de ville\"` `!meteo \"nom de ville\"` `!m \"nom de ville\"` : pour avoir la météo en temps réel !\n\nJe peux vous faire écouter plein de choses, demande-moi avec  :\n\n- `!join` : pour m'appeler, j'ai besoin d'un peu de préparation !\n- `!play URLyoutube`  : pour jouer le lien\n- `!pause` : pour mettre en pause la vidéo actuelle\n- `!resume` : pour reprendre la musique\n- `!skip` : pour changer de lien youtube\n- `!stop` : pour m'arrêter\n- `!leave`: pour me déconnecter\n", inline=False)    
    help2.set_image(url='https://media.tenor.com/Ar0TxNJSFSgAAAAC/line.gif')
  
    await ctx.send(embed=help)
    await ctx.send(embed=help2)

@bot.command()
async def avatar(ctx) :
    author = ctx.message.author
    avatar=discord.Embed(color=0xfcba03)
    avatar.set_author(name=bot.user.name, icon_url=bot.user.avatar)
    avatar.set_image(url=author.avatar)
    await ctx.send(embed=avatar)

@bot.command()
async def invite(ctx):
    author = ctx.message.author
    embed = discord.Embed(title = f"Inviter {bot.user.name}",
    color=0xff0000,
    description = f"Tu peux inviter le bot sur ton serveur en cliquant [ici](https://discord.com/api/oauth2/authorize?client_id={bot.user.id}&permissions=8&scope=bot).")
    embed.set_footer(text=f"Requête de {ctx.message.author.name}", icon_url=ctx.message.author.avatar)
    await ctx.send(embed=embed)
    await buttons.send(
          content = None,
          embed = embed,
          channel = ctx.channel.id,
          components = [
              ActionRow([
                Button(
                      style = ButtonType().Link,
                      label = "Invite",
                      url = f"https://discord.com/api/oauth2/authorize?client_id={bot.user.id}&permissions=8&scope=bot"
                ) # fin button
            ]) # action row
        ] # component
    ) # buttons.send


@bot.command()
async def greet(ctx):
    await ctx.send("Say hello!")

    def check(m):
        return m.content == "hello" and m.channel == ctx.message.channel

    msg = await bot.wait_for("message", check=check)
    await ctx.send(f"Hello {msg.author.mention} !")

def indices_used(ind1, ind2, ind3) :
  malus = 0
  if not ind1 :
    malus -= 0.3
  if not ind2 :
    malus -= 0.5
  if not ind3 :
    malus -= 1
  return malus

class enigme_embed() :
  def __init__(self, numero_question, enigme, footer, image):
    super().__init__()
    self.numero_question = numero_question
    self.enigme = enigme
    self.footer = footer
    self.image = image
    self.embed = discord.Embed(title=f"✨ {numero_question} ✨",color=0x5990e0)
    self.embed.add_field(name=f"\u200b", value=f"{self.enigme}", inline=False)
    self.embed.set_image(url=self.image)
    self.embed.set_footer(text=f"{self.footer}")

  def to_dict(self):
      return self.embed.to_dict()

bot.n_enigme = -1

@bot.command(name='start')
async def start(ctx) : 
  with open("/data/enigmes.json", 'r', encoding='utf-8') as f:
    data = json.loads(f.read())
  questions = data["enigmes"]

  def check_author(m):
    return m.author == ctx.message.author and m.channel == ctx.message.channel

  async def get_response(ctx, response) :
    msg = await bot.wait_for("message", check=check_author)

    while response not in msg.content.lower() :
        if msg.content == '!indice' or msg.content == '!join' or msg.content == '!score' or msg.content.startswith("!play"):
          pass
        else :
          embed = discord.Embed(description="Mauvaise réponse", color=0x1F2023)
          await ctx.send(embed=embed)
        msg = await bot.wait_for("message", check=check_author)

  bot.jeu = True
  bot.is_score = True

  embed = discord.Embed(title=f"✨ Salle inconnue ✨", description="*Vous vous réveillez dans une pièce sombre éclairée grâce aux rayons de la lune.*", color=0x5990e0)
  embed.set_image(url='https://i.pinimg.com/originals/78/f9/fc/78f9fc8c8c7ac8dc27b6197ed6496df3.jpg')
  await ctx.send(embed=embed)
  await asyncio.sleep(2)

  for i in range(5) :
    embed = enigme_embed(questions[i]["id"], questions[i]["value"], questions[i]["footer"], questions[i]["image"])
    await ctx.send(embed=embed)

    # booleens a true pour que y a les indices selons les salles
    if (i+1) == 1 :
      bot.salle1 = True
      bot.salle_indice1, bot.salle_indice2, bot.salle_indice3 = True, True, True
      bot.n_enigme += 1
    elif (i+1) == 2 :
      bot.salle2 = True
      bot.salle_indice1, bot.salle_indice2, bot.salle_indice3 = True, True, True
      bot.n_enigme += 1
    elif (i+1) == 3 :
      bot.salle3 = True
      bot.salle_indice1, bot.salle_indice2, bot.salle_indice3 = True, True, True
      bot.n_enigme += 1
    elif (i+1) == 4 :
      bot.salle4 = True
      bot.salle_indice1, bot.salle_indice2, bot.salle_indice3 = True, True, True
      bot.n_enigme += 1
    elif (i+1) == 5 :
      bot.salle5 = True
      bot.salle_indice1, bot.salle_indice2, bot.salle_indice3 = True, True, True
      bot.n_enigme += 1

    await get_response(ctx, questions[i]["solution"])

    if (i+1) == 1 :
      bot.salle1 = False
    elif (i+1) == 2 :
      # salle couloir
      bot.salle2 = False

      # jeu morpion
      await asyncio.sleep(2)
      embed = discord.Embed(title=f"✨ Véranda ✨", description="*Vous ouvrez timidement la porte et une bouffée d'air frais vous chatouille le visage. \nVous respirez un grand coup mais soudainement le téléphone vibre et vous ramène sur Terre.\n\nDevant vous se trouve une table entourée de verdure et la notification que vous venez de recevoir contient cette phrase.*", color=0x5990e0)
      embed.set_image(url='https://www.zupimages.net/up/22/49/06v8.png')
      await ctx.send(embed=embed)
      await asyncio.sleep(2)

      ctx.command = bot.get_command("morpion")
      await bot.invoke(ctx)
      while bot.point_morpion < 1 :
        if bot.gagnant == "Joueur" :
          bot.point_morpion +=1
        embed = discord.Embed(title=f"✨ Véranda ✨", description="Vous devez gagner pour passer à la salle suivante.", color=0x1F2023)
        await ctx.send(embed=embed)
        await bot.invoke(ctx)

    elif (i+1) == 3 :
      # salle trois portes
      bot.salle3 = False

    elif (i+1) == 4 :
      # salle des signes
      bot.salle4 = False
      await asyncio.sleep(2)

      # jeu guess the number
      embed = discord.Embed(title=f"✨ Salle mystère ✨", description="*Après avoir entrer la réponse dans votre téléphone, vous entendez une alarme retentir. La lumière de la pièce est devenue rouge.\n\nLe téléphone vous montre une carte avec un chemin à suivre. Vous suivez l'itinéraire et arrivé dans la pièce, vous trouvez un coffre avec un décompte. Elle affiche 30 secondes.\nEn vous approchant, vous remarquez un pavé numérique et on vous demande de trouver le bon nombre avant le temps écoulé.*", color=0x1F2023)
      embed.set_image(url='https://img.gamewith.net/article/thumbnail/rectangle/17725.png')
      await ctx.send(embed=embed)
      await asyncio.sleep(8)

      ctx.command = bot.get_command("gtn")
      await bot.invoke(ctx)
      while bot.guessthenumbertime > 30 :
        embed = discord.Embed(title=f"✨ Salle mystère ✨", description="Vous devez gagner en moins de 30 secondes pour passer à la salle suivante.", color=0x1F2023)
        await ctx.send(embed=embed)
        await bot.invoke(ctx)

      # jeu meteo
      embed = discord.Embed(title=f"✨ Salle des saisons ✨", description="*En sortant de la salle, un étrange événement se produit.\nTout le couloir du manoir se trouve inondé par la pluie mais aucune fissure semble apparaitre au plafond. Vous refermez la porte de la salle dans laquelle vous étiez et en l'ouvrant de nouveau, la pluie s'est changé en neige et des flocons se mirent à tomber. Vous décidez tout de même d'avancer dans le couloir mais la porte qui vous relie à la salle Pisces est désormais fermée.\nLe téléphone vous envoie une notification.*", color=0x1F2023)
      embed.set_image(url='https://zupimages.net/up/22/49/y5zr.png')
      embed.set_footer(text=f"N'oubliez pas les applications sur le téléphone.")
      await ctx.send(embed=embed)
      await asyncio.sleep(2)

      async def get_response_meteo(ctx, response) :
        msg = await bot.wait_for("message", check=check_author)

        while response not in msg.content.lower() :
            if msg.content.startswith("!w") or msg.content.startswith("!weather") or msg.content.startswith("!meteo") or msg.content.startswith("!m") or msg.content == '!score':
              pass
            else :
              await ctx.send("Mauvaise réponse ! Format : HH:MM")
            msg = await bot.wait_for("message", check=check_author)


      url_weather = 'https://api.openweathermap.org/data/2.5/weather?q=montreuil&lang=fr&units=metric&appid=e9f3750ffd4e3ac5ecd6061cc1bbd2fc'
      response = requests.get(url_weather)

      if response.status_code == 200:
        data = response.json()
        sys = data['sys']
        timezone = data['timezone']
        couche = sys['sunset'] + timezone
        h_couche = datetime.fromtimestamp(couche).strftime('%H:%M')

        await get_response_meteo(ctx, h_couche)

      # # QCM
      embed = discord.Embed(title=f"✨ Salle astrologie ✨", description="*La température semble enfin revenir à la normale dans les pièces. Vous commencez à moins trembler de froid.\n\nVous ouvrez la porte et curieusement, vous vous trouvez dans une salle baignée par les étoiles avec un télescope au centre. Sur le plafond se trouve plusieurs questions.*", color=0x1F2023)
      embed.set_image(url='https://i.pinimg.com/564x/99/ea/b7/99eab71412a93ffca167b73a114e535e.jpg')
      await ctx.send(embed=embed)
      await asyncio.sleep(8)

      ctx.command = bot.get_command("qcm")
      await bot.invoke(ctx)
      while bot.QCMscore < 3 :
        embed = discord.Embed(title=f"✨ Salle astrologie ✨", description="Vous devez avoir au moins un score de 3/5 pour passer à la salle suivante.", color=0x1F2023)
        await ctx.send(embed=embed)
        await asyncio.sleep(2)
        await bot.invoke(ctx)

      # vrai ou faux
      embed = discord.Embed(title=f"✨ Premier sous-sol ✨", description="*Après avoir répondu aux cinq questions, le télescope se mit à bouger et libère une trappe avec un escalier sous-terrain. Vous vous y aventurez avec crainte, la trappe se referme derrière vous et plusieurs torches s'allument devant vous.\nChaque chemin a un vide béant ainsi que deux piliers pour avancer, l'un est marqué d'un 'V' et l'autre d'un 'F', vous vous y approchez pour voir la profondeur du trou et une notification apparait sur votre téléphone.*", color=0x1F2023)
      embed.set_image(url='https://i.pinimg.com/564x/a5/b2/25/a5b2252a55b3cd54eec0c7ecacc5e140.jpg')
      await ctx.send(embed=embed)
      await asyncio.sleep(8)

      ctx.command = bot.get_command("vf")
      await bot.invoke(ctx)
      while bot.VFscore < 3 :
        embed = discord.Embed(title=f"✨ Salle astrologie ✨", description="Vous devez avoir au moins un score de 3/5 pour passer à la salle suivante.", color=0x1F2023)
        await ctx.send(embed=embed)
        await asyncio.sleep(2)
        await bot.invoke(ctx)

      # chien
      embed = discord.Embed(title=f"✨ Deuxième sous-sol ✨", description="*Vous vous essuyez le front. Vous venez de terminer le parcours et à peine les deux pieds au sol, que des yeux rouges apparaissent dans la pénombre. Ils avancent petit à petit vers vous.\n\nDeux choix s'offrent à vous, avancer vers les yeux rouges ou reculer et tomber dans le ravin... Après quelques secondes de réflexion, vous recevez de nouveau une notification sur le téléphone...*", color=0x1F2023)
      embed.set_image(url='https://zupimages.net/up/22/49/zdy7.png ')
      embed.set_footer(text=f"N'oubliez pas les applications sur le téléphone.")
      await ctx.send(embed=embed)
      await asyncio.sleep(2)

      async def get_response_chien(ctx) :
        msg = await bot.wait_for("message", check=check_author)
        response = ["staff", "american staffordshire terrier", "staffordshire terrier americain"]
        while msg.content.lower() not in response:
            if msg.content.startswith("!dog") or msg.content.startswith("!chien") or msg.content == '!score':
              pass
            else :
              await ctx.send("Mauvaise réponse ! Format : nom de la race")
            msg = await bot.wait_for("message", check=check_author)

      await get_response_chien(ctx)


    elif (i+1) == 5 :
      #salle pisces
      bot.salle5 = False

    malus = indices_used(bot.salle_indice1, bot.salle_indice2, bot.salle_indice3)
    bot.point += 2 + malus

    bonne_reponse=discord.Embed(title=f"Bonne réponse {ctx.author.name} !", 
    description=f"Vous avez {round(bot.point, 2)} points !", color=0x0b9e30)
    await ctx.send(embed=bonne_reponse)
    await asyncio.sleep(1.5)


  #shifumi
  embed = discord.Embed(title=f"✨ Jardin ✨", description="*Félicitations ! La porte en pierre s'ouvre et une bouffée d'air envahi vos poumons, vous êtes libre ! Enfin... Presque.\n\nDevant vous se trouve un chemin qui vous mène vers un portail. Il semble entrouvert mais quelque chose vous dérange...\n\nLe téléphone s'est éteint et le manoir derrière vous semble figé. Vous avancez avec prudence et soudainement vous entendez un bruit métallique dans les buissons à côté de vous. Vous vous figez et un robot en sort. Son visage amical vous soulage mais il se mis d'une seconde à l'autre à vous defier au pierre-feuille-ciseaux (shifumi).*", color=0x1F2023)
  embed.set_image(url='https://i.pinimg.com/564x/0c/a2/09/0ca2090b6d62a7d34de09b527f620974.jpg')
  await ctx.send(embed=embed)
  await asyncio.sleep(8)

  ctx.command = bot.get_command("shifumi")
  await bot.invoke(ctx)
  while bot.shifumiscore  < 3 :
    if bot.shifumiscore == 0 :
      embed = discord.Embed(title=f"✨ Salle astrologie ✨", description="Vous devez gagner trois fois pour passer à la salle suivante.", color=0x1F2023)
    elif bot.shifumiscore == 1 :
      embed = discord.Embed(title=f"✨ Salle astrologie ✨", description="Vous gagner encore deux fois pour passer à la salle suivante.", color=0x1F2023)
    elif bot.shifumiscore == 2 :
      embed = discord.Embed(title=f"✨ Salle astrologie ✨", description="Vous gagner encore une fois pour passer à la salle suivante.", color=0x1F2023)
    await ctx.send(embed=embed)
    await asyncio.sleep(2)
    await bot.invoke(ctx)

  #fin
  embed = discord.Embed(title=f"✨ Chambre ✨", description="*Après ce combat acharné, le robot est H-S. Vous vous dirigez vers le portail et en le touchant, vous entendez un son strident et répétitif qui vous semble familier...\n\nFélicitations, vous vous réveillez dans votre lit. Tout ceci était juste un rêve... enfin... en l'espérant...*", color=0x1F2023)
  embed.set_image(url='https://i.pinimg.com/564x/61/98/56/6198568fece95a8742bb94836224acfc.jpg')
  await ctx.send(embed=embed)

  await asyncio.sleep(1.5)

  # affichage du score a la fin du quiz
  bonne_reponse=discord.Embed(title=f"Félicitations {ctx.author.name}, vous avez terminé le quiz !", 
  description=f"Vous avez au total {round(bot.point, 2)} / {bot.POINTSMAX} points !", color=0x0b9e30)
  await ctx.send(embed=bonne_reponse)

  # reset des variables pour le prochain lancement du jeu
  bot.point = 0
  bot.jeu = True
  bot.is_score = False
  bot.salle1, bot.salle2, bot.salle3, bot.salle4, bot.salle5 = True, True, True, True, True
  bot.salle_indice1, bot.salle_indice2, bot.salle_indice3 = True, True, True
  bot.point_morpion = 0
  bot.shifumiscore = 0


@bot.command(name='indice')
async def indice(ctx) :
  with open("/data/enigmes.json", 'r', encoding='utf-8') as f:
    data = json.loads(f.read())
  questions = data["enigmes"]

  if bot.jeu :
    if bot.salle1 or bot.salle2 or bot.salle3 or bot.salle4 or bot.salle5 :
      if bot.salle_indice1 :
        salle_indice=discord.Embed(title=f"{questions[bot.n_enigme]['id']} - Indice 1", description = f"{questions[bot.n_enigme]['indice1']}" ,color=0xfcba03)
        salle_indice.set_footer(text='Vous perdez 0.3 points sur la question.')
        await ctx.send(embed=salle_indice)
        bot.salle_indice1 = False
      elif bot.salle_indice2 :
        salle_indice=discord.Embed(title=f"{questions[bot.n_enigme]['id']} - Indice 2", description = f"{questions[bot.n_enigme]['indice2']}" ,color=0xfcba03)
        salle_indice.set_footer(text='Vous perdez 0.5 points sur la question.')
        await ctx.send(embed=salle_indice)
        bot.salle_indice2 = False
      elif bot.salle_indice3 :
        salle_indice=discord.Embed(title=f"{questions[bot.n_enigme]['id']} - Indice 3", description = f"{questions[bot.n_enigme]['indice3']}" ,color=0xfcba03)
        salle_indice.set_footer(text='Vous perdez 1 point sur la question.')
        await ctx.send(embed=salle_indice)
        bot.salle_indice3 = False
      else : 
        no=discord.Embed(description="Vous avez déjà eu tous les indices disponibles pour cette salle.", color=0xfcba03)
        await ctx.send(embed=no)
  else:
    embed=discord.Embed(description=f"Vous devez lancer le quiz en faisant la commande `!start` pour obtenir des indices sur le jeu!",
    color=0x0b9e30)
    await ctx.send(embed=embed)

@bot.command(name='score', help='Pour afficher le score durant le quiz', category='jeu')
async def score(ctx):
  if bot.is_score :
    embed=discord.Embed(title=f"Score de {ctx.message.author.name}", description=f"Vous avez {round(bot.point, 2)} points !",
    color=0x0b9e30)
    await ctx.send(embed=embed)
  else:
    embed=discord.Embed(description=f"Vous devez lancer le quiz en faisant la commande `!start` pour voir votre score !",
    color=0x0b9e30)
    await ctx.send(embed=embed)


# morpion

GAGNE = "Gagné"
PERDU = "Perdu"

JOUEUR = "Joueur"
JOUEUR_IA = "IA"

def is_combinaisons(l):
# Verifie si il y a une combinaison de symbol horizontalement, verticalement ou en diagonale, sinon renvoie false

    # horizontal
    if (l[0] == l[1] and l[1] == l[2]):
        if l[1] == '⬜' :
            return False
        return True
    elif (l[3] == l[4] and l[4] == l[5]):
        if l[4] == '⬜' :
            return False
        return True
    elif (l[6] == l[7] and l[7] == l[8]):
        if l[7] == '⬜' :
            return False
        return True

    # colonnes
    elif (l[0] == l[3] and l[3] == l[6]):
        if l[3] == '⬜' :
            return False
        return True
    elif (l[1] == l[4] and l[4] == l[7]):
        if l[4] == '⬜' :
            return False
        return True
    elif (l[2] == l[5] and l[5] == l[8]):
        if l[5] == '⬜' :
            return False
        return True

    # diagonales
    elif (l[0] == l[4] and l[4] == l[8]):
        if l[4] == '⬜' :
            return False
        return True
    elif (l[2] == l[4] and l[4] == l[6]):
        if l[4] == '⬜' :
            return False
        return True
    # pas de combinaison
    else :
        False

def tour_de_jeu(tour):
# Change le tour du joueur si le tour actuel est l'IA, le tour suivant sera au JOUEUR et inversemen
    if tour == JOUEUR :
        tour = JOUEUR_IA
    else:
        tour = JOUEUR
    return tour

@bot.command(name = 'morpion', aliases = ['tictactoe', 'ttt', 'mp'])
async def morpion(ctx):
    bot.gagnant = ""
    async def affiche_morpion(ctx, l) :
      embed=discord.Embed(title="Morpion", description=f"Grille :\n\n| {l[0]} | {l[1]} | {l[2]} |\n\n| {l[3]} | {l[4]} | {l[5]} |\n\n| {l[6]} | {l[7]} | {l[8]} |" ,color=0xff7700)
      embed.set_author(name=bot.user.name, icon_url=bot.user.avatar)
      await ctx.send(embed=embed)

    joueur_1 = ctx.message.author.name
    joueur_2 = bot.user.name

    embed=discord.Embed(title="Morpion", description=f"Bienvenue sur le jeu du morpion!\n\n{joueur_1} aura les [ ❌ ].\n\n{joueur_2} aura les [ ⭕ ]." ,color=0xc70d00)
    embed.set_author(name=bot.user.name, icon_url=bot.user.avatar)
    await ctx.send(embed=embed)

    await asyncio.sleep(1)

    liste_joueurs = [JOUEUR, JOUEUR_IA]
    user = random.choice(liste_joueurs)
    l = ["⬜"] * 9

    await affiche_morpion(ctx, l)

    await asyncio.sleep(1)

    i = 0
    while i < len(l) :
        if user == JOUEUR :
            embed=discord.Embed(title=f"Morpion - Tour {i+1}" ,color=0x0449bf)
            embed.set_author(name=bot.user.name, icon_url=bot.user.avatar)
            embed.add_field(name=f"Tour", value=f"{joueur_1} ( symbole [ ❌ ] )")
            embed.set_footer(text="Vous pouvez placer un symbole en appuyant sur [ 1 ] à [ 9 ].")  
            await ctx.send(embed=embed)
            response = await bot.wait_for('message')
            answer = str(response.content)
            while not answer.isdigit():
              embed=discord.Embed(color=0x0449bf)
              embed.set_author(name=bot.user.name, icon_url=bot.user.avatar)
              embed.add_field(name= "Morpion", value="Ce n'est pas un nombre ! Mettez un nombre qui soit compris entre [1] et [9] !", inline=False)
              await ctx.send(embed=embed)  
              response = await bot.wait_for('message')
              answer = str(response.content)     

            symbole = int(response.content)
            symbole -=1

        else :
            embed=discord.Embed(title=f"Morpion - Tour {i+1}" ,color=0xc70d00)
            embed.set_author(name=bot.user.name, icon_url=bot.user.avatar)
            symbole = random.randint(1,9)
            symbole -=1

        while (symbole < 0 or symbole > 8) or ((symbole > 0 or symbole < 8) and l[symbole] != "⬜"):
          if user == JOUEUR :
            if symbole < 0 or symbole > 8 :
                embed=discord.Embed(color=0x0449bf)
                embed.set_author(name=bot.user.name, icon_url=bot.user.avatar)
                embed.add_field(name= "Morpion", value="La case n'est pas valide, choissisez une case entre [1] et [9]!", inline=False)
                await ctx.send(embed=embed)
            elif l[symbole] != "⬜" :
                embed=discord.Embed(color=0x0449bf)
                embed.set_author(name=bot.user.name, icon_url=bot.user.avatar)
                embed.add_field(name= "Morpion", value="La case est déjà occupé par un symbole, choissisez une case libre !", inline=False)
                await ctx.send(embed=embed)
            response = await bot.wait_for('message')
            answer = str(response.content)
            while not answer.isdigit():
              embed=discord.Embed(color=0x0449bf)
              embed.set_author(name=bot.user.name, icon_url=bot.user.avatar)
              embed.add_field(name= "Morpion", value="Ce n'est pas un nombre ! Mettez un nombre qui soit compris entre [1] et [9] !", inline=False)
              await ctx.send(embed=embed)  
              response = await bot.wait_for('message')
              answer = str(response.content)     
                  
            symbole = int(response.content)
            symbole -=1
          else :
            symbole = random.randint(1,9)
            embed=discord.Embed(color=0xc70d00)
            embed.set_author(name=bot.user.name, icon_url=bot.user.avatar)
            # print(symbole, "deja pris !!")
            symbole -= 1

        if l[symbole] == "⬜" :
            if user == JOUEUR :
                l[symbole] = "❌"
            else :
                embed.add_field(name= "Morpion", value=f"{joueur_2} choisit la case {symbole+1}.", inline=False)
                await ctx.send(embed=embed)
                l[symbole] = "⭕"
        
        await asyncio.sleep(1)
        await affiche_morpion(ctx, l)
        await asyncio.sleep(1)

        if is_combinaisons(l) :
            if user == JOUEUR :
                bot.gagnant = "Joueur"
                embed=discord.Embed(title="Morpion - Fin du jeu", description=f"{joueur_1} a gagné !",color=0x0449bf)
                bot.point_morpion += 1
                embed.set_author(name=bot.user.name, icon_url=bot.user.avatar)
                await ctx.send(embed=embed)
            else :
                bot.gagnant = "IA"
                embed=discord.Embed(title="Morpion - Fin du jeu", description=f"{joueur_2} a gagné !",color=0xc70d00)
                embed.set_author(name=bot.user.name, icon_url=bot.user.avatar)
                await ctx.send(embed=embed)
            break
        else:
            i += 1
            
        user = tour_de_jeu(user)

    if not is_combinaisons(l) :
      embed=discord.Embed(title="Morpion - Fin du jeu", description=f"Egalité !",color=0x04bf0a)
      bot.gagnant = "aucun"
      embed.set_author(name=bot.user.name, icon_url=bot.user.avatar)
      await ctx.send(embed=embed)


@bot.command(name="tag", aliases=['spam', 't', 'sp'])
async def tag(ctx):
  liste_textes = ["Coucou", "Enchanté(e)", "Salut", "Bonjour", "Bonsoir", "Yo", "Hello", "Es-tu là,", "Répond", "Eh oh, t'es là"]
  cons = ctx.message.content.lower().split(" ")
  if (len(cons) < 3 or len(cons) > 3) or not ctx.message.mentions :
    embed=discord.Embed(description=f'Mettez une commande valide !\n !tag <nombre de répétitions> <mention de l\'utilisateur>', color=0x1F2023)
    embed.set_author(name=bot.user.name, icon_url=bot.user.avatar)
    await ctx.send(embed=embed)
    return
  elif not (str(cons[1])).isdigit() :
    embed=discord.Embed(description=f'Mettez une commande valide !\n !tag <nombre de répétitions> <mention de l\'utilisateur>', color=0x1F2023)
    embed.set_author(name=bot.user.name, icon_url=bot.user.avatar)
    await ctx.send(embed=embed)
    return
  else :
    nb_repet = int(cons[1])
    if nb_repet > 25 :
      embed=discord.Embed(description=f'Evitez de trop spammer !\n<nombre de répétitions> inférieur ou égal à 25 !', color=0x1F2023)
      embed.set_author(name=bot.user.name, icon_url=bot.user.avatar)
      await ctx.send(embed=embed)
      return
    for i in range(nb_repet):
      texte = random.choice(liste_textes)
      await ctx.send(f"{texte} {cons[2]} !!")

@bot.command(name="shifumi", aliases=["sfm", "pfc", "pierrefeuilleciseaux"])
async def shifumi(ctx):
  embed=discord.Embed(title="Règlement",color=0xfff6df)
  embed.add_field(name= "Comment jouer", value= "Vous jouez contre le bot, vous devez écrire votre choix.\nLa plus forte des formes l’emporte et le joueur marque le point gagnant.\n Si les deux joueurs utilisent la même forme c’est un match nul.\nLe jeu se déroulera en une manche gagnante.", inline = False)
  embed.add_field(name= "Les différentes formes", value= "La pierre écrase les ciseaux et gagne.\nLa feuille enveloppe la pierre et gagne.\nLes ciseaux découpent la feuille et gagnent.\n\n", inline = False)
  await ctx.send(embed=embed)

  j1 = ctx.message.author.name
  ia = bot.user.name

  await asyncio.sleep(1)

  embed=discord.Embed(title="La partie commence !",color=0xfff6df)
  embed.add_field(name= "Ecrivez votre choix", value= "Pierre, feuille ou ciseaux ?", inline = False)
  await ctx.send(embed=embed)
  def check_author(m):
    return m.author == ctx.message.author and m.channel == ctx.message.channel  
    
  async def get_response(ctx):
    msg = await bot.wait_for("message", check=check_author) 

    while msg.content.lower() != "pierre" and msg.content.lower() != "feuille" and msg.content.lower() != "ciseaux":
      embed=discord.Embed(description="Je ne comprends pas votre choix, veuillez choisir entre pierre, feuille ou ciseaux.",color=0xfff6df)
      await ctx.send(embed=embed)
      msg = await bot.wait_for("message", check=check_author) 
    if msg.content.lower() == "pierre":
      embed=discord.Embed(description=f"{ctx.message.author.name} a choisi : pierre ✊ .",color=0xfff6df)
      await ctx.send(embed=embed)
    elif msg.content.lower() == "feuille":
      embed=discord.Embed(description=f"{ctx.message.author.name} a choisi : feuille 🤚 .",color=0xfff6df)
      await ctx.send(embed=embed)
    elif msg.content.lower() == "ciseaux":
      embed=discord.Embed(description=f"{ctx.message.author.name} a choisi : ciseaux ✌️ .",color=0xfff6df)
      await ctx.send(embed=embed)
    return msg.content
  choix_j1 = await get_response(ctx)

  async def choice(ctx):
    shifumi = ["pierre", "feuille", "ciseaux"]
    choix_ia = random.choice(shifumi)
    if choix_ia == "pierre":
      embed=discord.Embed(description=f"{bot.user.name} a pris : pierre ✊ .",color=0xfff6df)
      await ctx.send(embed=embed)
    elif choix_ia == "feuille":
      embed=discord.Embed(description=f"{bot.user.name} a pris : feuille 🤚 .",color=0xfff6df)
      await ctx.send(embed=embed)
    elif choix_ia == "ciseaux":
      embed=discord.Embed(description=f"{bot.user.name} a pris : ciseaux ✌️ .",color=0xfff6df)
      await ctx.send(embed=embed)
    return choix_ia
  choix_ia = await choice(ctx)

  async def combinaison_shifumi(ctx,choix_ia,choix_j1):

    if choix_j1 == "pierre" and choix_ia == "feuille":
      embed=discord.Embed(title=f"{bot.user.name} a gagné la partie !",color=0x990000)
      await ctx.send(embed=embed)

    elif choix_j1 == "pierre" and choix_ia == "ciseaux":
      embed=discord.Embed(title=f"{ctx.message.author.name} a gagné la partie !",color=0x009933)
      await ctx.send(embed=embed)
      bot.shifumiscore += 1

    elif choix_j1 == "feuille" and choix_ia == "ciseaux":
      embed=discord.Embed(title=f"{bot.user.name} a gagné la partie !",color=0x990000)
      await ctx.send(embed=embed)

    elif choix_j1 == "feuille" and choix_ia == "pierre":
      embed=discord.Embed(title=f"{ctx.message.author.name} a gagné la partie !",color=0x009933)
      await ctx.send(embed=embed)
      bot.shifumiscore += 1

    elif choix_j1 == "ciseaux" and choix_ia == "pierre":
      embed=discord.Embed(title=f"{bot.user.name} a gagné la partie !",color=0x990000)
      await ctx.send(embed=embed)

    elif choix_j1 == "ciseaux" and choix_ia == "feuille":
      embed=discord.Embed(title=f"{ctx.message.author.name} a gagné la partie !",color=0x009933)
      await ctx.send(embed=embed)
      bot.shifumiscore += 1


    else:
      embed=discord.Embed(title=f"Dommage, égalité !",color=0xff9933)
      await ctx.send(embed=embed)
        
  await combinaison_shifumi(ctx,choix_ia,choix_j1)


@bot.command(name='cat', aliases=['chat'])
async def cat(ctx):
  with open("/data/liste_chats.json", 'r', encoding='utf-8') as f:
    liste_chats= json.loads(f.read())
  cat_image = random.choice(liste_chats["list_cats"])
  couleur = random.choice(bot.liste_couleurs)
  embed=discord.Embed(color=couleur)
  embed.set_image(url=cat_image)
  embed.set_author(name=bot.user.name, icon_url=bot.user.avatar)
  embed.set_footer(text=f"Requête de {ctx.message.author.name}", icon_url=ctx.message.author.avatar)
  await ctx.send(embed=embed)

@bot.command(name='slap', aliases=['s'])
async def slap(ctx):
  with open("/data/liste_slaps.json", 'r', encoding='utf-8') as f:
    list_images_slap = json.loads(f.read())
  slap_image = random.choice(list_images_slap["list_slaps"])
  couleur = random.choice(bot.liste_couleurs)
  cons = ctx.message.content.lower().split(" ")
  if (len(cons) < 2 or len(cons) > 3) or not ctx.message.mentions :
    embed=discord.Embed(description=f'Mettez une commande valide !\n `!slap <mention de l\'utilisateur>`', color=couleur)
    embed.set_author(name=bot.user.name, icon_url=bot.user.avatar)
    await ctx.send(embed=embed)
    return
  else :
    couleur = random.choice(bot.liste_couleurs)
    embed=discord.Embed(title=f"{ctx.message.author.name} a giflé {ctx.message.mentions[0].name}", color=couleur)
    embed.set_image(url=slap_image)
    embed.set_author(name=bot.user.name, icon_url=bot.user.avatar)
    embed.set_footer(text=f"Requête de {ctx.message.author.name}", icon_url=ctx.message.author.avatar)
    await ctx.send(embed=embed)

@bot.command(name='poll')
async def poll(ctx):
  couleur = random.choice(bot.liste_couleurs)
  question = ctx.message.content.split('"')[1::2]

  if len(question) < 3 :
    embed=discord.Embed(description=f'Mettez une commande valide !\nIl faut au moins une question et deux options ! (jusqu\'à 10 options au maximum)\n\n`!poll <"question"> <"option1"> <"option2">`', color=couleur)
    embed.set_author(name=bot.user.name, icon_url=bot.user.avatar)
    await ctx.send(embed=embed)
    return
  elif len(question) > 11 :
    embed=discord.Embed(description=f'Mettez une commande valide !\nIl faut au moins une question et jusqu\'à 10 options au maximum\n\n`!poll <"question"> <"option1"> <"option2">`', color=couleur)
    embed.set_author(name=bot.user.name, icon_url=bot.user.avatar)
    await ctx.send(embed=embed)
    return
  else :
    if len(question) == 3 and ('oui' in question[1].lower() and 'non' in question[2].lower()):
        reactions = ['✅', '❌']
    elif len(question) == 3 and ('non' in question[1].lower() and 'oui' in question[2].lower()):
        reactions = ['❌', '✅']
    else:
        reactions = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']

    embed=discord.Embed(description=f'{question[0]}', color=couleur)
    embed.set_author(name=bot.user.name, icon_url=bot.user.avatar)
    for i in range(len(question)-1) :
      for reaction in reactions[:len(question)-1]:
        pass
      embed.add_field(name="\u200b", value=f"{reactions[i]} - {question[i+1]}", inline=False)
    embed.set_author(name=bot.user.name, icon_url=bot.user.avatar)
    embed.set_footer(text=f"Requête de {ctx.message.author.name}", icon_url=ctx.message.author.avatar)
    react_message = await ctx.send(embed=embed)
    for reaction in reactions[:len(question)-1]:
        await react_message.add_reaction(reaction)

@bot.command(name="dog", aliases=["chien"])
async def dog(ctx):       
  with open("/data/chiens.json", 'r', encoding='utf-8') as f:
    chiens = json.loads(f.read()) # Cherche le fichier dans fichier importer (local de google)
  liste_doggy = chiens["chiens"]

  recup_nom_chiens = ctx.message.content.lower().split('"')[1::2] #On doit mettre entre guillemet le nom de la race pour l'appeler
  if len(recup_nom_chiens) < 1 or len(recup_nom_chiens) > 1 : #Minimum deux arguments pour afficher les chiens "!dog = ne fonctionnera pas" faudrait mettre "!dog Golden Retriever"
    embed=discord.Embed(description="Je ne comprends pas votre choix, veuillez mettre une commande valide.\n\n`!dog \"nom de race\"`\n\nNoms des races disponibles :\n\n`\"golden retriever\", \"golden\",\"retriever\"\n\"dalmatien\"\n\"staffordshire terrier americain\", \"staff\", \"american staffordshire terrier\"\n\"patou\", \"chien montagne des pyrénées\", \"chien des pyrénées\", \"chien montagne des pyrenees\", \"chien des pyrenees\", \"montagne des pyrenees\", \"montagne des pyrenees\"\n\"podenco de canaria\", \"canaria\", \"podenco\"\n\"samoyede\"\n\"border collier\", \"collier\", \"border\"\n\"akita inu\", \"hachiko\", \"akita\"\n\"shiba inu\", \"shiba\"\n\"eurasier\"\n\"malamute de l\"alaska\", \"malamute\"\n\"corgi\", \"welsh corgi pembroke\"\n\"spitz nain\", \"loulou de poméranie\", \"poméranie\", \"poméranien\"\n\"malinois\", \"berger belge malinois\"`", color=0xfff6df)
    await ctx.send(embed=embed)
  else:
    for i in liste_doggy :
      if recup_nom_chiens[0] in i["race"] :
        image_chien = random.choice(i["image"])
        embed=discord.Embed(title=f"{recup_nom_chiens[0].capitalize()}",color=0xfff6df)
        embed.add_field(name= "Origine", value=i["histoire"], inline = False)
        embed.add_field(name= "Caractère", value=i["caractere"], inline = False)
        embed.set_image(url=image_chien)
    await ctx.send(embed=embed) 


# météo
@bot.command(name = 'weather', aliases = ['w', 'meteo', 'm'])
async def weather(ctx) :
  couleur = random.choice(bot.liste_couleurs)
  api_weather_token = 'token_api'
 
  city_name = ctx.message.content.split('"')[1::2] 
  
  if len(city_name) < 1 :
    embed=discord.Embed(description="Veuillez mettre une commande valide.\n\n`!meteo <\"nom de ville\">`", color=couleur)
    await ctx.send(embed=embed)
  else :
    url_weather = 'https://api.openweathermap.org/data/2.5/weather?q=' + city_name[0] + '&lang=fr&units=metric&appid=' + api_weather_token

    response = requests.get(url_weather)

    # verification du code statut de la requete
    if response.status_code == 200:
      # on recupere les donnes de l'api au format json
      data = response.json()
      main = data['main']
      report = data['weather']
      ville = data['name']
      sys = data['sys']
      vent = data['wind']
      timezone = data['timezone']
      nuage = data['clouds']['all']
      visib = data['visibility']
  
      descp = report[0]['description']
      img = report[0]['icon']


      pays = sys['country']
      leve = sys['sunrise'] + timezone
      couche = sys['sunset'] + timezone

      temperature = main['temp']
      temperature_min = main['temp_min']
      temperature_max = main['temp_max']
      humidite = main['humidity']
      pression = main['pressure']
      ressenti = main['feels_like']

      timezone = int(data['timezone'] / 3600)

      h_leve = datetime.fromtimestamp(leve).strftime('%H:%M:%S')
      h_couche = datetime.fromtimestamp(couche).strftime('%H:%M:%S')
      h = datetime.fromtimestamp(data['dt'] + data['timezone']).strftime('%H:%M:%S')

      vitesse_vent = round(vent['speed'] * 3.6, 2)
      degree_vent = vent['deg']

      if timezone > 0 :
        embed=discord.Embed(title=f"Météo à {ville} :flag_{pays.lower()}:", description=f"Aujourd'hui,\nil est actuellement {h} (UTC +{timezone}), {descp}.", color=couleur)
      else :
        embed=discord.Embed(title=f"Météo à {ville} :flag_{pays.lower()}:", description=f"Aujourd'hui,\nil est actuellement {h} (UTC {timezone}), {descp}.", color=couleur)
      
      embed.set_author(name=bot.user.name, icon_url=bot.user.avatar)
      embed.set_thumbnail(url=f'http://openweathermap.org/img/w/{img}.png')    


      embed.add_field(name="🌡️ Temp.", value=f"{temperature} °C", inline=True)
      embed.add_field(name="Ressenti", value=f"{ressenti} °C", inline=True)
      embed.add_field(name="Pression", value=f"{pression} hPa", inline=True)

      embed.add_field(name="🔺Temp. min", value=f"{temperature_min} °C", inline=True)
      embed.add_field(name="🔻Temp. max", value=f"{temperature_max} °C", inline=True)
      embed.add_field(name="☁️ Nuage", value=f"{nuage} %", inline=True)

      embed.add_field(name="💧 Humidité", value=f"{humidite} %", inline=True)

      if 'gust' in data['wind'] :
        embed.add_field(name=f"🌬️ Vent | 🎏 Rafale", value=f"{vitesse_vent} km/H ({degree_vent}°)\n {round(data['wind']['gust'] *3.6, 2)} km/H", inline=True)
      else :
        embed.add_field(name=f"🌬️ Vent", value=f"{vitesse_vent} km/H ({degree_vent}°)", inline=True)

      if 'rain' in data :
        if '1h' in data['rain'] :
          if '3h' in data['rain'] :
            embed.add_field(name="🌧️ Précipitation", value=f"{data['rain']['1h']} mm (il y a 1h)\n{data['rain']['3h']} mm (il y a 3h)", inline=True)
          embed.add_field(name="🌧️ Précipitation", value=f"{data['rain']['1h']} mm (il y a 1h)", inline=True)
        elif '1h' not in data['rain'] and '3h' in data['rain'] :
          embed.add_field(name="🌧️ Précipitation", value=f"{data['rain']['3h']} mm (il y a 3h)", inline=True)

      if 'snow' in data :
        if '1h' in data['snow'] :
          if '3h' in data['snow'] :
            embed.add_field(name="❄️ Neige", value=f"{data['snow']['1h']} mm (il y a 1h)\n{data['snow']['3h']} mm (il y a 3h)", inline=True)
          embed.add_field(name="❄️ Neige", value=f"{data['snow']['1h']} mm (il y a 1h)", inline=True)
        elif '1h' not in data['snow'] and '3h' in data['snow'] :
          embed.add_field(name="❄️ Neige", value=f"{data['snow']['3h']} mm (il y a 3h)", inline=True)

      embed.add_field(name="🌫️ Visibilité", value=f"{visib} m", inline=True)
      embed.add_field(name="🌅 Levé", value=f"{h_leve}", inline=True)
      embed.add_field(name="🌇 Couché", value=f"{h_couche}", inline=True)

      embed.set_footer(text=f"Requête de {ctx.message.author.name}", icon_url=ctx.message.author.avatar)
      
      await ctx.send(embed=embed)

    else:
      embed=discord.Embed(title=f"Veuillez mettre une commande valide.", description="`!meteo <\"nom de ville\">`\n\nSi vous ne trouvez pas la ville souhaitée :\n\n`!meteo <\"nom de ville\, abréviation du pays\">`\n\n Exemple : `!meteo \"rome, it\"`", color=couleur)
      embed.set_author(name=bot.user.name, icon_url=bot.user.avatar)
      embed.set_footer(text=f"Requête de {ctx.message.author.name}", icon_url=ctx.message.author.avatar)
      await ctx.send(embed=embed)

# vrai ou faux
class VFView(discord.ui.View) :

  foo : bool = None

  def __init__(self, numero_question, question, vrai, faux, is_first, anecdote ,timeout):
    super().__init__()
    self.value = None
    self.numero_question = numero_question
    self.vrai = vrai
    self.faux = faux
    self.question = question
    self.is_first = is_first
    self.anecdote = anecdote
    self.timeout = timeout

  async def disable_all_items(self):
    for item in self.children: 
      item.disabled = True
      await self.message.edit(view=self)

  async def on_timeout(self) -> None :
    embed=discord.Embed(title="✨ Vrai ou faux - Etoile ✨",color=0x1F2023)
    embed.add_field(name=f"Réponse de la question {self.numero_question}", value="Dommage... le temps est écoulé.", inline=False)
    embed.set_footer(text=f"Vous gagné aucun point.")
    embed.set_image(url='https://media.tenor.com/Ar0TxNJSFSgAAAAC/line.gif')
    await self.message.channel.send(embed=embed)
    await self.disable_all_items()

  @discord.ui.button(label=f"Vrai", style=discord.ButtonStyle.success)
  async def bouton1(self, button: discord.ui.Button, interaction: discord.Interaction):
    embed=discord.Embed(title="✨ Vrai ou faux - Etoile ✨",color=0x1F2023)
    embed.add_field(name=f"Réponse de la question {self.numero_question}", value=f"{self.vrai}\n\n{self.anecdote}", inline=False)
    if self.is_first :
      bot.VFscore += 1
      embed.set_footer(text=f"Vous gagné 1 point.")
    else :
      embed.set_footer(text=f"Vous gagné 0 point.")
    embed.set_image(url='https://media.tenor.com/Ar0TxNJSFSgAAAAC/line.gif')
    await interaction.response.send_message(embed=embed)
    self.foo = True
    self.stop()

  @discord.ui.button(label=f"Faux", style=discord.ButtonStyle.red)
  async def bouton2(self,button: discord.ui.Button, interaction: discord.Interaction):
    embed=discord.Embed(title="✨ Vrai ou faux - Etoile ✨",color=0x1F2023)
    embed.add_field(name=f"Réponse de la question {self.numero_question}", value=f"{self.faux}\n\n{self.anecdote}", inline=False)
    if not self.is_first :
      bot.VFscore += 1
      embed.set_footer(text=f"Vous gagné 1 point.")
    else :
      embed.set_footer(text=f"Vous gagné 0 point.")
    embed.set_image(url='https://media.tenor.com/Ar0TxNJSFSgAAAAC/line.gif')
    await interaction.response.send_message(embed=embed)
    self.foo = False
    self.stop()
# fin class VFView()


class VFEmbed() :
  def __init__(self, numero_question, question):
    super().__init__()
    self.numero_question = numero_question
    self.question = question
    self.embed = discord.Embed(title="✨ Vrai ou faux - Etoile ✨",color=0x1F2023)
    self.embed.add_field(name=f"Question {self.numero_question}", value=f"{self.question}", inline=False)
    self.embed.set_image(url='https://media.tenor.com/Ar0TxNJSFSgAAAAC/line.gif')

  def to_dict(self):
      return self.embed.to_dict()


@bot.command(name='vf', aliases=['vraifaux', 'tf', 'truefalse'])
async def vf(ctx):
  with open("/data/vf.json", 'r', encoding='utf-8') as f:
    data = json.loads(f.read())
  questions = data["VF"]
  bot.VFscore = 0


  for i in range(5) :
    r_questions = random.choice(questions)
    questions.remove(r_questions)

    embed = VFEmbed(i+1, r_questions["question"])
    view = VFView(i+1, r_questions["question"] ,r_questions["Vrai"], r_questions["Faux"], r_questions["is_first"], r_questions["Anecdote"] , 10)
    message = await ctx.send(embed=embed, view=view)
    view.message = message
    await view.wait()
    await view.disable_all_items()
  
  embed= discord.Embed(title="✨ Fin du vrai ou faux - Etoile ✨", description=f"Score : {bot.VFscore} / 5")
  embed.set_author(name=bot.user.name, icon_url=bot.user.avatar)
  await ctx.send(embed=embed)

# qcm
class QCMView(discord.ui.View) :

  foo : bool = None

  def __init__(self, numero_question, question, reponse1, reponse2, reponse3, solution, anecdote ,timeout):
    super().__init__()
    self.value = None
    self.numero_question = numero_question
    self.reponse1 = reponse1
    self.reponse2 = reponse2
    self.reponse3 = reponse3
    self.question = question
    self.solution = solution
    self.anecdote = anecdote
    self.timeout = timeout

  async def disable_all_items(self):
    for item in self.children: 
      item.disabled = True
      await self.message.edit(view=self)

  async def on_timeout(self) -> None :
    embed=discord.Embed(title="✨ QCM - Etoile ✨",color=0x1F2023)
    embed.add_field(name=f"Réponse de la question {self.numero_question}", value=f"Dommage... le temps est écoulé.\n\nLa réponse était {self.solution}.\n\n{self.anecdote}.", inline=False)
    embed.add_field(name=f"Score", value=f"Vous gagné aucun point.", inline=False)
    embed.set_footer(text=f"Vous gagné aucun point.")
    embed.set_image(url='https://media.tenor.com/Ar0TxNJSFSgAAAAC/line.gif')
    await self.message.channel.send(embed=embed)
    await self.disable_all_items()

  @discord.ui.button(label=f"Choix 1", style=discord.ButtonStyle.success)
  async def bouton1(self,button: discord.ui.Button, interaction: discord.Interaction):
    embed=discord.Embed(title="✨ QCM - Etoile ✨",color=0x1F2023)
    embed.add_field(name=f"Réponse de la question {self.numero_question}", value=f"{self.anecdote}.", inline=False)
    if self.reponse1 == self.solution : 
      bot.QCMscore += 1
      embed.set_footer(text=f"Vous gagné 1 point.")
    else :
      embed.set_footer(text=f"Vous gagné 0 point.")
    embed.set_image(url='https://media.tenor.com/Ar0TxNJSFSgAAAAC/line.gif')
    await interaction.response.send_message(embed=embed)
    self.foo = True
    self.stop() 

  @discord.ui.button(label=f"Choix 2", style=discord.ButtonStyle.blurple)
  async def bouton2(self,button: discord.ui.Button, interaction: discord.Interaction):
    embed=discord.Embed(title="✨ QCM - Etoile ✨",color=0x1F2023)
    embed.add_field(name=f"Réponse de la question {self.numero_question}", value=f"{self.anecdote}.", inline=False)
    if self.reponse2 == self.solution :
      bot.QCMscore += 1
      embed.set_footer(text=f"Vous gagné 1 point.")
    else :
      embed.set_footer(text=f"Vous gagné 0 point.")
    embed.set_image(url='https://media.tenor.com/Ar0TxNJSFSgAAAAC/line.gif')
    await interaction.response.send_message(embed=embed)
    self.foo = False
    self.stop()

  @discord.ui.button(label=f"Choix 3", style=discord.ButtonStyle.red)
  async def bouton3(self,button: discord.ui.Button, interaction: discord.Interaction):
    embed=discord.Embed(title="✨ QCM - Etoile ✨",color=0x1F2023)
    embed.add_field(name=f"Réponse {self.numero_question}", value=f"{self.anecdote}", inline=False)
    if self.reponse3 == self.solution :
      bot.QCMscore += 1
      embed.set_footer(text=f"Vous gagné 1 point.")
    else :
      embed.set_footer(text=f"Vous gagné 0 point.")
    embed.set_image(url='https://media.tenor.com/Ar0TxNJSFSgAAAAC/line.gif')
    await interaction.response.send_message(embed=embed)
    self.foo = False
    self.stop()

# fin QCMView

class QCMEmbed() :
  def __init__(self, numero_question, question,choix1,choix2,choix3):
    super().__init__()
    self.numero_question = numero_question
    self.choix1 = choix1
    self.choix2 = choix2
    self.choix3 = choix3
    self.question = question
    self.embed = discord.Embed(title="✨ QCM - Etoile ✨",color=0x1F2023)
    self.embed.add_field(name=f"Question {self.numero_question}", value=f"{self.question}", inline=False)
    self.embed.add_field(name=f"Choix :",value=f"1. {self.choix1}\n\n2. {self.choix2}\n\n3. {self.choix3}", inline=False)
    self.embed.set_image(url='https://media.tenor.com/Ar0TxNJSFSgAAAAC/line.gif')

  def to_dict(self):
      return self.embed.to_dict()

@bot.command(name='qcm')
async def qcm(ctx):
  with open("/data/qcm.json", 'r', encoding='utf-8') as f:
    data = json.loads(f.read())
  questions = data["QCM"]
  bot.QCMscore = 0
  for i in range(5) :
    r_questions = random.choice(questions)
    questions.remove(r_questions)

    embed = QCMEmbed(i+1, r_questions["question"],r_questions["reponse1"], r_questions["reponse2"], r_questions["reponse3"])
    view = QCMView(i+1, r_questions["question"] ,r_questions["reponse1"], r_questions["reponse2"], r_questions["reponse3"],r_questions["solution"], r_questions["Anecdote"] , 10) 
    message = await ctx.send(embed=embed,view=view)
    view.message = message
    await view.wait()
    await view.disable_all_items()

  embed= discord.Embed(title="✨ Fin du QCM - Etoile ✨", description=f"Score : {bot.QCMscore} / 5")
  embed.set_author(name=bot.user.name, icon_url=bot.user.avatar)
  await ctx.send(embed=embed)

bot.run("TOKEN")