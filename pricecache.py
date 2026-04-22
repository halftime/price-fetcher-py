from datetime import date, datetime

from pricerecord import MinimalPriceRecord
from sqlalchemy import Date, Float, Integer, String, UniqueConstraint, create_engine, select
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


class Base(DeclarativeBase):
    pass


class LocalPrice(Base):
    __tablename__ = "price_cache"
    __table_args__ = (UniqueConstraint("symbol", "price_date", name="uq_symbol_price_date"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(String, nullable=False, index=True)
    price_date: Mapped[date] = mapped_column(Date, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)


class PriceCache:
    def __init__(self, db_path: str = "price_cache.db"):
        self.db_path = db_path
        self.db_url = f"sqlite:///{db_path}"
        self.engine = create_engine(self.db_url, future=True)

    def init_schema(self):
        Base.metadata.create_all(self.engine)

    def save_prices(self, symbol: str, prices: dict[date, float]) -> int:
        if not prices:
            return 0

        rows = []
        for raw_date, raw_price in prices.items():
            try:
                normalized_date = self._coerce_to_date(raw_date)
            except Exception as ex:
                print(f"Skipping price row with invalid date '{raw_date}': {ex}")
                continue

            rows.append(
                {
                    "symbol": symbol,
                    "price_date": normalized_date,
                    "price": float(raw_price),
                }
            )

        if not rows:
            return 0

        with Session(self.engine) as session:
            for row in rows:
                stmt = insert(LocalPrice).values(**row)
                upsert = stmt.on_conflict_do_update(
                    index_elements=[LocalPrice.symbol, LocalPrice.price_date],
                    set_={
                        "price": row["price"],
                    },
                )
                session.execute(upsert)
            session.commit()

        return len(rows)

    def get_latest_cached_date(self, symbol: str) -> date | None:
        with Session(self.engine) as session:
            latest_row = session.execute(
                select(LocalPrice.price_date)
                .where(LocalPrice.symbol == symbol)
                .order_by(LocalPrice.price_date.desc())
                .limit(1)
            ).scalar_one_or_none()

        return latest_row

    def load_cached_pricerecords(
        self,
        symbol: str,
        investment_id: int,
        from_date_exclusive: date | None = None,
    ) -> list[MinimalPriceRecord]:
        with Session(self.engine) as session:
            stmt = (
                select(LocalPrice.price_date, LocalPrice.price)
                .where(LocalPrice.symbol == symbol)
                .order_by(LocalPrice.price_date.asc())
            )
            if from_date_exclusive is not None:
                stmt = stmt.where(LocalPrice.price_date > from_date_exclusive)
            rows = session.execute(stmt).all()

        return [
            MinimalPriceRecord(
                investmentId=investment_id,
                date=row[0],
                price=float(row[1]),
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
