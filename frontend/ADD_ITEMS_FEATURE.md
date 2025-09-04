# Add Items Feature

## Overview
The Add Items feature allows users to add, edit, and delete line items in construction estimates through a comprehensive form with validation and catalog integration.

## Features

### Form Fields
- **Phase** (required): Construction phase or trade category
- **Division**: MasterFormat division for categorization
- **Item Description** (required): Work item or material description
- **Unit** (required): Unit of measurement (EA, SF, CY, etc.)
- **Quantity** (required): Total quantity needed
- **Waste %**: Extra percentage for waste/breakage (0-100%)
- **Unit Cost ($)**: Cost per unit
- **Lump Sum ($)**: Fixed cost alternative to unit cost

### User Experience
- **React Hook Form + Zod Validation**: Form validation with inline error messages
- **Catalog Integration**: Pre-populated phases and MasterFormat items
- **Tooltips**: Helpful explanations for all fields
- **Add/Edit/Delete Modes**: Single component handles all operations
- **Real-time Validation**: Prevents invalid submissions
- **Loading States**: Visual feedback during API operations

### Validation Rules
- **Phase**: Required, must be selected from catalog
- **Item Description**: Required, minimum 1 character
- **Unit**: Required, must be selected from catalog
- **Quantity**: Required, minimum 0
- **Waste %**: Optional, 0-100% range
- **Unit Cost**: Optional, minimum 0
- **Lump Sum**: Optional, minimum 0

## Technical Implementation

### Components
- `AddItemDialog.tsx`: Main dialog component with form
- `form.tsx`: React Hook Form components with validation
- `label.tsx`: Label component for form fields

### API Routes
- `/api/catalogs` (GET): Provides phase, division, and unit data
- `/api/estimates/{id}/items` (POST): Adds new item
- `/api/estimates/{id}/items/{itemId}` (PUT): Updates existing item
- `/api/estimates/{id}/items/{itemId}` (DELETE): Removes item

### Form Validation
```typescript
const itemFormSchema = z.object({
  phase: z.string().min(1, "Phase is required"),
  item: z.string().min(1, "Item description is required"),
  unit: z.string().min(1, "Unit is required"),
  quantity: z.number().min(0, "Quantity must be 0 or greater"),
  waste: z.number().min(0).max(100, "Waste cannot exceed 100%"),
  unit_cost: z.number().min(0, "Unit cost must be 0 or greater"),
  lump_sum: z.number().min(0, "Lump sum must be 0 or greater"),
})
```

## Usage

### Adding Items
1. Click "+ Add Item" button on estimate workspace
2. Fill in required fields (Phase, Item Description, Unit, Quantity)
3. Optionally set Waste %, Unit Cost, or Lump Sum
4. Click "Add Item" to save

### Editing Items
1. Click "Edit" button on any item row
2. Modify fields as needed
3. Click "Update Item" to save changes

### Deleting Items
1. Click "Delete" button on any item row, or
2. Open edit dialog and click "Delete" button
3. Confirm deletion

## Catalog Data

### Phases
- Pre-Construction
- Site Work
- Foundation
- Structure
- Enclosure
- Interiors
- Mechanical
- Electrical
- Finishes
- Closeout

### MasterFormat Divisions
- 00: Procurement and Contracting Requirements
- 01: General Requirements
- 02: Existing Conditions
- 03: Concrete
- 04: Masonry
- 05: Metals
- 06: Wood and Plastics
- 07: Thermal and Moisture Protection
- 08: Doors and Windows
- 09: Finishes
- 15: Mechanical
- 16: Electrical

### Units
- EA (Each)
- LF (Linear Feet)
- SF (Square Feet)
- SY (Square Yards)
- CY (Cubic Yards)
- TON (Tons)
- LB (Pounds)
- GAL (Gallons)
- LOT (Lot)
- LS (Lump Sum)

## Error Handling

The feature includes comprehensive error handling:
- Form validation errors with inline messages
- API error handling with user-friendly messages
- Network error handling
- Confirmation dialogs for destructive actions

## Future Enhancements

Potential improvements for future iterations:
- Bulk item import from Excel/CSV
- Item templates and favorites
- Advanced search and filtering
- Cost history tracking
- Integration with pricing databases
- Unit cost suggestions based on location/market
