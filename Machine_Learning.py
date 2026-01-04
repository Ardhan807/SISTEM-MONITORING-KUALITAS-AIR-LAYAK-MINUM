"""
Water Quality Machine Learning Model
Random Forest Classifier for water potability prediction
"""

import joblib
import pandas as pd
import numpy as np


class WaterQualityModel:
    """
    Machine Learning model for water quality prediction using Random Forest
    
    This model predicts whether water is potable (drinkable) based on:
    - pH level
    - Total Dissolved Solids (TDS)
    - Turbidity (NTU)
    
    Output: "Layak Minum" or "Tidak Layak Minum"
    
    Note: Confidence level is calculated by the Expert System, not by this ML model.
    """
    
    def __init__(self, model_path="water_potability_model.pkl"):
        """
        Initialize the water quality prediction model
        
        Args:
            model_path (str): Path to the saved model file
            
        Raises:
            FileNotFoundError: If model file not found
            Exception: If model loading fails
        """
        self.model = None
        self.feature_names = None
        self._load_model(model_path)
    
    def _load_model(self, model_path):
        """
        Load the trained model from disk
        
        Args:
            model_path (str): Path to the model file
        """
        try:
            self.model = joblib.load(model_path)
            print(f"✅ Model loaded successfully from {model_path}")
            
            # Get feature names from the trained model
            if hasattr(self.model, 'feature_names_in_'):
                self.feature_names = list(self.model.feature_names_in_)
                print(f"📋 Model expects features: {self.feature_names}")
            else:
                # Fallback to default feature names
                self.feature_names = ['ph', 'Solids', 'Turbidity']
                print(f"⚠️ Model doesn't have feature_names_in_, using default: {self.feature_names}")
                
        except FileNotFoundError:
            print(f"❌ Error: Model file '{model_path}' not found!")
            raise
        except Exception as e:
            print(f"❌ Error loading model: {str(e)}")
            raise
    
    def _prepare_input(self, ph, tds, ntu):
        """
        Prepare input data for model prediction
        
        Args:
            ph (float): pH level
            tds (float): Total Dissolved Solids in mg/L
            ntu (float): Turbidity in NTU
            
        Returns:
            pd.DataFrame: Formatted input for model prediction
        """
        # Feature mapping: sensor values to model features
        feature_mapping = {
            'ph': ph,
            'Solids': tds,      # TDS = Total Dissolved Solids
            'Turbidity': ntu    # NTU = Turbidity
        }
        
        # Create data array in correct order
        data = []
        for feature_name in self.feature_names:
            if feature_name in feature_mapping:
                data.append(feature_mapping[feature_name])
            elif feature_name.lower() == 'ph':
                data.append(ph)
            elif feature_name.lower() in ['solids', 'tds']:
                data.append(tds)
            elif feature_name.lower() in ['turbidity', 'ntu']:
                data.append(ntu)
            else:
                # Unknown feature - use 0 as default
                print(f"⚠️ Unknown feature '{feature_name}', filling with 0")
                data.append(0)
        
        # Create DataFrame
        return pd.DataFrame([data], columns=self.feature_names)
    
    def _get_prediction_probability(self, X):
        """
        Get prediction probability if model supports it
        
        Args:
            X (pd.DataFrame): Input features
            
        Returns:
            np.array or None: Probability array or None if not supported
        """
        if hasattr(self.model, 'predict_proba'):
            return self.model.predict_proba(X)[0]
        return None
    
    def predict(self, ph, tds, ntu):
        """
        Predict water quality based on sensor readings
        
        This is the main prediction method that should be used.
        
        Args:
            ph (float): pH level (6.5-8.5 ideal)
            tds (float): Total Dissolved Solids in mg/L
            ntu (float): Turbidity in NTU
            
        Returns:
            str: "Layak Minum" or "Tidak Layak Minum"
            
        Note:
            - Model only predicts: "Layak Minum" or "Tidak Layak Minum"
            - Confidence is NOT calculated here
            - Confidence is calculated by Expert System based on:
              * ML agrees with ES = +25%
              * ML disagrees with ES = 0%
        """
        try:
            # Debug: Print input values
            print(f"\n🔍 ML Model Input:")
            print(f"   pH  : {ph}")
            print(f"   TDS : {tds}")
            print(f"   NTU : {ntu}")
            
            # Prepare input
            X = self._prepare_input(ph, tds, ntu)
            
            print(f"📊 DataFrame for prediction:")
            print(X)
            
            # Make prediction
            pred = self.model.predict(X)[0]
            
            # Get probability if available (for information only)
            proba = self._get_prediction_probability(X)
            if proba is not None:
                print(f"🎯 Prediction probabilities: {proba}")
            
            # Convert to readable format
            result = "Layak Minum" if pred == 1 else "Tidak Layak Minum"
            print(f"✅ ML Prediction: {result}")
            print(f"   (Confidence will be calculated by Expert System)")
            
            return result
            
        except Exception as e:
            print(f"❌ Error during prediction: {str(e)}")
            print(f"   Input values: ph={ph}, tds={tds}, ntu={ntu}")
            # Return safe default on error
            return "Tidak Layak Minum"
    
    def predict_with_confidence(self, ph, tds, ntu):
        """
        Predict with confidence score
        
        ⚠️ DEPRECATED: This method is kept for backward compatibility only.
        
        Confidence is now calculated by the Expert System, not by the ML model.
        Use predict() method instead and let the Expert System calculate confidence.
        
        Confidence Calculation (New System):
        - ML agrees with ES → +25%
        - ML disagrees with ES → 0%
        - ES "Layak Minum" → 0-75%
        - ES "Cukup Layak" → 0-50%
        - ES "Tidak Layak" → 0%
        
        Args:
            ph (float): pH level
            tds (float): Total Dissolved Solids in mg/L
            ntu (float): Turbidity in NTU
            
        Returns:
            tuple: (prediction, placeholder_confidence)
        """
        try:
            # Prepare input
            X = self._prepare_input(ph, tds, ntu)
            
            # Get prediction
            pred = self.model.predict(X)[0]
            result = "Layak Minum" if pred == 1 else "Tidak Layak Minum"
            
            # Get placeholder confidence (for backward compatibility only)
            proba = self._get_prediction_probability(X)
            if proba is not None:
                placeholder_confidence = int(max(proba) * 100)
            else:
                placeholder_confidence = 85
            
            print(f"⚠️ DEPRECATED: predict_with_confidence() is no longer used.")
            print(f"   Confidence is now calculated by Expert System.")
            print(f"   Use predict() instead and let ES calculate confidence.")
            
            return result, placeholder_confidence
            
        except Exception as e:
            print(f"❌ Error in predict_with_confidence: {str(e)}")
            return "Tidak Layak Minum", 50
    
    def get_model_info(self):
        """
        Get information about the loaded model
        
        Returns:
            dict: Model information including feature names and model type
        """
        info = {
            "model_type": type(self.model).__name__,
            "feature_names": self.feature_names,
            "has_probability": hasattr(self.model, 'predict_proba')
        }
        
        # Add additional info if available
        if hasattr(self.model, 'n_estimators'):
            info["n_estimators"] = self.model.n_estimators
        if hasattr(self.model, 'max_depth'):
            info["max_depth"] = self.model.max_depth
            
        return info


def test_model():
    """
    Test the water quality model with sample data
    """
    print("=" * 60)
    print("TESTING WATER QUALITY ML MODEL")
    print("=" * 60)
    
    try:
        model = WaterQualityModel("water_potability_model.pkl")
        
        # Display model information
        print("\n📋 Model Information:")
        info = model.get_model_info()
        for key, value in info.items():
            print(f"   {key}: {value}")
        
        # Test cases
        test_cases = [
            (7.2, 120, 0.8, "Sempurna - pH netral, TDS rendah, jernih"),
            (6.8, 350, 8, "Cukup - pH sedikit asam, TDS sedang, agak keruh"),
            (5.5, 600, 15, "Buruk - pH asam, TDS tinggi, keruh"),
            (7.0, 300, 3.5, "Baik - pH netral, TDS baik, jernih"),
        ]
        
        print("\n📝 NOTE: ML only predicts 'Layak' or 'Tidak Layak'")
        print("         Confidence is calculated by Expert System later.\n")
        
        for i, (ph, tds, ntu, desc) in enumerate(test_cases, 1):
            print(f"\n{'='*60}")
            print(f"Test Case {i}: {desc}")
            print(f"{'='*60}")
            result = model.predict(ph, tds, ntu)
            print(f"Final ML Result: {result}")
            print(f"(ES will validate and calculate confidence)")
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")


if __name__ == "__main__":
    test_model()
