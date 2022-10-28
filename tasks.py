import datetime
from discord.ext.tasks import loop; import aiosqlite, re
from discord.ext import commands
from utilities import choosewinners
@loop(seconds = 5)
async def giveawaychecker(client : commands.Bot):
    async with aiosqlite.connect('GiveAwayDB.db') as db:
        execute = await db.execute('SELECT * FROM Giveaways')
        fetch = await execute.fetchall()
        for row in fetch:
            if not row[7]:
             channelid = row[1]; msgid = row[2]; timestamp = row[3]; amount_of_winners = row[6]
             date = datetime.datetime.fromtimestamp(int(re.search(r'\d+', timestamp).group()))

             if date > datetime.datetime.now():
                 continue

             channel = client.get_channel(channelid)
             if channel is not None:
                  embed = await choosewinners(db, msgid, amount_of_winners, fetch[0][4])
                  await channel.send(embed=embed)

                  await db.execute('UPDATE Giveaways SET HasEnded = ? WHERE messageid = ?', (True, msgid,))
                  await db.commit()
             else:
                await db.execute('DELETE FROM Giveaways WHERE messageid = ?', (row[2],))
                await db.commit()



