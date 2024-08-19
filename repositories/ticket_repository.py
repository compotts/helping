from db.models import SupportTicket


class TicketRepository:
    def __init__(self):
        self.database = SupportTicket


    async def create(
            self,
            member_id: int,
            channel_id: int
    ) -> None:
        ticket = await self.database.objects.create(
            member_id=member_id,
            channel_id=channel_id
        )


    async def get(
            self,
            member_id: int = None,
            channel_id: int = None
    ) -> SupportTicket:
        ticket = None
        if member_id is not None:
            ticket = await self.database.objects.get_or_none(
                member_id=member_id
            )
        elif channel_id is not None:
            ticket = await self.database.objects.get_or_none(
                channel_id=channel_id
            )

        return ticket


    async def close(
            self,
            member_id: int,
            channel_id: int
    ) -> None:
        ticket = await self.database.objects.filter(
            member_id=member_id,
            channel_id=channel_id
        ).delete()


    # async def get_by_member_id(
    #         self,
    #         member_id: int
    # ):
    #     ticket = await self.database.objects.select_related(
    #         'channel'
    #     ).filter(
    #         member_id=member_id
    #     ).first()
    #
    #     return ticket
    #
    # async def get_by_channel_id(
    #         self,
    #         channel_id: int
    # ):
    #     ticket = await self.database.objects.get_or_none(
    #         channel_id=channel_id
    #     )
    #
    #     return ticket.member_id
