import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://hetzner:hetzner@localhost:5432/hetzner_sim",
)
