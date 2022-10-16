import datetime
from discord import app_commands
import aiosqlite, discord
from discord.ext import commands
from tasks import choosewinners


async def convert(time):
    pos = ["s", "m", "h", "d", "w"]
    time_dict = {"s": 1, "m": 60, "h": 3600, "d": 3600 * 24, "w": 3600 * 24 * 7}
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
        super().__init__(timeout=None)

    @discord.ui.button(label="0", emoji="🎉", custom_id="JoinGiveaway")
    async def JoinGiveaway(
            self,
            interaction: discord.Interaction,
            button: discord.ui.Button):
        async with aiosqlite.connect('GiveAwayDB.db') as db:

            execute = await db.execute('SELECT * FROM Participators WHERE userid = ? AND msgid = ?',
                                       (interaction.user.id, interaction.message.id))
            fetch = await execute.fetchall()
            match len(fetch):
                case 0:
                    await db.execute('INSERT INTO Participators values(?,?)',
                                     (interaction.user.id, interaction.message.id,))
                    await db.commit()
                    label = int(button.label)
                    label += 1
                    button.label = str(label)
                    await interaction.message.edit(view=self)
                    await interaction.response.send_message(embed=discord.Embed(title="Successfully Joined!",
                                                                                description="Successfully Participated In The Giveaway."),
                                                                                ephemeral=True)
                case _:
                    await interaction.response.send_message("You are already in.", ephemeral=True)


class StartEndCommands(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @app_commands.command()
    async def gstart(
            self,
            interaction: discord.Interaction,
            time: str,
            prize: str,
            amount_of_winners: int):
        async with aiosqlite.connect('GiveAwayDB.db') as db:

            convertedtime = await convert(time)
            match convertedtime:
                case -1:
                    await interaction.response.send_message("Invalid Unit")
                case -2:
                    await interaction.response.send_message("Can not convert time, make sure you wrote the time + unit "
                                                            "correctly.")
                case _:
                    timestamp = discord.utils.format_dt(
                        datetime.datetime.now() + datetime.timedelta(seconds=convertedtime), 'R')
                    embed = discord.Embed(title="🎉 New Giveaway 🎉", description=f"""
**Prize** : {prize}
**Time Left** : {timestamp}
**Hosted By** : {interaction.user.mention}""", colour=discord.Colour.random())
                    await interaction.response.send_message("Giveaway Started!", ephemeral = True)
                    message = await interaction.channel.send(embed=embed, view=JoinGiveaway())
                    await db.execute('insert into Giveaways values(?,?,?,?,?,?,?,?)',
                                     (interaction.guild.id, interaction.channel_id,
                                      message.id, timestamp, prize, interaction.user.id, amount_of_winners, False))
                    await db.commit()

    @app_commands.command()
    async def gend(
            self,
            interaction: discord.Interaction,
            messageid: str
    ):
        async with aiosqlite.connect('GiveAwayDB.db') as db:

            int(messageid)
            fetch = await (await db.execute('SELECT * FROM Giveaways WHERE messageid = ?', (messageid,))).fetchall()
            match len(fetch):
                case 0:
                    await interaction.response.send_message(embed=discord.Embed(title="Command Error",
                                                                                description="This Giveaway Does Not exist.",
                                                                                colour=discord.Colour.red()))
                case _:
                    if fetch[0][7]:
                        await interaction.response.send_message(embed=discord.Embed(title="Error", description="""
This Giveaway Has Already Ended!"""))
                    else:
                        channel = interaction.client.get_channel(fetch[0][1])
                        if channel is not None:
                            embed = await choosewinners(db, messageid, fetch[0][6], fetch[0][4])
                            await interaction.response.send_message("Ended The Giveaway")
                            await channel.send(
                               embed = embed)
                        else:
                            await interaction.response.send_message(
                                "The channel that the giveaway was hosted in Does Not Exist anymore.", ephemeral=True)


async def setup(bot):
    await bot.add_cog(StartEndCommands(bot))
