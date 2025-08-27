# Export & Save Feature

## Overview
The Export & Save feature provides comprehensive data export capabilities and automatic saving functionality for construction estimates. Users can export their estimates in multiple formats and save changes to the backend with real-time feedback.

## Features

### Export Functionality
- **Multiple Formats**: Excel (.xlsx), CSV (.csv), and JSON (.json)
- **Comprehensive Data**: Project metadata, line items, cost summaries, and rollup data
- **Structured Output**: Organized worksheets and sections for easy analysis
- **Automatic Naming**: Files named with project name and timestamp

### Save Functionality
- **Automatic Saving**: Save estimate metadata to backend
- **Real-Time Feedback**: Success/error messages with toast notifications
- **API Integration**: Uses PUT `/api/estimates/{id}` endpoint
- **Data Persistence**: Changes persist as long as server runs

## Export Formats

### Excel (.xlsx)
**Multiple Worksheets:**
1. **Summary Sheet**: Project metadata and cost totals
2. **Line Items Sheet**: All line items with quantities and costs
3. **Phase Summary Sheet**: Cost breakdown by construction phase

**Summary Sheet Columns:**
- Project Name, Client, AACE Class, Status
- Created Date, Last Modified Date
- Direct Costs, Overhead, Profit, Total Estimate

**Line Items Sheet Columns:**
- Phase, Item, Unit, Quantity, Waste %
- Unit Cost, Lump Sum, Subtotal

**Phase Summary Sheet Columns:**
- Phase, Material, Labor, Equipment
- Overhead, Profit, Total

### CSV (.csv)
**Structured Sections:**
1. **ESTIMATE SUMMARY**: Project metadata and totals
2. **LINE ITEMS**: All line items in tabular format

**Format:**
```
ESTIMATE SUMMARY
Project Name,Office Building - Phase 1
Client,ABC Construction
AACE Class,Class 3
Status,Draft
Created,2024-01-15T10:30:00
Last Modified,2024-01-15T14:45:00

Direct Costs,715000.00
Overhead,107250.00
Profit,71500.00
Total Estimate,893750.00

LINE ITEMS
Phase,Item,Unit,Quantity,Waste %,Unit Cost,Lump Sum,Subtotal
Site Work,Excavation,CY,1500,10,25.50,0,42187.50
Concrete,Foundation,CY,800,8,450.00,0,388800.00
```

### JSON (.json)
**Complete Data Export:**
```json
{
  "estimate": {
    "id": "uuid",
    "name": "Office Building - Phase 1",
    "client": "ABC Construction",
    "description": "Phase 1 construction estimate",
    "overhead_percent": 15.0,
    "profit_percent": 10.0,
    "aace_class": "Class 3",
    "status": "Draft",
    "created": "2024-01-15T10:30:00",
    "lastModified": "2024-01-15T14:45:00",
    "items": [...]
  },
  "rollup": {
    "cost_summary": {...},
    "rollups": {
      "by_phase": {...},
      "by_trade": {...}
    }
  },
  "exported_at": "2024-01-15T15:00:00"
}
```

## Technical Implementation

### Export Components
- **ExportDialog**: Main export dialog with format selection
- **ExcelJS Integration**: Generate structured Excel workbooks
- **CSV Generation**: Manual CSV formatting with proper escaping
- **JSON Export**: Complete data serialization

### Save Components
- **SaveEstimate**: Save functionality with feedback
- **API Integration**: PUT requests to update estimate metadata
- **Error Handling**: Comprehensive error handling and user feedback

### File Generation
```typescript
// Excel generation
const workbook = new XLSX.Workbook()
const summarySheet = workbook.addWorksheet("Summary")
const itemsSheet = workbook.addWorksheet("Line Items")
const phaseSheet = workbook.addWorksheet("Phase Summary")

// CSV generation
const lines = []
lines.push("ESTIMATE SUMMARY")
lines.push("Project Name," + estimateData.name)
// ... more data

// JSON generation
const jsonData = {
  estimate: estimateData,
  rollup: rollupData,
  exported_at: new Date().toISOString()
}
```

## User Experience

### Export Workflow
1. **Click Export**: Opens export dialog with format options
2. **Select Format**: Choose Excel, CSV, or JSON
3. **Preview Contents**: See what data will be exported
4. **Generate File**: Creates and downloads file automatically
5. **Success Feedback**: Confirmation message displayed

### Save Workflow
1. **Click Save**: Triggers save operation
2. **API Call**: Sends data to backend
3. **Success Feedback**: Toast notification on success
4. **Error Handling**: Clear error messages if save fails

### Loading States
- **Export**: Loading spinner during file generation
- **Save**: Loading spinner during API call
- **Progress Indicators**: Visual feedback for all operations

## API Integration

### Save Endpoint
```
PUT /api/estimates/{id}
Content-Type: application/json

{
  "name": "Project Name",
  "client": "Client Name",
  "description": "Project description",
  "overhead_percent": 15.0,
  "profit_percent": 10.0,
  "aace_class": "Class 3",
  "status": "Draft",
  "metadata": {}
}
```

### Response
```json
{
  "estimate": {
    "id": "uuid",
    "name": "Updated Project Name",
    "lastModified": "2024-01-15T15:30:00"
  },
  "message": "Estimate updated successfully"
}
```

## File Management

### Naming Convention
- **Excel**: `{project_name}_{date}.xlsx`
- **CSV**: `{project_name}_{date}.csv`
- **JSON**: `{project_name}_{date}.json`

### File Size Optimization
- **Efficient Generation**: Streamlined file creation
- **Memory Management**: Proper cleanup after download
- **Large Dataset Support**: Handles estimates with many items

### Browser Compatibility
- **Modern Browsers**: Full support for all formats
- **Download Handling**: Automatic file download
- **Cross-Platform**: Works on desktop and mobile

## Error Handling

### Export Errors
- **File Generation**: Graceful handling of generation failures
- **Download Issues**: Fallback mechanisms for download problems
- **Format Errors**: Clear error messages for unsupported formats

### Save Errors
- **Network Issues**: Retry logic and offline handling
- **Validation Errors**: Backend validation feedback
- **Server Errors**: Comprehensive error reporting

## Benefits

### Data Portability
- **Multiple Formats**: Choose the best format for your needs
- **Complete Data**: Export all estimate information
- **Structured Output**: Easy to import into other systems

### Data Safety
- **Automatic Saving**: Changes are preserved
- **Backup Capability**: Export provides data backup
- **Version Control**: Timestamped exports for tracking

### Collaboration
- **Share Estimates**: Export for sharing with stakeholders
- **External Analysis**: Import into external tools
- **Audit Trail**: Complete data export for auditing

## Future Enhancements

### Advanced Export Features
- **Custom Templates**: User-defined export templates
- **Batch Export**: Export multiple estimates at once
- **Scheduled Exports**: Automatic export scheduling
- **Cloud Integration**: Direct export to cloud storage

### Enhanced Save Features
- **Auto-Save**: Automatic saving of changes
- **Version History**: Track changes over time
- **Conflict Resolution**: Handle concurrent edits
- **Offline Support**: Save when offline, sync when online

### Integration Improvements
- **Third-Party Tools**: Export to construction software
- **API Webhooks**: Notify external systems of changes
- **Real-Time Sync**: Live synchronization with external systems
