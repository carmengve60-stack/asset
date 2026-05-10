import discord
import os
import json
from discord import app_commands
from discord.ext import commands

TOKEN = os.getenv("DISCORD_TOKEN")
DATA_FILE = "assets_data.json"

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({}, f)

class AssetManager(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)
    
    async def setup_hook(self):
        await self.tree.sync()

bot = AssetManager()

def load_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

@bot.tree.command(name="names", description="List all stored asset names")
async def names(interaction: discord.Interaction):
    data = load_data()
    if not data:
        await interaction.response.send_message("No assets found.")
        return
    name_list = "\n".join([f"- {name}: {info['description']}" for name, info in data.items()])
    await interaction.response.send_message(f"**Stored assets:**\n{name_list}")

@bot.tree.command(name="assets", description="Upload a file with a name and description")
async def assets(interaction: discord.Interaction, name: str, description: str, file: discord.Attachment):
    await interaction.response.defer()
    data = load_data()
    if name in data:
        await interaction.followup.send(f"Asset '{name}' already exists. Use a different name.")
        return
    file_path = f"stored_{name}_{file.filename}"
    await file.save(file_path)
    data[name] = {
        "description": description,
        "path": file_path,
        "original_filename": file.filename
    }
    save_data(data)
    await interaction.followup.send(f"Asset '{name}' saved with description: {description}")

@bot.tree.command(name="name", description="Get description of a specific asset")
async def name_info(interaction: discord.Interaction, name: str):
    data = load_data()
    if name not in data:
        await interaction.response.send_message(f"Asset '{name}' not found.")
        return
    await interaction.response.send_message(f"**{name}**: {data[name]['description']}")

@bot.tree.command(name="send", description="Send a stored file by its name")
async def send_file(interaction: discord.Interaction, name: str):
    data = load_data()
    if name not in data:
        await interaction.response.send_message(f"Asset '{name}' not found.")
        return
    file_path = data[name]["path"]
    if not os.path.exists(file_path):
        await interaction.response.send_message(f"File for '{name}' is missing.")
        return
    with open(file_path, "rb") as f:
        discord_file = discord.File(f, filename=data[name]["original_filename"])
    await interaction.response.send_message(f"Sending: **{name}** - {data[name]['description']}", file=discord_file)

bot.run(TOKEN)
