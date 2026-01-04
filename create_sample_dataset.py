"""
Create Sample Water Potability Dataset
This script generates a sample dataset for demonstration purposes
"""

import pandas as pd
import numpy as np

# Set random seed for reproducibility
np.random.seed(42)

# Number of samples
n_samples = 3276

print("Creating sample water potability dataset...")
print("=" * 60)

# Generate realistic water quality data
data = {
    'ph': np.random.normal(7.0, 1.5, n_samples).clip(0, 14),
    'Hardness': np.random.normal(200, 50, n_samples).clip(0, 500),
    'Solids': np.random.normal(20000, 10000, n_samples).clip(0, 60000),
    'Chloramines': np.random.normal(7.0, 2.0, n_samples).clip(0, 14),
    'Sulfate': np.random.normal(350, 100, n_samples).clip(0, 800),
    'Conductivity': np.random.normal(400, 100, n_samples).clip(0, 800),
    'Organic_carbon': np.random.normal(15, 5, n_samples).clip(0, 30),
    'Trihalomethanes': np.random.normal(70, 30, n_samples).clip(0, 150),
    'Turbidity': np.random.gamma(2, 2, n_samples).clip(0, 10)
}

# Create DataFrame
df = pd.DataFrame(data)

# Generate target based on simplified rules
def determine_potability(row):
    """Simple rule-based potability determination"""
    score = 0
    
    # pH: ideal range 6.5-8.5
    if 6.5 <= row['ph'] <= 8.5:
        score += 1
    
    # Solids (TDS): ideal < 500 ppm for our sensors (scaled from original)
    if row['Solids'] < 30000:
        score += 1
    
    # Turbidity: ideal < 5 NTU
    if row['Turbidity'] < 5:
        score += 1
    
    # Chloramines: ideal < 4
    if row['Chloramines'] < 8:
        score += 1
    
    # If most criteria are met, water is potable
    return 1 if score >= 3 else 0

df['Potability'] = df.apply(determine_potability, axis=1)

# Add some random noise (15% random flips)
flip_indices = np.random.choice(df.index, size=int(0.15 * len(df)), replace=False)
df.loc[flip_indices, 'Potability'] = 1 - df.loc[flip_indices, 'Potability']

# Add some missing values to make it realistic (~10%)
for col in df.columns[:-1]:  # Don't add missing to target
    missing_indices = np.random.choice(df.index, size=int(0.1 * len(df)), replace=False)
    df.loc[missing_indices, col] = np.nan

# Save to CSV
df.to_csv('water_potability.csv', index=False)

print(f"✅ Dataset created successfully!")
print(f"\nDataset Statistics:")
print(f"  - Total samples: {len(df)}")
print(f"  - Features: {len(df.columns) - 1}")
print(f"  - Target distribution:")
print(f"    Not Potable (0): {(df['Potability'] == 0).sum()} ({(df['Potability'] == 0).sum()/len(df)*100:.1f}%)")
print(f"    Potable (1): {(df['Potability'] == 1).sum()} ({(df['Potability'] == 1).sum()/len(df)*100:.1f}%)")
print(f"\n  - Missing values: {df.isnull().sum().sum()} ({df.isnull().sum().sum()/(len(df)*len(df.columns))*100:.1f}%)")
print(f"\nFile saved as: water_potability.csv")
print("\nYou can now use this dataset with train_model.ipynb")
