"""
Rollup calculations and summaries for construction cost estimation.
"""

from typing import Dict, List, Optional, Union, Any
from decimal import Decimal
import pandas as pd
from collections import defaultdict
import logging

from .schemas import Project, LineItem, Trade, Phase, CostType, Room
from .calculator import CostCalculation

logger = logging.getLogger(__name__)


class CostRollup:
    """Handles cost rollups and summaries across different dimensions."""
    
    def __init__(self):
        self.rollup_data = {}
    
    def rollup_by_phase(self, 
                        calculations: Dict[str, CostCalculation],
                        line_items: List[LineItem]) -> Dict[Phase, Dict[str, Decimal]]:
        """Roll up costs by project phase."""
        phase_rollup = defaultdict(lambda: {
            'material': Decimal('0'),
            'labor': Decimal('0'),
            'equipment': Decimal('0'),
            'overhead': Decimal('0'),
            'profit': Decimal('0'),
            'subtotal': Decimal('0'),
            'total': Decimal('0'),
            'line_items': [],
            'quantity': Decimal('0')
        })
        
        # Create mapping from line item ID to phase
        item_phase_map = {item.id: item.phase for item in line_items}
        
        for calc_id, calc in calculations.items():
            phase = item_phase_map.get(calc_id, Phase.GENERAL)
            
            phase_rollup[phase]['material'] += calc.material_cost
            phase_rollup[phase]['labor'] += calc.labor_cost
            phase_rollup[phase]['equipment'] += calc.equipment_cost
            
            # Handle breakdown fields safely
            if 'overhead' in calc.breakdown:
                phase_rollup[phase]['overhead'] += calc.breakdown['overhead']
            if 'profit' in calc.breakdown:
                phase_rollup[phase]['profit'] += calc.breakdown['profit']
            if 'subtotal' in calc.breakdown:
                phase_rollup[phase]['subtotal'] += calc.breakdown['subtotal']
            
            phase_rollup[phase]['total'] += calc.total_cost
            phase_rollup[phase]['line_items'].append(calc_id)
            phase_rollup[phase]['quantity'] += calc.quantity
        
        return dict(phase_rollup)
    
    def rollup_by_trade(self, 
                        calculations: Dict[str, CostCalculation],
                        line_items: List[LineItem]) -> Dict[Trade, Dict[str, Decimal]]:
        """Roll up costs by construction trade."""
        trade_rollup = defaultdict(lambda: {
            'material': Decimal('0'),
            'labor': Decimal('0'),
            'equipment': Decimal('0'),
            'overhead': Decimal('0'),
            'profit': Decimal('0'),
            'subtotal': Decimal('0'),
            'total': Decimal('0'),
            'line_items': [],
            'quantity': Decimal('0')
        })
        
        # Create mapping from line item ID to trade
        item_trade_map = {item.id: item.trade for item in line_items}
        
        for calc_id, calc in calculations.items():
            trade = item_trade_map.get(calc_id, Trade.GENERAL)
            
            trade_rollup[trade]['material'] += calc.material_cost
            trade_rollup[trade]['labor'] += calc.labor_cost
            trade_rollup[trade]['equipment'] += calc.equipment_cost
            
            # Handle breakdown fields safely
            if 'overhead' in calc.breakdown:
                trade_rollup[trade]['overhead'] += calc.breakdown['overhead']
            if 'profit' in calc.breakdown:
                trade_rollup[trade]['profit'] += calc.breakdown['profit']
            if 'subtotal' in calc.breakdown:
                trade_rollup[trade]['subtotal'] += calc.breakdown['subtotal']
            
            trade_rollup[trade]['total'] += calc.total_cost
            trade_rollup[trade]['line_items'].append(calc_id)
            trade_rollup[trade]['quantity'] += calc.quantity
        
        return dict(trade_rollup)
    
    def rollup_by_cost_type(self, 
                           calculations: Dict[str, CostCalculation],
                           line_items: List[LineItem]) -> Dict[CostType, Dict[str, Decimal]]:
        """Roll up costs by cost type (material, labor, equipment, etc.)."""
        cost_type_rollup = defaultdict(lambda: {
            'total': Decimal('0'),
            'line_items': [],
            'quantity': Decimal('0'),
            'by_trade': defaultdict(lambda: Decimal('0')),
            'by_phase': defaultdict(lambda: Decimal('0'))
        })
        
        # Create mappings
        item_cost_type_map = {item.id: item.cost_type for item in line_items}
        item_trade_map = {item.id: item.trade for item in line_items}
        item_phase_map = {item.id: item.phase for item in line_items}
        
        for calc_id, calc in calculations.items():
            cost_type = item_cost_type_map.get(calc_id, CostType.MATERIAL)
            trade = item_trade_map.get(calc_id, Trade.GENERAL)
            phase = item_phase_map.get(calc_id, Phase.GENERAL)
            
            # Add to main cost type total
            cost_type_rollup[cost_type]['total'] += calc.total_cost
            cost_type_rollup[cost_type]['line_items'].append(calc_id)
            cost_type_rollup[cost_type]['quantity'] += calc.quantity
            
            # Add to trade breakdown
            cost_type_rollup[cost_type]['by_trade'][trade] += calc.total_cost
            
            # Add to phase breakdown
            cost_type_rollup[cost_type]['by_phase'][phase] += calc.total_cost
        
        return dict(cost_type_rollup)
    
    def rollup_by_room(self, 
                       calculations: Dict[str, CostCalculation],
                       line_items: List[LineItem],
                       rooms: List[Room]) -> Dict[str, Dict[str, Decimal]]:
        """Roll up costs by room."""
        room_rollup = defaultdict(lambda: {
            'material': Decimal('0'),
            'labor': Decimal('0'),
            'equipment': Decimal('0'),
            'overhead': Decimal('0'),
            'profit': Decimal('0'),
            'subtotal': Decimal('0'),
            'total': Decimal('0'),
            'line_items': [],
            'area': Decimal('0'),
            'cost_per_sf': Decimal('0')
        })
        
        # Create room name mapping
        room_name_map = {room.name: room for room in rooms}
        
        for calc_id, calc in calculations.items():
            # Find which rooms this line item applies to
            line_item = next((item for item in line_items if item.id == calc_id), None)
            if not line_item:
                continue
            
            # If no specific rooms assigned, distribute proportionally
            if not line_item.rooms:
                # Distribute to all rooms proportionally by area
                total_area = sum(room.area for room in rooms)
                if total_area > 0:
                    for room in rooms:
                        room_ratio = room.area / total_area
                        room_rollup[room.name]['material'] += calc.material_cost * room_ratio
                        room_rollup[room.name]['labor'] += calc.labor_cost * room_ratio
                        room_rollup[room.name]['equipment'] += calc.equipment_cost * room_ratio
                        
                        # Handle breakdown fields safely
                        if 'overhead' in calc.breakdown:
                            room_rollup[room.name]['overhead'] += calc.breakdown['overhead'] * room_ratio
                        if 'profit' in calc.breakdown:
                            room_rollup[room.name]['profit'] += calc.breakdown['profit'] * room_ratio
                        if 'subtotal' in calc.breakdown:
                            room_rollup[room.name]['subtotal'] += calc.breakdown['subtotal'] * room_ratio
                        
                        room_rollup[room.name]['total'] += calc.total_cost * room_ratio
                        room_rollup[room.name]['line_items'].append(calc_id)
                        room_rollup[room.name]['area'] = room.area
            else:
                # Distribute to specific rooms
                for room_name in line_item.rooms:
                    if room_name in room_name_map:
                        room = room_name_map[room_name]
                        room_rollup[room_name]['material'] += calc.material_cost
                        room_rollup[room_name]['labor'] += calc.labor_cost
                        room_rollup[room_name]['equipment'] += calc.equipment_cost
                        
                        # Handle breakdown fields safely
                        if 'overhead' in calc.breakdown:
                            room_rollup[room_name]['overhead'] += calc.breakdown['overhead']
                        if 'profit' in calc.breakdown:
                            room_rollup[room_name]['profit'] += calc.breakdown['profit']
                        if 'subtotal' in calc.breakdown:
                            room_rollup[room_name]['subtotal'] += calc.breakdown['subtotal']
                        
                        room_rollup[room_name]['total'] += calc.total_cost
                        room_rollup[room_name]['line_items'].append(calc_id)
                        room_rollup[room_name]['area'] = room.area
        
        # Calculate cost per square foot for each room
        for room_name, data in room_rollup.items():
            if data['area'] > 0:
                data['cost_per_sf'] = data['total'] / data['area']
        
        return dict(room_rollup)
    
    def rollup_by_phase_and_trade(self, 
                                 calculations: Dict[str, CostCalculation],
                                 line_items: List[LineItem]) -> Dict[str, Dict[str, Decimal]]:
        """Roll up costs by phase and trade combination."""
        phase_trade_rollup = defaultdict(lambda: defaultdict(lambda: {
            'material': Decimal('0'),
            'labor': Decimal('0'),
            'equipment': Decimal('0'),
            'overhead': Decimal('0'),
            'profit': Decimal('0'),
            'subtotal': Decimal('0'),
            'total': Decimal('0'),
            'line_items': [],
            'quantity': Decimal('0')
        }))
        
        # Create mappings
        item_phase_map = {item.id: item.phase for item in line_items}
        item_trade_map = {item.id: item.trade for item in line_items}
        
        for calc_id, calc in calculations.items():
            phase = item_phase_map.get(calc_id, Phase.GENERAL)
            trade = item_trade_map.get(calc_id, Trade.GENERAL)
            
            phase_trade_rollup[phase][trade]['material'] += calc.material_cost
            phase_trade_rollup[phase][trade]['labor'] += calc.labor_cost
            phase_trade_rollup[phase][trade]['equipment'] += calc.equipment_cost
            
            # Handle breakdown fields safely
            if 'overhead' in calc.breakdown:
                phase_trade_rollup[phase][trade]['overhead'] += calc.breakdown['overhead']
            if 'profit' in calc.breakdown:
                phase_trade_rollup[phase][trade]['profit'] += calc.breakdown['profit']
            if 'subtotal' in calc.breakdown:
                phase_trade_rollup[phase][trade]['subtotal'] += calc.breakdown['subtotal']
            
            phase_trade_rollup[phase][trade]['total'] += calc.total_cost
            phase_trade_rollup[phase][trade]['line_items'].append(calc_id)
            phase_trade_rollup[phase][trade]['quantity'] += calc.quantity
        
        # Convert to flat dictionary with phase_trade keys
        flat_rollup = {}
        for phase, trades in phase_trade_rollup.items():
            for trade, data in trades.items():
                key = f"{phase.value}_{trade.value}"
                flat_rollup[key] = data
        
        return flat_rollup
    
    def create_summary_report(self, 
                            calculations: Dict[str, CostCalculation],
                            project: Project) -> Dict[str, Any]:
        """Create a comprehensive summary report."""
        
        # Perform all rollups
        phase_rollup = self.rollup_by_phase(calculations, project.line_items)
        trade_rollup = self.rollup_by_trade(calculations, project.line_items)
        cost_type_rollup = self.rollup_by_cost_type(calculations, project.line_items)
        room_rollup = self.rollup_by_room(calculations, project.line_items, project.rooms)
        phase_trade_rollup = self.rollup_by_phase_and_trade(calculations, project.line_items)
        
        # Calculate totals
        total_material = sum(calc.material_cost for calc in calculations.values())
        total_labor = sum(calc.labor_cost for calc in calculations.values())
        total_equipment = sum(calc.equipment_cost for calc in calculations.values())
        
        # Handle breakdown fields safely
        total_overhead = sum(calc.breakdown.get('overhead', Decimal('0')) for calc in calculations.values())
        total_profit = sum(calc.breakdown.get('profit', Decimal('0')) for calc in calculations.values())
        total_cost = sum(calc.total_cost for calc in calculations.values())
        
        # Calculate percentages
        total_direct = total_material + total_labor + total_equipment
        material_pct = (total_material / total_direct * 100) if total_direct > 0 else 0
        labor_pct = (total_labor / total_direct * 100) if total_direct > 0 else 0
        equipment_pct = (total_equipment / total_direct * 100) if total_direct > 0 else 0
        overhead_pct = (total_overhead / total_cost * 100) if total_cost > 0 else 0
        profit_pct = (total_profit / total_cost * 100) if total_cost > 0 else 0
        
        # Calculate cost per square foot
        cost_per_sf = total_cost / project.total_area if project.total_area > 0 else Decimal('0')
        
        summary = {
            'project_info': {
                'name': project.name,
                'location': project.location,
                'project_type': project.project_type,
                'total_area': float(project.total_area),
                'room_count': len(project.rooms),
                'line_item_count': len(project.line_items)
            },
            'cost_summary': {
                'total_cost': float(total_cost),
                'total_material': float(total_material),
                'total_labor': float(total_labor),
                'total_equipment': float(total_equipment),
                'total_overhead': float(total_overhead),
                'total_profit': float(total_profit),
                'cost_per_sf': float(cost_per_sf)
            },
            'cost_percentages': {
                'material_pct': float(material_pct),
                'labor_pct': float(labor_pct),
                'equipment_pct': float(equipment_pct),
                'overhead_pct': float(overhead_pct),
                'profit_pct': float(profit_pct)
            },
            'rollups': {
                'by_phase': {k.value: {key: float(value) if isinstance(value, Decimal) else value 
                                      for key, value in v.items() if key != 'line_items'} 
                            for k, v in phase_rollup.items()},
                'by_trade': {k.value: {key: float(value) if isinstance(value, Decimal) else value 
                                      for key, value in v.items() if key != 'line_items'} 
                            for k, v in trade_rollup.items()},
                'by_cost_type': {k.value: {key: float(value) if isinstance(value, Decimal) else value 
                                          for key, value in v.items() if key != 'line_items'} 
                                for k, v in cost_type_rollup.items()},
                'by_room': {k: {key: float(value) if isinstance(value, Decimal) else value 
                                for key, value in v.items() if key != 'line_items'} 
                           for k, v in room_rollup.items()},
                'by_phase_trade': {k: {key: float(value) if isinstance(value, Decimal) else value 
                                      for key, value in v.items() if key != 'line_items'} 
                                  for k, v in phase_trade_rollup.items()}
            }
        }
        
        return summary
    
    def export_to_dataframe(self, rollup_data: Dict, rollup_type: str) -> pd.DataFrame:
        """Export rollup data to pandas DataFrame."""
        rows = []
        
        for key, data in rollup_data.items():
            row = {'category': key}
            row.update({k: float(v) if isinstance(v, Decimal) else v 
                       for k, v in data.items() if k != 'line_items'})
            rows.append(row)
        
        df = pd.DataFrame(rows)
        df['rollup_type'] = rollup_type
        return df


class CostAnalyzer:
    """Advanced cost analysis and comparison tools."""
    
    def __init__(self):
        self.analysis_results = {}
    
    def analyze_cost_distribution(self, rollup_data: Dict) -> Dict[str, float]:
        """Analyze the distribution of costs across categories."""
        total_cost = sum(data.get('total', 0) for data in rollup_data.values())
        
        if total_cost <= 0:
            return {}
        
        distribution = {}
        for category, data in rollup_data.items():
            category_cost = data.get('total', 0)
            distribution[category] = float(category_cost / total_cost * 100)
        
        return distribution
    
    def find_cost_outliers(self, calculations: Dict[str, CostCalculation], 
                          threshold: float = 2.0) -> List[str]:
        """Find line items with costs significantly above average."""
        if not calculations:
            return []
        
        # Calculate mean and standard deviation
        costs = [calc.total_cost for calc in calculations.values()]
        mean_cost = sum(costs) / len(costs)
        
        # Calculate variance and standard deviation
        variance = sum((cost - mean_cost) ** 2 for cost in costs) / len(costs)
        std_dev = variance ** 0.5
        
        # Find outliers
        outliers = []
        for calc_id, calc in calculations.items():
            z_score = abs(calc.total_cost - mean_cost) / std_dev
            if z_score > threshold:
                outliers.append(calc_id)
        
        return outliers
    
    def calculate_cost_efficiency(self, calculations: Dict[str, CostCalculation]) -> Dict[str, float]:
        """Calculate cost efficiency metrics for each line item."""
        efficiency_metrics = {}
        
        for calc_id, calc in calculations.items():
            # Cost per unit efficiency (lower is better)
            cost_per_unit = calc.cost_per_unit
            
            # Labor efficiency (labor cost / total cost ratio)
            labor_efficiency = float(calc.labor_cost / calc.total_cost) if calc.total_cost > 0 else 0
            
            # Material efficiency (material cost / total cost ratio)
            material_efficiency = float(calc.material_cost / calc.total_cost) if calc.total_cost > 0 else 0
            
            efficiency_metrics[calc_id] = {
                'cost_per_unit': float(cost_per_unit),
                'labor_efficiency': labor_efficiency,
                'material_efficiency': material_efficiency,
                'overall_efficiency': 1.0 - (labor_efficiency + material_efficiency)  # Lower overhead/profit is better
            }
        
        return efficiency_metrics
    
    def compare_with_benchmarks(self, 
                               rollup_data: Dict,
                               benchmarks: Dict) -> Dict[str, Dict]:
        """Compare actual costs with industry benchmarks."""
        comparison = {}
        
        for category, data in rollup_data.items():
            if category in benchmarks:
                benchmark = benchmarks[category]
                actual_cost = data.get('total', 0)
                
                variance = actual_cost - benchmark
                variance_pct = (variance / benchmark * 100) if benchmark > 0 else 0
                
                comparison[category] = {
                    'actual': float(actual_cost),
                    'benchmark': float(benchmark),
                    'variance': float(variance),
                    'variance_pct': float(variance_pct),
                    'status': 'above' if variance > 0 else 'below' if variance < 0 else 'on_target'
                }
        
        return comparison


# Convenience functions
def create_cost_rollup() -> CostRollup:
    """Create a default cost rollup instance."""
    return CostRollup()


def create_cost_analyzer() -> CostAnalyzer:
    """Create a default cost analyzer instance."""
    return CostAnalyzer()


def quick_rollup(calculations: Dict[str, CostCalculation], 
                line_items: List[LineItem]) -> Dict[str, Dict]:
    """Quick rollup of costs by phase and trade."""
    rollup = CostRollup()
    
    return {
        'by_phase': rollup.rollup_by_phase(calculations, line_items),
        'by_trade': rollup.rollup_by_trade(calculations, line_items)
    }
