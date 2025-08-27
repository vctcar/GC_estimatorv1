# Create Estimate Feature

## Overview
The Create Estimate feature allows users to create new construction estimates through a user-friendly dialog form. The feature includes form validation, tooltips for field explanations, and automatic redirection to the estimate detail page upon successful creation.

## Features

### Form Fields
- **Estimate Name** (required): The name of the estimate project
- **Client**: Client name or organization
- **Description**: Brief description of the project
- **AACE Class**: Estimate accuracy classification with tooltip explanation
- **Overhead %**: Percentage for indirect costs (default: 15%)
- **Profit %**: Percentage for contractor profit margin (default: 10%)

### User Experience
- **Tooltips**: Help icons with explanations for technical fields (AACE Class, Overhead %, Profit %)
- **Form Validation**: Required field validation and proper input types
- **Loading States**: Visual feedback during API calls
- **Error Handling**: User-friendly error messages
- **Auto-redirect**: Automatic navigation to the new estimate page after creation
- **Form Reset**: Form clears when dialog is closed

## Technical Implementation

### Components
- `CreateEstimateDialog.tsx`: Main dialog component with form
- API Routes: Next.js API routes that proxy to FastAPI backend
  - `/api/estimates` (POST): Creates new estimate
  - `/api/estimates/[id]` (GET/PUT/DELETE): Individual estimate operations

### API Integration
- **Backend Endpoint**: `POST /api/estimates`
- **Default Values**: 
  - Name: "New Estimate"
  - AACE Class: "Class 3"
  - Overhead: 15%
  - Profit: 10%
- **Response**: Returns estimate object with generated UUID

### Environment Configuration
The API base URL is configured via environment variable:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Usage

1. Click the "+ New Estimate" button on the dashboard
2. Fill in the required fields (Estimate Name is required)
3. Optionally adjust AACE Class, Overhead %, and Profit %
4. Click "Create Estimate" to submit
5. Upon success, you'll be redirected to the new estimate detail page

## AACE Class Reference

- **Class 1**: Order of Magnitude Estimate
- **Class 2**: Study Estimate  
- **Class 3**: Preliminary Estimate (default)
- **Class 4**: Definitive Estimate
- **Class 5**: Detailed Estimate

## Error Handling

The feature includes comprehensive error handling:
- Network errors
- API validation errors
- User-friendly error messages
- Form state preservation on error

## Future Enhancements

Potential improvements for future iterations:
- Toast notifications for success/error states
- Form field validation with real-time feedback
- Integration with settings/assumptions page for default values
- Template-based estimate creation
- Bulk estimate creation
