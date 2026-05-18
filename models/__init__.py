import logging

from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    pass


class Player(Base):
    """ORM model for a player.

    Attributes:
        id: Basketball Reference player ID (e.g. ``martike01``), used as primary key.
        name: Player name.
        draft_year: Year the player was drafted, or None if undrafted.
        draft_position: Overall pick number, or None if undrafted.
        nba_career_stats: Related NBACareerStats record, if present.
    """

    __tablename__ = "players"
    __table_args__ = {"schema": "nba"}

    id: Mapped[str] = mapped_column(String(20), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    draft_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    draft_position: Mapped[int | None] = mapped_column(Integer, nullable=True)

    nba_career_stats: Mapped["NBACareerStats"] = relationship(back_populates="player")

    @classmethod
    def from_draft_stats(cls, stats: dict, draft_year: int | None = None) -> "Player":
        """Create a Player instance from a dict yielded by get_draft_stats.

        Args:
            stats: Dict with keys ``player``, ``player_id``, and optionally ``pick_overall``.
            draft_year: Year the player was drafted, or None if undrafted.

        Returns:
            A new Player instance.
        """
        player_id = stats.get("player_id")
        player_name = stats.get("player")
        if not player_id or not player_name:
            raise ValueError(
                f"stats dict missing required keys 'player_id' or 'player': {stats!r}"
            )
        pick_raw = stats.get("pick_overall")
        try:
            draft_position = int(pick_raw) if pick_raw else None
        except ValueError:
            logger.warning(
                "Player %s (%s) has non-numeric pick_overall %r — setting draft_position=None",
                player_name,
                player_id,
                pick_raw,
            )
            draft_position = None
        return cls(
            id=player_id,
            name=player_name,
            draft_year=draft_year,
            draft_position=draft_position,
        )


class NBACareerStats(Base):
    """ORM model for NBA player career stats sourced from Basketball Reference draft pages.

    Attributes:
        player_id: FK to players.id.
        ws: Win Shares.
        ws_48: Win Shares Per 48 Minutes.
        bpm: Box Plus/Minus.
        vorp: Value Over Replacement Player.
        player: Related Player record.
    """

    __tablename__ = "career_stats"
    __table_args__ = {"schema": "nba"}

    player_id: Mapped[str] = mapped_column(
        String(20), ForeignKey("nba.players.id"), primary_key=True
    )
    ws: Mapped[float | None] = mapped_column(Float, nullable=True)
    ws_48: Mapped[float | None] = mapped_column(Float, nullable=True)
    bpm: Mapped[float | None] = mapped_column(Float, nullable=True)
    vorp: Mapped[float | None] = mapped_column(Float, nullable=True)

    player: Mapped["Player"] = relationship(back_populates="nba_career_stats")

    @classmethod
    def from_draft_stats(cls, player_id: str, stats: dict) -> "NBACareerStats":
        """Create an NBACareerStats instance from a dict yielded by get_draft_stats.

        Args:
            player_id: Basketball Reference player ID.
            stats: Dict with keys ``ws``, ``ws_per_48``, ``bpm``, ``vorp``.

        Returns:
            A new NBACareerStats instance with float-converted stat values.
        """

        def to_float(value: str | None) -> float | None:
            try:
                return float(value) if value else None
            except ValueError:
                return None

        return cls(
            player_id=player_id,
            ws=to_float(stats.get("ws")),
            ws_48=to_float(stats.get("ws_per_48")),
            bpm=to_float(stats.get("bpm")),
            vorp=to_float(stats.get("vorp")),
        )
