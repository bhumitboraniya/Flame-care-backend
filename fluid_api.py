"""
Simple Flask API for Burn Fluid Calculator
This version focuses only on fluid calculations without image processing
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os

# Add the models directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'models'))

from calculators import get_fluid_requirements_simple

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/', methods=['GET'])
def index():
    return jsonify({
        'status': 'success',
        'message': 'FlameCare Burn Fluid Calculator API is running',
        'endpoints': {
            '/api/calculate-fluid': 'POST - Calculate fluid requirements',
            '/api/test-fluid': 'GET - Test fluid calculator with sample data'
        }
    })

@app.route('/api/calculate-fluid', methods=['POST'])
def calculate_fluid():
    """API endpoint to calculate burn fluid requirements"""
    try:
        # Get JSON data from request
        data = request.json
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Check for required fields
        required_fields = ['weight_kg', 'tbsa_percentage']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Extract data with defaults
        weight_kg = float(data['weight_kg'])
        tbsa_percentage = float(data['tbsa_percentage'])
        delayed_hours = float(data.get('delayed_hours', 0))
        is_adult = bool(data.get('is_adult', True))
        
        # Calculate fluid requirements
        fluid_result = get_fluid_requirements_simple(weight_kg, tbsa_percentage, delayed_hours, is_adult)
        
        # Check for calculation errors
        if 'error' in fluid_result:
            return jsonify({
                'status': 'error',
                'error': fluid_result['error']
            }), 400
        
        # Add additional clinical information
        patient_type = 'Adult' if is_adult else 'Pediatric'
        severity_level = 'Minor'
        if tbsa_percentage >= 10 and tbsa_percentage < 20:
            severity_level = 'Moderate'
        elif tbsa_percentage >= 20 and tbsa_percentage < 40:
            severity_level = 'Major'
        elif tbsa_percentage >= 40:
            severity_level = 'Critical'
        

        print(fluid_result)
        # Return successful response
        return jsonify({
            'status': 'success',
            'fluid_requirements': fluid_result,
            'patient_info': {
                'weight_kg': weight_kg,
                'tbsa_percentage': tbsa_percentage,
                'delayed_hours': delayed_hours,
                'patient_type': patient_type,
                'burn_severity': severity_level
            },
            'clinical_notes': {
                'formula': 'Parkland Formula (4ml/kg/%TBSA for adults, 4.4ml/kg/%TBSA for children)',
                'monitoring': 'Monitor urine output (0.5-1 ml/kg/hr adults, 1-2 ml/kg/hr children)',
                'adjustment': 'Adjust rate based on urine output and clinical response',
                'fluid_type': 'Lactated Ringers or Normal Saline'
            },
            'message': f'Fluid requirements calculated for {weight_kg}kg {patient_type.lower()} patient with {tbsa_percentage}% TBSA burn'
        })
        
    except ValueError as ve:
        return jsonify({
            'status': 'error',
            'error': f'Invalid input data: {str(ve)}'
        }), 400
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': f'Internal server error: {str(e)}'
        }), 500

@app.route('/api/test-fluid', methods=['GET'])
def test_fluid_calculator():
    """Test endpoint for the fluid calculator"""
    try:
        # Test with sample data
        test_cases = [
            {'weight': 70, 'tbsa': 25, 'delay': 0, 'adult': True, 'description': 'Standard adult'},
            {'weight': 30, 'tbsa': 20, 'delay': 0, 'adult': False, 'description': 'Pediatric patient'},
            {'weight': 80, 'tbsa': 45, 'delay': 3, 'adult': True, 'description': 'Major burn with delay'}
        ]
        
        results = []
        for case in test_cases:
            fluid_result = get_fluid_requirements_simple(
                case['weight'], case['tbsa'], case['delay'], case['adult']
            )
            results.append({
                'description': case['description'],
                'input': {
                    'weight_kg': case['weight'],
                    'tbsa_percentage': case['tbsa'],
                    'delayed_hours': case['delay'],
                    'is_adult': case['adult']
                },
                'result': fluid_result
            })
        
        return jsonify({
            'status': 'success',
            'message': 'Fluid calculator test completed',
            'test_results': results
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("🔥 Starting FlameCare Burn Fluid Calculator API...")
    print("📍 Running on http://localhost:5001")
    print("📋 Available endpoints:")
    print("   GET  /                    - Health check")
    print("   POST /api/calculate-fluid - Calculate fluid requirements")
    print("   GET  /api/test-fluid     - Test with sample data")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=5001, debug=True)
