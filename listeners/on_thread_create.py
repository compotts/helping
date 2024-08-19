from utils.settings import load_config

import disnake
from disnake.ext import commands


class OnThreadCreateListener(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.config = load_config("settings.json")


    @commands.Cog.listener(name="on_thread_create")
    async def on_thread_create(
            self,
            thread: disnake.Thread
    ):
        if thread.parent.id == self.config["forum_id"]:
            in_waiting = thread.parent.get_tag_by_name(
                "В ожидании"
            )

            await thread.edit(applied_tags=[in_waiting])

            view = disnake.ui.View()
            view.add_item(
                disnake.ui.Button(
                    label="Принять диалог",
                    style=disnake.ButtonStyle.gray,
                    custom_id="confirm_acceptance_dialog",
                )
            )
            view.add_item(
                disnake.ui.Button(
                    label="Отказать диалог",
                    style=disnake.ButtonStyle.gray,
                    custom_id="cancel_acceptance_dialog",
                )
            )

            message = await thread.send(
                embed=disnake.Embed(
                    title="Новое обращение",
                    description="Поступило новое обращение, вы можете принять диалог или отказаться\n"
                                "Для принятия диалога нажмите на 'Принять диалог', для отказа нажмите 'Отказать диалог'",
                    color=0x2F3136,

                ).set_thumbnail(url=thread.owner.display_avatar.url),
                view=view
            )
            await message.pin()


def setup(bot: commands.Bot):
    bot.add_cog(OnThreadCreateListener(bot))
