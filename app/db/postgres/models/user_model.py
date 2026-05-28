from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.db.postgres.session import Base
from app.enums.role_enum import Role


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True)
    hashed_password: Mapped[str]
    full_name: Mapped[str]
    role: Mapped[Role] = mapped_column(
        SAEnum(Role, values_callable=lambda x: [e.value for e in x]),
        default=Role.PASSENGER,
    )
    is_verified: Mapped[bool] = mapped_column(default=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    avg_rating: Mapped[float] = mapped_column(default=0.0)
    payment_id: Mapped[str | None] = mapped_column(nullable=True)

    trips_as_passenger: Mapped[list["Trip"]] = relationship(
        back_populates="passenger", foreign_keys="[Trip.passenger_id]"
    )
    trips_as_driver: Mapped[list["Trip"]] = relationship(
        back_populates="driver", foreign_keys="[Trip.driver_id]"
    )
    ratings_as_passenger: Mapped[list["Rating"]] = relationship(
        back_populates="passenger", foreign_keys="[Rating.passenger_id]"
    )
    ratings_as_driver: Mapped[list["Rating"]] = relationship(
        back_populates="driver", foreign_keys="[Rating.driver_id]"
    )
