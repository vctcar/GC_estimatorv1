# GC Estimator API

FastAPI backend for the General Contractor Estimation Tool.

## Features

- RESTful API endpoints for estimate management
- Excel/CSV file import and parsing
- Cost rollup calculations
- CORS support for Next.js frontend
- Interactive API documentation

## API Endpoints

### Estimates Management
- `GET /api/estimates` - List all estimates
- `POST /api/estimates` - Create new estimate
- `GET /api/estimates/{id}` - Get estimate details
- `PUT /api/estimates/{id}` - Update estimate metadata
- `DELETE /api/estimates/{id}` - Delete estimate

### File Import
- `POST /api/estimates/import` - Import QTO from Excel/CSV file

### Items Management
- `POST /api/estimates/{id}/items` - Add new line item
- `PUT /api/estimates/{id}/items/{item_id}` - Update line item
- `DELETE /api/estimates/{id}/items/{item_id}` - Delete line item

### Calculations
- `GET /api/estimates/{id}/rollup` - Get cost rollup summary

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Start the server:
```bash
python start_api.py
```

## Development

The API server runs on `http://localhost:8000` with:
- Interactive docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/`

## Integration with Frontend

The API is configured with CORS to work with the Next.js frontend running on `http://localhost:3000`.

## Data Storage

Currently uses in-memory storage. For production, replace with a database solution.
