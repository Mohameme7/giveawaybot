import aiosqlite
from discord import Embed, Colour

async def choosewinners(connection, messageid, amountofwinners, prize):
        fetch = await (
            await connection.execute("SELECT userid FROM Participators WHERE msgid = ? ORDER BY RANDOM() LIMIT ?",
                                     (messageid, amountofwinners))).fetchall()
        match len(fetch):
            case 0:
                return Embed(title="Giveaway Ended", description="""The giveaway
has ended unfortunately no one participated, No Winners.""")
            case _:
                listofwinners = []
                for row in fetch:
                    listofwinners.append(f"<@{row[0]}>")
                w = '\n'.join(listofwinners)
                return Embed(title="Giveaway Ended", description=f"""Congratulations 
to the following members for winning {prize}:\n {w}""")

async def reroll(connection : aiosqlite.Connection, messageid : int, amountofwinners : int):
          fetch = await (await connection.execute('SELECT * FROM Giveaways where messageid = ?', (messageid,))).fetchall()
          if len(fetch) == 0:
            return Embed(title="Command Error",description="There's no giveaway with this messageid!", colour = Colour.red())
          else:
            winnersfetch = await (await connection.execute("SELECT userid FROM Participators WHERE msgid = ? ORDER BY RANDOM() LIMIT ?", (messageid, amountofwinners,))).fetchall()
            if len(winnersfetch) == 0:
                return Embed(title="Reroll Failed", description="""The giveaway
has no participators thus I can not reroll the giveaway.""", colour = Colour.red())
            else:
                listofwinners = []
                for row in winnersfetch:
                    listofwinners.append(f"<@{row[0]}>")
                return Embed(title="Giveaway Rerolled", description=f"""Congratulations 
                                                                  to the following members for winning {fetch[0][4]}:"""
                                                                         '\n'.join(listofwinners))