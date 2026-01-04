# Water Quality Model Training

This folder contains materials for training the Random Forest model used in the Water Quality Monitoring System.

## 📁 Files Included

1. **train_model.ipynb** - Jupyter Notebook for training the model
2. **water_potability.csv** - Sample dataset (3,276 samples)
3. **create_sample_dataset.py** - Script to generate sample dataset
4. **README_TRAINING.md** - This file

## 🎯 Quick Start

### Option 1: Using the Provided Dataset

```bash
# Install required packages
pip install pandas numpy matplotlib seaborn scikit-learn joblib jupyter

# Launch Jupyter Notebook
jupyter notebook train_model.ipynb

# Run all cells to train the model
```

### Option 2: Generate New Dataset

```bash
# Generate a new dataset
python create_sample_dataset.py

# This will create water_potability.csv with 3,276 samples
```

### Option 3: Use Real Kaggle Dataset

Download the real dataset from Kaggle:
- Dataset: [Water Potability](https://www.kaggle.com/datasets/adityakadiwal/water-potability)
- Replace `water_potability.csv` with the downloaded file
- Run the notebook

## 📊 Dataset Overview

### Features (Columns):
1. **ph** - pH level (0-14)
2. **Hardness** - Water hardness
3. **Solids** - Total Dissolved Solids (TDS)
4. **Chloramines** - Chloramine levels
5. **Sulfate** - Sulfate concentration
6. **Conductivity** - Electrical conductivity
7. **Organic_carbon** - Organic carbon levels
8. **Trihalomethanes** - THM levels
9. **Turbidity** - Turbidity (NTU)
10. **Potability** - Target (0 = Not Potable, 1 = Potable)

### Model Features Used:
We only use 3 features that match our IoT sensors:
- **ph** → pH sensor
- **Solids** → TDS sensor
- **Turbidity** → NTU sensor

## 🔬 Model Details

### Algorithm: Random Forest Classifier
- **Number of trees:** 100
- **Max depth:** 10
- **Min samples split:** 10
- **Min samples leaf:** 5

### Training Configuration:
- **Train/Test Split:** 80/20
- **Random State:** 42 (for reproducibility)
- **Stratified Split:** Yes (maintains class distribution)

### Expected Performance:
- **Accuracy:** ~65-70%
- **Precision:** ~0.65
- **Recall:** ~0.60
- **F1-Score:** ~0.62

Note: These metrics are typical for this dataset due to inherent complexity in water quality prediction.

## 📓 Notebook Contents

The notebook includes:

1. **Data Loading** - Load and explore the dataset
2. **Data Exploration** - Statistics and visualizations
3. **Feature Selection** - Select pH, Solids, Turbidity
4. **Preprocessing** - Handle missing values
5. **Data Split** - 80/20 train/test split
6. **Model Training** - Train Random Forest
7. **Evaluation** - Metrics and confusion matrix
8. **Feature Importance** - See which features matter most
9. **Testing** - Test with sample sensor data
10. **Model Saving** - Save as `water_potability_model.pkl`

## 🚀 Using the Trained Model

After training, you'll get `water_potability_model.pkl`:

```python
import joblib
import pandas as pd

# Load model
model = joblib.load('water_potability_model.pkl')

# Prepare input (from IoT sensors)
X = pd.DataFrame([{
    'ph': 7.2,
    'Solids': 120,
    'Turbidity': 0.85
}])

# Predict
prediction = model.predict(X)[0]
result = "Layak Minum" if prediction == 1 else "Tidak Layak Minum"

print(f"Prediction: {result}")
```

## 📦 Integration with IoT System

Copy the generated `water_potability_model.pkl` to your main project directory:

```
your_project/
├── app.py
├── Machine_Learning.py
├── water_potability_model.pkl  ← Place here
└── ...
```

The `Machine_Learning.py` module will automatically load and use this model.

## 🔄 Retraining the Model

To retrain with new data:

1. Update `water_potability.csv` with new data
2. Open `train_model.ipynb`
3. Run all cells
4. New `water_potability_model.pkl` will be generated
5. Replace the old model file in your project

## 📈 Improving Model Performance

### Tips for Better Accuracy:

1. **More Data**
   - Collect more training samples
   - Ensure balanced classes (50/50 potable/not potable)

2. **Feature Engineering**
   - Add interaction features (e.g., ph * turbidity)
   - Add polynomial features
   - Try feature scaling

3. **Hyperparameter Tuning**
   ```python
   from sklearn.model_selection import GridSearchCV
   
   param_grid = {
       'n_estimators': [100, 200, 300],
       'max_depth': [10, 20, 30],
       'min_samples_split': [5, 10, 20]
   }
   
   grid_search = GridSearchCV(model, param_grid, cv=5)
   grid_search.fit(X_train, y_train)
   ```

4. **Ensemble Methods**
   - Combine Random Forest with other models
   - Use voting or stacking

5. **Handle Imbalanced Data**
   ```python
   from imblearn.over_sampling import SMOTE
   
   smote = SMOTE(random_state=42)
   X_resampled, y_resampled = smote.fit_resample(X_train, y_train)
   ```

## 🧪 Testing the Model

Test cases included in notebook:

| Test Case | pH | TDS | NTU | Expected |
|-----------|-----|------|------|----------|
| Excellent | 7.2 | 120 | 0.8 | Potable |
| Fair | 6.8 | 350 | 8.0 | Potable |
| Poor | 5.5 | 600 | 15.0 | Not Potable |
| Good | 7.0 | 300 | 3.5 | Potable |

## 📊 Visualizations

The notebook generates:
- Feature distribution histograms
- Correlation matrix heatmap
- Confusion matrix
- Feature importance bar chart
- Target distribution chart

## 🛠️ Troubleshooting

### Issue: Low accuracy

**Solutions:**
- Collect more training data
- Check for data quality issues
- Try different algorithms (XGBoost, SVM)
- Tune hyperparameters

### Issue: Model won't load

**Solutions:**
- Check scikit-learn version compatibility
- Ensure model was saved correctly
- Verify file path

### Issue: Missing values

**Solutions:**
- Use median/mean imputation (already implemented)
- Try more advanced imputation (KNN, MICE)
- Collect better quality data

## 📚 Additional Resources

### Documentation:
- [Scikit-learn Random Forest](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [Matplotlib Gallery](https://matplotlib.org/stable/gallery/index.html)

### Datasets:
- [Kaggle Water Quality Dataset](https://www.kaggle.com/datasets/adityakadiwal/water-potability)
- [UCI Water Treatment Dataset](https://archive.ics.uci.edu/ml/datasets/water+treatment+plant)

### Tutorials:
- [Random Forest Tutorial](https://scikit-learn.org/stable/modules/ensemble.html#forest)
- [Feature Selection Guide](https://scikit-learn.org/stable/modules/feature_selection.html)

## 📝 Notes

- The model uses only 3 features (pH, TDS, Turbidity) to match IoT sensors
- Other features in the dataset are available but not used
- Model performance is reasonable for real-time IoT applications
- Combine with Expert System for best results

## ⚙️ Requirements

```
pandas>=2.0.0
numpy>=1.24.0
matplotlib>=3.7.0
seaborn>=0.12.0
scikit-learn>=1.3.0
joblib>=1.3.0
jupyter>=1.0.0
```

Install all requirements:
```bash
pip install -r requirements_training.txt
```

## 🎓 Learning Path

1. **Beginner:** Run the notebook as-is
2. **Intermediate:** Modify hyperparameters
3. **Advanced:** Try different algorithms and feature engineering
4. **Expert:** Implement ensemble methods and AutoML

## 🤝 Contributing

If you improve the model:
1. Document your changes
2. Update the notebook
3. Share your results
4. Consider contributing back

## 📞 Support

If you encounter issues:
1. Check this README
2. Review notebook comments
3. Verify data format
4. Check library versions

---

**Happy Training! 🎉**
