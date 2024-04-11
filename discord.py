import discord
import pycord
from discord.ext import commands, tasks
from discord.ui import Button, View
from discord import Embed, Interaction
import asyncio
import re

# Define allowed roles that can use moderation commands
allowed_roles = ['【👑】𝒦𝒾𝓃𝑔 - 𝒻𝑜𝓊𝓃𝒹𝑒𝓇', 'Director', 'Administrator']

# Define all intents
intents = discord.Intents.all()
intents.guilds = True
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix='$', intents=intents)

# Set the welcome channel ID manually
welcome_channel_id = 1219626166218916052  # Replace YOUR_WELCOME_CHANNEL_ID with the actual channel ID

# Channel ID where observations will be sent
observation_channel_id = 1226427803700957205  # Replace with the actual channel ID

# Define the channel where audit logs will be sent
audit_log_channel_id = 1222834485444481039  # Replace with the actual channel ID
last_audit_log_entry_id = None 

ticket_channel_id = 1227194937817301032

# Questions for the application
questions = [
    "What is your name?",
    "What is your age?",
    "Why do you want to join?",
    "What experience do you have?",
    "Any additional comments?"
]


# Welcome Message without Image
@bot.event
async def on_member_join(member):
    global welcome_channel_id

    if welcome_channel_id:
        channel = bot.get_channel(welcome_channel_id)

        if channel:
            # Send the welcome message with member mention
            await channel.send(f"Welcome to the server, {member.mention}!")
        else:
            print("Welcome channel not found.")
    else:
        print("Welcome channel ID is not set. Please set it manually in the code.")


@bot.slash_command(name='kick', description='Kick a member from the server.')
async def kick(ctx, member: discord.Member, *, reason=None):
    if any(role.name in allowed_roles for role in ctx.author.roles):
      # Check if author's role is lower than target user's role
      if ctx.author.top_role < member.top_role:
          await ctx.send("You cannot kick this user because their role is higher than yours.")
          return
      try:
            await member.kick(reason=reason)
            await ctx.send(f"{member.mention} has been kicked from the server.")
      except discord.Forbidden:
            await ctx.send("I don't have permission to kick that user.")
      except discord.HTTPException as e:
            await ctx.send(f"An error occurred while trying to kick {member.mention}: {e}")
    else:
        await ctx.send("You are not allowed to use this command.")

# Command to ban a member
@bot.slash_command(name='ban', description='Ban a member from the server.')
async def ban(ctx, member: discord.Member, *, reason=None):
    if any(role.name in allowed_roles for role in ctx.author.roles):
      # Check if author's role is lower than target user's role
      if ctx.author.top_role < member.top_role:
          await ctx.send("You cannot ban this user because their role is higher than yours.")
          return
      await member.ban(reason=reason)
      await ctx.send(f"{member.mention} has been banned from the server.")
    else:
        await ctx.send("You are not allowed to use this command.")

# Function to parse duration input
def parse_duration(duration_str):
    time_regex = re.compile(r'(\d+)([dDhHmMsS])')
    matches = time_regex.findall(duration_str)
    total_seconds = 0
    for amount, unit in matches:
        amount = int(amount)
        if unit.lower() == 'd':
            total_seconds += amount * 86400  # 1 day = 86400 seconds
        elif unit.lower() == 'h':
            total_seconds += amount * 3600   # 1 hour = 3600 seconds
        elif unit.lower() == 'm':
            total_seconds += amount * 60     # 1 minute = 60 seconds
        elif unit.lower() == 's':
             total_seconds += amount
    return total_seconds
@bot.slash_command(name='mute', description='Mute a member for a specific duration.')
async def mute(ctx, member: discord.Member, duration: str = None, reason=None):
    if any(role.name in allowed_roles for role in ctx.author.roles):
      # Check if author's role is lower than target user's role
      if ctx.author.top_role < member.top_role:
          await ctx.send("You cannot mute this user because their role is higher than yours.")
          return

        # Check if a duration is provided
      
      # Check if a duration is provided
      if duration is None:
          await ctx.send("Please specify the duration (e.g., 1d, 7d, 7h, 1m).")
          return

      # Parse the duration input
      mute_duration = parse_duration(duration)
      if mute_duration == 0:
          await ctx.send("Invalid duration format. Please use format like 1d, 1d, 1h, 1m, 1s.")
          return
        # Check if muted role exists, create if not
      muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
      if not muted_role:
            muted_role = await ctx.guild.create_role(name="Muted")
            for channel in ctx.guild.channels:
                await channel.set_permissions(muted_role, send_messages=False)

        # Add the muted role to the member
    await member.add_roles(muted_role, reason=reason)
    await ctx.send(f"{member.mention} has been muted for {duration} .")

        # Remove the muted role after the specified duration
    await asyncio.sleep(mute_duration)
    if muted_role in member.roles:
            await member.remove_roles(muted_role)
            await ctx.send(f"{member.mention} has been unmuted.")
    else:
        await ctx.send("You are not allowed to use this command.")
# Command to unmute a member
@bot.slash_command(name='unmute', description='Unmute a already muted member.')
async def unmute(ctx, member: discord.Member):
    if any(role.name in allowed_roles for role in ctx.author.roles):
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if muted_role in member.roles:
            await member.remove_roles(muted_role)
            await ctx.send(f"{member.mention} has been unmuted.")
        else:
            await ctx.send("This member is not muted.")
    else:
        await ctx.send("You are not allowed to use this command.")

@bot.slash_command(name='purge', description='Delete a specific no. of messages from a channel.')
async def purge(ctx, amount: int):
    if any(role.name in allowed_roles for role in ctx.author.roles):
        # Purge messages
        await ctx.channel.purge(limit=amount+1)
        # Send message indicating the number of messages cleared
        message = await ctx.send(f"{amount} messages have been purged.")
        # Delete the message after a short delay
        await asyncio.sleep(5)  # Adjust the delay as needed
        await message.delete()
    else:
        await ctx.send("You are not allowed to use this command.")

# Command to start the application process
# Dictionary to store user responses
user_responses = {}

# Command to start the application process
@bot.slash_command(name='apply', description='apply for staff role in the server!!!')
async def apply(ctx):
    await ctx.send("Application has been started in your DM.")
    global user_responses

    # Check if user has already applied
    if ctx.author.id in user_responses:
        await ctx.send("You have already applied. Contact the admins for any change in the application")
        return

    # Initialize dictionary to store responses
    responses = {}

    # Send questions to the user's DMs one by one
    for question in questions:
        await ctx.author.send(question)
        response = await bot.wait_for('message', check=lambda m: m.author == ctx.author)
        # Record responses
        responses[question] = response.content

    # Record user's responses
    user_responses[ctx.author.id] = responses

    # Send thank-you message to user
    await ctx.author.send("Thanks for applying. We'll let you know soon if you are selected.")

    # Send observations to the specified channel in an embedded format
    observation_channel = bot.get_channel(observation_channel_id)
    if observation_channel:
        # Construct observation message
        observation_message = "Application Observations:\n"
        for i, question in enumerate(questions, 1):
            observation_message += f"{i}. {question}\n"
            # Retrieve the corresponding response from the stored responses
            observation_message += f"Response: {responses[question]}\n\n"

        # Create embed for observations
        embed = discord.Embed(title="Application Observations", description=observation_message, color=discord.Color.purple())

        # Send observation message as an embedded message to the channel
        await observation_channel.send(embed=embed)
    else:
        print("Observation channel not found.")

@tasks.loop(seconds=1000000000000)  # Check the audit logs every 60 seconds
async def check_audit_logs():
    global last_audit_log_entry_id
    channel = bot.get_channel(audit_log_channel_id)
    if channel is None:
        print("Audit log channel not found.")
        return

    # Fetch the latest audit log entry
    try:
        # Use an async iterator to get the first audit log entry
        async for entry in bot.guilds[0].audit_logs(limit=1):
            # Check if this is a new entry
            if last_audit_log_entry_id is None or entry.id != last_audit_log_entry_id:
                last_audit_log_entry_id = entry.id  # Update the last seen entry ID
                embed = discord.Embed(title="Audit Log Update", description="A new audit log entry has been detected.", color=0x00ff00)
                embed.add_field(name="Action", value=str(entry.action), inline=False)
                embed.add_field(name="User", value=str(entry.user), inline=False)
                embed.add_field(name="Target", value=str(entry.target), inline=False)
                reason = entry.reason if entry.reason else "No reason provided"
                embed.add_field(name="Reason", value=reason, inline=False)
                await channel.send(embed=embed)
    except Exception as e:
        print(f"Failed to check audit logs: {e}")

@bot.event
async def on_message_edit(before, after):
    if before.content == after.content:  # Ignore if the edit didn't change the content
        return
    channel = bot.get_channel(audit_log_channel_id)  # The channel to send the notification
    embed = discord.Embed(title="Message Edited", description=f"A message by {before.author.mention} was edited.", color=0x00ff00)
    embed.add_field(name="Before", value=before.content, inline=False)
    embed.add_field(name="After", value=after.content, inline=False)
    await channel.send(embed=embed)

class TicketView(View):
  def __init__(self, allowed_roles):
      super().__init__(timeout=None)
      self.allowed_roles = allowed_roles

  @discord.ui.button(label="Open Ticket", style=discord.ButtonStyle.green)
  async def open_ticket_button(self, interaction: discord.Interaction, button: Button):
      guild = interaction.guild
      member = interaction.user

      # Determine if the member has the allowed role
      if not any(role.name in self.allowed_roles for role in member.roles):
          await interaction.response.send_message("You do not have permission to open a ticket.", ephemeral=True)
          return

      # Create a ticket
      ticket_category = discord.utils.get(guild.categories, name="Tickets")
      if not ticket_category:
          ticket_category = await guild.create_category("Tickets")

      ticket_channel = await guild.create_text_channel(f"ticket-{member.display_name}", category=ticket_category)
      await ticket_channel.set_permissions(guild.default_role, view_channel=False)  # Make it invisible to everyone else
      await ticket_channel.set_permissions(member, view_channel=True)  # Make it visible to the ticket creator

      # Optionally, grant access to specific roles
      for role_name in self.allowed_roles:
          role = discord.utils.get(guild.roles, name=role_name)
          if role:
              await ticket_channel.set_permissions(role, view_channel=True)

      await interaction.response.send_message(f"Ticket created: {ticket_channel.mention}", ephemeral=True)

@bot.command()
async def ticket(ctx):
  embed = discord.Embed(title="Support Tickets", description="Click the button below to open a ticket.", color=0x00ff00)
  await ctx.send(embed=embed, view=TicketView(["Administrator", "【👑】𝒦𝒾𝓃𝑔 - 𝒻𝑜𝓊𝓃𝒹𝑒𝓇"]))  # Adjust roles as needed

@bot.event
async def on_ready():
    print(f'{bot.user} has conneted to a server')
    check_audit_logs.start() 

bot.run('MTIxOTM4MDM1NDcyOTc3NTEwNA.G9oFK9.NzQH2aBit5NjWrijU7mSwoU_u6ZMpkCgkpriSs')