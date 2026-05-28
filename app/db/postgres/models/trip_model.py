from sqlalchemy import ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.db.postgres.session import Base
from app.enums.status_enum import Status


class Trip(Base):
    __tablename__ = "trips"

    id: Mapped[int] = mapped_column(primary_key=True)
    passenger_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    driver_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    status: Mapped[Status] = mapped_column(
        SAEnum(Status, values_callable=lambda x: [e.value for e in x]),
        default=Status.WAITING,
    )
    pickup_address: Mapped[str]
    dropoff_address: Mapped[str]
    pickup_lat: Mapped[float | None] = mapped_column(nullable=True)
    pickup_lon: Mapped[float | None] = mapped_column(nullable=True)
    dropoff_lat: Mapped[float | None] = mapped_column(nullable=True)
    dropoff_lon: Mapped[float | None] = mapped_column(nullable=True)
    price: Mapped[float] = mapped_column(default=0.0)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    passenger: Mapped["User"] = relationship(
        back_populates="trips_as_passenger", foreign_keys=[passenger_id]
    )
    driver: Mapped["User"] = relationship(
        back_populates="trips_as_driver", foreign_keys=[driver_id]
    )
    ratings: Mapped[list["Rating"]] = relationship(back_populates="trip")
