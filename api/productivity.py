"""
Productivity module for labor hours per unit and adjustment multipliers.
"""

import pandas as pd
from typing import Dict, Optional, Union
from decimal import Decimal
import logging
from pathlib import Path

from schemas import Trade, Phase

logger = logging.getLogger(__name__)


class ProductivityDatabase:
    """Database of labor productivity rates and adjustment factors."""
    
    def __init__(self):
        self.labor_rates = {}  # hours per unit by trade and item type
        self.adjustment_factors = {}  # multipliers for various conditions
        self._load_default_rates()
    
    def _load_default_rates(self):
        """Load default productivity rates for common construction items."""
        
        # Default labor hours per unit for common items
        default_rates = {
            'concrete': {
                'footing': Decimal('0.15'),  # hours per cubic foot
                'wall': Decimal('0.20'),
                'slab': Decimal('0.12'),
                'column': Decimal('0.25'),
            },
            'masonry': {
                'block_wall': Decimal('0.08'),  # hours per square foot
                'brick_wall': Decimal('0.12'),
                'stone_wall': Decimal('0.18'),
            },
            'metals': {
                'steel_beam': Decimal('0.30'),  # hours per linear foot
                'steel_column': Decimal('0.25'),
                'steel_joist': Decimal('0.15'),
            },
            'wood': {
                'framing': Decimal('0.06'),  # hours per square foot
                'sheathing': Decimal('0.04'),
                'trim': Decimal('0.08'),
            },
            'thermal': {
                'insulation': Decimal('0.03'),  # hours per square foot
                'vapor_barrier': Decimal('0.02'),
            },
            'doors_windows': {
                'door_install': Decimal('2.0'),  # hours per door
                'window_install': Decimal('1.5'),  # hours per window
            },
            'finishes': {
                'drywall': Decimal('0.12'),  # hours per square foot
                'paint': Decimal('0.08'),
                'flooring': Decimal('0.15'),
                'tile': Decimal('0.20'),
            },
            'mechanical': {
                'duct_install': Decimal('0.10'),  # hours per linear foot
                'pipe_install': Decimal('0.15'),
                'equipment_install': Decimal('8.0'),  # hours per unit
            },
            'electrical': {
                'conduit': Decimal('0.08'),  # hours per linear foot
                'wire_pull': Decimal('0.05'),
                'fixture_install': Decimal('0.5'),  # hours per fixture
            }
        }
        
        self.labor_rates = default_rates
        
        # Default adjustment factors
        self.adjustment_factors = {
            'weather': {
                'excellent': Decimal('0.9'),
                'good': Decimal('1.0'),
                'fair': Decimal('1.1'),
                'poor': Decimal('1.3'),
                'severe': Decimal('1.5')
            },
            'access': {
                'excellent': Decimal('0.9'),
                'good': Decimal('1.0'),
                'fair': Decimal('1.1'),
                'poor': Decimal('1.3'),
                'difficult': Decimal('1.6')
            },
            'complexity': {
                'simple': Decimal('0.8'),
                'standard': Decimal('1.0'),
                'complex': Decimal('1.3'),
                'very_complex': Decimal('1.7')
            },
            'crew_size': {
                'small': Decimal('1.2'),
                'standard': Decimal('1.0'),
                'large': Decimal('0.9')
            },
            'experience': {
                'apprentice': Decimal('1.5'),
                'journeyman': Decimal('1.0'),
                'master': Decimal('0.8')
            }
        }
    
    def get_labor_rate(self, trade: Trade, item_type: str) -> Optional[Decimal]:
        """Get labor hours per unit for a specific trade and item type."""
        trade_name = trade.value
        if trade_name in self.labor_rates and item_type in self.labor_rates[trade_name]:
            return self.labor_rates[trade_name][item_type]
        return None
    
    def get_adjustment_factor(self, factor_type: str, condition: str) -> Optional[Decimal]:
        """Get adjustment factor for a specific condition."""
        if factor_type in self.adjustment_factors and condition in self.adjustment_factors[factor_type]:
            return self.adjustment_factors[factor_type][condition]
        return None
    
    def calculate_adjusted_hours(self, 
                               base_hours: Decimal,
                               adjustments: Dict[str, str]) -> Decimal:
        """Calculate adjusted labor hours based on various factors."""
        adjusted_hours = base_hours
        
        for factor_type, condition in adjustments.items():
            factor = self.get_adjustment_factor(factor_type, condition)
            if factor:
                adjusted_hours *= factor
                logger.debug(f"Applied {factor_type}:{condition} factor: {factor}")
        
        return adjusted_hours
    
    def load_custom_rates(self, file_path: Union[str, Path]):
        """Load custom productivity rates from CSV file."""
        try:
            df = pd.read_csv(file_path)
            
            for _, row in df.iterrows():
                trade = row['trade'].lower()
                item_type = row['item_type']
                hours_per_unit = Decimal(str(row['hours_per_unit']))
                
                if trade not in self.labor_rates:
                    self.labor_rates[trade] = {}
                
                self.labor_rates[trade][item_type] = hours_per_unit
            
            logger.info(f"Loaded custom rates from {file_path}")
            
        except Exception as e:
            logger.error(f"Error loading custom rates from {file_path}: {e}")
            raise
    
    def load_custom_adjustments(self, file_path: Union[str, Path]):
        """Load custom adjustment factors from CSV file."""
        try:
            df = pd.read_csv(file_path)
            
            for _, row in df.iterrows():
                factor_type = row['factor_type']
                condition = row['condition']
                multiplier = Decimal(str(row['multiplier']))
                
                if factor_type not in self.adjustment_factors:
                    self.adjustment_factors[factor_type] = {}
                
                self.adjustment_factors[factor_type][condition] = multiplier
            
            logger.info(f"Loaded custom adjustments from {file_path}")
            
        except Exception as e:
            logger.error(f"Error loading custom adjustments from {file_path}: {e}")
            raise


class ProductivityCalculator:
    """Calculates labor productivity and costs."""
    
    def __init__(self, productivity_db: Optional[ProductivityDatabase] = None):
        self.db = productivity_db or ProductivityDatabase()
    
    def calculate_labor_hours(self, 
                            trade: Trade,
                            item_type: str,
                            quantity: Decimal,
                            adjustments: Optional[Dict[str, str]] = None) -> Decimal:
        """Calculate total labor hours for a line item."""
        
        # Get base labor rate
        base_rate = self.db.get_labor_rate(trade, item_type)
        if not base_rate:
            logger.warning(f"No labor rate found for {trade.value}:{item_type}")
            return Decimal('0')
        
        # Calculate base hours
        base_hours = base_rate * quantity
        
        # Apply adjustments if provided
        if adjustments:
            adjusted_hours = self.db.calculate_adjusted_hours(base_hours, adjustments)
            return adjusted_hours
        
        return base_hours
    
    def calculate_labor_cost(self,
                           labor_hours: Decimal,
                           labor_rate_per_hour: Decimal) -> Decimal:
        """Calculate labor cost from hours and hourly rate."""
        return labor_hours * labor_rate_per_hour
    
    def estimate_crew_size(self, 
                          total_hours: Decimal,
                          project_duration_days: int,
                          hours_per_day: int = 8) -> Dict[str, Union[int, Decimal]]:
        """Estimate required crew size for a project."""
        
        total_available_hours = project_duration_days * hours_per_day
        
        if total_available_hours <= 0:
            return {'crew_size': 1, 'efficiency': Decimal('1.0')}
        
        # Basic crew size calculation
        crew_size = (total_hours / total_available_hours).quantize(Decimal('0.1'))
        crew_size = max(1, int(crew_size))
        
        # Calculate efficiency factor
        efficiency = (total_hours / (crew_size * total_available_hours)).quantize(Decimal('0.01'))
        
        return {
            'crew_size': crew_size,
            'efficiency': efficiency,
            'total_hours': total_hours,
            'project_duration_days': project_duration_days,
            'hours_per_day': hours_per_day
        }
    
    def calculate_productivity_index(self, 
                                   actual_hours: Decimal,
                                   estimated_hours: Decimal) -> Decimal:
        """Calculate productivity index (PI) for performance measurement."""
        if estimated_hours == 0:
            return Decimal('0')
        
        pi = (estimated_hours / actual_hours).quantize(Decimal('0.01'))
        return pi


# Convenience functions
def get_productivity_calculator() -> ProductivityCalculator:
    """Get a default productivity calculator instance."""
    return ProductivityCalculator()


def calculate_line_item_labor(line_item,
                             labor_rate_per_hour: Decimal,
                             adjustments: Optional[Dict[str, str]] = None) -> Dict[str, Decimal]:
    """Calculate labor hours and cost for a line item."""
    
    calculator = ProductivityCalculator()
    
    # Determine item type from description (simplified)
    item_type = line_item.description.lower().split()[0] if line_item.description else 'standard'
    
    # Calculate labor hours
    labor_hours = calculator.calculate_labor_hours(
        line_item.trade,
        item_type,
        line_item.quantity,
        adjustments
    )
    
    # Calculate labor cost
    labor_cost = calculator.calculate_labor_cost(labor_hours, labor_rate_per_hour)
    
    return {
        'labor_hours': labor_hours,
        'labor_cost': labor_cost,
        'hours_per_unit': labor_hours / line_item.quantity if line_item.quantity > 0 else Decimal('0')
    }
