
from discord.ext import commands; import discord, aiosqlite, json, os
from tasks import giveawaychecker
from cogs.StartEndGiveaway import JoinGiveaway
BotConfiguration = json.load(open('config.json'))

class Bot(commands.Bot):
    def __init__(self):

        super().__init__(command_prefix = BotConfiguration['Prefix'], case_insensitive =
    BotConfiguration['Commands_IncaseSensitive'], intents = discord.Intents.all())
    async def on_ready(self):
        print(f"""
- User : {self.user}
- Guild Count : {len(self.guilds)}
        """)

        async with aiosqlite.connect('GiveAwayDB.db') as db:

            await db.execute('CREATE TABLE IF NOT EXISTS Giveaways(guildid int, channelid int, messageid int,'
                             'unixtimestamp text, prize text, hosteruserid int, AmountOfWinners int, HasEnded BOOLEAN)')
            await db.execute('CREATE TABLE IF NOT EXISTS Participators(userid int, msgid int)')
            await db.commit()
            print("Successfully Connected To Database")
        await giveawaychecker.start(client)
    async def setup_hook(self):
        for cog in os.listdir('cogs'):
          if cog.endswith('.py'):
            await self.load_extension(f"cogs.{cog[:-3]}")
        self.add_view(JoinGiveaway())


client = Bot()

@client.command()
async def synctree(ctx):
    await client.tree.sync()
    await ctx.send("Synced")



try:
 client.run(BotConfiguration["Token"])
except:
    print("Invalid Token Or Intents are disabled on your developer panel, make sure to enable all of them.")