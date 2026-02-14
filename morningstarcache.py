from datetime import date, datetime

from pricerecord import PriceRecord
from seriesdata import MorningStarSeries
from sqlalchemy import Date, Float, Integer, String, UniqueConstraint, create_engine, select
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


class Base(DeclarativeBase):
    pass


class LocalMorningstarPrice(Base):
    __tablename__ = "morningstar_prices"
    __table_args__ = (UniqueConstraint("bloomberg_ticker", "price_date", name="uq_ticker_price_date"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    bloomberg_ticker: Mapped[str] = mapped_column(String, nullable=False, index=True)
    morningstar_id: Mapped[str] = mapped_column(String, nullable=False)
    fund_id: Mapped[int] = mapped_column(Integer, nullable=False)
    price_date: Mapped[date] = mapped_column(Date, nullable=False)
    open: Mapped[float] = mapped_column(Float, nullable=False)
    high: Mapped[float] = mapped_column(Float, nullable=False)
    low: Mapped[float] = mapped_column(Float, nullable=False)
    close: Mapped[float] = mapped_column(Float, nullable=False)
    volume: Mapped[int] = mapped_column(Integer, nullable=False)
    nav: Mapped[float] = mapped_column(Float, nullable=False)


class MorningstarCache:
    def __init__(self, db_path: str = "morningstar_cache.db"):
        self.db_path = db_path
        self.db_url = f"sqlite:///{db_path}"
        self.engine = create_engine(self.db_url, future=True)

    def init_schema(self):
        Base.metadata.create_all(self.engine)

    def save_series(
        self,
        bloomberg_ticker: str,
        morningstar_id: str,
        fund_id: int,
        series: list[MorningStarSeries],
    ) -> int:
        if not series:
            return 0

        rows = []
        for item in series:
            try:
                normalized_date = self._coerce_to_date(item.date)
            except Exception as ex:
                print(f"Skipping series row with invalid date '{getattr(item, 'date', None)}': {ex}")
                continue

            rows.append(
                {
                    "bloomberg_ticker": bloomberg_ticker,
                    "morningstar_id": morningstar_id,
                    "fund_id": fund_id,
                    "price_date": normalized_date,
                    "open": item.open or 0,
                    "high": item.high or 0,
                    "low": item.low or 0,
                    "close": item.close or 0,
                    "volume": item.volume or 0,
                    "nav": item.nav or 0,
                }
            )

        if not rows:
            return 0

        with Session(self.engine) as session:
            for row in rows:
                stmt = insert(LocalMorningstarPrice).values(**row)
                upsert = stmt.on_conflict_do_update(
                    index_elements=[LocalMorningstarPrice.bloomberg_ticker, LocalMorningstarPrice.price_date],
                    set_={
                        "morningstar_id": row["morningstar_id"],
                        "fund_id": row["fund_id"],
                        "open": row["open"],
                        "high": row["high"],
                        "low": row["low"],
                        "close": row["close"],
                        "volume": row["volume"],
                        "nav": row["nav"],
                    },
                )
                session.execute(upsert)
            session.commit()
        return len(rows)

    def get_latest_cached_date(self, bloomberg_ticker: str) -> date | None:
        with Session(self.engine) as session:
            latest_row = session.execute(
                select(LocalMorningstarPrice.price_date)
                .where(LocalMorningstarPrice.bloomberg_ticker == bloomberg_ticker)
                .order_by(LocalMorningstarPrice.price_date.desc())
                .limit(1)
            ).scalar_one_or_none()

        return latest_row

    def load_cached_pricerecords(self, bloomberg_ticker: str, fund_id: int) -> list[PriceRecord]:
        with Session(self.engine) as session:
            rows = session.execute(
                select(
                    LocalMorningstarPrice.price_date,
                    LocalMorningstarPrice.open,
                    LocalMorningstarPrice.high,
                    LocalMorningstarPrice.low,
                    LocalMorningstarPrice.close,
                    LocalMorningstarPrice.volume,
                    LocalMorningstarPrice.nav,
                )
                .where(LocalMorningstarPrice.bloomberg_ticker == bloomberg_ticker)
                .order_by(LocalMorningstarPrice.price_date.asc())
            ).all()

        return [
            PriceRecord(
                fundId=fund_id,
                date=row[0],
                open=float(row[1]),
                high=float(row[2]),
                low=float(row[3]),
                close=float(row[4]),
                volume=int(row[5]),
                nav=float(row[6]),
            )
            for row in rows
        ]

    @staticmethod
    def _coerce_to_date(value) -> date:
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
            return value
        if isinstance(value, str):
            if "T" in value:
                return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
            return date.fromisoformat(value)
        if isinstance(value, (int, float)):
            timestamp_seconds = value / 1000.0 if value > 1_000_000_000_000 else value
            return datetime.utcfromtimestamp(timestamp_seconds).date()
        raise ValueError(f"Unsupported date value type: {type(value)}")
