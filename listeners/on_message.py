from repositories import TicketRepository
from utils.settings import load_config

import disnake
from disnake.ext import commands


class OnMessageListener(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.database = TicketRepository()
        self.config = load_config("settings.json")


    @commands.Cog.listener(name="on_message")
    async def on_message_thread(
            self,
            message: disnake.Message
    ):
        if message.author.bot:
            return

        if (
                not isinstance(message.channel, disnake.Thread)
                or message.channel.parent.id != self.config["forum_id"]
        ):
            return

        solved_ticket = message.channel.parent.get_tag_by_name(
            "Решено"
        )
        in_waiting = message.channel.parent.get_tag_by_name(
            "В ожидании"
        )

        if solved_ticket in message.channel.applied_tags or in_waiting in message.channel.applied_tags:
            return

        row = await self.database.get(
            channel_id=message.channel.id
        )
        if not row:
            return

        member = message.guild.get_member(row.member_id)
        if member:
            try:
                embed = disnake.Embed(
                    description=message.content,
                    color=0x2F3136,
                ).set_author(
                    name="Служба поддержки",
                    icon_url=message.guild.icon.url
                )
                if message.attachments:
                    if len(message.attachments) > 1:
                        for att in message.attachments:
                            file = await att.to_file()
                            if not file:
                                continue

                            embed.set_image(file=file)
                            await member.send(embed=embed)
                    else:
                        file = await message.attachments[0].to_file()
                        if file:
                            embed.set_image(file=file)
                            await member.send(embed=embed)
                else:
                    await member.send(
                        embed=embed
                    )
            except disnake.HTTPException:
                await message.channel.send(
                    embed=disnake.Embed(
                        title="Ошибка",
                        description="У пользователя закрыт ЛС, можно закрыть обращение вручную",
                        color=0x2F3136,
                    ).set_thumbnail(url=message.author.display_avatar.url)
                )


    @commands.Cog.listener(name="on_message")
    async def on_message_dm(
            self,
            message: disnake.Message
    ):
        if message.author.bot:
            return

        if not isinstance(message.channel, disnake.DMChannel):
            return

        row = await self.database.get(
            member_id=message.author.id
        )
        if not row:
            return

        guild = self.bot.get_guild(self.config["guild_id"])
        ticket_channel = guild.get_channel_or_thread(row.channel_id)
        if not ticket_channel:
            return

        solved_ticket = ticket_channel.parent.get_tag_by_name(
            "Решено"
        )
        in_waiting = ticket_channel.parent.get_tag_by_name(
            "В ожидании"
        )

        print(123)
        print(ticket_channel.applied_tags)
        if solved_ticket in ticket_channel.applied_tags or in_waiting in ticket_channel.applied_tags:
            return
        print(456)

        embed = disnake.Embed(
            description=message.content,
            color=0x2F3136,
        ).set_author(
            name=message.author.display_name,
            icon_url=guild.icon.url
        )

        if message.attachments:
            if len(message.attachments) > 1:
                for att in message.attachments:
                    file = await att.to_file()
                    if not file:
                        continue

                    embed.set_image(file=file)
                    await ticket_channel.send(
                        embed=embed
                    )
            else:
                file = await message.attachments[0].to_file()
                if file:
                    embed.set_image(file=file)
                    await ticket_channel.send(
                        embed=embed
                    )
                else:
                    return
        else:
            await ticket_channel.send(
                embed=embed
            )


def setup(bot: commands.Bot):
    bot.add_cog(OnMessageListener(bot))
