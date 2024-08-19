from db.models import SupportTicketBlacklist


class BlacklistRepository:
    def __init__(self):
        self.database = SupportTicketBlacklist


    async def create(
            self,
            banned_member_id: int,
            support_member_id: int
    ) -> None:
        ticket = await self.database.objects.create(
            banned_member_id=banned_member_id,
            support_member_id=support_member_id
        )


    async def get(
            self,
            banned_member_id: int
    ) -> SupportTicketBlacklist:
        ticket = await self.database.objects.get_or_none(
            banned_member_id=banned_member_id
        )
        return ticket


    async def delete(
            self,
            banned_member_id: int,
    ) -> None:
        await self.database.objects.filter(
            banned_member_id=banned_member_id
        ).delete()
