from enum import StrEnum

from sqlalchemy import Float, ForeignKey, ForeignKeyConstraint, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class SportTypeEnum(StrEnum):
    NBA = "NBA"
    NFL = "NFL"
    MLB = "MLB"
    NCAA = "NCAA"


class Base(DeclarativeBase):
    pass


class SportType(Base):
    """ORM model for a sport type.

    Attributes:
        code: Short sport identifier (e.g. ``NBA``), used as primary key.
    """

    __tablename__ = "sport_types"

    code: Mapped[str] = mapped_column(String(20), primary_key=True)


class Player(Base):
    """ORM model for a player across sports.

    Attributes:
        id: Basketball Reference player ID (e.g. ``martike01``), used as primary key.
        name: Player name.
        sport: Sport discriminator (see SportTypeEnum).
    """

    __tablename__ = "players"
    __mapper_args__ = {
        "polymorphic_on": "sport",
    }

    id: Mapped[str] = mapped_column(String(20), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    sport: Mapped[str] = mapped_column(
        String(20), ForeignKey("sport_types.code"), primary_key=True
    )


class NBAPlayer(Player):
    """Player subtype for NBA players.

    Attributes:
        advanced_stats: Related NBAAdvancedStats record.
    """

    __mapper_args__ = {"polymorphic_identity": SportTypeEnum.NBA}

    advanced_stats: Mapped["NBAAdvancedStats"] = relationship(back_populates="player")

    @classmethod
    def from_draft_stats(cls, stats: dict) -> "NBAPlayer":
        """Create an NBAPlayer instance from a dict yielded by get_draft_stats.

        Args:
            stats: Dict with keys ``player``, ``player_id``.

        Returns:
            A new NBAPlayer instance.
        """
        return cls(id=stats["player_id"], name=stats["player"])


class NBAAdvancedStats(Base):
    """ORM model for NBA player advanced stats sourced from Basketball Reference draft pages.

    Attributes:
        player_id: FK to players.id.
        player_sport: FK to players.sport.
        ws: Win Shares.
        ws_48: Win Shares Per 48 Minutes.
        bpm: Box Plus/Minus.
        vorp: Value Over Replacement Player.
        player: Related NBAPlayer record.
    """

    __tablename__ = "advanced_stats"
    __table_args__ = (
        ForeignKeyConstraint(
            ["player_id", "player_sport"],
            ["players.id", "players.sport"],
        ),
    )

    player_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    player_sport: Mapped[str] = mapped_column(String(20), default=SportTypeEnum.NBA)
    ws: Mapped[float | None] = mapped_column(Float, nullable=True)
    ws_48: Mapped[float | None] = mapped_column(Float, nullable=True)
    bpm: Mapped[float | None] = mapped_column(Float, nullable=True)
    vorp: Mapped[float | None] = mapped_column(Float, nullable=True)

    player: Mapped["NBAPlayer"] = relationship(back_populates="advanced_stats")

    @classmethod
    def from_draft_stats(cls, player_id: str, stats: dict) -> "NBAAdvancedStats":
        """Create an NBAAdvancedStats instance from a dict yielded by get_draft_stats.

        Args:
            player_id: Basketball Reference player ID.
            stats: Dict with keys ``ws``, ``ws_48``, ``bpm``, ``vorp``.

        Returns:
            A new NBAAdvancedStats instance with float-converted stat values.
        """

        def to_float(value: str | None) -> float | None:
            try:
                return float(value) if value else None
            except ValueError:
                return None

        return cls(
            player_id=player_id,
            player_sport=SportTypeEnum.NBA,
            ws=to_float(stats.get("ws")),
            ws_48=to_float(stats.get("ws_48")),
            bpm=to_float(stats.get("bpm")),
            vorp=to_float(stats.get("vorp")),
        )
