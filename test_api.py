import requests
import base64
import json
import os
import argparse

def test_api(image_path, weight_kg, is_adult, api_url='http://localhost:5000'):
    """
    Test the FlameCare API with a local image
    
    Args:
        image_path: Path to the image file
        weight_kg: Patient weight in kg
        is_adult: Boolean indicating if patient is adult
        api_url: Base URL of the API
    """
    # Check if image exists
    if not os.path.exists(image_path):
        print(f"Error: Image file {image_path} not found")
        return
    
    # Read and encode the image
    with open(image_path, "rb") as image_file:
        image_data = base64.b64encode(image_file.read()).decode('utf-8')
    
    # Create the request payload
    payload = {
        "image_data": image_data,
        "weight_kg": weight_kg,
        "is_adult": is_adult
    }
    
    # Make the API request
    try:
        response = requests.post(f"{api_url}/api/analyze-burn", json=payload)
        response.raise_for_status()  # Raise exception for 4XX/5XX responses
        
        # Process response
        result = response.json()
        
        # Print the results
        print("\n===== FLAMECARE BURN ANALYSIS =====")
        print(f"Status: {result['status']}")
        
        if result['status'] == 'success':
            burn_data = result['results']
            print(f"\nTotal Burn Percentage (TBSA): {burn_data['burn_percentage']:.2f}%")
            
            print("\nBurn Percentage by Body Part:")
            for part, percentage in burn_data['burn_by_part'].items():
                print(f"  {part}: {percentage:.2f}%")
            
            fluid = burn_data['fluid_requirements']
            print("\nFluid Requirements (Parkland Formula):")
            print(f"  Total fluid for 24 hours: {fluid['total_fluid_ml']:.0f} ml")
            print(f"  First 8 hours: {fluid['first_8hr_fluid_ml']:.0f} ml ({fluid['hourly_rate_first_8hr']:.0f} ml/hr)")
            print(f"  Next 16 hours: {fluid['subsequent_16hr_fluid_ml']:.0f} ml ({fluid['hourly_rate_subsequent_16hr']:.0f} ml/hr)")
            
            # If you want to save the segmentation mask
            if 'segmentation_mask_base64' in burn_data:
                mask_data = base64.b64decode(burn_data['segmentation_mask_base64'])
                output_path = "segmentation_mask.png"
                with open(output_path, "wb") as f:
                    f.write(mask_data)
                print(f"\nSegmentation mask saved to {output_path}")
        else:
            print(f"Error: {result.get('error', 'Unknown error')}")
            
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Test FlameCare Burn Analysis API')
    parser.add_argument('image_path', help='Path to the burn image')
    parser.add_argument('--weight', type=float, default=70.0, help='Patient weight in kg')
    parser.add_argument('--pediatric', action='store_false', dest='is_adult', help='Patient is a child (default: adult)')
    parser.add_argument('--api-url', default='http://localhost:5000', help='API URL')
    
    args = parser.parse_args()
    
    test_api(args.image_path, args.weight, args.is_adult, args.api_url)
