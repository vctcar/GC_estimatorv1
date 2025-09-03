"""
Reporting module for creating DataFrames and cost class ranges.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union, Any
from decimal import Decimal
import logging
from pathlib import Path
import json

from schemas import Project, LineItem, Trade, Phase, CostType, Room
from calculator import CostCalculation
from rollups import CostRollup

logger = logging.getLogger(__name__)


class ReportBuilder:
    """Builds various types of reports and DataFrames."""
    
    def __init__(self):
        self.report_templates = {}
        self._load_default_templates()
    
    def _load_default_templates(self):
        """Load default report templates."""
        self.report_templates = {
            'detailed': {
                'columns': ['id', 'description', 'quantity', 'unit', 'trade', 'phase', 
                           'material_cost', 'labor_cost', 'equipment_cost', 'overhead', 
                           'profit', 'total_cost', 'cost_per_unit'],
                'title': 'Detailed Cost Report',
                'group_by': ['trade', 'phase']
            },
            'summary': {
                'columns': ['trade', 'phase', 'total_cost', 'material_cost', 'labor_cost', 
                           'equipment_cost', 'overhead', 'profit', 'line_item_count'],
                'title': 'Cost Summary Report',
                'group_by': ['trade']
            },
            'room_breakdown': {
                'columns': ['room_name', 'area', 'total_cost', 'material_cost', 'labor_cost', 
                           'equipment_cost', 'cost_per_sf'],
                'title': 'Room Cost Breakdown',
                'group_by': ['room_name']
            }
        }
    
    def create_detailed_report(self, 
                             calculations: Dict[str, CostCalculation],
                             line_items: List[LineItem]) -> pd.DataFrame:
        """Create a detailed line-item report."""
        
        # Create mapping from line item ID to line item
        item_map = {item.id: item for item in line_items}
        
        rows = []
        for calc_id, calc in calculations.items():
            line_item = item_map.get(calc_id)
            if not line_item:
                continue
            
            row = {
                'id': calc_id,
                'description': calc.description,
                'quantity': float(calc.quantity),
                'unit': calc.unit,
                'trade': line_item.trade.value,
                'phase': line_item.phase.value,
                'material_cost': float(calc.material_cost),
                'labor_cost': float(calc.labor_cost),
                'equipment_cost': float(calc.equipment_cost),
                'overhead': float(calc.breakdown['overhead']),
                'profit': float(calc.breakdown['profit']),
                'total_cost': float(calc.total_cost),
                'cost_per_unit': float(calc.cost_per_unit)
            }
            rows.append(row)
        
        df = pd.DataFrame(rows)
        
        # Sort by trade, then phase, then description
        df = df.sort_values(['trade', 'phase', 'description'])
        
        return df
    
    def create_summary_report(self, 
                            calculations: Dict[str, CostCalculation],
                            line_items: List[LineItem]) -> pd.DataFrame:
        """Create a summary report grouped by trade and phase."""
        
        # Use rollup functionality
        rollup = CostRollup()
        trade_rollup = rollup.rollup_by_trade(calculations, line_items)
        phase_rollup = rollup.rollup_by_phase(calculations, line_items)
        
        # Create trade summary
        trade_rows = []
        for trade, data in trade_rollup.items():
            row = {
                'category_type': 'Trade',
                'category': trade.value,
                'total_cost': float(data['total']),
                'material_cost': float(data['material']),
                'labor_cost': float(data['labor']),
                'equipment_cost': float(data['equipment']),
                'overhead': float(data['overhead']),
                'profit': float(data['profit']),
                'line_item_count': len(data['line_items']),
                'quantity': float(data['quantity'])
            }
            trade_rows.append(row)
        
        # Create phase summary
        phase_rows = []
        for phase, data in phase_rollup.items():
            row = {
                'category_type': 'Phase',
                'category': phase.value,
                'total_cost': float(data['total']),
                'material_cost': float(data['material']),
                'labor_cost': float(data['labor']),
                'equipment_cost': float(data['equipment']),
                'overhead': float(data['overhead']),
                'profit': float(data['profit']),
                'line_item_count': len(data['line_items']),
                'quantity': float(data['quantity'])
            }
            phase_rows.append(row)
        
        # Combine and sort
        all_rows = trade_rows + phase_rows
        df = pd.DataFrame(all_rows)
        df = df.sort_values(['category_type', 'total_cost'], ascending=[True, False])
        
        return df
    
    def create_room_report(self, 
                          calculations: Dict[str, CostCalculation],
                          line_items: List[LineItem],
                          rooms: List[Room]) -> pd.DataFrame:
        """Create a room-by-room cost breakdown."""
        
        rollup = CostRollup()
        room_rollup = rollup.rollup_by_room(calculations, line_items, rooms)
        
        rows = []
        for room_name, data in room_rollup.items():
            row = {
                'room_name': room_name,
                'area': float(data['area']),
                'total_cost': float(data['total']),
                'material_cost': float(data['material']),
                'labor_cost': float(data['labor']),
                'equipment_cost': float(data['equipment']),
                'overhead': float(data['overhead']),
                'profit': float(data['profit']),
                'cost_per_sf': float(data['cost_per_sf']),
                'line_item_count': len(data['line_items'])
            }
            rows.append(row)
        
        df = pd.DataFrame(rows)
        df = df.sort_values('total_cost', ascending=False)
        
        return df
    
    def create_cost_analysis_report(self, 
                                  calculations: Dict[str, CostCalculation],
                                  line_items: List[LineItem]) -> pd.DataFrame:
        """Create a cost analysis report with efficiency metrics."""
        
        from rollups import CostAnalyzer
        analyzer = CostAnalyzer()
        
        # Get efficiency metrics
        efficiency_metrics = analyzer.calculate_cost_efficiency(calculations)
        
        # Create mapping from line item ID to line item
        item_map = {item.id: item for item in line_items}
        
        rows = []
        for calc_id, calc in calculations.items():
            line_item = item_map.get(calc_id)
            if not line_item:
                continue
            
            efficiency = efficiency_metrics.get(calc_id, {})
            
            row = {
                'id': calc_id,
                'description': calc.description,
                'trade': line_item.trade.value,
                'phase': line_item.phase.value,
                'total_cost': float(calc.total_cost),
                'cost_per_unit': float(calc.cost_per_unit),
                'labor_efficiency': efficiency.get('labor_efficiency', 0),
                'material_efficiency': efficiency.get('material_efficiency', 0),
                'overall_efficiency': efficiency.get('overall_efficiency', 0),
                'quantity': float(calc.quantity),
                'unit': calc.unit
            }
            rows.append(row)
        
        df = pd.DataFrame(rows)
        df = df.sort_values('total_cost', ascending=False)
        
        return df
    
    def create_comparison_report(self, 
                               calculations: Dict[str, CostCalculation],
                               line_items: List[LineItem],
                               benchmarks: Dict) -> pd.DataFrame:
        """Create a comparison report against benchmarks."""
        
        rollup = CostRollup()
        trade_rollup = rollup.rollup_by_trade(calculations, line_items)
        
        from rollups import CostAnalyzer
        analyzer = CostAnalyzer()
        
        # Compare with benchmarks
        comparison = analyzer.compare_with_benchmarks(trade_rollup, benchmarks)
        
        rows = []
        for trade_name, data in comparison.items():
            row = {
                'trade': trade_name,
                'actual_cost': data['actual'],
                'benchmark_cost': data['benchmark'],
                'variance': data['variance'],
                'variance_pct': data['variance_pct'],
                'status': data['status']
            }
            rows.append(row)
        
        df = pd.DataFrame(rows)
        df = df.sort_values('variance_pct', ascending=False)
        
        return df


class CostClassRanges:
    """Defines and manages cost class ranges for reporting."""
    
    def __init__(self):
        self.default_ranges = {
            'low': {'min': 0, 'max': 1000, 'label': 'Low Cost'},
            'medium': {'min': 1000, 'max': 10000, 'label': 'Medium Cost'},
            'high': {'min': 10000, 'max': 100000, 'label': 'High Cost'},
            'very_high': {'min': 100000, 'max': float('inf'), 'label': 'Very High Cost'}
        }
        self.custom_ranges = {}
    
    def add_custom_range(self, name: str, min_val: float, max_val: float, label: str):
        """Add a custom cost range."""
        self.custom_ranges[name] = {
            'min': min_val,
            'max': max_val,
            'label': label
        }
    
    def get_cost_class(self, cost: float, range_set: str = 'default') -> str:
        """Get the cost class for a given cost value."""
        ranges = self.custom_ranges if range_set == 'custom' else self.default_ranges
        
        for range_name, range_data in ranges.items():
            if range_data['min'] <= cost <= range_data['max']:
                return range_data['label']
        
        return 'Unknown'
    
    def classify_line_items(self, 
                           calculations: Dict[str, CostCalculation],
                           range_set: str = 'default') -> Dict[str, List[str]]:
        """Classify line items into cost classes."""
        classifications = {}
        
        for calc_id, calc in calculations.items():
            cost_class = self.get_cost_class(float(calc.total_cost), range_set)
            
            if cost_class not in classifications:
                classifications[cost_class] = []
            
            classifications[cost_class].append(calc_id)
        
        return classifications
    
    def create_cost_class_report(self, 
                               calculations: Dict[str, CostCalculation],
                               range_set: str = 'default') -> pd.DataFrame:
        """Create a report showing distribution by cost class."""
        
        classifications = self.classify_line_items(calculations, range_set)
        
        rows = []
        for cost_class, item_ids in classifications.items():
            total_cost = sum(calculations[item_id].total_cost for item_id in item_ids)
            item_count = len(item_ids)
            
            row = {
                'cost_class': cost_class,
                'item_count': item_count,
                'total_cost': float(total_cost),
                'avg_cost': float(total_cost / item_count) if item_count > 0 else 0,
                'percentage': float(item_count / len(calculations) * 100) if calculations else 0
            }
            rows.append(row)
        
        df = pd.DataFrame(rows)
        df = df.sort_values('total_cost', ascending=False)
        
        return df


class ReportExporter:
    """Handles exporting reports to various formats."""
    
    def __init__(self):
        self.supported_formats = ['csv', 'excel', 'json', 'html']
    
    def export_report(self, 
                     df: pd.DataFrame,
                     output_path: Union[str, Path],
                     format: str = 'csv',
                     **kwargs) -> bool:
        """Export a report DataFrame to the specified format."""
        
        try:
            output_path = Path(output_path)
            
            if format.lower() == 'csv':
                df.to_csv(output_path, index=False, **kwargs)
            elif format.lower() == 'excel':
                df.to_excel(output_path, index=False, **kwargs)
            elif format.lower() == 'json':
                df.to_json(output_path, orient='records', indent=2, **kwargs)
            elif format.lower() == 'html':
                html_content = df.to_html(index=False, **kwargs)
                with open(output_path, 'w') as f:
                    f.write(html_content)
            else:
                logger.error(f"Unsupported format: {format}")
                return False
            
            logger.info(f"Successfully exported report to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting report: {e}")
            return False
    
    def export_multiple_reports(self, 
                              reports: Dict[str, pd.DataFrame],
                              output_dir: Union[str, Path],
                              base_format: str = 'csv') -> Dict[str, bool]:
        """Export multiple reports to a directory."""
        
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        results = {}
        
        for report_name, df in reports.items():
            output_path = output_dir / f"{report_name}.{base_format}"
            success = self.export_report(df, output_path, base_format)
            results[report_name] = success
        
        return results


class ReportVisualizer:
    """Creates visual representations of cost data."""
    
    def __init__(self):
        self.chart_types = ['pie', 'bar', 'line', 'scatter']
    
    def create_pie_chart_data(self, 
                             df: pd.DataFrame,
                             value_column: str,
                             label_column: str) -> Dict[str, float]:
        """Prepare data for pie chart visualization."""
        
        chart_data = {}
        for _, row in df.iterrows():
            label = str(row[label_column])
            value = float(row[value_column])
            chart_data[label] = value
        
        return chart_data
    
    def create_bar_chart_data(self, 
                             df: pd.DataFrame,
                             x_column: str,
                             y_column: str) -> Dict[str, float]:
        """Prepare data for bar chart visualization."""
        
        chart_data = {}
        for _, row in df.iterrows():
            x_label = str(row[x_column])
            y_value = float(row[y_column])
            chart_data[x_label] = y_value
        
        return chart_data
    
    def create_cost_distribution_chart(self, 
                                     calculations: Dict[str, CostCalculation],
                                     group_by: str = 'trade') -> Dict[str, float]:
        """Create cost distribution data for charts."""
        
        if group_by == 'trade':
            # Group by trade
            trade_costs = {}
            for calc in calculations.values():
                # This would need to be implemented based on your data structure
                # For now, return placeholder
                pass
        
        return {}
    
    def generate_chart_config(self, 
                            chart_type: str,
                            data: Dict[str, float],
                            title: str = '',
                            **kwargs) -> Dict[str, Any]:
        """Generate configuration for various chart types."""
        
        config = {
            'type': chart_type,
            'data': data,
            'title': title,
            'options': kwargs
        }
        
        if chart_type == 'pie':
            config['options'].update({
                'responsive': True,
                'maintainAspectRatio': False
            })
        elif chart_type == 'bar':
            config['options'].update({
                'scales': {
                    'y': {'beginAtZero': True}
                }
            })
        
        return config


# Convenience functions
def create_report_builder() -> ReportBuilder:
    """Create a default report builder instance."""
    return ReportBuilder()


def create_cost_classifier() -> CostClassRanges:
    """Create a default cost classifier instance."""
    return CostClassRanges()


def create_report_exporter() -> ReportExporter:
    """Create a default report exporter instance."""
    return ReportExporter()


def create_report_visualizer() -> ReportVisualizer:
    """Create a default report visualizer instance."""
    return ReportVisualizer()


def quick_report(calculations: Dict[str, CostCalculation],
                line_items: List[LineItem],
                report_type: str = 'detailed') -> pd.DataFrame:
    """Quick report generation."""
    builder = ReportBuilder()
    
    if report_type == 'detailed':
        return builder.create_detailed_report(calculations, line_items)
    elif report_type == 'summary':
        return builder.create_summary_report(calculations, line_items)
    elif report_type == 'analysis':
        return builder.create_cost_analysis_report(calculations, line_items)
    else:
        logger.warning(f"Unknown report type: {report_type}")
        return pd.DataFrame()
