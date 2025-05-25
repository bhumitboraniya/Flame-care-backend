import numpy as np

class BurnAreaCalculator:
    def __init__(self, is_adult=True):
        self.is_adult = is_adult
        # Rule of Nines percentages
        if is_adult:
            self.body_parts = {
                'head': 9,
                'arm_right': 9,
                'arm_left': 9,
                'trunk_front': 18,
                'trunk_back': 18,
                'leg_right': 18,
                'leg_left': 18,
                'genitalia': 1
            }
        else:  # For children
            # Adjusted Rule of Nines for pediatric patients (simplified)
            self.body_parts = {
                'head': 18,
                'arm_right': 9,
                'arm_left': 9,
                'trunk_front': 18,
                'trunk_back': 18,
                'leg_right': 14,
                'leg_left': 14,
                'genitalia': 1
            }

    def calculate_burn_percentage(self, segmented_image, body_part_mask):
        """
        Calculate burn percentage based on segmented burn image and body part mask

        Parameters:
        segmented_image: Binary mask where 1 indicates burn
        body_part_mask: Dictionary of binary masks for each body part

        Returns:
        total_burn_percentage: Estimated TBSA percentage
        burn_area_by_part: Dictionary of burn percentage by body part
        """
        burn_area_by_part = {}
        total_burn_percentage = 0

        for part, mask in body_part_mask.items():
            # Calculate the intersection of burn with this body part
            intersection = np.logical_and(segmented_image, mask)
            # Calculate what percentage of this body part is burned
            if np.sum(mask) > 0:
                part_burn_percentage = np.sum(intersection) / np.sum(mask) * self.body_parts[part]
                burn_area_by_part[part] = part_burn_percentage
                total_burn_percentage += part_burn_percentage

        return total_burn_percentage, burn_area_by_part


class FluidCalculator:
    def __init__(self):
        pass

    def calculate_parkland_formula(self, weight_kg, burn_percentage):
        """
        Calculate fluid requirements using the Parkland formula

        Parameters:
        weight_kg: Patient's weight in kilograms
        burn_percentage: TBSA percentage of burn

        Returns:
        total_fluid_ml: Total fluid requirement for 24 hours
        first_8hr_fluid_ml: Fluid for first 8 hours
        subsequent_16hr_fluid_ml: Fluid for subsequent 16 hours
        hourly_rate_first_8hr: Hourly rate for first 8 hours (ml/hr)
        hourly_rate_subsequent_16hr: Hourly rate for subsequent 16 hours (ml/hr)
        """
        # Parkland formula: 4 ml × weight (kg) × %TBSA burn
        total_fluid_ml = 4 * weight_kg * burn_percentage

        # Half of the fluid is given in first 8 hours, remainder over next 16 hours
        first_8hr_fluid_ml = total_fluid_ml / 2
        subsequent_16hr_fluid_ml = total_fluid_ml / 2

        # Calculate hourly rates
        hourly_rate_first_8hr = first_8hr_fluid_ml / 8
        hourly_rate_subsequent_16hr = subsequent_16hr_fluid_ml / 16

        return {
            'total_fluid_ml': total_fluid_ml,
            'first_8hr_fluid_ml': first_8hr_fluid_ml,
            'subsequent_16hr_fluid_ml': subsequent_16hr_fluid_ml,
            'hourly_rate_first_8hr': hourly_rate_first_8hr,
            'hourly_rate_subsequent_16hr': hourly_rate_subsequent_16hr
        }


def get_fluid_requirements_simple(weight_kg, tbsa_percentage, delayed_hours=0, is_adult=True):
    """
    Calculate burn fluid requirements using Parkland formula
    
    Parameters:
    weight_kg (float): Patient weight in kg
    tbsa_percentage (float): Total burn surface area percentage (0-100)
    delayed_hours (float): Hours of delay before treatment starts
    is_adult (bool): True for adult, False for child
    
    Returns:
    dict: Essential fluid requirements
    {
        'total_ml': float,
        'first_8h_ml': float,
        'next_16h_ml': float,
        'first_8h_rate': float,
        'next_16h_rate': float
    }
    """
    
    try:
        # Convert and validate inputs
        weight = float(weight_kg)
        tbsa = float(tbsa_percentage)
        delay = float(delayed_hours)
        
        # Validation
        if weight <= 0 or tbsa < 0 or tbsa > 100 or delay < 0:
            return {
                'total_ml': 0,
                'first_8h_ml': 0,
                'next_16h_ml': 0,
                'first_8h_rate': 0,
                'next_16h_rate': 0,
                'error': 'Invalid input parameters'
            }
        
        # Parkland formula with pediatric adjustment
        # Standard: 4ml/kg/%TBSA, Pediatric: 4.4ml/kg/%TBSA (10% increase)
        multiplier = 4.4 if not is_adult else 4.0
        total_ml = multiplier * weight * tbsa
        
        # Standard distribution: 50% in first 8 hours, 50% in next 16 hours
        first_8h = total_ml / 2
        next_16h = total_ml / 2
        
        # Adjust for delayed resuscitation
        if delay > 0:
            if delay <= 8:
                # Compress first period
                remaining_hours = max(8 - delay, 0.1)
                first_8h_rate = first_8h / remaining_hours if remaining_hours > 0 else 0
            else:
                # Delay exceeds 8 hours - all fluid in remaining time
                first_8h = 0
                next_16h = total_ml
                first_8h_rate = 0
        else:
            first_8h_rate = first_8h / 8
        
        next_16h_rate = next_16h / 16
        
        return {
            'total_ml': round(total_ml, 1),
            'first_8h_ml': round(first_8h, 1),
            'next_16h_ml': round(next_16h, 1),
            'first_8h_rate': round(first_8h_rate, 1),
            'next_16h_rate': round(next_16h_rate, 1)
        }
        
    except (ValueError, TypeError):
        return {
            'total_ml': 0,
            'first_8h_ml': 0,
            'next_16h_ml': 0,
            'first_8h_rate': 0,
            'next_16h_rate': 0,
            'error': 'Invalid input format'
        }
