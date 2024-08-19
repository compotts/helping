import ormar
from db.base import base_ormar_config


class SupportTicket(ormar.Model):
    ormar_config = base_ormar_config.copy(
        tablename='support-tickets',
    )

    id: int = ormar.Integer(
        primary_key=True,
        auto_increment=True
    )
    member_id: int = ormar.BigInteger()
    channel_id: int = ormar.BigInteger()


class SupportTicketBlacklist(ormar.Model):
    ormar_config = base_ormar_config.copy(
        tablename='support-ticket-blacklist',
    )

    id: int = ormar.Integer(
        primary_key=True,
        auto_increment=True
    )
    banned_member_id: int = ormar.BigInteger()
    support_member_id: int = ormar.BigInteger()
