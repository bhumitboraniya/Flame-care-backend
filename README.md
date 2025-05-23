# FlameCare Backend API

This is a Flask-based API for the FlameCare application that handles burn image analysis, calculates burn percentage (TBSA), and determines fluid requirements using the Parkland formula.

## Features

- Burn image analysis and segmentation
- TBSA (Total Body Surface Area) calculation
- Fluid requirements calculation using the Parkland formula
- API endpoints for image upload and analysis

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Run the application:

```bash
python app.py
```

The API will be available at http://localhost:5000

## API Endpoints

### GET /

Check if the API is running.

**Response:**
```json
{
    "status": "success",
    "message": "FlameCare Burn Analysis API is running"
}
```

### POST /api/analyze-burn

Analyze a burn image.

**Request Body:**
```json
{
    "image_data": "base64_encoded_image_data",
    "weight_kg": 35,
    "is_adult": true
}
```

**Response:**
```json
{
    "status": "success",
    "results": {
        "burn_percentage": 12.5,
        "burn_by_part": {
            "trunk_front": 12.5
        },
        "fluid_requirements": {
            "total_fluid_ml": 1750.0,
            "first_8hr_fluid_ml": 875.0,
            "subsequent_16hr_fluid_ml": 875.0,
            "hourly_rate_first_8hr": 109.375,
            "hourly_rate_subsequent_16hr": 54.6875
        },
        "segmentation_mask_base64": "base64_encoded_mask_image"
    }
}
```

### POST /api/upload-image

Upload an image file (alternative to sending base64 data).

**Request:**
Form data with a file field named 'file'.

**Response:**
```json
{
    "status": "success",
    "filename": "burn_image.jpg",
    "file_path": "static/uploads/burn_image.jpg"
}
```

## Model Information

The backend uses a simplified version of a UNet architecture for image segmentation. For demonstration purposes, the current implementation uses a HSV color-based segmentation as a placeholder for the actual deep learning model.

In a production environment, you would replace this with a properly trained burn segmentation model.
