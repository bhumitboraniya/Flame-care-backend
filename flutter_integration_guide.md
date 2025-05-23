# API Integration Guide - Flutter Client

This document provides guidance on integrating the FlameCare Backend API with your Flutter application.

## API Endpoints

Base URL: `http://[server_ip]:5000`

### 1. Analyze Burn Image

**Endpoint**: `POST /api/analyze-burn`

**Request Format**:
```json
{
  "image_data": "base64_encoded_image_data",
  "weight_kg": 35.5,
  "is_adult": true
}
```

**Response Format**:
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

## Flutter Implementation Example

Here's an example of how to implement the API call in your Flutter application:

```dart
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:image_picker/image_picker.dart';
import 'dart:io';

class BurnAnalysisService {
  final String baseUrl = 'http://your-server-ip:5000';
  
  Future<Map<String, dynamic>> analyzeBurnImage(File imageFile, double weightKg, bool isAdult) async {
    try {
      // Convert image to base64
      final bytes = await imageFile.readAsBytes();
      final base64Image = base64Encode(bytes);
      
      // Prepare request data
      final requestData = {
        'image_data': base64Image,
        'weight_kg': weightKg,
        'is_adult': isAdult
      };
      
      // Make API call
      final response = await http.post(
        Uri.parse('$baseUrl/api/analyze-burn'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(requestData),
      );
      
      // Check response status
      if (response.statusCode == 200) {
        final responseData = jsonDecode(response.body);
        
        if (responseData['status'] == 'success') {
          return responseData['results'];
        } else {
          throw Exception('API Error: ${responseData['error']}');
        }
      } else {
        throw Exception('HTTP Error: ${response.statusCode}');
      }
    } catch (e) {
      // Handle errors
      throw Exception('Failed to analyze burn image: $e');
    }
  }
  
  // Method to pick image from gallery or camera
  Future<File?> pickImage(ImageSource source) async {
    final picker = ImagePicker();
    final pickedFile = await picker.pickImage(source: source);
    
    if (pickedFile != null) {
      return File(pickedFile.path);
    }
    return null;
  }
}
```

## Example Usage in Flutter UI

```dart
// Inside a Flutter widget
void _analyzeButtonPressed() async {
  try {
    // Show loading indicator
    setState(() { isLoading = true; });
    
    // Pick image from camera or gallery
    final imageFile = await burnAnalysisService.pickImage(ImageSource.gallery);
    
    if (imageFile != null) {
      // Get user input
      final weight = double.parse(weightController.text);
      final isAdult = adultToggle.value;
      
      // Call API
      final results = await burnAnalysisService.analyzeBurnImage(
        imageFile, 
        weight, 
        isAdult
      );
      
      // Process results
      setState(() {
        burnPercentage = results['burn_percentage'];
        burnByPart = Map<String, double>.from(results['burn_by_part']);
        fluidRequirements = Map<String, double>.from(results['fluid_requirements']);
        
        // Convert base64 mask to image if needed
        if (results['segmentation_mask_base64'] != null) {
          final maskBytes = base64Decode(results['segmentation_mask_base64']);
          segmentationImage = Image.memory(maskBytes);
        }
        
        isLoading = false;
      });
    }
  } catch (e) {
    // Show error
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('Error: $e'))
    );
    setState(() { isLoading = false; });
  }
}
```

## Required Flutter Dependencies

Add these to your `pubspec.yaml`:

```yaml
dependencies:
  http: ^1.0.0
  image_picker: ^0.8.6
  path_provider: ^2.0.11
```
