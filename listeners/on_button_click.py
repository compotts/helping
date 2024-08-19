from repositories import TicketRepository
from utils.settings import load_config

import disnake
from disnake.ext import commands


class OnButtonClickListener(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.database = TicketRepository()
        self.config = load_config("settings.json")


    @commands.Cog.listener(name="on_button_click")
    async def acceptance_dialog_buttons_click(
            self,
            interaction: disnake.MessageInteraction
    ):
        if interaction.data.custom_id == "confirm_acceptance_dialog":
            row = await self.database.get(
                channel_id=interaction.channel.id
            )
            if not row:
                await interaction.response.send_message(
                    embed=disnake.Embed(
                        title="Ошибка",
                        description="Похоже, что обращение уже закрыто",
                        color=0x2F3136,
                    ).set_thumbnail(url=interaction.author.display_avatar.url),
                    ephemeral=True,
                )
                await interaction.message.edit(view=None)
                return

            in_waiting = interaction.channel.parent.get_tag_by_name(
                "В ожидании"
            )
            if in_waiting not in interaction.channel.applied_tags:
                await interaction.response.send_message(
                    embed=disnake.Embed(
                        title="Ошибка",
                        description="Похоже, что обращение уже закрыто",
                        color=0x2F3136,
                    ).set_thumbnail(url=interaction.author.display_avatar.url),
                    ephemeral=True,
                )
                await interaction.message.edit(view=None)
                return

            member = interaction.guild.get_member(row.member_id)
            if not member:
                await interaction.response.send_message(
                    embed=disnake.Embed(
                        title="Ошибка",
                        description="Не удалось найти создателя обращения",
                        color=0x2F3136,
                    ).set_thumbnail(url=interaction.author.display_avatar.url),
                    ephemeral=True,
                )
                await interaction.message.edit(view=None)
                return

            try:
                view = disnake.ui.View()
                view.add_item(
                    disnake.ui.Button(
                        label="Закрыть обращение",
                        style=disnake.ButtonStyle.green,
                        custom_id="close_ticket_author",
                    )
                )

                embed = disnake.Embed(
                    title="Пиши сообщения прямо сюда",
                    description="Спасибо за обращение в нашу службу поддержки\n"
                                "Сейчас постараемся решить твой вопрос, оставайся на связи",
                    color=0x2F3136
                )
                await member.send(embed=embed)
            except disnake.HTTPException:
                await interaction.response.send_message(
                    embed=disnake.Embed(
                        title="Ошибка",
                        description="ЛС создателя обращения закрыт, можете закрыть обращение вручную",
                        color=0x2F3136,
                    ),
                    ephemeral=True
                )
                await interaction.message.edit(view=None)
                return

            open_ticket = interaction.channel.parent.get_tag_by_name(
                "Активный тикет"
            )

            embed = disnake.Embed(
                title="Новое обращение",
                description="Не забудьте закрыть обращение нажав на кнопку ниже\n" 
                            "в случае если пользователь его не закрыл и у него нет вопросов",
                color=0x2F3136,
            ).set_thumbnail(url=interaction.channel.owner.display_avatar.url)

            view = disnake.ui.View()
            view.add_item(
                disnake.ui.Button(
                    label="Закрыть обращение",
                    style=disnake.ButtonStyle.green,
                    custom_id="close_ticket_support",
                )
            )

            await interaction.message.edit(
                embed=embed,
                view=view
            )
            await interaction.channel.edit(
                archived=False,
                locked=False,
                applied_tags=[open_ticket]
            )
            await interaction.response.send_message(
                embed=disnake.Embed(
                    title="Вы приняли диалог",
                    description="Вы приняли обращение, можете писать прямо сюда",
                    color=0x2F3136
                ).set_thumbnail(url=interaction.author.display_avatar.url),
                ephemeral=True,
            )

        elif interaction.data.custom_id == "cancel_acceptance_dialog":
            row = await self.database.get(
                channel_id=interaction.channel.id
            )
            if not row:
                await interaction.response.send_message(
                    embed=disnake.Embed(
                        title="Ошибка",
                        description="Похоже, что обращение уже закрыто",
                        color=0x2F3136,
                    ).set_thumbnail(url=interaction.author.display_avatar.url),
                    ephemeral=True,
                )
                await interaction.message.edit(view=None)
                return

            in_waiting = interaction.channel.parent.get_tag_by_name(
                "В ожидании"
            )
            if in_waiting not in interaction.channel.applied_tags:
                await interaction.response.send_message(
                    embed=disnake.Embed(
                        title="Ошибка",
                        description="Похоже, что обращение уже закрыто",
                        color=0x2F3136,
                    ).set_thumbnail(url=interaction.author.display_avatar.url),
                    ephemeral=True,
                )
                await interaction.message.edit(view=None)
                return

            canceled_dialog = interaction.channel.parent.get_tag_by_name(
                "Отклонено"
            )

            await self.database.close(
                member_id=row.member_id,
                channel_id=interaction.channel.id
            )

            member = interaction.guild.get_member(row.member_id)
            if member:
                try:
                    await member.send(
                        embed=disnake.Embed(
                            title="Ваше обращение отклонено",
                            description="Наши саппорты посчитали, что Вы отправили заявку которая не несет серьезного контекста"
                                        "Если Вы продолжите отправлять подобные запросы, то мы будем вынуждены заблокировать Вас в нашей службе поддержке",
                            color=0x2F3136,
                        )
                    )
                except disnake.HTTPException:
                    pass

            await interaction.message.edit(
                embed=disnake.Embed(
                    title="Отклонено",
                    description=f"{interaction.author.mention} отклонил это обращение",
                    color=0x2F3136
                ),
                view=None
            )
            await interaction.response.send_message(
                embed=disnake.Embed(
                    title="Вы отклонили диалог",
                    description="Вы отклонили обращение это обращение",
                    color=0x2F3136
                ).set_thumbnail(url=interaction.author.display_avatar.url),
                ephemeral=True,
            )
            await interaction.channel.edit(
                archived=True,
                locked=True,
                applied_tags=[canceled_dialog]
            )


    @commands.Cog.listener(name="on_button_click")
    async def stop_dialog_buttons_click(
            self,
            interaction: disnake.MessageInteraction
    ):
        if "cancel_stop_dialog" in interaction.data.custom_id:
            await interaction.response.defer()
            await interaction.delete_original_response()

        elif "confirm_stop_dialog" in interaction.data.custom_id:
            if interaction.guild:
                return await interaction.response.send_message(
                    embed=disnake.Embed(
                        title="Ошибка",
                        description="Похоже, что вы не в обращении",
                        color=0x2F3136,
                    ).set_thumbnail(url=interaction.author.display_avatar.url),
                    ephemeral=True,
                )

            guild = self.bot.get_guild(self.config["guild_id"])
            channel_id = int(interaction.data.custom_id.split(":")[1])
            ticket_channel = guild.get_channel_or_thread(channel_id)
            if not ticket_channel:
                return

            open_ticket = ticket_channel.parent.get_tag_by_name(
                "Активный тикет"
            )
            solved_ticket = ticket_channel.parent.get_tag_by_name(
                "Решено"
            )
            await ticket_channel.send(
                embed=disnake.Embed(
                    title="Обращение закрыто",
                    description=f"{interaction.author.mention} закрыл обращение принудительно",
                    color=0x2F3136
                ).set_thumbnail(url=interaction.author.display_avatar.url)
            )
            await ticket_channel.edit(
                archived=True,
                locked=True,
                applied_tags=[solved_ticket]
            )
            await self.database.close(
                member_id=interaction.author.id,
                channel_id=ticket_channel.id
            )

            await interaction.response.edit_message(
                embed=disnake.Embed(
                    title="Вы закрыли обращение",
                    description="Вы решили прервать диалог\n" 
                                "Если Вы будете прерывать диалог без веской причины, то можете получить\n"
                                "блокировку в нашей службе поддержки",
                    color=0x2F3136
                ),
                view=None
            )


    @commands.Cog.listener(name="on_button_click")
    async def close_buttons_click(
            self,
            interaction: disnake.MessageInteraction
    ):
        if interaction.data.custom_id == "close_ticket_support":
            if (
                    not isinstance(interaction.channel, disnake.Thread)
                    or interaction.channel.parent.id != self.config["forum_id"]
            ):
                return await interaction.response.send_message(
                    embed=disnake.Embed(
                        title="Ошибка",
                        description="Похоже, что вы не в обращении",
                        color=0x2F3136,
                    ).set_thumbnail(url=interaction.author.display_avatar.url),
                    ephemeral=True,
                )

            open_ticket = interaction.channel.parent.get_tag_by_name(
                "Активный тикет"
            )
            solved_ticket = interaction.channel.parent.get_tag_by_name(
                "Решено"
            )
            if solved_ticket in interaction.channel.applied_tags or open_ticket not in interaction.channel.applied_tags:
                await interaction.response.send_message(
                    embed=disnake.Embed(
                        title="Обращение закрыто",
                        description="Похоже, что обращение уже закрыто",
                        color=0x2F3136,
                    ).set_thumbnail(url=interaction.author.display_avatar.url),
                    ephemeral=True,
                )
                await interaction.message.edit(view=None)
                return

            row = await self.database.get(
                channel_id=interaction.channel.id
            )
            if not row:
                await interaction.response.send_message(
                    embed=disnake.Embed(
                        title="Ошибка",
                        description="Похоже, что обращение уже закрыто",
                        color=0x2F3136,
                    ).set_thumbnail(url=interaction.author.display_avatar.url),
                    ephemeral=True,
                )

            await interaction.response.send_message(
                embed=disnake.Embed(
                    title="Обращение закрыто",
                    description="Вы закрыли это обращение",
                    color=0x2F3136,
                ).set_thumbnail(url=interaction.author.display_avatar.url),
                ephemeral=True,
            )

            await interaction.message.edit(view=None)
            await interaction.channel.edit(
                archived=True,
                locked=True,
                applied_tags=[solved_ticket]
            )
            await self.database.close(
                member_id=row.member_id,
                channel_id=interaction.channel.id
            )
            member = interaction.guild.get_member(row.member_id)
            if member:
                try:
                    await member.send(
                        embed=disnake.Embed(
                            title="Ваше обращение закрыто",
                            description="Саппорт закрыл ваше обращение",
                            color=0x2F3136
                        ).set_thumbnail(url=member.display_avatar.url)
                    )
                except disnake.HTTPException:
                    pass

        elif interaction.data.custom_id == "close_ticket_author":
            if interaction.guild:
                return await interaction.response.send_message(
                    embed=disnake.Embed(
                        title="Ошибка",
                        description="Похоже, что вы не в обращении",
                        color=0x2F3136,
                    ).set_thumbnail(url=interaction.author.display_avatar.url),
                    ephemeral=True,
                )

            row = await self.database.get(
                member_id=interaction.author.id
            )
            if not row:
                await interaction.message.edit(view=None)
                return await interaction.response.send_message(
                    embed=disnake.Embed(
                        title="Закрыть обращение",
                        description="У вас нету открытого обращения",
                        color=0x2F3136,
                    ).set_thumbnail(url=interaction.author.display_avatar.url),
                    ephemeral=True,
                )

            view = disnake.ui.View()
            view.add_item(
                disnake.ui.Button(
                    emoji="✅",
                    style=disnake.ButtonStyle.gray,
                    custom_id=f"confirm_stop_dialog:{row.channel_id}",
                )
            )
            view.add_item(
                disnake.ui.Button(
                    emoji="❌",
                    style=disnake.ButtonStyle.gray,
                    custom_id="cancel_stop_dialog",
                )
            )
            await interaction.response.send_message(
                embed=disnake.Embed(
                    title="Прервать диалог",
                    description=f"{interaction.author.mention}, Вы **уверены**, что хотите **прервать** диалог?\n"
                                "Если Вы будете прерывать диалог **без веской причины**, то\n"
                                "**можете получить блокировку** в нашей службе поддержки\n"
                                "Для **согласия** нажмите на :white_check_mark:, для **отказа** на :x:",
                    color=0x2F3136,
                ).set_thumbnail(url=interaction.author.display_avatar.url),
                view=view,
            )


def setup(bot: commands.Bot):
    bot.add_cog(OnButtonClickListener(bot))
