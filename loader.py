from typing import List, Dict, Optional
import logging
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass




class DogDataLoader:
    """Class-based loader for writing transformed dog breed data to a SQL database."""
    def __init__(self, database_url: Optional[str] = None, connect_timeout: int = 30):


        value = os.environ.get('DATABASE_URL')
        self.database_url = value
        if not self.database_url:
            raise RuntimeError('DATABASE_URL not set in environment. Add it to a .env file or export it.')

        self.engine = create_engine(
            self.database_url,
            poolclass=NullPool,
            connect_args={
                'connect_timeout': connect_timeout,
                'keepalives': 1,
                'keepalives_idle': 30,
                'keepalives_interval': 10,
                'keepalives_count': 5,
                'options': '-c client_encoding=utf8'
            }
        )

    def load(self, transformed_data_list: List[Dict]):
        """Load transformed dog breeds data into the configured database.

        This mirrors the previous function behavior but exposes it as a class method.
        The engine is disposed after the load completes (successfully or not).
        """
        from sqlalchemy import text

        try:
            with self.engine.begin() as conn:
                # Create table if not exists
                conn.execute(text("""
                CREATE TABLE IF NOT EXISTS dog_breeds (
                    breed_id INTEGER PRIMARY KEY,
                    breed_name TEXT NOT NULL,
                    breed_group TEXT,
                    bred_for TEXT,
                    life_span TEXT,
                    temperament TEXT,
                    origin TEXT,
                    weight_kg TEXT,
                    height_cm TEXT,
                    temperament_count INTEGER,
                    avg_lifespan_years REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                                  
                    CREATE TABLE IF NOT EXISTS pipeline_logs (
                        id SERIAL PRIMARY KEY,
                        run_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        status TEXT NOT NULL,
                        records_processed INTEGER,
                        error_message TEXT
                    );

                """))
                
                # In loader.py, add this to your CREATE TABLE section:


                print("✅ Table created/verified")

                insert_count = 0

                for data in transformed_data_list:
                    conn.execute(
                        text("""
                        INSERT INTO dog_breeds 
                        (breed_id, breed_name, breed_group, bred_for, life_span, 
                         temperament, origin, weight_kg, height_cm, 
                         temperament_count, avg_lifespan_years)
                        VALUES 
                        (:breed_id, :breed_name, :breed_group, :bred_for, :life_span,
                         :temperament, :origin, :weight_kg, :height_cm,
                         :temperament_count, :avg_lifespan_years)
                        ON CONFLICT (breed_id) 
                        DO UPDATE SET
                            breed_name = EXCLUDED.breed_name,
                            breed_group = EXCLUDED.breed_group,
                            bred_for = EXCLUDED.bred_for,
                            life_span = EXCLUDED.life_span,
                            temperament = EXCLUDED.temperament,
                            origin = EXCLUDED.origin,
                            weight_kg = EXCLUDED.weight_kg,
                            height_cm = EXCLUDED.height_cm,
                            temperament_count = EXCLUDED.temperament_count,
                            avg_lifespan_years = EXCLUDED.avg_lifespan_years
                        """),
                        {
                            'breed_id': data.get('breed_id'),
                            'breed_name': data.get('breed_name'),
                            'breed_group': data.get('breed_group'),
                            'bred_for': data.get('bred_for'),
                            'life_span': data.get('life_span'),
                            'temperament': data.get('temperament'),
                            'origin': data.get('origin'),
                            'weight_kg': data.get('weight_kg'),
                            'height_cm': data.get('height_cm'),
                            'temperament_count': data.get('temperament_count'),
                            'avg_lifespan_years': data.get('avg_lifespan_years')
                        }
                    )
                    insert_count += 1

                print(f"✅ Successfully processed {insert_count} records into dog_breeds table")

        except Exception as e:
            print(f"❌ Error: {str(e)}")
            raise
        finally:
            # Dispose engine to close connections and clean up resources
            try:
                self.engine.dispose()
            except Exception:
                pass