from extract import DogDataExtractor
from transfom import DogDataTransformer
from loader import DogDataLoader
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass


def main():
    from sqlalchemy import create_engine, text
    url = os.environ.get('DATABASE_URL')
    engine = create_engine(url)

    extractor = DogDataExtractor()
    transformer = DogDataTransformer()
    loader = DogDataLoader()
    
    try:
        print("🚀 Starting ETL pipeline...")
        raw_data = extractor.extract_data()
        transformed_data =transformer .transform_data(raw_data)
        loader.load(transformed_data)
        
        # Log success
        with engine.begin() as conn:
            conn.execute(text("""
                INSERT INTO pipeline_logs (status, records_processed)
                VALUES ('SUCCESS', :count)
            """), {'count': len(transformed_data)})
        
        print("✅ ETL pipeline completed!")
    except Exception as e:
        # Log failure
        with engine.begin() as conn:
            conn.execute(text("""
                INSERT INTO pipeline_logs (status, error_message)
                VALUES ('FAILED', :error)
            """), {'error': str(e)})
        raise

if __name__ == "__main__":
    main()