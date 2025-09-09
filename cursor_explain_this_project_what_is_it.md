# explain this project. what is it doing and how is
_Exported on 8/29/2025 at 18:41:25 PDT from Cursor (1.5.5)_

---

**User**

explain this project. what is it doing and how is it doing it?

---

**Cursor**

I'll explore this project to understand what it's doing and how it works. Let me start by reading the main README file and examining the project structure.

Now let me explore more of the core functionality to understand the estimation system better:

Now let me check the frontend structure and see how it integrates with the backend:

Based on my exploration of the codebase, I can now provide you with a comprehensive explanation of this project.

## GC Estimator - What It Is

**GC Estimator** is a comprehensive **General Contractor Cost Estimation Tool** designed for construction professionals to create, manage, and analyze construction project estimates. It's a full-stack web application that helps contractors calculate project costs with professional accuracy and detailed breakdowns.

## What It Does

The system provides several key capabilities:

### 1. **Estimate Management**
- Create new construction estimates with project metadata (name, client, description, AACE class)
- Set overhead and profit percentages (defaults: 15% overhead, 10% profit)
- Manage multiple estimates through a dashboard interface

### 2. **Quantity Takeoff (QTO)**
- Add individual line items with detailed specifications:
  - Construction phases (Site Work, Foundation, Structure, etc.)
  - Item descriptions and codes (MasterFormat/CSI standards)
  - Units of measurement (SF, CY, EA, LF, etc.)
  - Quantities with waste percentages
  - Unit costs or lump sum amounts
- Import QTO data from Excel/CSV files
- Edit and delete line items

### 3. **Cost Calculations**
- **Material Costs**: Unit costs × quantities (including waste)
- **Labor Costs**: Based on labor classes, productivity rates, and burdened hourly rates
- **Equipment Costs**: Hourly rates × usage hours
- **Subcontractor Costs**: Unit rates or lump sum amounts
- **Overhead & Profit**: Applied as percentages to direct costs

### 4. **Advanced Analytics & Reporting**
- **Phase Rollups**: Cost breakdowns by construction phases
- **Trade Rollups**: Costs organized by construction trades
- **Cost Type Analysis**: Material vs. Labor vs. Equipment breakdowns
- **Room-based Allocations**: Costs distributed across building areas
- **Visual Charts**: Pie charts and bar graphs for cost visualization
- **Cost per Square Foot**: Efficiency metrics

## How It Works - Architecture

### **Backend (FastAPI/Python)**

The backend uses a sophisticated estimation engine:

1. **Data Models** (`schemas.py`):
   - `Project`: Overall project with overhead/profit settings
   - `Item`: Individual line items with quantities and costs
   - `LaborClass`: Labor rates with burden calculations
   - `Productivity`: Hours per unit for different work types

2. **Cost Calculator** (`calculator.py`):
   - Processes each line item through cost computation
   - Applies waste percentages, labor productivity, and regional factors
   - Calculates direct costs (material + labor + equipment + subcontract)
   - Applies contingency, overhead, and profit in proper sequence

3. **Rollup Engine** (`rollups.py`):
   - Aggregates costs across multiple dimensions
   - Creates comprehensive summary reports
   - Provides cost analysis and efficiency metrics
   - Generates data for charts and visualizations

4. **QTO Loader** (`qto.py`):
   - Imports data from Excel/CSV files
   - Validates data integrity and completeness
   - Converts raw data into structured objects

### **Frontend (Next.js/React)**

The frontend provides a modern, responsive interface:

1. **Dashboard**: Overview of all estimates with creation/management tools

2. **Estimate Workspace**: Comprehensive project interface with:
   - **Items Tab**: Sortable table of all line items with add/edit/delete
   - **Phase Summary**: Visual breakdown by construction phases
   - **Trade Summary**: Cost analysis by construction trades  
   - **Cost Breakdown**: Complete financial analysis

3. **Real-time Updates**: Live totals and calculations as items are modified

4. **Import/Export**: File upload for QTO data and export capabilities

### **Key Technical Features**

1. **Professional Standards**:
   - AACE (Association for Advancement of Cost Engineering) classification
   - MasterFormat/CSI work breakdown structure
   - UNIFORMAT II phase organization

2. **Precision Calculations**:
   - Uses `Decimal` type for financial accuracy
   - Proper cost escalation sequence (direct → contingency → overhead → profit)
   - Regional adjustment factors

3. **Flexible Costing**:
   - Multiple cost types (material, labor, equipment, subcontract)
   - Unit-based or lump sum pricing
   - Waste and productivity factors

4. **Scalable Architecture**:
   - Docker containerization
   - Microservices separation (frontend/backend)
   - RESTful API design

## Business Value

This system addresses real construction industry needs:

- **Accuracy**: Professional-grade calculations following industry standards
- **Efficiency**: Automated calculations and data import capabilities  
- **Transparency**: Detailed breakdowns for client presentations and internal analysis
- **Flexibility**: Handles various project types and costing methods
- **Scalability**: Can manage multiple projects and complex estimates

The tool essentially digitizes and automates the traditionally manual process of construction cost estimation, providing contractors with a professional, accurate, and efficient way to bid on projects and manage costs.

