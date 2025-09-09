#!/usr/bin/env python3
"""Simple test script to verify backend imports work correctly."""

import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

try:
    print("Testing backend imports...")
    
    # Test basic imports
    from schemas import Project, LineItem, Item, CostBreakdown
    print("✅ schemas imported successfully")
    
    from qto import QTOLoader
    print("✅ qto imported successfully")
    
    from rollups import CostRollup
    print("✅ rollups imported successfully")
    
    from calculator import CostCalculation
    print("✅ calculator imported successfully")
    
    from productivity import ProductivityCalculator
    print("✅ productivity imported successfully")
    
    from reporting import ReportBuilder
    print("✅ reporting imported successfully")
    
    print("\n🎉 All backend imports successful!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    sys.exit(1)
