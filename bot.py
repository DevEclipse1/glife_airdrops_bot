import discord
from discord.ext import tasks, commands
import datetime
import pytz

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='$', intents=intents)

TOKEN = 'MTIyMTAyOTIwNjU4Mjg5MDUwNw.GeIJEL.aS8FeYG-Wsa1bV3qFgDZq2HMPemGwL3rb-X6_8'

CHANNEL_ID_TO_NOTIFY = 0
CHANNEL_ID_FILE = 'channel_id.txt'  # File to store channel ID

@bot.event
async def on_ready():
    print("Bot is ready")
    main_loop.start()
    # Load channel ID from file on bot startup
    load_channel_id()

def is_admin(ctx):
    return ctx.author.guild_permissions.administrator

@bot.command()
@commands.check(is_admin)
async def setchannel(ctx):
    global CHANNEL_ID_TO_NOTIFY
    CHANNEL_ID_TO_NOTIFY = ctx.channel.id
    save_channel_id()  # Save channel ID to file
    print(f"Set channel id to {ctx.channel.id}")

# Function to save channel ID to file
def save_channel_id():
    with open(CHANNEL_ID_FILE, 'w') as file:
        file.write(str(CHANNEL_ID_TO_NOTIFY))

# Function to load channel ID from file
def load_channel_id():
    global CHANNEL_ID_TO_NOTIFY
    try:
        with open(CHANNEL_ID_FILE, 'r') as file:
            CHANNEL_ID_TO_NOTIFY = int(file.read())
            print(f"Loaded channel id: {CHANNEL_ID_TO_NOTIFY}")
    except FileNotFoundError:
        print("Channel ID file not found.")
    except ValueError:
        print("Invalid channel ID found in file.")

@tasks.loop(seconds=1)
async def main_loop():
    current_time = datetime.datetime.now(pytz.timezone("Europe/Paris"))
    
    airdrop_times = ["01:55:00", "04:25:00", "06:25:00", "09:25:00",
                     "13:55:00", "16:55:00", "18:25:00", "19:55:00",
                     "20:55:00", "23:25:00"]
    
    next_airdrop_time = None
    for airdrop_time_str in airdrop_times:
        airdrop_time = datetime.datetime.strptime(airdrop_time_str, "%H:%M:%S")
        airdrop_datetime = pytz.timezone("Europe/Paris").localize(datetime.datetime.combine(current_time.date(), airdrop_time.time()))
        if airdrop_datetime > current_time:
            next_airdrop_time = airdrop_datetime
            break
    
    if next_airdrop_time:
        time_until_airdrop = next_airdrop_time - current_time
        hours, remainder = divmod(time_until_airdrop.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        time_until_airdrop_str = f"{hours}h, {minutes}m, {seconds}s"
        
        if time_until_airdrop.seconds == 0:
            channel = bot.get_channel(CHANNEL_ID_TO_NOTIFY)
            await channel.send("@everyone Airdrop is coming in 5 minutes")
    else:
        time_until_airdrop_str = "Unknown"
    
    if(CHANNEL_ID_TO_NOTIFY == 0):
        activity = discord.Game(name=f"$setchannel to setup in a channel you want")
        await bot.change_presence(status=discord.Status.idle, activity=activity)
    else:
        activity = discord.Game(name=f"Airdrop in {time_until_airdrop_str}")
        await bot.change_presence(status=discord.Status.idle, activity=activity)

bot.run(TOKEN)
