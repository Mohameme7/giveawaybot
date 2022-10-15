import datetime
from discord import app_commands
import aiosqlite, discord
from discord.ext import commands
from discord.app_commands import AppCommandError
async def convert(time):
    pos = ["s", "m", "h", "d", "w"]
    time_dict = {"s": 1, "m": 60, "h": 3600, "d": 3600 * 24, "w" : 3600*24*7}
    unit = time[-1]

    if unit not in pos:
        return -1
    try:
        val = int(time[:-1])
    except:
        return -2

    return val * time_dict[unit]

class JoinGiveaway(discord.ui.View):
    def __init__(self):
        super().__init__(timeout = None)

    @discord.ui.button(label = "0", emoji= "🎉", custom_id = "JoinGiveaway")
    async def JoinGiveaway(self, interaction : discord.Interaction, button : discord.ui.Button):
      self.db = await aiosqlite.connect('GiveAwayDB.db')
      execute = await self.db.execute('SELECT * FROM Participators WHERE userid = ? AND msgid = ?', (interaction.user.id, interaction.message.id))
      fetch = await execute.fetchall()
      match len(fetch):
          case 0:
              await self.db.execute('INSERT INTO Participators values(?,?)', (interaction.user.id, interaction.message.id,))
              await self.db.commit()
              await interaction.response.send_message(embed = discord.Embed(title = "joined", description="joined") , ephemeral = True)
          case _:
              await interaction.response.send_message("Your are already in.", ephemeral = True)

class StartEndCommands(commands.Cog):
    def __init__(self, client : commands.Bot):
        self.client = client

    @app_commands.command()
    async def gstart(self, interaction : discord.Interaction, time : str, prize : str, amount_of_winners : int):
        self.db = await aiosqlite.connect('GiveAwayDB.db')

        convertedtime = await convert(time)
        match convertedtime:
            case -1:
                await interaction.response.send_message("Invalid Unit")
            case -2:
                await interaction.response.send_message("Can not convert time, make sure you wrote the time + unit correctly.")
            case _:
             timestamp = discord.utils.format_dt(datetime.datetime.now() + datetime.timedelta(seconds = convertedtime), 'R')
             embed = discord.Embed(title = "🎉 New Giveaway 🎉", description = f"""
**Prize** : {prize}
**Time Left** : {timestamp}
**Hosted By** : {interaction.user.mention}""", colour = discord.Colour.random())
             message = await interaction.channel.send(embed = embed, view = JoinGiveaway())
             await self.db.execute('insert into Giveaways values(?,?,?,?,?,?,?,?)', (interaction.guild.id, interaction.channel_id,
                                           message.id, timestamp, prize, interaction.user.id, amount_of_winners, False))
             await self.db.commit()



async def setup(bot):
    await bot.add_cog(StartEndCommands(bot))