"""
CSV-based pricing provider for local pricing data.
"""

import pandas as pd
import csv
from pathlib import Path
from typing import Dict, Optional, List, Union
from decimal import Decimal, InvalidOperation
import logging
from datetime import datetime
import re

from .base import PricingProvider, PricingRequest, PricingResponse
from ..schemas import Trade, Phase, CostType

logger = logging.getLogger(__name__)


class CSVPricingProvider(PricingProvider):
    """Pricing provider that reads pricing data from CSV files."""
    
    def __init__(self, 
                 pricing_file: Union[str, Path],
                 labor_rates_file: Optional[Union[str, Path]] = None,
                 name: str = "CSV Provider"):
        super().__init__(name)
        self.pricing_file = Path(pricing_file)
        self.labor_rates_file = Path(labor_rates_file) if labor_rates_file else None
        
        # Load pricing data
        self.pricing_data = {}
        self.labor_rates = {}
        self._load_pricing_data()
        self._load_labor_rates()
    
    def _load_pricing_data(self):
        """Load pricing data from CSV file."""
        try:
            if not self.pricing_file.exists():
                logger.warning(f"Pricing file not found: {self.pricing_file}")
                return
            
            df = pd.read_csv(self.pricing_file)
            required_columns = ['item_description', 'trade', 'material_unit_cost', 'unit']
            
            # Check required columns
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                logger.error(f"Missing required columns in pricing file: {missing_columns}")
                return
            
            # Process each row
            for _, row in df.iterrows():
                try:
                    # Parse trade
                    trade_str = str(row['trade']).lower().strip()
                    if trade_str not in [t.value for t in Trade]:
                        logger.warning(f"Invalid trade '{trade_str}' in row {_}")
                        continue
                    
                    trade = Trade(trade_str)
                    
                    # Parse material cost
                    try:
                        material_cost = Decimal(str(row['material_unit_cost']))
                    except (InvalidOperation, ValueError):
                        logger.warning(f"Invalid material cost '{row['material_unit_cost']}' in row {_}")
                        continue
                    
                    # Create key for lookup
                    key = self._create_lookup_key(
                        str(row['item_description']).strip(),
                        trade,
                        str(row['unit']).strip()
                    )
                    
                    # Store pricing data
                    self.pricing_data[key] = {
                        'item_description': str(row['item_description']).strip(),
                        'trade': trade,
                        'material_unit_cost': material_cost,
                        'unit': str(row['unit']).strip(),
                        'labor_hours_per_unit': self._parse_decimal(row.get('labor_hours_per_unit')),
                        'equipment_cost_per_unit': self._parse_decimal(row.get('equipment_cost_per_unit')),
                        'overhead_rate': self._parse_decimal(row.get('overhead_rate')),
                        'profit_rate': self._parse_decimal(row.get('profit_rate')),
                        'source': str(row.get('source', 'CSV')),
                        'date_updated': self._parse_date(row.get('date_updated')),
                        'notes': str(row.get('notes', ''))
                    }
                    
                except Exception as e:
                    logger.warning(f"Error processing row {_}: {e}")
                    continue
            
            logger.info(f"Loaded {len(self.pricing_data)} pricing items from {self.pricing_file}")
            
        except Exception as e:
            logger.error(f"Error loading pricing data from {self.pricing_file}: {e}")
            self.is_available = False
    
    def _load_labor_rates(self):
        """Load labor rates from CSV file if provided."""
        if not self.labor_rates_file or not self.labor_rates_file.exists():
            return
        
        try:
            df = pd.read_csv(self.labor_rates_file)
            required_columns = ['trade', 'labor_rate_per_hour', 'location']
            
            # Check required columns
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                logger.error(f"Missing required columns in labor rates file: {missing_columns}")
                return
            
            # Process each row
            for _, row in df.iterrows():
                try:
                    trade_str = str(row['trade']).lower().strip()
                    if trade_str not in [t.value for t in Trade]:
                        continue
                    
                    trade = Trade(trade_str)
                    location = str(row['location']).strip()
                    labor_rate = self._parse_decimal(row['labor_rate_per_hour'])
                    
                    if labor_rate is not None:
                        if trade not in self.labor_rates:
                            self.labor_rates[trade] = {}
                        self.labor_rates[trade][location] = labor_rate
                        
                except Exception as e:
                    logger.warning(f"Error processing labor rate row {_}: {e}")
                    continue
            
            logger.info(f"Loaded labor rates for {len(self.labor_rates)} trades from {self.labor_rates_file}")
            
        except Exception as e:
            logger.error(f"Error loading labor rates from {self.labor_rates_file}: {e}")
    
    def _parse_decimal(self, value) -> Optional[Decimal]:
        """Parse a value to Decimal, returning None if invalid."""
        if pd.isna(value) or value is None:
            return None
        
        try:
            return Decimal(str(value))
        except (InvalidOperation, ValueError):
            return None
    
    def _parse_date(self, value) -> Optional[datetime]:
        """Parse a date value, returning None if invalid."""
        if pd.isna(value) or value is None:
            return None
        
        try:
            if isinstance(value, str):
                # Try common date formats
                for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y']:
                    try:
                        return datetime.strptime(value, fmt)
                    except ValueError:
                        continue
            elif isinstance(value, pd.Timestamp):
                return value.to_pydatetime()
            
            return None
        except Exception:
            return None
    
    def _create_lookup_key(self, description: str, trade: Trade, unit: str) -> str:
        """Create a lookup key for pricing data."""
        # Normalize description and unit for better matching
        normalized_desc = re.sub(r'\s+', ' ', description.lower().strip())
        normalized_unit = unit.lower().strip()
        
        return f"{normalized_desc}|{trade.value}|{normalized_unit}"
    
    def _find_best_match(self, description: str, trade: Trade, unit: str) -> Optional[str]:
        """Find the best matching key for a pricing request."""
        request_desc = re.sub(r'\s+', ' ', description.lower().strip())
        request_unit = unit.lower().strip()
        
        best_match = None
        best_score = 0
        
        for key in self.pricing_data.keys():
            key_desc, key_trade, key_unit = key.split('|')
            
            # Check if trade and unit match
            if key_trade != trade.value or key_unit != request_unit:
                continue
            
            # Calculate similarity score
            score = self._calculate_similarity(request_desc, key_desc)
            if score > best_score and score > 0.7:  # Minimum similarity threshold
                best_score = score
                best_match = key
        
        return best_match
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """Calculate similarity between two strings using simple word overlap."""
        words1 = set(str1.split())
        words2 = set(str2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def get_pricing(self, request: PricingRequest) -> Optional[PricingResponse]:
        """Get pricing for a specific item."""
        if not self.validate_request(request):
            return None
        
        # Try to find exact match first
        lookup_key = self._create_lookup_key(
            request.item_description,
            request.trade,
            request.unit
        )
        
        if lookup_key not in self.pricing_data:
            # Try to find best match
            lookup_key = self._find_best_match(
                request.item_description,
                request.trade,
                request.unit
            )
        
        if not lookup_key:
            return None
        
        pricing_item = self.pricing_data[lookup_key]
        
        # Get labor rate for this trade and location
        labor_rate = None
        if request.trade in self.labor_rates:
            # Try exact location match first, then fall back to any location
            if request.location in self.labor_rates[request.trade]:
                labor_rate = self.labor_rates[request.trade][request.location]
            elif self.labor_rates[request.trade]:
                # Use first available location
                labor_rate = next(iter(self.labor_rates[request.trade].values()))
        
        # Calculate confidence score based on match quality
        confidence_score = self._calculate_similarity(
            request.item_description.lower(),
            pricing_item['item_description'].lower()
        )
        
        return PricingResponse(
            item_description=pricing_item['item_description'],
            material_unit_cost=pricing_item['material_unit_cost'],
            labor_hours_per_unit=pricing_item['labor_hours_per_unit'],
            labor_rate_per_hour=labor_rate,
            equipment_cost_per_unit=pricing_item['equipment_cost_per_unit'],
            overhead_rate=pricing_item['overhead_rate'],
            profit_rate=pricing_item['profit_rate'],
            source=pricing_item['source'],
            confidence_score=confidence_score,
            date_retrieved=pricing_item['date_updated'] or datetime.now(),
            notes=pricing_item['notes']
        )
    
    def search_items(self, query: str, trade: Optional[Trade] = None) -> List[str]:
        """Search for available items matching a query."""
        query_lower = query.lower()
        matches = []
        
        for key, data in self.pricing_data.items():
            # Check if trade matches
            if trade and data['trade'] != trade:
                continue
            
            # Check if description matches query
            if query_lower in data['item_description'].lower():
                matches.append(data['item_description'])
        
        return list(set(matches))  # Remove duplicates
    
    def get_supported_trades(self) -> List[Trade]:
        """Get list of trades supported by this provider."""
        trades = set()
        for data in self.pricing_data.values():
            trades.add(data['trade'])
        return list(trades)
    
    def get_supported_locations(self) -> List[str]:
        """Get list of locations supported by this provider."""
        locations = set()
        for trade_rates in self.labor_rates.values():
            locations.update(trade_rates.keys())
        return list(locations) if locations else ['default']
    
    def add_pricing_item(self, 
                         description: str,
                         trade: Trade,
                         unit: str,
                         material_cost: Decimal,
                         **kwargs):
        """Add a new pricing item to the provider."""
        key = self._create_lookup_key(description, trade, unit)
        
        self.pricing_data[key] = {
            'item_description': description,
            'trade': trade,
            'material_unit_cost': material_cost,
            'unit': unit,
            'labor_hours_per_unit': kwargs.get('labor_hours_per_unit'),
            'equipment_cost_per_unit': kwargs.get('equipment_cost_per_unit'),
            'overhead_rate': kwargs.get('overhead_rate'),
            'profit_rate': kwargs.get('profit_rate'),
            'source': kwargs.get('source', 'Manual Entry'),
            'date_updated': datetime.now(),
            'notes': kwargs.get('notes', '')
        }
        
        logger.info(f"Added pricing item: {description}")
    
    def export_pricing_data(self, output_file: Union[str, Path]):
        """Export current pricing data to CSV file."""
        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'item_description', 'trade', 'unit', 'material_unit_cost',
                    'labor_hours_per_unit', 'equipment_cost_per_unit',
                    'overhead_rate', 'profit_rate', 'source', 'date_updated', 'notes'
                ]
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for data in self.pricing_data.values():
                    row = {field: data.get(field, '') for field in fieldnames}
                    if row['date_updated']:
                        row['date_updated'] = row['date_updated'].strftime('%Y-%m-%d')
                    writer.writerow(row)
            
            logger.info(f"Exported pricing data to {output_file}")
            
        except Exception as e:
            logger.error(f"Error exporting pricing data: {e}")
            raise
