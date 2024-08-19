from repositories import TicketRepository, BlacklistRepository
from utils.settings import load_config

import json
import disnake
from disnake.ext import commands


class SupportTicket(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.database = TicketRepository()
        self.blacklist_database = BlacklistRepository()
        self.config = load_config("settings.json")


    @commands.slash_command(name="установить_систему", description="Установить систему обращений")
    async def setup(
            self,
            inter: disnake.AppCmdInter,
            forum: disnake.ForumChannel = commands.Param(
                default=None,
                description="Форум для обращений, если не указано, то будет создан"
            )
    ):
        await inter.response.defer(ephemeral=True)

        forum = forum if forum else await inter.guild.create_forum_channel(
            name="Обращения",
            reason="Установка системы обращений",
            available_tags=[
                disnake.ForumTag(
                    name="В ожидании",
                ),
                disnake.ForumTag(
                    name="Активный тикет",
                ),
                disnake.ForumTag(
                    name="Решено",
                ),
                disnake.ForumTag(
                    name="Отклонено",
                )
            ]
        )

        self.config["forum_id"] = forum.id
        self.config["guild_id"] = inter.guild.id
        with open(
                "settings.json",
                "w",
                encoding="utf-8"
        ) as f:
            json.dump(
                self.config,
                f,
                ensure_ascii=False,
                indent=4
            )

        await inter.edit_original_response(
            embed=disnake.Embed(
                title="Система обращений успешно установлена",
                description="Система обращений успешно установлена",
                color=0x2F3136,
            ).set_thumbnail(url=inter.author.display_avatar.url)
        )



    @commands.slash_command(name="помощь", description="Открыть обращение")
    async def support(
            self,
            inter: disnake.AppCmdInter,
            question: str = commands.Param(description="Распишите свой вопрос")
    ):
        await inter.response.defer(ephemeral=True)

        banned = await self.blacklist_database.get(
            banned_member_id=inter.author.id
        )
        if banned:
            return await inter.edit_original_response(
                embed=disnake.Embed(
                    title="Нет доступа",
                    description="У вас запрет на обращения в службу поддержки",
                    color=0x2F3136,
                ).set_thumbnail(url=inter.author.display_avatar.url)
            )

        existing_ticket = await self.database.get(
            member_id=inter.author.id
        )
        if existing_ticket:
            return await inter.edit_original_response(
                embed=disnake.Embed(
                    title="Открыть обращение",
                    description="У вас **уже** есть **открытое** обращение, **дождитесь** на него ответа",
                    color=0x2F3136,
                ).set_thumbnail(url=inter.author.display_avatar.url)
            )

        forum_channel = inter.guild.get_channel(self.config["forum_id"])
        if not forum_channel:
            return await inter.edit_original_response(
                embed=disnake.Embed(
                    title="Похоже, что возникла проблема, сообщите администрации",
                    color=0x2F3136,
                ).set_thumbnail(url=inter.author.display_avatar.url)
            )

        try:
            await inter.author.send(
                embed=disnake.Embed(
                    title="Ваше обращение успешно отправлено",
                    description="Ожидайте...",
                    color=0x2F3136,
                ).set_author(
                    name="Служба поддержки",
                    icon_url=inter.guild.icon.url
                )
            )
        except disnake.HTTPException:
            return await inter.edit_original_response(
                embed=disnake.Embed(
                    title="Похоже, что ваш ЛС закрыт, откройте и попробуйте снова",
                    color=0x2F3136,
                ).set_thumbnail(url=inter.author.display_avatar.url)
            )

        number = None
        last_appeal_channel_id = forum_channel.last_thread_id
        if last_appeal_channel_id:
            last_appeal_channel = await inter.guild.fetch_channel(last_appeal_channel_id)
            if last_appeal_channel:
                last_id = last_appeal_channel.name.split("№")[1]
                number = int(last_id) + 1
            else:
                number = 1
        else:
            number = 1

        ticket = await forum_channel.create_thread(
            name=f"Обращение №{number}",
            content=f"Обращение от {inter.author.mention}",
            embed=disnake.Embed(
                title="Новое обращение",
                description=(
                    f"Новое обращение от {inter.author.mention} ({inter.author.id})\n"
                    f"Вопрос:\n ```{question}```"
                ),
                color=0x2F3136,
            )
        )

        await self.database.create(
            member_id=inter.author.id,
            channel_id=ticket.thread.id
        )

        await inter.edit_original_response(
            embed=disnake.Embed(
                title="Ваше обращение успешно отправлено",
                description="Спасибо за обращение в нашу службу поддержки\n"
                            "Сейчас постараемся решить твой вопрос, оставайся на связи",
                color=0x2F3136
            ).set_thumbnail(url=inter.author.display_avatar.url)
        )


    @commands.slash_command(name="help_ban", description="Блокировка пользователя в системе обращений")
    async def ban(
            self,
            inter: disnake.AppCmdInter,
            user: disnake.Member = commands.Param(description="Пользователь, которого необходимо заблокировать")
    ):
        if user.bot or user.system:
            return await inter.response.send_message(
                embed=disnake.Embed(
                    title="Нет доступа",
                    description="Нельзя использовать на этого пользователя",
                    color=0x2F3136,
                ).set_thumbnail(url=inter.author.display_avatar.url),
                ephemeral=True
            )

        if_banned = await self.blacklist_database.get(
            banned_member_id=user.id
        )
        if if_banned:
            return await inter.response.send_message(
                embed=disnake.Embed(
                    title="Пользователь уже заблокирован",
                    description="У пользователя уже есть запрет на обращения в службу поддержки",
                    color=0x2F3136,
                ).set_thumbnail(url=inter.author.display_avatar.url),
                ephemeral=True
            )

        if_active_ticket = await self.database.get(
            member_id=user.id
        )
        if if_active_ticket:
            ticket_channel = inter.guild.get_channel_or_thread(if_active_ticket.channel_id)
            if not ticket_channel:
                return

            solved_ticket = ticket_channel.parent.get_tag_by_name(
                "Решено"
            )
            if solved_ticket in ticket_channel.applied_tags:
                return

            await ticket_channel.send(
                embed=disnake.Embed(
                    title="Обращение закрыто",
                    description=f"{inter.author.mention} выдал блокировку обращений в службу поддержки для {user.mention}\n"
                                "Обращение закрыто автоматически",
                    color=0x2F3136,
                ).set_thumbnail(url=inter.author.display_avatar.url),
            )
            await ticket_channel.edit(
                archived=True,
                locked=True,
                applied_tags=[solved_ticket]
            )
            await self.database.close(
                member_id=user.id,
                channel_id=ticket_channel.id
            )

            try:
                await user.send(
                    embed=disnake.Embed(
                        title="Вам выдана блокировка",
                        description=f"{user.mention}, вам выдана блокировка в службе поддержки, ваши обращения\n"
                                    "будут закрыты автоматически",
                        color=0x2F3136
                    ).set_thumbnail(url=user.display_avatar.url)
                )
            except disnake.HTTPException:
                pass


        await self.blacklist_database.create(
            banned_member_id=user.id,
            support_member_id=inter.author.id
        )

        await inter.response.send_message(
            embed=disnake.Embed(
                title="Пользователь заблокирован",
                description="Пользователь заблокирован в системе обращений, его открытые обращения будут закрыты автоматически",
                color=0x2F3136,
            ).set_thumbnail(url=inter.author.display_avatar.url),
            ephemeral=True
        )


    @commands.slash_command(name="help_unban", description="Разблокировка пользователя в системе обращений")
    async def unban(
            self,
            inter: disnake.AppCmdInter,
            user: disnake.Member = commands.Param(description="Пользователь, которого необходимо разблокировать")
    ):
        if user.bot or user.system:
            return await inter.response.send_message(
                embed=disnake.Embed(
                    title="Нет доступа",
                    description="Нельзя использовать на этого пользователя",
                    color=0x2F3136,
                ).set_thumbnail(url=inter.author.display_avatar.url),
                ephemeral=True
            )

        if_banned = await self.blacklist_database.get(
            banned_member_id=user.id
        )
        if not if_banned:
            return await inter.response.send_message(
                embed=disnake.Embed(
                    title="Пользователь не заблокирован",
                    description="У пользователя нет запрета на обращения в службу поддержки",
                    color=0x2F3136,
                ).set_thumbnail(url=inter.author.display_avatar.url),
                ephemeral=True
            )

        await self.blacklist_database.delete(
            banned_member_id=user.id
        )

        try:
            await user.send(
                embed=disnake.Embed(
                    title="С вас снята блокировка",
                    description=f"{user.mention}, с вас снята блокировка в службе поддержки",
                    color=0x2F3136
                ).set_thumbnail(url=user.display_avatar.url)
            )
        except disnake.HTTPException:
            pass

        await inter.response.send_message(
            embed=disnake.Embed(
                title="Пользователь разблокирован",
                description="Пользователь разблокирован в системе обращений",
                color=0x2F3136,
            ).set_thumbnail(url=inter.author.display_avatar.url),
            ephemeral=True
        )


def setup(bot: commands.Bot):
    bot.add_cog(SupportTicket(bot))
