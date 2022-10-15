import datetime

from discord.ext.tasks import loop; import aiosqlite, re, discord
from discord.ext import commands

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
             msg = await channel.fetch_message(msgid)
             if channel is not None and msg is not None:
                  execute2 = await db.execute("SELECT userid FROM Participators WHERE msgid = ? ORDER BY RANDOM() LIMIT ?", (msgid, amount_of_winners))
                  winnerfetch = await execute2.fetchall()

                  match len(winnerfetch):
                      case 0:
                        await msg.reply(embed = discord.Embed(title = "Giveaway Ended", description = "The giveaway "
                                                       "has ended unfortunately no one participated, No Winners."))
                      case _:
                          winners = []
                          for winner in winnerfetch:
                               winners.append(f"<@{winner[0]}>")
                          imshitatformatting = '\n'.join(winners)
                          await msg.reply(embed = discord.Embed(title = "Giveaway Ended", description = "Congratulations "
                          f"to the following members for winning {row[4]}:"
                                                                                                        f"{imshitatformatting}"))
                  await db.execute('UPDATE Giveaways SET HasEnded = ? WHERE messageid = ?', (True, msgid,))
                  await db.commit()
             else:
                await db.execute('DELETE FROM Giveaways WHERE messageid = ?', (row[2],))
                await db.commit()



