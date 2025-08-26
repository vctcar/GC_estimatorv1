from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional
import os
import tempfile
import shutil
from datetime import datetime
import uuid

# Import your existing estimator modules
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from estimator.schemas import Project, LineItem, Item, CostBreakdown
from estimator.qto import QTOLoader
from estimator.rollups import CostRollup

app = FastAPI(
    title="GC Estimator API",
    description="REST API for General Contractor Estimation Tool",
    version="1.0.0"
)

# Add CORS middleware for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for estimates (replace with database in production)
estimates_db = {}

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "GC Estimator API is running", "version": "1.0.0"}

@app.get("/api/estimates")
async def list_estimates():
    """List all estimates for dashboard"""
    estimates = []
    for estimate_id, estimate in estimates_db.items():
        estimates.append({
            "id": estimate_id,
            "name": estimate.get("name", "Unnamed Estimate"),
            "client": estimate.get("client", ""),
            "total": estimate.get("total", 0),
            "status": estimate.get("status", "Draft"),
            "created": estimate.get("created", ""),
            "lastModified": estimate.get("lastModified", "")
        })
    return {"estimates": estimates}

@app.post("/api/estimates")
async def create_estimate(project_data: dict):
    """Create a new empty estimate or from template"""
    estimate_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    
    new_estimate = {
        "id": estimate_id,
        "name": project_data.get("name", "New Estimate"),
        "client": project_data.get("client", ""),
        "description": project_data.get("description", ""),
        "overhead_percent": project_data.get("overhead_percent", 15.0),
        "profit_percent": project_data.get("profit_percent", 10.0),
        "aace_class": project_data.get("aace_class", "Class 3"),
        "status": "Draft",
        "created": now,
        "lastModified": now,
        "items": [],
        "metadata": project_data.get("metadata", {})
    }
    
    estimates_db[estimate_id] = new_estimate
    return {"estimate": new_estimate, "message": "Estimate created successfully"}

@app.post("/api/estimates/import")
async def import_qto(file: UploadFile = File(...)):
    """Upload and parse a QTO Excel/CSV file"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Check file extension
    if not file.filename.lower().endswith(('.xlsx', '.xls', '.csv')):
        raise HTTPException(status_code=400, detail="File must be Excel (.xlsx, .xls) or CSV (.csv)")
    
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_file_path = temp_file.name
        
        # Parse the file using your existing QTOLoader
        loader = QTOLoader()
        df = loader.load_excel(temp_file_path)
        items = loader.parse_line_items(df)
        
        # Clean up temporary file
        os.unlink(temp_file_path)
        
        # Convert items to dictionaries for JSON response
        line_items = []
        for item in items:
            line_items.append({
                "id": str(uuid.uuid4()),
                "phase": item.phase,
                "item": item.item,
                "unit": item.unit,
                "quantity": item.quantity,
                "waste": item.waste,
                "unit_cost": item.unit_cost,
                "lump_sum": item.lump_sum,
                "subtotal": item.subtotal
            })
        
        return {
            "message": f"Successfully imported {len(line_items)} items",
            "line_items": line_items,
            "total_items": len(line_items)
        }
        
    except Exception as e:
        # Clean up temp file if it exists
        if 'temp_file_path' in locals():
            try:
                os.unlink(temp_file_path)
            except:
                pass
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.get("/api/estimates/{estimate_id}")
async def get_estimate(estimate_id: str):
    """Fetch an estimate's data (meta, line items)"""
    if estimate_id not in estimates_db:
        raise HTTPException(status_code=404, detail="Estimate not found")
    
    estimate = estimates_db[estimate_id]
    return {"estimate": estimate}

@app.put("/api/estimates/{estimate_id}")
async def update_estimate(estimate_id: str, update_data: dict):
    """Update project metadata"""
    if estimate_id not in estimates_db:
        raise HTTPException(status_code=404, detail="Estimate not found")
    
    estimate = estimates_db[estimate_id]
    
    # Update allowed fields
    allowed_fields = ["name", "client", "description", "overhead_percent", "profit_percent", "aace_class", "status", "metadata"]
    for field in allowed_fields:
        if field in update_data:
            estimate[field] = update_data[field]
    
    estimate["lastModified"] = datetime.now().isoformat()
    estimates_db[estimate_id] = estimate
    
    return {"estimate": estimate, "message": "Estimate updated successfully"}

@app.post("/api/estimates/{estimate_id}/items")
async def add_item(estimate_id: str, item_data: dict):
    """Add a new line item to estimate"""
    if estimate_id not in estimates_db:
        raise HTTPException(status_code=404, detail="Estimate not found")
    
    estimate = estimates_db[estimate_id]
    
    # Create new item with ID
    new_item = {
        "id": str(uuid.uuid4()),
        "phase": item_data.get("phase", ""),
        "item": item_data.get("item", ""),
        "unit": item_data.get("unit", ""),
        "quantity": item_data.get("quantity", 0),
        "waste": item_data.get("waste", 0),
        "unit_cost": item_data.get("unit_cost", 0),
        "lump_sum": item_data.get("lump_sum", 0),
        "subtotal": item_data.get("subtotal", 0)
    }
    
    # Add to estimate items
    if "items" not in estimate:
        estimate["items"] = []
    estimate["items"].append(new_item)
    
    # Update last modified
    estimate["lastModified"] = datetime.now().isoformat()
    estimates_db[estimate_id] = estimate
    
    return {"item": new_item, "message": "Item added successfully"}

@app.put("/api/estimates/{estimate_id}/items/{item_id}")
async def update_item(estimate_id: str, item_id: str, item_data: dict):
    """Update an existing line item"""
    if estimate_id not in estimates_db:
        raise HTTPException(status_code=404, detail="Estimate not found")
    
    estimate = estimates_db[estimate_id]
    
    # Find and update the item
    for item in estimate.get("items", []):
        if item["id"] == item_id:
            # Update item fields
            allowed_fields = ["phase", "item", "unit", "quantity", "waste", "unit_cost", "lump_sum", "subtotal"]
            for field in allowed_fields:
                if field in item_data:
                    item[field] = item_data[field]
            
            # Update estimate last modified
            estimate["lastModified"] = datetime.now().isoformat()
            estimates_db[estimate_id] = estimate
            
            return {"item": item, "message": "Item updated successfully"}
    
    raise HTTPException(status_code=404, detail="Item not found")

@app.delete("/api/estimates/{estimate_id}/items/{item_id}")
async def delete_item(estimate_id: str, item_id: str):
    """Delete a line item from estimate"""
    if estimate_id not in estimates_db:
        raise HTTPException(status_code=404, detail="Estimate not found")
    
    estimate = estimates_db[estimate_id]
    
    # Find and remove the item
    for i, item in enumerate(estimate.get("items", [])):
        if item["id"] == item_id:
            estimate["items"].pop(i)
            estimate["lastModified"] = datetime.now().isoformat()
            estimates_db[estimate_id] = estimate
            return {"message": "Item deleted successfully"}
    
    raise HTTPException(status_code=404, detail="Item not found")

@app.get("/api/estimates/{estimate_id}/rollup")
async def get_rollup(estimate_id: str):
    """Run cost calculations and return rollup summary"""
    if estimate_id not in estimates_db:
        raise HTTPException(status_code=404, detail="Estimate not found")
    
    estimate = estimates_db[estimate_id]
    
    try:
        # Create CostRollup instance with estimate data
        items = estimate.get("items", [])
        
        # Convert items to Item objects for rollup calculation
        items_list = []
        for item in items:
            # Create Item object based on the actual schema
            item_obj = Item(
                phase_code=item["phase"],
                code=item.get("item", ""),
                description=item.get("item", ""),
                uom=item["unit"],
                quantity=item["quantity"],
                waste_pct=item["waste"],
                material_unit_cost=item["unit_cost"],
                subcontract_lump_sum=item["lump_sum"]
            )
            items_list.append(item_obj)
        
        # Create project for rollup
        project = Project(
            name=estimate["name"],
            estimate_class=estimate.get("aace_class", "Class 3"),
            overhead_pct=estimate.get("overhead_percent", 15.0) / 100.0,
            profit_pct=estimate.get("profit_percent", 10.0) / 100.0
        )
        
        # Calculate rollup
        rollup = CostRollup(project, items_list)
        summary = rollup.create_summary_report()
        
        return {
            "estimate_id": estimate_id,
            "rollup": summary,
            "project_info": {
                "name": project.name,
                "client": project.client,
                "overhead_percent": project.overhead_percent,
                "profit_percent": project.profit_percent,
                "aace_class": project.aace_class
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating rollup: {str(e)}")

@app.delete("/api/estimates/{estimate_id}")
async def delete_estimate(estimate_id: str):
    """Delete an estimate"""
    if estimate_id not in estimates_db:
        raise HTTPException(status_code=404, detail="Estimate not found")
    
    del estimates_db[estimate_id]
    return {"message": "Estimate deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
