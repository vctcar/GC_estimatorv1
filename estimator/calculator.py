from typing import Dict, List
from dataclasses import dataclass
from decimal import Decimal
from .schemas import Project, Phase, Item, LaborClass, Productivity

@dataclass
class CostCalculation:
    """Result of a cost calculation."""
    line_item_id: str
    description: str
    quantity: Decimal
    unit: str
    material_cost: Decimal
    labor_cost: Decimal
    equipment_cost: Decimal
    total_cost: Decimal
    cost_per_unit: Decimal
    breakdown: Dict[str, Decimal]

def _burdened_rate(lc: LaborClass) -> float:
    return lc.base_rate * (1 + lc.burden_pct)

def _labor_hours(item: Item, prod_map: Dict[str, Productivity], regional_factor: float) -> float:
    p = prod_map.get(item.code)
    if not p or item.labor_class is None:
        return 0.0
    mult = 1.0
    for _, v in p.factors.items():
        mult *= v
    return item.quantity * p.hours_per_unit * mult * regional_factor

def compute(project: Project, phases: List[Phase], items: List[Item],
            labor_classes: List[LaborClass], productivities: List[Productivity]):
    # Indexes - use phase value as code since Phase is now an enum
    phase_by_code = {p.value: p for p in phases}
    labor_by_name = {l.name: l for l in labor_classes}
    prod_by_code  = {p.item_code: p for p in productivities}

    rows = []
    phase_direct = {p.value: 0.0 for p in phases}

    for it in items:
        qty_waste = it.quantity * (1 + it.waste_pct)
        material = qty_waste * it.material_unit_cost
        equip    = it.usage_hours * it.equipment_rate_per_hr

        sub = 0.0
        if it.subcontract_lump_sum is not None:
            sub = it.subcontract_lump_sum
        elif it.subcontract_unit_rate is not None:
            sub = it.quantity * it.subcontract_unit_rate

        labor = 0.0
        hours = 0.0
        if it.labor_class:
            hours = _labor_hours(it, prod_by_code, project.regional_factor)
            rate  = _burdened_rate(labor_by_name[it.labor_class])
            labor = hours * rate

        direct = labor + material + equip + sub
        phase_direct[it.phase_code] += direct

        rows.append({
            "phase_code": it.phase_code,
            "item_code": it.code,
            "description": it.description,
            "uom": it.uom,
            "quantity": it.quantity,
            "waste_pct": it.waste_pct,
            "labor_hours": hours,
            "labor_cost": labor,
            "material_cost": material,
            "equipment_cost": equip,
            "subcontract_cost": sub,
            "direct_cost": direct,
            "room_zone": it.room_zone
        })

    # Per-phase contingency - use default 10% since Phase enum doesn't have contingency_pct
    phase_cont = {}
    for code, dcost in phase_direct.items():
        # Default contingency of 10%
        phase_cont[code] = dcost * 0.10

    direct_total = sum(phase_direct.values())
    cont_total   = sum(phase_cont.values())

    overhead = (direct_total + cont_total) * project.overhead_pct
    profit   = (direct_total + cont_total + overhead) * project.profit_pct
    grand_total = direct_total + cont_total + overhead + profit

    summary = {
        "estimate_class": project.estimate_class,
        "direct_total": direct_total,
        "phase_contingency_total": cont_total,
        "overhead": overhead,
        "profit": profit,
        "grand_total": grand_total,
    }
    return rows, phase_direct, phase_cont, summary
