from typing import List, Dict, Optional
import logging
import re
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DogDataTransformer:
    def __init__(self):
        self.required_fields = ['id', 'name']
    
    def transform_data(self, raw_data: List[Dict]) -> List[Dict]:
        transformed_data = []
        
        for record in raw_data:
            try:
                # Extract and rename fields
                transformed_record = {
                    'breed_id': record.get('id'),
                    'breed_name': record.get('name', 'Unknown').strip(),
                    'breed_group': record.get('breed_group', 'Unknown').strip() if record.get('breed_group') else 'Unknown',
                    'bred_for': record.get('bred_for', 'Unknown').strip() if record.get('bred_for') else 'Unknown',
                    'life_span': record.get('life_span', 'Unknown').strip() if record.get('life_span') else 'Unknown',
                    'temperament': record.get('temperament', '').strip() if record.get('temperament') else '',
                    'origin': record.get('origin', 'Unknown').strip() if record.get('origin') else 'Unknown',
                    'weight_kg': self._clean_metric_value(record.get('weight', {}).get('metric')),
                    'height_cm': self._clean_metric_value(record.get('height', {}).get('metric')),
                }
                
                # Add calculated fields
                transformed_record['temperament_count'] = self._count_temperaments(
                    transformed_record['temperament']
                )
                
                # Calculate average lifespan
                transformed_record['avg_lifespan_years'] = self._calculate_avg_lifespan(
                    transformed_record['life_span']
                )
                
                # Add timestamp
                transformed_record['created_at'] = datetime.now()
                
                # Skip records with missing critical data
                if not transformed_record['breed_id'] or not transformed_record['breed_name']:
                    logger.warning(f"Skipping record with missing critical data: {record}")
                    continue
                
                transformed_data.append(transformed_record)
                
            except Exception as e:
                logger.error(f"Error transforming record {record.get('id', 'unknown')}: {e}")
                continue
        
        logger.info(f"Transformed {len(transformed_data)} records successfully")
        return transformed_data
    
    def _count_temperaments(self, temperament: str) -> int:
        """Count temperament traits, handling commas and whitespace properly"""
        if not temperament or temperament == 'Unknown':
            return 0
        # Split by comma and filter out empty strings after stripping
        traits = [t.strip() for t in temperament.split(',') if t.strip()]
        return len(traits)
    
    def _clean_metric_value(self, value: Optional[str]) -> Optional[str]:
        """Clean and validate metric values"""
        if not value or value == 'Unknown':
            return None
        return value.strip()
    
    def _calculate_avg_lifespan(self, life_span: str) -> Optional[float]:
        """Calculate average lifespan from range like '10 - 12 years' or '15 years'"""
        if not life_span or life_span == 'Unknown':
            return None
        
        try:
            # Extract all numbers from the string
            numbers = re.findall(r'\d+', life_span)
            
            if not numbers:
                return None
            
            # Convert to integers
            numbers = [int(n) for n in numbers]
            
            if len(numbers) >= 2:
                # Range format: "10 - 12 years"
                return round((numbers[0] + numbers[1]) / 2, 1)
            elif len(numbers) == 1:
                # Single value: "15 years"
                return float(numbers[0])
            
        except (ValueError, IndexError) as e:
            logger.warning(f"Could not parse lifespan '{life_span}': {e}")
        
        return None