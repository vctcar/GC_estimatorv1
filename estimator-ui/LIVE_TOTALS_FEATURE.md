# Live Totals & Charts Feature

## Overview
The Live Totals & Charts feature ensures that all cost calculations and visualizations are synchronized with the backend rollup API. Instead of computing totals locally, the UI fetches real-time calculations from the backend whenever items are added, edited, or deleted.

## Features

### Real-Time Calculations
- **Backend Rollup API**: Uses `GET /api/estimates/{id}/rollup` for all calculations
- **Automatic Refresh**: Totals update whenever items change
- **Consistent Logic**: UI always matches backend calculation logic
- **Fallback Support**: Local calculations as backup when API unavailable

### Live Summary Cards
- **Direct Costs**: Material + Labor + Equipment costs
- **Overhead**: Dynamic percentage from estimate settings
- **Profit**: Dynamic percentage from estimate settings
- **Total Estimate**: Complete project cost
- **Loading States**: Visual feedback during API calls
- **Additional Metrics**: Cost per square foot, material/labor percentages

### Dynamic Charts
- **Phase Distribution**: Pie chart showing cost breakdown by construction phase
- **Trade Summary**: Bar chart with direct, indirect, and overhead costs by trade
- **Cost Breakdown**: Detailed cost analysis with rollup data
- **Real-Time Updates**: Charts refresh when data changes

## Technical Implementation

### React Query Integration
```typescript
// Custom hook for rollup data
const {
  rollupData,
  isLoading: rollupLoading,
  error: rollupError,
  refreshRollupData,
  getPhaseChartData,
  getTradeChartData,
  getCostBreakdownData
} = useRollupData(estimateId);
```

### API Integration
- **Rollup Endpoint**: `/api/estimates/{id}/rollup`
- **Automatic Invalidation**: Query cache invalidated on item changes
- **Error Handling**: Graceful fallback to local calculations
- **Loading States**: Visual feedback during API calls

### Data Flow
1. **Item Changes**: Add/edit/delete items triggers rollup refresh
2. **API Call**: Backend calculates totals using CostRollup
3. **UI Update**: Summary cards and charts update with new data
4. **Cache Management**: React Query manages data freshness

## Backend Rollup API

### Endpoint
```
GET /api/estimates/{estimate_id}/rollup
```

### Response Structure
```json
{
  "estimate_id": "uuid",
  "rollup": {
    "project_info": {
      "name": "Project Name",
      "client": "Client Name",
      "overhead_percent": 15.0,
      "profit_percent": 10.0,
      "aace_class": "Class 3"
    },
    "cost_summary": {
      "total_cost": 1000000.00,
      "total_material": 600000.00,
      "total_labor": 300000.00,
      "total_equipment": 100000.00,
      "total_overhead": 150000.00,
      "total_profit": 100000.00,
      "cost_per_sf": 150.00
    },
    "cost_percentages": {
      "material_pct": 60.0,
      "labor_pct": 30.0,
      "equipment_pct": 10.0,
      "overhead_pct": 15.0,
      "profit_pct": 10.0
    },
    "rollups": {
      "by_phase": {
        "Site Work": {
          "material": 50000.00,
          "labor": 25000.00,
          "equipment": 10000.00,
          "overhead": 12750.00,
          "profit": 8500.00,
          "subtotal": 85000.00,
          "total": 106250.00
        }
      },
      "by_trade": {
        "Concrete": {
          "material": 200000.00,
          "labor": 100000.00,
          "equipment": 50000.00,
          "overhead": 52500.00,
          "profit": 35000.00,
          "subtotal": 350000.00,
          "total": 437500.00
        }
      }
    }
  }
}
```

## User Experience

### Loading States
- **Summary Cards**: Show loading spinners during API calls
- **Charts**: Display loading placeholders while data loads
- **Tables**: Show loading indicators for data tables
- **Smooth Transitions**: Graceful loading and error states

### Error Handling
- **API Failures**: Fallback to local calculations
- **Network Issues**: Retry logic with React Query
- **Data Validation**: Ensure data integrity
- **User Feedback**: Clear error messages

### Performance
- **Caching**: React Query caches rollup data
- **Optimistic Updates**: Immediate UI feedback
- **Background Refresh**: Non-blocking data updates
- **Efficient Re-renders**: Only update changed components

## Integration Points

### Item Management
- **Add Item**: Triggers rollup refresh after successful addition
- **Edit Item**: Updates totals when item is modified
- **Delete Item**: Recalculates totals after removal
- **Import Items**: Bulk import triggers comprehensive refresh

### Settings Changes
- **Overhead Percentage**: Updates when estimate settings change
- **Profit Percentage**: Reflects new profit margins
- **AACE Class**: May affect calculation methodology

### Chart Updates
- **Phase Distribution**: Updates when phase costs change
- **Trade Summary**: Reflects new trade breakdowns
- **Cost Breakdown**: Shows updated cost analysis

## Benefits

### Accuracy
- **Single Source of Truth**: Backend calculations are authoritative
- **Consistent Logic**: Same calculation engine for all operations
- **Data Integrity**: Prevents calculation drift between UI and backend

### Real-Time Updates
- **Immediate Feedback**: Users see changes instantly
- **Live Collaboration**: Multiple users see synchronized data
- **Audit Trail**: All calculations are traceable

### Scalability
- **Backend Processing**: Heavy calculations handled server-side
- **Caching Strategy**: Efficient data management
- **Performance**: Optimized for large datasets

## Future Enhancements

### Advanced Features
- **Real-Time Collaboration**: WebSocket updates for live collaboration
- **Calculation History**: Track changes over time
- **Custom Rollups**: User-defined calculation methods
- **Export Capabilities**: Export rollup data to various formats

### Performance Improvements
- **Incremental Updates**: Only recalculate changed portions
- **Background Processing**: Non-blocking calculations
- **Smart Caching**: Intelligent cache invalidation
- **Optimization**: Performance tuning for large estimates
