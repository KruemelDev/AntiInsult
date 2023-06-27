import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import mysql.connector

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(
    intents=intents,
    help_command=None,
    command_prefix='$'
)
load_dotenv()
datenbank_password = os.getenv("DATENBANK_PASSWORD")

mydb = mysql.connector.connect(
    host="localhost",
    port="3306",
    user="root",
    passwd=datenbank_password
)
mycursor = mydb.cursor(buffered=True)
mycursor.execute("CREATE DATABASE IF NOT EXISTS schimpfwoerter")
mycursor.execute("USE schimpfwoerter")


@bot.event
async def on_message(message):
    list_of_insults = []

    server_id = message.guild.id
    server_name = message.guild.name

    insult_table_name = "insults_{}".format(server_id)

    allowed_authors_table_name = "allowed_{}".format(server_id)
    server_table_name = "server_{}".format(server_id)
    try:
        mycursor.execute("SHOW TABLES")
        tables = mycursor.fetchall()
    except:
        pass

    try:
        if not tables == []:
            mycursor.execute("SELECT insult FROM {}".format(insult_table_name))
            list_of_insults = mycursor.fetchall()
            mycursor.execute("SELECT allowed_user_id FROM {}".format(allowed_authors_table_name))
            allowed_authors = mycursor.fetchall()
    except:
        pass

    if message.content.startswith('$test'):
        await message.channel.send("$addInsult test")

    guild = bot.get_guild(server_id)
    member = guild.get_member(message.author.id)


    async def create_insult():
        for char in message.guild.name:
            if char == "$" or char == "'" or char == """""" or char == "#":
                embed = discord.Embed(
                    title="Fehler",
                    description="Es sind keine '', '', $ oder # erlaubt, tut mir leid.",
                    color=discord.Color.red()
                )
                await message.channel.send(embed=embed)
                return
        mycursor.execute("CREATE TABLE IF NOT EXISTS {} (id INT AUTO_INCREMENT PRIMARY KEY, insult VARCHAR(255))".format(insult_table_name))
        mycursor.execute("CREATE TABLE IF NOT EXISTS {} (id INT AUTO_INCREMENT PRIMARY KEY, allowed_user_name VARCHAR(255), allowed_user_id BIGINT UNIQUE)".format(allowed_authors_table_name))
        mycursor.execute("CREATE TABLE IF NOT EXISTS {} (id INT AUTO_INCREMENT PRIMARY KEY, server VARCHAR(255))".format(server_table_name))
        mycursor.execute("INSERT INTO {} (server) VALUES (%s)".format(server_table_name), (server_name,))
        mydb.commit()
        embed = discord.Embed(
            title="Beleidigungsliste erstellt",
            description=f"Die Beleidigungsliste '{server_name}' wurde erstellt.",
            color=discord.Color.green()
        )
        await message.channel.send(embed=embed)
        return
    async def add_user():
        key_word_list = []
        for key_word in message.content.split():
            key_word_list.append(key_word)

        user_mention = message.mentions[0].id
        mycursor.execute("SELECT allowed_user_id FROM {}".format(allowed_authors_table_name))
        all_user = mycursor.fetchall()

        if not all_user == []:
            for i in range(0, len(all_user)):
                if all_user[i] == (user_mention,):
                    embed = discord.Embed(title="Fehler",
                                          description="Der Benutzer ist bereits eingetragen.",
                                          color=discord.Color.red())
                    await message.channel.send(embed=embed)
                    return

            try:
                mycursor.execute("INSERT INTO {} (allowed_user_name, allowed_user_id) VALUES (%s, %s)".format(allowed_authors_table_name), (message.mentions[0].name, user_mention))
                mydb.commit()
                embed = discord.Embed(title="Benutzer hinzugefügt",
                                      description=f"Der Account {key_word_list[1]} wurde zu der Erlaubten Liste von '{server_name}' hinzugefügt.",
                                      color=discord.Color.green())
                await message.channel.send(embed=embed)
            except mysql.connector.IntegrityError:
                embed = discord.Embed(title="Fehler",
                                      description="Der Benutzer ist bereits eingetragen.",
                                      color=discord.Color.red())
                await message.channel.send(embed=embed)
            return
        else:
            try:
                mycursor.execute("INSERT INTO {} (allowed_user_name, allowed_user_id) VALUES (%s, %s)".format(allowed_authors_table_name), (message.mentions[0].name, user_mention))
                mydb.commit()
                embed = discord.Embed(title="Benutzer hinzugefügt",
                                      description=f"Der Account {key_word_list[1]} wurde zu der Beleidigungsliste von '{server_name}' hinzugefügt.",
                                      color=discord.Color.green())
                await message.channel.send(embed=embed)
            except mysql.connector.IntegrityError:
                embed = discord.Embed(title="Fehler",
                                      description="Der Benutzer ist bereits eingetragen.",
                                      color=discord.Color.red())
                await message.channel.send(embed=embed)
            return

    async def remove_user():
        key_word_list = []
        for key_word in message.content.split():
            key_word_list.append(key_word)
        user_mention = message.mentions[0].id
        mycursor.execute("SELECT allowed_user_id FROM {}".format(allowed_authors_table_name))
        all_user = mycursor.fetchall()

        for user in all_user:
            if user_mention in user:
                mycursor.execute("DELETE FROM {} WHERE allowed_user_id=(%s)".format(allowed_authors_table_name),(user_mention,))
                mydb.commit()
                embed = discord.Embed(title="Erlaubter Nutzer löschen",
                                      description=f"Der Erlaubte Nutzer {message.mentions[0].name} wurde gelöscht.",
                                      color=discord.Color.green())
                await message.channel.send(embed=embed)
                return
        embed = discord.Embed(title="Fehler",
                              description=f"Der Benutzer ist als kein Erlaubter Nutzer eingetragen.",
                              color=discord.Color.red())
        await message.channel.send(embed=embed)
        return
    async def add_insult():
        addinsultword = message.content[11:].lower().replace(" ", "")
        addinsultlist = [addinsultword]
        mycursor.execute("SELECT allowed_user_id FROM {}".format(allowed_authors_table_name))
        allowed_authors = mycursor.fetchall()

        if not allowed_authors == []:
            for i in allowed_authors:
                if message.author.id in i:
                    if not list_of_insults == []:
                        for j in list_of_insults:
                            if addinsultlist[0] in j:
                                embed = discord.Embed(title="Fehler",
                                                      description=f"Die Beleidigung: '{addinsultword}' ist schon eingetragen.",
                                                      color=discord.Color.red())
                                await message.channel.send(embed=embed)
                                return
                            else:
                                mycursor.execute("INSERT INTO {} (insult) VALUES (%s)".format(insult_table_name),(addinsultlist[0],))
                                mydb.commit()
                                embed = discord.Embed(title="Beleidigung hinzugefügt",
                                                      description=f"Die Beleidigung '{addinsultword}' wurde hinzugefügt.",
                                                      color=discord.Color.green())
                                await message.channel.send(embed=embed)
                                return
                    else:
                        mycursor.execute("INSERT INTO {} (insult) VALUES (%s)".format(insult_table_name),(addinsultlist[0],))
                        mydb.commit()
                        embed = discord.Embed(title="Beleidigung hinzugefügt",
                                              description=f"Die Beleidigung '{addinsultword}' wurde hinzugefügt.",
                                              color=discord.Color.green())
                        await message.channel.send(embed=embed)
                        return

            embed = discord.Embed(title="Fehler",
                                  description="Du hast leider keine Rechte, um Beleidigungen hinzuzufügen :/.",
                                  color=discord.Color.red())
            await message.channel.send(embed=embed)
            return
    async def remove_insult():
        removeinsultword = message.content[14:].lower().replace(" ", "")
        removeinsultlist = [removeinsultword]
        mycursor.execute("SELECT allowed_user_id FROM {}".format(allowed_authors_table_name))
        allowed_authors = mycursor.fetchall()
        if not allowed_authors == []:
            for i in allowed_authors:
                if message.author.id in i:
                    if list_of_insults == []:
                        embed = discord.Embed(title="Fehler",
                                              description="Es tut mir leid, aber es gibt keine Beleidigungs Einträge.",
                                              color=discord.Color.red())
                        await message.channel.send(embed=embed)
                        return
                    else:
                        for j in list_of_insults:
                            if removeinsultlist[0] in j:
                                embed = discord.Embed(title="Beleidigung gelöscht",
                                                      description=f"Die Beleidigung '{removeinsultword}' wird aus der Beleidigungsliste gelöscht.",
                                                      color=discord.Color.red())
                                await message.channel.send(embed=embed)
                                mycursor.execute("DELETE FROM {} WHERE insult=(%s)".format(insult_table_name),(removeinsultlist[0],))
                                mydb.commit()
                                return
                        embed = discord.Embed(title="Fehler",
                                              description=f"Es tut mir leid, aber die Beleidigung '{removeinsultword}' gibt es nicht in der Datenbank.",
                                              color=discord.Color.red())
                        await message.channel.send(embed=embed)
                        return

            embed = discord.Embed(title="Fehler",
                                  description="Du hast leider keine Rechte, um Beleidigungen zu löschen :/.",
                                  color=discord.Color.red())
            await message.channel.send(embed=embed)
            return
    async def remove_all():
        mycursor.execute("DELETE FROM {}".format(insult_table_name))
        mydb.commit()
        embed = discord.Embed(title="Löschen Aller Einträge",
                              description=f"Es wurden alle Beleidigungseinträge gelöscht",
                              color=discord.Color.green())
        await message.channel.send(embed=embed)
        return
    async def remove_messages():
        for i in list_of_insults:
            if message.content.lower().replace(" ", "") in i:
                await message.delete()
                return

    if message.content.startswith('$createInsult'):
        if message.author.guild_permissions.administrator:
            await create_insult()
        else:
            print("Check allowed authors")
            for allowed in allowed_authors:
                if message.author.id in allowed:
                    await create_insult()

    if message.content.startswith('$addAllowedUser'):
        if message.author.guild_permissions.administrator:
            await add_user()
        else:
            for allowed in allowed_authors:
                if message.author.id in allowed:
                    await add_user()

    if message.content.startswith('$removeAllowedUser'):
        if message.author.guild_permissions.administrator:
            await remove_user()
        else:
            for allowed in allowed_authors:
                if message.author.id in allowed:
                     await remove_user()

    if message.content.startswith('$addInsult'):
        if message.author.guild_permissions.administrator:
            await add_insult()
        else:
            for allowed in allowed_authors:
                if message.author.id in allowed:
                    await add_insult()

    if message.content.startswith('$removeInsult'):
        if message.author.guild_permissions.administrator:
            await remove_insult()
        else:
            for allowed in allowed_authors:
                if message.author.id in allowed:
                    await remove_insult()

    if message.content.startswith("$removeInsults"):
        if message.author.guild_permissions.administrator:
             await remove_all()
        else:
            for allowed in allowed_authors:
                if message.author.id in allowed:
                    await remove_all()

    await remove_messages()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
bot.run(DISCORD_TOKEN)


