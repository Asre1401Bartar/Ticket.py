import discord
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions
import json
import asyncio



bot = commands.Bot(intents = discord.Intents.all() , command_prefix ='Prefix', help_command=None)

@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.idle ,activity=discord.Game(name = f"{Prefix_Ticket}new"))
    print(f"I am running on {bot.user.name}")


@bot.command()
async def help(ctx):
    with open("data.json") as f:
        data = json.load(f)
    
    valid_user = False

    for role_id in data["verified-roles"]:
        try:
            if ctx.guild.get_role(role_id) in ctx.author.roles:
                valid_user = True
        except:
            pass
    
    if ctx.author.guild_permissions.administrator or valid_user:

        em = discord.Embed(title="Asre Bartar Tickets Help", description="", color=0x00a8ff)
        em.add_field(name="`#new <message>`", value="This creates a new ticket. Add any words after the command if you'd like to send a message when we initially create your ticket.")
        em.add_field(name="`#close`", value="Use this to close a ticket. This command only works in ticket channels.")
        em.set_footer(text="Team : AsreBartar")

        await ctx.send(embed=em)
    
    else:

        em = discord.Embed(title = "Asre Bartar Tickets Help", description ="", color = 0x00a8ff)
        em.add_field(name="`.new <message>`", value="This creates a new ticket. Add any words after the command if you'd like to send a message when we initially create your ticket.")
        em.add_field(name="`.close`", value="Use this to close a ticket. This command only works in ticket channels.")
        em.set_footer(text="Team : AsreBartar ")

        await ctx.send(embed=em)

@bot.command()
async def new(ctx, *, args = None):
        await bot.wait_until_ready()

        if args == None:
            message_content = "سلام ، لطفا صبور باشيد تا تيم پشتيماني سرور پاسخ دهند "
        
        else:
            message_content = "".join(args)

        with open("data.json") as f:
            data = json.load(f)

        ticket_number = int(data["ticket-counter"])
        ticket_number += 1

        ticket_channel = await ctx.guild.create_text_channel("ticket-{}".format(ticket_number))
        await ticket_channel.set_permissions(ctx.guild.get_role(ctx.guild.id), send_messages=False, read_messages=False)

        for role_id in data["valid-roles"]:
            role = ctx.guild.get_role(role_id)

            await ticket_channel.set_permissions(role, send_messages=True, read_messages=True, add_reactions=True, embed_links=True, attach_files=True, read_message_history=True, external_emojis=True)
        
        await ticket_channel.set_permissions(ctx.author, send_messages=True, read_messages=True, add_reactions=True, embed_links=True, attach_files=True, read_message_history=True, external_emojis=True)

        em = discord.Embed(title="New ticket from {}#{}".format(ctx.author.name, ctx.author.discriminator), description= "{}".format(message_content), color=0x00a8ff)

        await ticket_channel.send(embed=em)

        pinged_msg_content = ""
        non_mentionable_roles = []

        if data["pinged-roles"] != []:

            for role_id in data["pinged-roles"]:
                role = ctx.guild.get_role(role_id)

                pinged_msg_content += role.mention
                pinged_msg_content += " "

                if role.mentionable:
                    pass
                else:
                    await role.edit(mentionable=True)
                    non_mentionable_roles.append(role)
            
            await ticket_channel.send(pinged_msg_content)

            for role in non_mentionable_roles:
                await role.edit(mentionable=False)
        
        data["ticket-channel-ids"].append(ticket_channel.id)

        data["ticket-counter"] = int(ticket_number)
        with open("data.json", 'w') as f:
            json.dump(data, f)
        
        created_em = discord.Embed(title="Asre Bartar Tickets", description="تيکت شما با موفقيت ساخته شد{}".format(ticket_channel.mention), color=0x00a8ff)
        
        await ctx.send(embed=created_em)

@bot.command()
async def close(ctx):
    with open('data.json') as f:
        data = json.load(f)

    if ctx.channel.id in data["ticket-channel-ids"]:

        channel_id = ctx.channel.id

        def check(message):
            return message.author == ctx.author and message.channel == ctx.channel and message.content.lower() == "close"

        try:

            em = discord.Embed(title="Asre Bartar Tickets", description="اگر مطمئن هستيد از بستن تيکت واژه ``close`` را تايپ کنيد", color=0x00a8ff)
        
            await ctx.send(embed=em)
            await bot.wait_for('message', check=check, timeout=60)
            await ctx.channel.delete()

            index = data["ticket-channel-ids"].index(channel_id)
            del data["ticket-channel-ids"][index]

            with open('data.json', 'w') as f:
                json.dump(data, f)
        
        except asyncio.TimeoutError:
            em = discord.Embed(title="Asre Bartar Tickets", description=f"زمان شما به پايان رسيد ، دوباره ``{Prefix_Ticket}close`` را تايپ کنيد", color=0x00a8ff)
            await ctx.send(embed=em)

bot.run('TOKEN')
