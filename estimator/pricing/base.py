"""
Base pricing provider protocol and interfaces.
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional, List, Union
from decimal import Decimal
from dataclasses import dataclass
from datetime import datetime

from ..schemas import Trade, Phase, CostType


@dataclass
class PricingRequest:
    """Request for pricing information."""
    item_description: str
    trade: Trade
    phase: Phase
    cost_type: CostType
    quantity: Decimal
    unit: str
    location: str
    date_requested: datetime
    additional_context: Optional[Dict[str, str]] = None


@dataclass
class PricingResponse:
    """Response with pricing information."""
    item_description: str
    source: str
    material_unit_cost: Optional[Decimal] = None
    labor_hours_per_unit: Optional[Decimal] = None
    labor_rate_per_hour: Optional[Decimal] = None
    equipment_cost_per_unit: Optional[Decimal] = None
    overhead_rate: Optional[Decimal] = None
    profit_rate: Optional[Decimal] = None
    confidence_score: float = 0.0  # 0.0 to 1.0
    date_retrieved: datetime = None
    notes: Optional[str] = None
    
    def __post_init__(self):
        if self.date_retrieved is None:
            self.date_retrieved = datetime.now()
    
    @property
    def total_unit_cost(self) -> Optional[Decimal]:
        """Calculate total cost per unit including all components."""
        if self.material_unit_cost is None:
            return None
        
        total = self.material_unit_cost
        
        # Add labor cost if available
        if self.labor_hours_per_unit and self.labor_rate_per_hour:
            total += self.labor_hours_per_unit * self.labor_rate_per_hour
        
        # Add equipment cost if available
        if self.equipment_cost_per_unit:
            total += self.equipment_cost_per_unit
        
        # Apply overhead and profit if available
        if self.overhead_rate:
            total *= (1 + self.overhead_rate)
        
        if self.profit_rate:
            total *= (1 + self.profit_rate)
        
        return total


class PricingProvider(ABC):
    """Abstract base class for pricing providers."""
    
    def __init__(self, name: str, config: Optional[Dict] = None):
        self.name = name
        self.config = config or {}
        self.is_available = True
    
    @abstractmethod
    def get_pricing(self, request: PricingRequest) -> Optional[PricingResponse]:
        """Get pricing for a specific item."""
        pass
    
    @abstractmethod
    def search_items(self, query: str, trade: Optional[Trade] = None) -> List[str]:
        """Search for available items matching a query."""
        pass
    
    @abstractmethod
    def get_supported_trades(self) -> List[Trade]:
        """Get list of trades supported by this provider."""
        pass
    
    @abstractmethod
    def get_supported_locations(self) -> List[str]:
        """Get list of locations supported by this provider."""
        pass
    
    def is_item_supported(self, item_description: str, trade: Trade) -> bool:
        """Check if this provider supports a specific item."""
        supported_items = self.search_items(item_description, trade)
        return len(supported_items) > 0
    
    def get_confidence_score(self, request: PricingRequest) -> float:
        """Get confidence score for pricing accuracy (0.0 to 1.0)."""
        # Default implementation - subclasses should override
        return 0.5
    
    def validate_request(self, request: PricingRequest) -> bool:
        """Validate if a pricing request can be processed."""
        if not self.is_available:
            return False
        
        if request.trade not in self.get_supported_trades():
            return False
        
        if request.location not in self.get_supported_locations():
            return False
        
        return True
    
    def get_provider_info(self) -> Dict:
        """Get information about this pricing provider."""
        return {
            'name': self.name,
            'type': self.__class__.__name__,
            'available': self.is_available,
            'supported_trades': [t.value for t in self.get_supported_trades()],
            'supported_locations': self.get_supported_locations(),
            'config': self.config
        }


class CompositePricingProvider(PricingProvider):
    """Combines multiple pricing providers with fallback logic."""
    
    def __init__(self, providers: List[PricingProvider], name: str = "Composite"):
        super().__init__(name)
        self.providers = providers
        self.provider_weights = {p.name: 1.0 for p in providers}  # Equal weighting by default
    
    def get_pricing(self, request: PricingRequest) -> Optional[PricingResponse]:
        """Get pricing from multiple providers with fallback logic."""
        responses = []
        
        for provider in self.providers:
            if provider.validate_request(request):
                try:
                    response = provider.get_pricing(request)
                    if response:
                        responses.append(response)
                except Exception as e:
                    # Log error but continue with other providers
                    continue
        
        if not responses:
            return None
        
        # Return the response with highest confidence score
        best_response = max(responses, key=lambda r: r.confidence_score)
        return best_response
    
    def search_items(self, query: str, trade: Optional[Trade] = None) -> List[str]:
        """Search across all providers."""
        all_items = set()
        for provider in self.providers:
            try:
                items = provider.search_items(query, trade)
                all_items.update(items)
            except Exception:
                continue
        
        return list(all_items)
    
    def get_supported_trades(self) -> List[Trade]:
        """Get union of all supported trades."""
        all_trades = set()
        for provider in self.providers:
            all_trades.update(provider.get_supported_trades())
        
        return list(all_trades)
    
    def get_supported_locations(self) -> List[str]:
        """Get union of all supported locations."""
        all_locations = set()
        for provider in self.providers:
            all_locations.update(provider.get_supported_locations())
        
        return list(all_locations)
    
    def set_provider_weight(self, provider_name: str, weight: float):
        """Set weight for a specific provider in composite calculations."""
        if provider_name in self.provider_weights:
            self.provider_weights[provider_name] = weight
    
    def get_weighted_pricing(self, request: PricingRequest) -> Optional[PricingResponse]:
        """Get weighted average pricing from multiple providers."""
        responses = []
        weights = []
        
        for provider in self.providers:
            if provider.validate_request(request):
                try:
                    response = provider.get_pricing(request)
                    if response and response.material_unit_cost:
                        responses.append(response)
                        weights.append(self.provider_weights.get(provider.name, 1.0))
                except Exception:
                    continue
        
        if not responses:
            return None
        
        # Calculate weighted average
        total_weight = sum(weights)
        weighted_cost = sum(r.material_unit_cost * w for r, w in zip(responses, weights)) / total_weight
        
        # Create composite response
        best_response = max(responses, key=lambda r: r.confidence_score)
        composite_response = PricingResponse(
            item_description=request.item_description,
            material_unit_cost=weighted_cost,
            labor_hours_per_unit=best_response.labor_hours_per_unit,
            labor_rate_per_hour=best_response.labor_rate_per_hour,
            equipment_cost_per_unit=best_response.equipment_cost_per_unit,
            overhead_rate=best_response.overhead_rate,
            profit_rate=best_response.profit_rate,
            source=f"Composite({', '.join(r.source for r in responses)})",
            confidence_score=sum(r.confidence_score * w for r, w in zip(responses, weights)) / total_weight,
            notes=f"Weighted average from {len(responses)} providers"
        )
        
        return composite_response


class PricingCache:
    """Simple in-memory cache for pricing data."""
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.cache = {}
        self.access_times = {}
    
    def get(self, key: str) -> Optional[PricingResponse]:
        """Get cached pricing data."""
        if key in self.cache:
            self.access_times[key] = datetime.now()
            return self.cache[key]
        return None
    
    def set(self, key: str, value: PricingResponse):
        """Cache pricing data."""
        if len(self.cache) >= self.max_size:
            # Remove least recently used item
            oldest_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
            del self.cache[oldest_key]
            del self.access_times[oldest_key]
        
        self.cache[key] = value
        self.access_times[key] = datetime.now()
    
    def clear(self):
        """Clear all cached data."""
        self.cache.clear()
        self.access_times.clear()
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics."""
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'hit_rate': 0.0  # Would need to track hits/misses for actual rate
        }
