# Import Excel/CSV Feature

## Overview
The Import Excel/CSV feature allows users to bulk import line items from Excel (.xlsx, .xls) or CSV files into construction estimates. The feature includes client-side parsing, preview functionality, and integration with the existing backend import endpoint.

## Features

### File Support
- **Excel Files**: .xlsx and .xls formats
- **CSV Files**: Comma-separated values
- **File Validation**: Automatic file type checking
- **Size Limits**: Handles files up to browser memory limits

### Parsing Capabilities
- **Smart Column Detection**: Automatically identifies columns by name patterns
- **Flexible Headers**: Supports various column naming conventions
- **Data Validation**: Ensures numeric fields are properly parsed
- **Error Handling**: Graceful handling of malformed data

### Column Mapping
The parser automatically detects these column types:
- **Phase**: Columns containing "phase" or "trade"
- **Item**: Columns containing "item" or "description"
- **Unit**: Columns containing "unit" or "uom"
- **Quantity**: Columns containing "quantity" or "qty"
- **Waste**: Columns containing "waste" or "overage"
- **Unit Cost**: Columns containing "unit" and "cost"
- **Lump Sum**: Columns containing "lump" or "fixed"

### User Experience
- **Preview Table**: Shows parsed items before import
- **Target Selection**: Choose which estimate to import into
- **Progress Indicators**: Loading states during parsing and import
- **Error Messages**: Clear feedback for file issues
- **Success Feedback**: Confirmation of successful imports

## Technical Implementation

### Components
- `ImportDialog.tsx`: Main import dialog component
- `alert.tsx`: Alert components for error/success messages
- API Routes: Proxy to FastAPI backend import endpoint

### Client-Side Parsing
```typescript
// Uses ExcelJS for Excel files
const workbook = new XLSX.Workbook()
await workbook.xlsx.load(data as ArrayBuffer)

// Manual CSV parsing for CSV files
const lines = csvText.split('\n')
const headers = lines[0]?.split(',').map(h => h.trim()) || []
```

### API Integration
- **Client Parsing**: Parse file on client, send items to backend
- **Backend Parsing**: Use existing `/api/estimates/import` endpoint
- **Batch Import**: Import multiple items to specific estimate

## Usage

### From Dashboard
1. Click "Import Excel/CSV" button
2. Select target estimate from dropdown
3. Choose file to upload
4. Review parsed items in preview table
5. Click "Import Items" to complete

### From Estimate Page
1. Click "Import" button in estimate workspace
2. Choose file to upload
3. Review parsed items in preview table
4. Click "Import Items" to add to current estimate

### File Format Requirements
The file should have a header row with columns for:
- Phase (construction phase or trade)
- Item (work item description)
- Unit (unit of measurement)
- Quantity (numeric value)
- Waste (percentage, optional)
- Unit Cost (numeric value, optional)
- Lump Sum (numeric value, optional)

## Sample Template

A sample CSV template is available for download:
```
Phase,Item,Unit,Quantity,Waste,Unit Cost,Lump Sum
Site Work,Excavation,CY,1500,10,25.50,0
Concrete,Foundation,CY,800,8,450.00,0
Masonry,CMU Walls,SF,3000,5,28.00,0
```

## Error Handling

### File Validation
- Invalid file types are rejected with clear error messages
- File size limits are enforced
- Corrupted files are handled gracefully

### Parsing Errors
- Missing required columns are reported
- Invalid numeric data is handled
- Empty rows are automatically skipped

### Import Errors
- Network failures are caught and reported
- Backend validation errors are displayed
- Partial import failures are handled

## Performance Considerations

### Large Files
- Files are processed in chunks to avoid memory issues
- Progress indicators show parsing status
- Preview table is scrollable for large datasets

### Memory Management
- File data is cleaned up after processing
- Temporary objects are properly disposed
- Browser memory limits are respected

## Future Enhancements

Potential improvements for future iterations:
- **Column Mapping UI**: Allow users to manually map columns
- **Data Validation Rules**: Custom validation for specific fields
- **Import Templates**: Save and reuse import configurations
- **Batch Operations**: Import to multiple estimates
- **Data Transformation**: Pre-import data cleaning and formatting
- **Import History**: Track and review previous imports
- **Conflict Resolution**: Handle duplicate items during import
