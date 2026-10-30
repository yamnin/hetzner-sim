from datetime import datetime, timezone

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base

# Catálogo simplificado de tipos de servidor Hetzner Cloud
SERVER_TYPES = {
    "cx22": {"cores": 2, "memory_gb": 4, "disk_gb": 40, "price_eur_month": 4.59},
    "cx32": {"cores": 4, "memory_gb": 8, "disk_gb": 80, "price_eur_month": 7.59},
    "cx42": {"cores": 8, "memory_gb": 16, "disk_gb": 160, "price_eur_month": 18.59},
    "cpx11": {"cores": 2, "memory_gb": 2, "disk_gb": 40, "price_eur_month": 5.18},
}
LOCATIONS = ["fsn1", "nbg1", "hel1", "ash", "hil"]
IMAGES = ["ubuntu-24.04", "ubuntu-22.04", "debian-12", "rocky-9"]


class Server(Base):
    __tablename__ = "servers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(63), unique=True)
    server_type: Mapped[str] = mapped_column(String(20))
    location: Mapped[str] = mapped_column(String(10))
    image: Mapped[str] = mapped_column(String(40))
    status: Mapped[str] = mapped_column(String(20), default="running")
    ipv4: Mapped[str] = mapped_column(String(15))
    created: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
