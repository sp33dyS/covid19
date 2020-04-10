import random, os, discord, time, traceback, urllib.request, threading, subprocess, textwrap, pandas as pd
# import wget, requests

from dotenv import load_dotenv
from discord.ext import commands
from datetime import datetime #, timedelta
# from tabulate import tabulate
from dateutil.parser import parse as parsedate

#--------------------------------------------------------DOWNLOAD DATA FILE ON START--------------------------------------------------------

url = 'https://covid.ourworldindata.org/data/ecdc/full_data.csv'
urllib.request.urlretrieve(url, 'full_data.csv')

#-----------------------------------------------------------DISCORD CONFIGURATION-----------------------------------------------------------

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# client = discord.Client()

@bot.event
async def on_ready():
  print(f'{bot.user.name} dołączył do serwera!')

#-----------------------------------------------------------------FUNCTIONS-----------------------------------------------------------------

# Setting function execution from time to time
def every(delay, task):
  next_time = time.time() + delay
  while True:
    time.sleep(max(0, next_time - time.time()))
    try:
      task()
    except Exception:
      traceback.print_exc()
      # in production code you might want to have this instead of course:
      # logger.exception("Problem while executing repetitive task.")
    # skip tasks if we are behind schedule:
    # next_time += (time.time() - next_time) // delay * delay + delay

# Downloading of data file
def download():
  url = 'https://covid.ourworldindata.org/data/ecdc/full_data.csv'
#   url_time = requests.head(url).headers['last-modified']
#   url_date = parsedate(url_time)
#   file_time = datetime.datetime.fromtimestamp(os.path.getmtime('full_data.csv'))
#   if url_date > file_time:
  urllib.request.urlretrieve(url, 'full_data.csv')

threading.Thread(target=lambda: every(7200, download)).start()

# Downloading of data file in different way
# file_url = 'https://covid.ourworldindata.org/data/ecdc/full_data.csv'
# file_name = wget.download(file_url)

# File's last modifictaion date
def modification_date(filename):
  t = os.stat('full_data.csv').st_mtime # + timedelta(hours=2)
  return datetime.fromtimestamp(t).strftime("%d-%m-%Y %H:%M:%S") # + datetime.timedelta(hours=2)

#--------------------------------------------------------LOADING AND FORMATTING DATA--------------------------------------------------------

covid = pd.read_csv('full_data.csv')
covid.drop(covid.index[covid['location'] == 'World'], inplace = True)
covid.drop(covid.index[covid['location'] == 'International'], inplace = True)
covid['location'] = covid['location'].replace({'United States': 'USA'})
covidg = covid.groupby(['date', 'location']).sum().reset_index()
covids = covidg.sort_values(by=['date']).drop_duplicates(subset='location', keep='last')
covids['date'] = covids['date'].max()
covids['new_cases'] = pd.to_numeric(covids['new_cases'])
covids.set_index(pd.to_datetime(covids['date']), inplace=True)
covids.drop(['date'], axis=1, inplace=True)

# covid_new_cases = covid_mv.drop(['Nowe śmierci','Wszystkie przypadki','Wszystkie śmierci'], axis=1)
kraj = random.choice(covids['location'].unique())

#----------------------------------------------------------------BOT COMMANDS----------------------------------------------------------------

bot = commands.Bot(command_prefix=';')

# Just for testing. Comment if not needed
# @bot.event
# async def on_ready():
#   print(covidg)

@bot.event
async def on_command_error(error, ctx):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(print(f'Nie zesraj się'))
    else:
        raise error

bot.remove_command('help')
@bot.command()
async def help(ctx):
  embed = discord.Embed(title='Usage: ;command "kraj"', description="", color=0xeee657)

  embed.add_field(name=";help", value="Wyświetla to okno", inline=False)
  embed.add_field(name=";all-cases", value="Wyświetla wszystkie przypadki potwierdzone", inline=False)
  embed.add_field(name=";new-cases", value="Wyświetla nowe przypadki", inline=False)
  embed.add_field(name=";deaths", value="Wyświetla wszystkie przypadki śmiertelne", inline=False)
  await ctx.send(embed=embed)
    
@bot.command(name='all-cases', help='Wyświetla wszystkie przypadki potwierdzone')
# @commands.has_role('szefuncio')                                                                    # Check if user has role
async def cov(ctx, kraj: str):
  embed=discord.Embed(title="Wszystkie przypadki potwierdzone", description="", color=0xff0000)
  embed.add_field(name="Kraj:", value="{}".format(kraj), inline=True)
  embed.add_field(name="Ostatnia aktualizacja:", value=("{}".format(modification_date('full_data.csv') + " UTC")), inline=True)
  embed.add_field(name="Liczba:", value="{}".format(covids.loc[covids['location'] == kraj]['total_cases'].values), inline=True)     # .to_string()``
  embed.add_field(name="Total:", value="{}".format(covids['total_cases'].sum()), inline=True)     # .to_string()``
  await ctx.send(embed=embed)
#   embed.set_footer(text="")
#   await ctx.send(emoji)
#   print(ctx.message.id)
#   await mesg.pin()

@bot.command(name='new-cases', help='Wyświetla nowe przypadki z ostatniego dnia')
async def cov2(ctx, kraj: str):
  embed=discord.Embed(title="Nowe przypadki potwierdzone", description="", color=0xff0000)
  embed.add_field(name="Kraj:", value="{}".format(kraj), inline=True)
  embed.add_field(name="Ostatnia aktualizacja:", value="{}".format(modification_date('full_data.csv')), inline=True)
  embed.add_field(name="Liczba:", value="{}".format(covids.loc[covids['location'] == kraj]['new_cases'].values), inline=True)     # .to_string()``
  embed.add_field(name="Total:", value="{}".format(covids['new_cases'].sum()), inline=True)     # .to_string()``
  await ctx.send(embed=embed)

@bot.command(name='deaths', help='Wyświetla wszystkie przypadki śmiertelne')
async def cov3(ctx, kraj: str):
  embed=discord.Embed(title="Wszystkie przypadki śmiertelne", description="", color=0xff0000)
  embed.add_field(name="Kraj:", value="{}".format(kraj), inline=True)
  embed.add_field(name="Ostatnia aktualizacja:", value="{}".format(modification_date('full_data.csv')), inline=True)
  embed.add_field(name="Liczba:", value="{}".format(covids.loc[covids['location'] == kraj]['total_deaths'].values), inline=True)     # .to_string()``
  embed.add_field(name="Total:", value="{}".format(covids['total_deaths'].sum()), inline=True)     # .to_string()``
  await ctx.send(embed=embed)

bot.run(TOKEN)
# if input(KeyboardInterrupt):
#   subprocess.run(['pkill', '-f', 'cov.py'])