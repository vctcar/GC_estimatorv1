"""
Quantity Takeoff (QTO) module for loading and validating project data.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Union
import logging
from decimal import Decimal, InvalidOperation

from schemas import Project, LineItem, Room, Trade, Phase, CostType

logger = logging.getLogger(__name__)


class QTOValidator:
    """Validates quantity takeoff data for consistency and completeness."""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def validate_line_item(self, item: LineItem) -> bool:
        """Validate a single line item."""
        is_valid = True
        
        # Check quantity is positive
        if item.quantity <= 0:
            self.errors.append(f"Line item {item.id}: Quantity must be positive")
            is_valid = False
        
        # Check unit is not empty
        if not item.unit.strip():
            self.errors.append(f"Line item {item.id}: Unit cannot be empty")
            is_valid = False
        
        # Check description is not empty
        if not item.description.strip():
            self.errors.append(f"Line item {item.id}: Description cannot be empty")
            is_valid = False
        
        return is_valid
    
    def validate_project(self, project: Project) -> bool:
        """Validate entire project for consistency."""
        is_valid = True
        
        # Check total area matches sum of room areas
        room_area_sum = sum(room.area for room in project.rooms)
        if abs(room_area_sum - project.total_area) > Decimal('0.01'):
            self.warnings.append(
                f"Total project area ({project.total_area}) doesn't match sum of room areas ({room_area_sum})"
            )
        
        # Validate all line items
        for item in project.line_items:
            if not self.validate_line_item(item):
                is_valid = False
        
        return is_valid


class QTOLoader:
    """Loads quantity takeoff data from various file formats."""
    
    def __init__(self):
        self.validator = QTOValidator()
    
    def load_excel(self, file_path: Union[str, Path]) -> pd.DataFrame:
        """Load QTO data from Excel file."""
        try:
            df = pd.read_excel(file_path, sheet_name=0)
            logger.info(f"Successfully loaded Excel file: {file_path}")
            return df
        except Exception as e:
            logger.error(f"Error loading Excel file {file_path}: {e}")
            raise
    
    def load_csv(self, file_path: Union[str, Path]) -> pd.DataFrame:
        """Load QTO data from CSV file."""
        try:
            df = pd.read_csv(file_path)
            logger.info(f"Successfully loaded CSV file: {file_path}")
            return df
        except Exception as e:
            logger.error(f"Error loading CSV file {file_path}: {e}")
            raise
    
    def parse_line_items(self, df: pd.DataFrame) -> List[LineItem]:
        """Parse DataFrame into LineItem objects."""
        line_items = []
        
        for _, row in df.iterrows():
            try:
                # Convert quantity to Decimal for precision
                quantity = Decimal(str(row.get('quantity', 0)))
                
                # Parse trade and phase enums
                trade = Trade(row.get('trade', 'general').lower())
                phase = Phase(row.get('phase', 'general').lower())
                cost_type = CostType(row.get('cost_type', 'material').lower())
                
                # Parse rooms list
                rooms_str = row.get('rooms', '')
                rooms = [r.strip() for r in rooms_str.split(',')] if rooms_str else []
                
                line_item = LineItem(
                    id=str(row.get('id', f"item_{len(line_items)}")),
                    description=str(row.get('description', '')),
                    quantity=quantity,
                    unit=str(row.get('unit', '')),
                    trade=trade,
                    phase=phase,
                    cost_type=cost_type,
                    rooms=rooms
                )
                
                line_items.append(line_item)
                
            except (ValueError, KeyError) as e:
                logger.warning(f"Skipping invalid row {row}: {e}")
                continue
        
        return line_items
    
    def parse_rooms(self, df: pd.DataFrame) -> List[Room]:
        """Parse DataFrame into Room objects."""
        rooms = []
        
        for _, row in df.iterrows():
            try:
                area = Decimal(str(row.get('area', 0)))
                height = Decimal(str(row.get('height', 0))) if row.get('height') else None
                multiplier = Decimal(str(row.get('multiplier', 1.0)))
                
                room = Room(
                    name=str(row.get('name', '')),
                    area=area,
                    height=height,
                    multiplier=multiplier
                )
                
                rooms.append(room)
                
            except (ValueError, KeyError) as e:
                logger.warning(f"Skipping invalid room row {row}: {e}")
                continue
        
        return rooms
    
    def create_project(self, 
                      name: str,
                      location: str,
                      project_type: str,
                      total_area: Union[float, Decimal],
                      line_items_df: Optional[pd.DataFrame] = None,
                      rooms_df: Optional[pd.DataFrame] = None) -> Project:
        """Create a Project object from data."""
        
        # Convert total_area to Decimal
        if isinstance(total_area, float):
            total_area = Decimal(str(total_area))
        
        project = Project(
            name=name,
            location=location,
            project_type=project_type,
            total_area=total_area,
            rooms=[],
            line_items=[]
        )
        
        # Add rooms if provided
        if rooms_df is not None:
            project.rooms = self.parse_rooms(rooms_df)
        
        # Add line items if provided
        if line_items_df is not None:
            project.line_items = self.parse_line_items(line_items_df)
        
        # Validate the project
        if not self.validator.validate_project(project):
            logger.warning("Project validation completed with warnings/errors")
            for error in self.validator.errors:
                logger.error(error)
            for warning in self.validator.warnings:
                logger.warning(warning)
        
        return project


def load_project_from_files(project_config: Dict,
                           qto_file: Union[str, Path],
                           rooms_file: Optional[Union[str, Path]] = None) -> Project:
    """Convenience function to load a complete project from files."""
    
    loader = QTOLoader()
    
    # Load QTO data
    if str(qto_file).endswith('.xlsx') or str(qto_file).endswith('.xls'):
        qto_df = loader.load_excel(qto_file)
    else:
        qto_df = loader.load_csv(qto_file)
    
    # Load rooms data if provided
    rooms_df = None
    if rooms_file:
        if str(rooms_file).endswith('.xlsx') or str(rooms_file).endswith('.xls'):
            rooms_df = loader.load_excel(rooms_file)
        else:
            rooms_df = loader.load_csv(rooms_file)
    
    # Create project
    project = loader.create_project(
        name=project_config['name'],
        location=project_config['location'],
        project_type=project_config['project_type'],
        total_area=project_config['total_area'],
        line_items_df=qto_df,
        rooms_df=rooms_df
    )
    
    return project
