# routes_app/app/db.py
import os
import psycopg2
import psycopg2.extras

DB_HOST = os.getenv("DB_HOST", "routes-db-service")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_NAME = os.getenv("DB_NAME", "routes_db")


def get_conn():
    """
    Retorna una conexión nueva a PostgreSQL.
    Usa variables de entorno definidas en el Deployment de K8s.
    """
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        dbname=DB_NAME,
    )


def ensure_schema():
    """
    Crea la tabla requerida si no existe.
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS routes (
                    id UUID PRIMARY KEY,
                    flight_id TEXT NOT NULL UNIQUE,
                    source_airport_code TEXT NOT NULL,
                    source_country TEXT NOT NULL,
                    destiny_airport_code TEXT NOT NULL,
                    destiny_country TEXT NOT NULL,
                    bag_cost INTEGER NOT NULL,
                    planned_start_date TIMESTAMP NOT NULL,
                    planned_end_date TIMESTAMP NOT NULL,
                    created_at TIMESTAMP NOT NULL DEFAULT NOW()
                );
                """
            )
        conn.commit()


def reset_db():
    """
    Limpia la base de datos para la entrega (endpoint POST /reset).
    """
    ensure_schema()
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("TRUNCATE TABLE routes RESTART IDENTITY CASCADE;")
        conn.commit()
