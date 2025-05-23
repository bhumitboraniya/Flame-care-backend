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
