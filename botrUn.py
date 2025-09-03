import discord
from discord.ext import commands
import subprocess
import os
import asyncio

TOKEN = "YOUR_DISCORD_BOT_TOKEN"
PREFIX = "bfb!"
bot = commands.Bot(command_prefix=PREFIX, intents=discord.Intents.all())

export_counter = 0  # Keeps track of exports


async def run_ffmpeg(input_file, output_file, ffmpeg_args):
    """
    Runs FFmpeg with the provided arguments using subprocess.
    """
    cmd = ["ffmpeg", "-y", "-i", input_file] + ffmpeg_args + [output_file]
    process = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    return stdout, stderr


@bot.event
async def on_ready():
    print(f"✅ Beebo FFMPEG Bot is online as {bot.user}")


@bot.command(name="ffmpeg_any")
async def ffmpeg_any(ctx, *, args):
    """
    Apply custom FFmpeg arguments to an attached video.
    Usage: bfb!ffmpeg_any -vf "hflip,vflip" -af "volume=2"
    """
    global export_counter

    if not ctx.message.attachments:
        await ctx.send("❌ Please attach a video file.")
        return

    attachment = ctx.message.attachments[0]
    input_path = f"input_{export_counter}.mp4"
    output_path = f"output_{export_counter}.mp4"
    export_counter += 1

    await attachment.save(input_path)

    ffmpeg_args = args.split()
    await ctx.send(f"🔄 Processing video with FFmpeg args: `{args}`")

    stdout, stderr = await run_ffmpeg(input_path, output_path, ffmpeg_args)

    if os.path.exists(output_path):
        await ctx.send("✅ Done! Here's your processed video:", file=discord.File(output_path))
    else:
        await ctx.send("❌ Something went wrong.")
        print(stderr.decode())


@bot.command(name="process_video")
async def process_video(ctx):
    """
    Example with real_gm4 and curves + audio pitch
    Usage: bfb!process_video
    """
    global export_counter

    if not ctx.message.attachments:
        await ctx.send("❌ Please attach a video file.")
        return

    attachment = ctx.message.attachments[0]
    input_path = f"input_{export_counter}.mp4"
    output_path = f"output_{export_counter}.mp4"
    export_counter += 1

    await attachment.save(input_path)

    # Example: curves filter (real_gm4) and audio pitch shift
    ffmpeg_args = [
        "-vf", "curves=all='0/0 0.5/1 1/0'",  # Real GM4-like tone curve
        "-af", "asetrate=44100*1.334,aresample=44100"  # Approx +5 semitones
    ]

    await ctx.send("🎬 Applying curves and pitch shift...")

    stdout, stderr = await run_ffmpeg(input_path, output_path, ffmpeg_args)

    if os.path.exists(output_path):
        await ctx.send("✅ Video processed!", file=discord.File(output_path))
    else:
        await ctx.send("❌ FFmpeg error!")
        print(stderr.decode())


@bot.command(name="audio_mixer")
async def audio_mixer(ctx, vol: float = 2.0):
    """
    Example: change volume and mix
    Usage: bfb!audio_mixer 2
    """
    global export_counter

    if not ctx.message.attachments:
        await ctx.send("❌ Please attach an audio file.")
        return

    attachment = ctx.message.attachments[0]
    input_path = f"input_{export_counter}.mp3"
    output_path = f"output_{export_counter}.mp3"
    export_counter += 1

    await attachment.save(input_path)

    ffmpeg_args = ["-af", f"volume={vol}"]

    await ctx.send(f"🎧 Mixing audio with volume={vol}")

    stdout, stderr = await run_ffmpeg(input_path, output_path, ffmpeg_args)

    if os.path.exists(output_path):
        await ctx.send("✅ Audio processed!", file=discord.File(output_path))
    else:
        await ctx.send("❌ Error processing audio.")
        print(stderr.decode())


bot.run(TOKEN)
