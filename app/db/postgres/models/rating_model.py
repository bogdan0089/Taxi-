from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.db.postgres.session import Base


class Rating(Base):
    __tablename__ = "rating"

    id: Mapped[int] = mapped_column(primary_key=True)
    trip_id: Mapped[int] = mapped_column(ForeignKey("trips.id"))
    passenger_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    driver_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    score: Mapped[int]
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    trip: Mapped["Trip"] = relationship(back_populates="ratings")
    passenger: Mapped["User"] = relationship(
        back_populates="ratings_as_passenger", foreign_keys=[passenger_id]
    )
    driver: Mapped["User"] = relationship(
        back_populates="ratings_as_driver", foreign_keys=[driver_id]
    )
