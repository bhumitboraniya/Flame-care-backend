import os
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import cv2
from torchvision import transforms
# Set matplotlib backend to 'Agg' to avoid GUI issues with threading
import matplotlib
matplotlib.use('Agg')  # Must be before importing pyplot
import matplotlib.pyplot as plt
from PIL import Image
import io
import base64
from flask import Flask, request, jsonify
from flask_cors import CORS

# Import model classes
from models.unet import UNet
from models.calculators import BurnAreaCalculator, FluidCalculator

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Setup static folder for uploads if needed
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Image preprocessing function
def preprocess_image(image, target_size=(256, 256)):
    """Preprocess image for the model"""
    # Resize
    image = image.resize(target_size)

    # Convert to tensor and normalize
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    image_tensor = transform(image)
    return image_tensor.unsqueeze(0)  # Add batch dimension

def segment_burns(model, image_tensor):
    """Perform burn segmentation using the model"""
    model.eval()
    with torch.no_grad():
        outputs = model(image_tensor)
        # Threshold outputs to get binary mask
        predicted_mask = (outputs > 0.5).float()
        return predicted_mask.squeeze().numpy()

# Process burn image function
def process_burn_image(image, weight_kg, is_adult=True, model=None):
    """Process burn image end-to-end"""
    if model is None:
        # In a real application, you would load your trained model here
        model = UNet(n_channels=3, n_classes=1)
        # If you have a trained model:
        # model.load_state_dict(torch.load('models/burn_segmentation_model.pth'))

    # Preprocess the image (for a real model)
    image_tensor = preprocess_image(image)

    # For demonstration - using simple color thresholding
    np_image = np.array(image.resize((256, 256)))
    
    # Simple HSV-based segmentation for illustration
    hsv_image = cv2.cvtColor(np_image, cv2.COLOR_RGB2HSV)
    lower_bound = np.array([0, 50, 50])
    upper_bound = np.array([30, 255, 255])
    mock_mask = cv2.inRange(hsv_image, lower_bound, upper_bound) / 255

    # In actual implementation, use the model's prediction:
    # segmented_mask = segment_burns(model, image_tensor)
    segmented_mask = mock_mask

    # Create mock body part masks (simplified for demo)
    h, w = segmented_mask.shape
    body_part_mask = {
        'head': np.zeros((h, w)),
        'arm_right': np.zeros((h, w)),
        'arm_left': np.zeros((h, w)),
        'trunk_front': np.ones((h, w)),  # Assume the image shows front trunk
        'trunk_back': np.zeros((h, w)),
        'leg_right': np.zeros((h, w)),
        'leg_left': np.zeros((h, w)),
        'genitalia': np.zeros((h, w))
    }

    # Calculate burn percentage
    calculator = BurnAreaCalculator(is_adult=is_adult)
    burn_percentage, burn_by_part = calculator.calculate_burn_percentage(segmented_mask, body_part_mask)

    # Calculate fluid requirements
    fluid_calculator = FluidCalculator()
    fluid_requirements = fluid_calculator.calculate_parkland_formula(weight_kg, burn_percentage)

    # Prepare results
    results = {
        'burn_percentage': burn_percentage,
        'burn_by_part': burn_by_part,
        'fluid_requirements': fluid_requirements,
        'segmentation_mask': segmented_mask
    }

    return results

# Generate mask image as base64
def get_mask_base64(mask):
    """Convert a mask array to a base64-encoded PNG image without requiring GUI"""
    # Create a colormap-like conversion (similar to 'hot' colormap)
    # Normalize mask to 0-1 range if it's not already
    if mask.max() > 1.0:
        mask = mask / 255.0
        
    # Create an RGB representation of the mask
    h, w = mask.shape
    rgb_mask = np.zeros((h, w, 3), dtype=np.uint8)
    # Similar to 'hot' colormap: black -> red -> yellow -> white
    rgb_mask[..., 0] = np.clip(mask * 510, 0, 255).astype(np.uint8)  # Red channel
    rgb_mask[..., 1] = np.clip((mask - 0.5) * 510, 0, 255).astype(np.uint8)  # Green channel
    rgb_mask[..., 2] = np.clip((mask - 0.75) * 1020, 0, 255).astype(np.uint8)  # Blue channel
    
    # Convert to PIL Image
    img = Image.fromarray(rgb_mask)
    
    # Save to buffer
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    
    # Convert to base64
    mask_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return mask_base64

@app.route('/', methods=['GET'])
def index():
    return jsonify({
        'status': 'success',
        'message': 'FlameCare Burn Analysis API is running'
    })

@app.route('/api/analyze-burn', methods=['POST'])
def analyze_burn():
    """API endpoint to analyze burn images"""
    # Get JSON data from request
    data = request.json
    
    # Extract parameters from request body
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Check for required fields
    required_fields = ['image_data', 'weight_kg', 'is_adult']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Extract data
    image_data = data['image_data']  # Base64 encoded image
    weight_kg = float(data['weight_kg'])
    is_adult = bool(data['is_adult'])
    
    try:
        # Decode base64 image
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))
        
        # Process the image using our function
        results = process_burn_image(image, weight_kg, is_adult)
        
        # Convert numpy arrays to lists for JSON serialization
        serializable_results = {
            'burn_percentage': float(results['burn_percentage']),
            'burn_by_part': {k: float(v) for k, v in results['burn_by_part'].items() if float(v) > 0},
            'fluid_requirements': {
                'total_fluid_ml': float(results['fluid_requirements']['total_fluid_ml']),
                'first_8hr_fluid_ml': float(results['fluid_requirements']['first_8hr_fluid_ml']),
                'subsequent_16hr_fluid_ml': float(results['fluid_requirements']['subsequent_16hr_fluid_ml']),
                'hourly_rate_first_8hr': float(results['fluid_requirements']['hourly_rate_first_8hr']),
                'hourly_rate_subsequent_16hr': float(results['fluid_requirements']['hourly_rate_subsequent_16hr'])
            }
        }
        
        # Get the segmentation mask as base64
        mask_base64 = get_mask_base64(results['segmentation_mask'])
        serializable_results['segmentation_mask_base64'] = mask_base64
        
        return jsonify({
            'status': 'success',
            'results': serializable_results
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/upload-image', methods=['POST'])
def upload_image():
    """Endpoint for uploading images if needed"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file:
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filename)
        
        return jsonify({
            'status': 'success',
            'filename': file.filename,
            'file_path': filename
        })

if __name__ == '__main__':
    app.run()
