from typing import List, Optional, Dict, Literal
from pydantic import BaseModel, Field
from decimal import Decimal
from enum import Enum

EstimateClass = Literal["Class 5","Class 4","Class 3","Class 2","Class 1"]

# Legacy enums for backward compatibility
class Phase(str, Enum):
    """Project phases."""
    PRE_CONSTRUCTION = "pre_construction"
    SITE_WORK = "site_work"
    FOUNDATION = "foundation"
    STRUCTURE = "structure"
    ENCLOSURE = "enclosure"
    INTERIORS = "interiors"
    MECHANICAL = "mechanical"
    ELECTRICAL = "electrical"
    FINISHES = "finishes"
    CLOSEOUT = "closeout"
    GENERAL = "general"

class Project(BaseModel):
    name: str
    estimate_class: EstimateClass = "Class 3"
    overhead_pct: float = 0.10      # 10% default
    profit_pct: float = 0.10        # 10% default
    regional_factor: float = 1.00   # scale on materials/productivity
    currency: str = "USD"
    units: Literal["US"] = "US"

class PhaseConfig(BaseModel):
    """Phase configuration for UNIFORMAT II."""
    code: str              # UNIFORMAT II code (e.g., B20, C30)
    name: str
    contingency_pct: float = 0.10   # per-phase default contingency

class LaborClass(BaseModel):
    name: str              # "Laborer", "Carpenter"
    base_rate: float       # $/hr
    burden_pct: float = 0.45  # 45% default burden (editable)

class Productivity(BaseModel):
    item_code: str         # CSI code (e.g., 09 30 00)
    hours_per_unit: float  # e.g., 0.12 h/SF
    factors: Dict[str, float] = {}  # e.g., {"access":1.10}

class Item(BaseModel):
    phase_code: str
    code: str              # CSI MasterFormat
    description: str
    uom: str               # "SF","LF","EA","CY"
    quantity: float
    waste_pct: float = 0.10
    # ONE of the following is used:
    labor_class: Optional[str] = None
    subcontract_unit_rate: Optional[float] = None   # $/unit
    subcontract_lump_sum: Optional[float] = None
    material_unit_cost: float = 0.0                 # $/unit material
    equipment_rate_per_hr: float = 0.0              # $/hr equip
    usage_hours: float = 0.0                        # equipment hours
    room_zone: Optional[str] = None

# Legacy models for backward compatibility
class CostType(str, Enum):
    """Types of costs in construction."""
    MATERIAL = "material"
    LABOR = "labor"
    EQUIPMENT = "equipment"
    OVERHEAD = "overhead"
    PROFIT = "profit"

class Trade(str, Enum):
    """Construction trades."""
    GENERAL = "general"
    EXCAVATION = "excavation"
    CONCRETE = "concrete"
    MASONRY = "masonry"
    METALS = "metals"
    WOOD = "wood"
    THERMAL = "thermal"
    DOORS_WINDOWS = "doors_windows"
    FINISHES = "finishes"
    SPECIALTIES = "specialties"
    EQUIPMENT = "equipment"
    MECHANICAL = "mechanical"
    ELECTRICAL = "electrical"

class Room(BaseModel):
    """Room definition for cost allocation."""
    name: str
    area: Decimal = Field(gt=0, description="Area in square feet")
    height: Optional[Decimal] = Field(None, gt=0, description="Height in feet")
    multiplier: Decimal = Field(default=1.0, description="Cost multiplier for this room")

class LineItem(BaseModel):
    """Individual line item for quantity takeoff."""
    id: str
    description: str
    quantity: Decimal = Field(gt=0)
    unit: str
    trade: Trade
    phase: Phase
    cost_type: CostType
    rooms: List[str] = Field(default_factory=list, description="Room IDs this item applies to")

class CostBreakdown(BaseModel):
    """Cost breakdown by various categories."""
    material_cost: Decimal = Field(default=0, ge=0)
    labor_cost: Decimal = Field(default=0, ge=0)
    equipment_cost: Decimal = Field(default=0, ge=0)
    overhead_cost: Decimal = Field(default=0, ge=0)
    profit: Decimal = Field(default=0, ge=0)
    
    @property
    def total_cost(self) -> Decimal:
        """Calculate total cost."""
        return sum([
            self.material_cost,
            self.labor_cost,
            self.equipment_cost,
            self.overhead_cost,
            self.profit
        ])

class PricingData(BaseModel):
    """Pricing information for materials and labor."""
    item_id: str
    material_unit_cost: Optional[Decimal] = Field(None, ge=0)
    labor_hours_per_unit: Optional[Decimal] = Field(None, ge=0)
    labor_rate_per_hour: Optional[Decimal] = Field(None, ge=0)
    source: str = Field(description="Source of pricing data")
    date_updated: Optional[str] = Field(None, description="Date when pricing was last updated")
