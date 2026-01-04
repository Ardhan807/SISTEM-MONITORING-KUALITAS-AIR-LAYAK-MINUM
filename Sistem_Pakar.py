"""
Expert System for Water Quality Assessment
Fuzzy Logic-based system with 22 inference rules based on WHO standards
"""

import numpy as np


# =============================
# FUZZY MEMBERSHIP FUNCTIONS
# =============================

def trapmf(x, params):
    """
    Trapezoidal membership function
    
    Args:
        x (float): Input value
        params (list): [a, b, c, d] where a <= b <= c <= d
        
    Returns:
        float: Membership degree (0.0 to 1.0)
    """
    a, b, c, d = params
    
    if x < a or x > d:
        return 0.0
    elif a <= x <= b:
        return (x - a) / (b - a) if b != a else 1.0
    elif b < x < c:
        return 1.0
    elif c <= x <= d:
        return (d - x) / (d - c) if d != c else 1.0
    else:
        return 0.0


# =============================
# FUZZIFICATION FUNCTIONS
# =============================

def fuzzifikasi_ph(ph):
    """
    pH fuzzification using trapezoidal membership functions
    
    Classification based on WHO standards (Table 1):
    - Asam (Acidic): pH ≤ 6.5 (Not Potable)
    - Sedikit Asam (Slightly Acidic): 6.6-6.9 (Acceptable)
    - Netral (Neutral): pH = 7.0 (Optimal)
    - Sedikit Basa (Slightly Alkaline): 7.1-8.5 (Acceptable)
    - Basa (Alkaline): pH ≥ 8.6 (Not Potable)
    
    Args:
        ph (float): pH level value
        
    Returns:
        dict: Membership degrees for each fuzzy set
    """
    membership = {}
    
    membership['Asam'] = trapmf(ph, [0, 0, 6.5, 6.6])
    membership['Sedikit Asam'] = trapmf(ph, [6.5, 6.6, 6.9, 7.0])
    membership['Netral'] = trapmf(ph, [6.9, 7.0, 7.0, 7.1])
    membership['Sedikit Basa'] = trapmf(ph, [7.0, 7.1, 8.5, 8.6])
    membership['Basa'] = trapmf(ph, [8.5, 8.6, 14, 14])
    
    return membership


def fuzzifikasi_tds(tds):
    """
    TDS fuzzification using trapezoidal membership functions
    
    Classification (Table 2):
    - Sempurna (Excellent): 0-300 mg/L (Potable)
    - Baik (Good): 301-600 mg/L (Potable)
    - Cukup (Fair): 601-900 mg/L (Acceptable)
    - Buruk (Poor): 901-1199 mg/L (Not Potable)
    - Tidak Diterima (Unacceptable): ≥1200 mg/L (Not Potable)
    
    Args:
        tds (float): Total Dissolved Solids in mg/L
        
    Returns:
        dict: Membership degrees for each fuzzy set
    """
    membership = {}
    
    membership['Sempurna'] = trapmf(tds, [0, 0, 300, 301])
    membership['Baik'] = trapmf(tds, [300, 301, 600, 601])
    membership['Cukup'] = trapmf(tds, [600, 601, 900, 901])
    membership['Buruk'] = trapmf(tds, [900, 901, 1199, 1200])
    membership['Tidak Diterima'] = trapmf(tds, [1199, 1200, 2000, 2000])
    
    return membership


def fuzzifikasi_kekeruhan(ntu):
    """
    Turbidity fuzzification using trapezoidal membership functions
    
    Classification (Table 3):
    - Sempurna (Excellent): 0-1 NTU (Potable)
    - Baik (Good): 1.1-5 NTU (Potable)
    - Cukup (Fair): 5.1-25 NTU (Acceptable)
    - Buruk (Poor): 25.1-100 NTU (Not Potable)
    - Tidak Diterima (Unacceptable): ≥100 NTU (Not Potable)
    
    Args:
        ntu (float): Turbidity in NTU
        
    Returns:
        dict: Membership degrees for each fuzzy set
    """
    membership = {}
    
    membership['Sempurna'] = trapmf(ntu, [0, 0, 1.0, 1.1])
    membership['Baik'] = trapmf(ntu, [1.0, 1.1, 5.0, 5.1])
    membership['Cukup'] = trapmf(ntu, [5.0, 5.1, 25.0, 25.1])
    membership['Buruk'] = trapmf(ntu, [25.0, 25.1, 100.0, 100.1])
    membership['Tidak Diterima'] = trapmf(ntu, [100.0, 100.1, 300.0, 300.0])
    
    return membership


# =============================
# DEFUZZIFICATION
# =============================

def defuzzifikasi_output(firing_strength):
    """
    Defuzzification using Centroid method with trapezoidal output sets
    
    Output parameters:
    - Tidak Layak: [0, 0, 40, 50]
    - Cukup Layak: [40, 50, 70, 80]
    - Layak: [70, 80, 100, 100]
    
    Args:
        firing_strength (dict): Firing strength for each output class
        
    Returns:
        float: Crisp output value (0-100)
    """
    output_params = {
        'Tidak Layak': [0, 0, 40, 50],
        'Cukup Layak': [40, 50, 70, 80],
        'Layak': [70, 80, 100, 100]
    }
    
    numerator = 0
    denominator = 0
    
    x_range = np.linspace(0, 100, 1000)
    
    for x in x_range:
        membership_agregat = 0
        for status, strength in firing_strength.items():
            if strength > 0:
                membership_at_x = trapmf(x, output_params[status])
                membership_agregat = max(membership_agregat, min(strength, membership_at_x))
        
        numerator += x * membership_agregat
        denominator += membership_agregat
    
    if denominator == 0:
        return 50
    
    return numerator / denominator


# =============================
# FUZZY INFERENCE RULES
# =============================

def apply_danger_rules(ph_membership, tds_membership, ntu_membership, firing_strength, rules_fired):
    """
    Apply danger rules (R1-R6): Single-condition rules for unsafe water
    
    Args:
        ph_membership (dict): pH membership values
        tds_membership (dict): TDS membership values
        ntu_membership (dict): Turbidity membership values
        firing_strength (dict): Firing strength accumulator
        rules_fired (list): List of fired rules
    """
    # R1: IF pH Asam (≤ 6.5) → STATUS Tidak Layak Minum
    r1 = ph_membership['Asam']
    if r1 > 0:
        firing_strength['Tidak Layak'] = max(firing_strength['Tidak Layak'], r1)
        rules_fired.append(('R1', r1, 'pH Asam (≤ 6.5)'))
    
    # R2: IF pH Basa (≥ 8.6) → STATUS Tidak Layak Minum
    r2 = ph_membership['Basa']
    if r2 > 0:
        firing_strength['Tidak Layak'] = max(firing_strength['Tidak Layak'], r2)
        rules_fired.append(('R2', r2, 'pH Basa (≥ 8.6)'))
    
    # R3: IF TDS Buruk (901-1199 mg/L) → STATUS Tidak Layak Minum
    r3 = tds_membership['Buruk']
    if r3 > 0:
        firing_strength['Tidak Layak'] = max(firing_strength['Tidak Layak'], r3)
        rules_fired.append(('R3', r3, 'TDS Buruk (901-1199 mg/L)'))
    
    # R4: IF TDS Tidak Diterima (≥ 1200 mg/L) → STATUS Tidak Layak Minum
    r4 = tds_membership['Tidak Diterima']
    if r4 > 0:
        firing_strength['Tidak Layak'] = max(firing_strength['Tidak Layak'], r4)
        rules_fired.append(('R4', r4, 'TDS Tidak Diterima (≥ 1200 mg/L)'))
    
    # R5: IF Kekeruhan Buruk (25.1-100 NTU) → STATUS Tidak Layak Minum
    r5 = ntu_membership['Buruk']
    if r5 > 0:
        firing_strength['Tidak Layak'] = max(firing_strength['Tidak Layak'], r5)
        rules_fired.append(('R5', r5, 'Kekeruhan Buruk (25.1-100 NTU)'))
    
    # R6: IF Kekeruhan Tidak Diterima (≥ 100 NTU) → STATUS Tidak Layak Minum
    r6 = ntu_membership['Tidak Diterima']
    if r6 > 0:
        firing_strength['Tidak Layak'] = max(firing_strength['Tidak Layak'], r6)
        rules_fired.append(('R6', r6, 'Kekeruhan Tidak Diterima (≥ 100 NTU)'))


def apply_fair_rules(ph_membership, tds_membership, ntu_membership, firing_strength, rules_fired):
    """
    Apply fair quality rules (R7-R16): Multi-condition rules for acceptable water
    
    Args:
        ph_membership (dict): pH membership values
        tds_membership (dict): TDS membership values
        ntu_membership (dict): Turbidity membership values
        firing_strength (dict): Firing strength accumulator
        rules_fired (list): List of fired rules
    """
    # R7: pH Sedikit Asam AND TDS Cukup AND Kekeruhan Cukup
    r7 = min(ph_membership['Sedikit Asam'], tds_membership['Cukup'], ntu_membership['Cukup'])
    if r7 > 0:
        firing_strength['Cukup Layak'] = max(firing_strength['Cukup Layak'], r7)
        rules_fired.append(('R7', r7, 'pH Sedikit Asam AND TDS Cukup AND Kekeruhan Cukup'))
    
    # R8: pH Sedikit Basa AND TDS Cukup AND Kekeruhan Cukup
    r8 = min(ph_membership['Sedikit Basa'], tds_membership['Cukup'], ntu_membership['Cukup'])
    if r8 > 0:
        firing_strength['Cukup Layak'] = max(firing_strength['Cukup Layak'], r8)
        rules_fired.append(('R8', r8, 'pH Sedikit Basa AND TDS Cukup AND Kekeruhan Cukup'))
    
    # R9: pH Netral AND TDS Cukup AND Kekeruhan Baik
    r9 = min(ph_membership['Netral'], tds_membership['Cukup'], ntu_membership['Baik'])
    if r9 > 0:
        firing_strength['Cukup Layak'] = max(firing_strength['Cukup Layak'], r9)
        rules_fired.append(('R9', r9, 'pH Netral AND TDS Cukup AND Kekeruhan Baik'))
    
    # R10: pH Netral AND TDS Baik AND Kekeruhan Cukup
    r10 = min(ph_membership['Netral'], tds_membership['Baik'], ntu_membership['Cukup'])
    if r10 > 0:
        firing_strength['Cukup Layak'] = max(firing_strength['Cukup Layak'], r10)
        rules_fired.append(('R10', r10, 'pH Netral AND TDS Baik AND Kekeruhan Cukup'))
    
    # R11: pH Sedikit Asam AND TDS Baik AND Kekeruhan Baik
    r11 = min(ph_membership['Sedikit Asam'], tds_membership['Baik'], ntu_membership['Baik'])
    if r11 > 0:
        firing_strength['Cukup Layak'] = max(firing_strength['Cukup Layak'], r11)
        rules_fired.append(('R11', r11, 'pH Sedikit Asam AND TDS Baik AND Kekeruhan Baik'))
    
    # R12: pH Sedikit Basa AND TDS Baik AND Kekeruhan Baik
    r12 = min(ph_membership['Sedikit Basa'], tds_membership['Baik'], ntu_membership['Baik'])
    if r12 > 0:
        firing_strength['Cukup Layak'] = max(firing_strength['Cukup Layak'], r12)
        rules_fired.append(('R12', r12, 'pH Sedikit Basa AND TDS Baik AND Kekeruhan Baik'))
    
    # R13: pH Sedikit Asam AND TDS Baik AND Kekeruhan Sempurna
    r13 = min(ph_membership['Sedikit Asam'], tds_membership['Baik'], ntu_membership['Sempurna'])
    if r13 > 0:
        firing_strength['Cukup Layak'] = max(firing_strength['Cukup Layak'], r13)
        rules_fired.append(('R13', r13, 'pH Sedikit Asam AND TDS Baik AND Kekeruhan Sempurna'))
    
    # R14: pH Sedikit Basa AND TDS Baik AND Kekeruhan Sempurna
    r14 = min(ph_membership['Sedikit Basa'], tds_membership['Baik'], ntu_membership['Sempurna'])
    if r14 > 0:
        firing_strength['Cukup Layak'] = max(firing_strength['Cukup Layak'], r14)
        rules_fired.append(('R14', r14, 'pH Sedikit Basa AND TDS Baik AND Kekeruhan Sempurna'))
    
    # R15: pH Sedikit Asam AND TDS Sempurna AND Kekeruhan Baik
    r15 = min(ph_membership['Sedikit Asam'], tds_membership['Sempurna'], ntu_membership['Baik'])
    if r15 > 0:
        firing_strength['Cukup Layak'] = max(firing_strength['Cukup Layak'], r15)
        rules_fired.append(('R15', r15, 'pH Sedikit Asam AND TDS Sempurna AND Kekeruhan Baik'))
    
    # R16: pH Sedikit Basa AND TDS Sempurna AND Kekeruhan Baik
    r16 = min(ph_membership['Sedikit Basa'], tds_membership['Sempurna'], ntu_membership['Baik'])
    if r16 > 0:
        firing_strength['Cukup Layak'] = max(firing_strength['Cukup Layak'], r16)
        rules_fired.append(('R16', r16, 'pH Sedikit Basa AND TDS Sempurna AND Kekeruhan Baik'))


def apply_potable_rules(ph_membership, tds_membership, ntu_membership, firing_strength, rules_fired):
    """
    Apply potable water rules (R17-R22): Multi-condition rules for safe drinking water
    
    Args:
        ph_membership (dict): pH membership values
        tds_membership (dict): TDS membership values
        ntu_membership (dict): Turbidity membership values
        firing_strength (dict): Firing strength accumulator
        rules_fired (list): List of fired rules
    """
    # R17: pH Sedikit Asam AND TDS Sempurna AND Kekeruhan Sempurna
    r17 = min(ph_membership['Sedikit Asam'], tds_membership['Sempurna'], ntu_membership['Sempurna'])
    if r17 > 0:
        firing_strength['Layak'] = max(firing_strength['Layak'], r17)
        rules_fired.append(('R17', r17, 'pH Sedikit Asam AND TDS Sempurna AND Kekeruhan Sempurna'))
    
    # R18: pH Sedikit Basa AND TDS Sempurna AND Kekeruhan Sempurna
    r18 = min(ph_membership['Sedikit Basa'], tds_membership['Sempurna'], ntu_membership['Sempurna'])
    if r18 > 0:
        firing_strength['Layak'] = max(firing_strength['Layak'], r18)
        rules_fired.append(('R18', r18, 'pH Sedikit Basa AND TDS Sempurna AND Kekeruhan Sempurna'))
    
    # R19: pH Netral AND TDS Sempurna AND Kekeruhan Sempurna
    r19 = min(ph_membership['Netral'], tds_membership['Sempurna'], ntu_membership['Sempurna'])
    if r19 > 0:
        firing_strength['Layak'] = max(firing_strength['Layak'], r19)
        rules_fired.append(('R19', r19, 'pH Netral AND TDS Sempurna AND Kekeruhan Sempurna'))
    
    # R20: pH Netral AND TDS Baik AND Kekeruhan Baik
    r20 = min(ph_membership['Netral'], tds_membership['Baik'], ntu_membership['Baik'])
    if r20 > 0:
        firing_strength['Layak'] = max(firing_strength['Layak'], r20)
        rules_fired.append(('R20', r20, 'pH Netral AND TDS Baik AND Kekeruhan Baik'))
    
    # R21: pH Netral AND TDS Sempurna AND Kekeruhan Baik
    r21 = min(ph_membership['Netral'], tds_membership['Sempurna'], ntu_membership['Baik'])
    if r21 > 0:
        firing_strength['Layak'] = max(firing_strength['Layak'], r21)
        rules_fired.append(('R21', r21, 'pH Netral AND TDS Sempurna AND Kekeruhan Baik'))
    
    # R22: pH Netral AND TDS Baik AND Kekeruhan Sempurna
    r22 = min(ph_membership['Netral'], tds_membership['Baik'], ntu_membership['Sempurna'])
    if r22 > 0:
        firing_strength['Layak'] = max(firing_strength['Layak'], r22)
        rules_fired.append(('R22', r22, 'pH Netral AND TDS Baik AND Kekeruhan Sempurna'))


def fuzzy_inference(ph, tds, ntu):
    """
    Fuzzy inference system for water quality evaluation
    
    Applies 22 fuzzy rules:
    - R1-R6: Danger rules (single conditions)
    - R7-R16: Fair quality rules (multi-conditions)
    - R17-R22: Potable water rules (multi-conditions)
    
    Args:
        ph (float): pH level
        tds (float): Total Dissolved Solids in mg/L
        ntu (float): Turbidity in NTU
        
    Returns:
        tuple: (status, score, details, has_active_rules)
    """
    details = {}
    
    # 1. FUZZIFICATION
    ph_membership = fuzzifikasi_ph(ph)
    tds_membership = fuzzifikasi_tds(tds)
    ntu_membership = fuzzifikasi_kekeruhan(ntu)
    
    details['ph_membership'] = ph_membership
    details['tds_membership'] = tds_membership
    details['ntu_membership'] = ntu_membership
    
    # 2. FUZZY INFERENCE
    firing_strength = {
        'Tidak Layak': 0,
        'Cukup Layak': 0,
        'Layak': 0
    }
    
    rules_fired = []
    
    # Apply all fuzzy rules
    apply_danger_rules(ph_membership, tds_membership, ntu_membership, firing_strength, rules_fired)
    apply_fair_rules(ph_membership, tds_membership, ntu_membership, firing_strength, rules_fired)
    apply_potable_rules(ph_membership, tds_membership, ntu_membership, firing_strength, rules_fired)
    
    details['firing_strength'] = firing_strength
    details['rules_fired'] = rules_fired
    
    has_active_rules = len(rules_fired) > 0
    
    # 3. DEFUZZIFICATION
    if has_active_rules:
        score = defuzzifikasi_output(firing_strength)
        
        # Determine status based on maximum firing strength
        max_strength = max(firing_strength.values())
        if max_strength == 0:
            status = "Cukup Layak Minum"
        else:
            for s, strength in firing_strength.items():
                if strength == max_strength:
                    if s == 'Tidak Layak':
                        status = "Tidak Layak Minum"
                    elif s == 'Cukup Layak':
                        status = "Cukup Layak Minum"
                    else:
                        status = "Layak Minum"
                    break
    else:
        status = "Tidak Layak Minum"
        score = 0
    
    details['score'] = score
    details['status'] = status
    details['has_active_rules'] = has_active_rules
    
    return status, score, details, has_active_rules


# =============================
# CONFIDENCE CALCULATION
# =============================

def calculate_confidence(status, firing_strength, rules_fired, ph, tds, ntu, 
                        ph_membership, tds_membership, ntu_membership, 
                        ml_result=None, es_result=None):
    """
    Calculate confidence level based on ML and ES agreement
    
    Confidence System:
    
    DANGER RULES (R1-R6):
    - R1-R6 active AND ML = "Tidak Layak Minum" → 0% (both agree dangerous)
    - R1-R6 active AND ML = "Layak Minum" → 25% (only ML says safe)
    
    ML Contribution (0-25%):
    - ML agrees with ES → +25%
    - ML disagrees with ES → 0%
    
    ES Contribution (0-75%):
    - Status "Layak Minum" → 0-75% (base + bonuses)
    - Status "Cukup Layak Minum" → 0-50% (base + bonuses)
    - Status "Tidak Layak Minum" → 0%
    
    Total: ML + ES (max 100%)
    
    Args:
        status (str): Final water quality status
        firing_strength (dict): Firing strength for each class
        rules_fired (list): List of fired rules
        ph, tds, ntu (float): Sensor values
        ph_membership, tds_membership, ntu_membership (dict): Membership values
        ml_result (str): ML prediction result
        es_result (str): ES prediction result
        
    Returns:
        tuple: (confidence, explanation)
    """
    # Check for danger rules (R1-R6)
    danger_rules = ['R1', 'R2', 'R3', 'R4', 'R5', 'R6']
    active_danger_rules = [r[0] for r in rules_fired if r[0] in danger_rules]
    
    if active_danger_rules:
        rule_names = ', '.join(active_danger_rules)
        
        # Special case: ML says "Layak Minum" when danger rules active
        if ml_result is not None and ml_result.strip() == "Layak Minum":
            confidence = 25
            explanation = f"""
Perhitungan Confidence (Sistem Baru):
⚠️ ALARM BAHAYA AKTIF: {rule_names}
• Rule R1-R6 mendeteksi parameter berbahaya
• TETAPI ML memprediksi: "Layak Minum"
• ML berani berbeda pendapat dengan ES → +25%
• ES contribution: 0% (alarm bahaya)
• TOTAL: 25% (HANYA DARI ML - TETAP WASPADAI ALARM ES)

⚠️ CATATAN PENTING: 
Meskipun ML memprediksi "Layak Minum", sistem pakar mendeteksi 
parameter yang melewati batas aman. Disarankan untuk berhati-hati 
dan memverifikasi dengan pengukuran ulang atau sumber lain.
"""
            return confidence, explanation
        
        # Normal case: ML agrees with ES or more pessimistic
        else:
            confidence = 0
            explanation = f"""
Perhitungan Confidence (Sistem Baru):
⚠️ ALARM BAHAYA AKTIF: {rule_names}
• Rule R1-R6 adalah alarm keamanan
• ML prediction: {ml_result if ml_result else 'N/A'}
• Confidence MUTLAK: 0%
• ML contribution: 0% (setuju dengan alarm atau lebih pesimis)
• ES contribution: 0% (alarm bahaya)
• TOTAL: 0% (TIDAK ADA KEPERCAYAAN - AIR BERBAHAYA)
"""
            return confidence, explanation
    
    # Calculate ML contribution
    ml_confidence = 0
    if ml_result is not None and es_result is not None:
        ml_normalized = ml_result.strip()
        es_normalized = es_result.strip()
        
        if ml_normalized == es_normalized:
            ml_confidence = 25
            ml_note = f"ML SETUJU dengan ES ({ml_normalized}) → +25%"
        else:
            ml_confidence = 0
            ml_note = f"ML TIDAK SETUJU dengan ES (ML: {ml_normalized}, ES: {es_normalized}) → 0%"
    else:
        ml_note = "ML tidak tersedia"
    
    # Calculate ES contribution
    es_confidence = 0
    
    if status == "Layak Minum":
        base_es = 40
        max_es = 75
        
        max_firing_strength = max(firing_strength.values()) if firing_strength else 0
        strength_bonus = int(max_firing_strength * 10)
        
        # Parameter quality adjustment
        quality_adjustment = 0
        
        if 6.95 <= ph <= 7.05:
            quality_adjustment += 3
        elif 6.8 <= ph <= 7.2:
            quality_adjustment += 2
        elif 6.5 <= ph <= 8.5:
            quality_adjustment += 1
        
        if tds <= 300:
            quality_adjustment += 3
        elif tds <= 500:
            quality_adjustment += 2
        elif tds <= 600:
            quality_adjustment += 1
        
        if ntu <= 1:
            quality_adjustment += 4
        elif ntu <= 3:
            quality_adjustment += 3
        elif ntu <= 5:
            quality_adjustment += 2
        
        # Rule specificity bonus
        rule_specificity_bonus = 0
        priority_rules = ['R19', 'R20', 'R21', 'R22']
        high_priority_rules = ['R17', 'R18']
        
        for rule_name, strength, condition in rules_fired:
            if rule_name in priority_rules:
                rule_specificity_bonus = max(rule_specificity_bonus, 15)
            elif rule_name in high_priority_rules:
                rule_specificity_bonus = max(rule_specificity_bonus, 10)
        
        es_confidence = base_es + strength_bonus + quality_adjustment + rule_specificity_bonus
        es_confidence = max(0, min(max_es, es_confidence))
        
        explanation_detail = f"""
  - Base ES (Layak Minum): {base_es}%
  - Firing Strength: +{strength_bonus}% (μ={max_firing_strength:.3f})
  - Parameter Quality: +{quality_adjustment}%
    · pH {ph:.2f}: {'optimal' if 6.95 <= ph <= 7.05 else 'baik' if 6.5 <= ph <= 8.5 else 'buruk'}
    · TDS {tds:.1f}: {'optimal' if tds <= 300 else 'baik' if tds <= 600 else 'cukup'}
    · NTU {ntu:.2f}: {'optimal' if ntu <= 1 else 'baik' if ntu <= 5 else 'cukup'}
  - Rule Specificity: +{rule_specificity_bonus}%"""
    
    elif status == "Cukup Layak Minum":
        base_es = 25
        max_es = 50
        
        max_firing_strength = max(firing_strength.values()) if firing_strength else 0
        strength_bonus = int(max_firing_strength * 10)
        
        # Parameter quality adjustment
        quality_adjustment = 0
        
        if 6.95 <= ph <= 7.05:
            quality_adjustment += 2
        elif 6.8 <= ph <= 7.2:
            quality_adjustment += 1
        
        if tds <= 300:
            quality_adjustment += 2
        elif tds <= 500:
            quality_adjustment += 1
        
        if ntu <= 1:
            quality_adjustment += 1
        
        # Rule specificity bonus
        rule_specificity_bonus = 0
        medium_priority_rules = ['R11', 'R12', 'R13', 'R14', 'R15', 'R16']
        
        for rule_name, strength, condition in rules_fired:
            if rule_name in medium_priority_rules:
                rule_specificity_bonus = max(rule_specificity_bonus, 10)
            else:
                rule_specificity_bonus = max(rule_specificity_bonus, 5)
        
        es_confidence = base_es + strength_bonus + quality_adjustment + rule_specificity_bonus
        es_confidence = max(0, min(max_es, es_confidence))
        
        explanation_detail = f"""
  - Base ES (Cukup Layak): {base_es}%
  - Firing Strength: +{strength_bonus}% (μ={max_firing_strength:.3f})
  - Parameter Quality: +{quality_adjustment}%
  - Rule Specificity: +{rule_specificity_bonus}%"""
    
    else:  # "Tidak Layak Minum"
        es_confidence = 0
        explanation_detail = "  - Base ES (Tidak Layak): 0% (tidak ada kontribusi)"
    
    # Total confidence
    confidence = ml_confidence + es_confidence
    confidence = max(0, min(100, confidence))
    
    explanation = f"""
Perhitungan Confidence (Sistem Baru):
• Komponen ML (0% atau 25%): {ml_confidence}%
  {ml_note}
• Komponen ES (0-75%): {es_confidence}%
{explanation_detail}
• TOTAL: {confidence}% ({ml_confidence}% ML + {es_confidence}% ES)
"""
    
    return confidence, explanation


# =============================
# HYBRID DECISION SYSTEM
# =============================

def hybrid_decision(ph, tds, ntu, ml_result):
    """
    Hybrid decision system combining ML and ES with voting logic
    
    Decision Rules:
    - If ML = ES → Use agreed result
    - If ML = "Tidak Layak" and ES = "Layak" → Use ES (more specific)
    - If ML = "Tidak Layak" and ES = "Cukup Layak" → Use ES (more specific)
    - If ML = "Layak" and ES = "Cukup Layak" → Use ES (more specific)
    - If ML = "Layak" and ES = "Tidak Layak" → Use ES (safety priority)
    
    Args:
        ph (float): pH level
        tds (float): Total Dissolved Solids in mg/L
        ntu (float): Turbidity in NTU
        ml_result (str): ML prediction result
        
    Returns:
        tuple: (final_status, es_status, ml_status, decision_note, details, has_active_rules)
    """
    es_status, score, details, has_active_rules = fuzzy_inference(ph, tds, ntu)
    
    if ml_result == es_status:
        final_status = ml_result
        decision_note = "✅ ML dan ES setuju"
    
    elif ml_result == "Tidak Layak Minum" and es_status == "Layak Minum":
        final_status = "Layak Minum"
        decision_note = "⚖️ ES diprioritaskan (rule-based lebih spesifik untuk kondisi Layak)"
    
    elif ml_result == "Tidak Layak Minum" and es_status == "Cukup Layak Minum":
        final_status = "Cukup Layak Minum"
        decision_note = "⚖️ ES diprioritaskan (rule-based lebih spesifik untuk kondisi Cukup Layak)"
    
    elif ml_result == "Layak Minum" and es_status == "Cukup Layak Minum":
        final_status = "Cukup Layak Minum"
        decision_note = "⚖️ ES diprioritaskan (rule-based lebih spesifik untuk kondisi Cukup Layak)"
    
    elif ml_result == "Layak Minum" and es_status == "Tidak Layak Minum":
        final_status = "Tidak Layak Minum"
        decision_note = "⚠️ Prioritas keamanan (ES mendeteksi kondisi tidak aman)"
    
    else:
        final_status = es_status
        decision_note = "⚖️ Menggunakan hasil ES"
    
    return final_status, es_status, ml_result, decision_note, details, has_active_rules


# =============================
# MAIN EVALUATION FUNCTION
# =============================

def evaluate_water_quality(ph, tds, ntu, ml_result=None):
    """
    Evaluate water quality using Fuzzy Logic Expert System
    
    This is the main entry point for water quality evaluation.
    Combines ML prediction with ES fuzzy inference for final decision.
    
    Args:
        ph (float): pH level
        tds (float): Total Dissolved Solids in mg/L
        ntu (float): Turbidity in NTU
        ml_result (str, optional): ML prediction result
        
    Returns:
        tuple: (final_status, explanations, confidence, has_active_rules)
    """
    explanations = []
    
    # Run hybrid decision if ML result provided
    if ml_result is not None:
        final_status, es_status, ml_status, decision_note, details, has_active_rules = hybrid_decision(ph, tds, ntu, ml_result)
        score = details['score']
    else:
        es_status, score, details, has_active_rules = fuzzy_inference(ph, tds, ntu)
        final_status = es_status
        ml_status = None
        decision_note = None
    
    # Build explanations
    explanations.append(f"pH = {ph}")
    explanations.append(f"TDS = {tds} mg/L")
    explanations.append(f"Kekeruhan = {ntu} NTU")
    
    # Add fuzzy membership values
    ph_sig = [f"{k}: {v:.3f}" for k, v in details['ph_membership'].items() if v > 0]
    if ph_sig:
        explanations.append(f"\npH Fuzzy: {', '.join(ph_sig)}")
    
    tds_sig = [f"{k}: {v:.3f}" for k, v in details['tds_membership'].items() if v > 0]
    if tds_sig:
        explanations.append(f"TDS Fuzzy: {', '.join(tds_sig)}")
    
    ntu_sig = [f"{k}: {v:.3f}" for k, v in details['ntu_membership'].items() if v > 0]
    if ntu_sig:
        explanations.append(f"Kekeruhan Fuzzy: {', '.join(ntu_sig)}")
    
    # Handle case with no active rules
    if not has_active_rules:
        explanations.append("\n❌ Tidak ada aturan sistem pakar yang aktif")
        explanations.append("Kombinasi parameter tidak memenuhi kriteria keamanan apapun")
        
        if ml_result is not None:
            if ml_result == "Layak Minum":
                confidence = 25
                explanations.append(f"\n⚠️ Confidence: {confidence}% (hanya dari ML yang memprediksi Layak, ES tidak aktif)")
            else:
                confidence = 0
                explanations.append(f"\n⚠️ Confidence: {confidence}% (ML setuju dengan kondisi tidak pasti, tidak ada kontribusi)")
        else:
            confidence = 0
        
        return final_status, explanations, confidence, has_active_rules
    
    # Add fired rules
    if details['rules_fired']:
        explanations.append("\n✅ Aturan Aktif:")
        for rule_name, strength, condition in details['rules_fired']:
            explanations.append(f"  {rule_name} (μ={strength:.3f}): {condition}")
    
    # Add firing strengths
    explanations.append("\nFiring Strength:")
    for status_label, strength in details['firing_strength'].items():
        if strength > 0:
            explanations.append(f"  {status_label}: {strength:.3f}")
    
    # Calculate confidence
    confidence, confidence_explanation = calculate_confidence(
        final_status,
        details['firing_strength'],
        details['rules_fired'],
        ph, tds, ntu,
        details['ph_membership'],
        details['tds_membership'],
        details['ntu_membership'],
        ml_result,
        es_status
    )
    
    # Add final results
    explanations.append(f"\nDefuzzifikasi Score: {score:.2f}")
    
    if ml_result is not None:
        explanations.append(f"\n🤖 Prediksi ML: {ml_status}")
        explanations.append(f"🧠 Prediksi ES: {es_status}")
        explanations.append(f"⚖️ Keputusan: {decision_note}")
        explanations.append(f"🎯 Status Final: {final_status}")
    else:
        explanations.append(f"Status Akhir: {final_status}")
    
    explanations.append(confidence_explanation)
    
    return final_status, explanations, confidence, has_active_rules


# =============================
# RECOMMENDATIONS
# =============================

def get_recommendations(status, ph, tds, ntu):
    """
    Provide recommendations based on water quality status
    
    Args:
        status (str): Water quality status
        ph (float): pH level
        tds (float): Total Dissolved Solids in mg/L
        ntu (float): Turbidity in NTU
        
    Returns:
        list: List of recommendations
    """
    recommendations = []
    
    if status == "Tidak Layak Minum":
        recommendations.append("❌ AIR TIDAK AMAN UNTUK DIMINUM")
        recommendations.append("• JANGAN konsumsi air ini dalam kondisi apapun")
        recommendations.append("")
        
        problems = []
        
        # Check pH problems
        if ph <= 6.5:
            problems.append(f"pH terlalu asam ({ph:.2f}) - risiko iritasi lambung")
        elif ph >= 8.6:
            problems.append(f"pH terlalu basa ({ph:.2f}) - risiko gangguan pencernaan")
        
        # Check TDS problems
        if tds >= 1200:
            problems.append(f"TDS sangat tinggi ({tds:.1f} mg/L) - kandungan mineral berlebihan")
        elif tds >= 901:
            problems.append(f"TDS tinggi ({tds:.1f} mg/L) - melebihi batas standar")
        
        # Check turbidity problems
        if ntu > 100:
            problems.append(f"Kekeruhan sangat tinggi ({ntu:.2f} NTU) - risiko kontaminasi mikroba")
        elif ntu > 25:
            problems.append(f"Kekeruhan tinggi ({ntu:.2f} NTU) - tidak memenuhi standar")
        
        if problems:
            recommendations.append("**Masalah Terdeteksi:**")
            for problem in problems:
                recommendations.append(f"• {problem}")
            recommendations.append("")
        
        recommendations.append("**Tindakan:**")
        recommendations.append("• Hentikan konsumsi segera")
        recommendations.append("• Gunakan sumber air alternatif yang aman")
        recommendations.append("• Laporkan ke pihak terkait jika dari kemasan/distributor")
    
    elif status == "Cukup Layak Minum":
        recommendations.append("⚠️ AIR DAPAT DIMINUM DENGAN CATATAN")
        recommendations.append("• Kualitas memenuhi batas minimal namun belum optimal")
        recommendations.append("")
        
        notes = []
        
        # Check pH
        if 6.6 <= ph <= 6.9:
            notes.append(f"pH sedikit asam ({ph:.2f}) - masih aman")
        elif 7.1 <= ph <= 8.5:
            notes.append(f"pH sedikit basa ({ph:.2f}) - masih aman")
        
        # Check TDS
        if 601 <= tds <= 900:
            notes.append(f"TDS cukup tinggi ({tds:.1f} mg/L) - dapat diterima")
        elif 301 <= tds <= 600:
            notes.append(f"TDS baik ({tds:.1f} mg/L)")
        
        # Check turbidity
        if 5.1 <= ntu <= 25:
            notes.append(f"Kekeruhan cukup tinggi ({ntu:.2f} NTU)")
        elif 1.1 <= ntu <= 5:
            notes.append(f"Kekeruhan baik ({ntu:.2f} NTU)")
        
        if notes:
            recommendations.append("**Catatan:**")
            for note in notes:
                recommendations.append(f"• {note}")
            recommendations.append("")
        
        recommendations.append("**Saran:**")
        recommendations.append("• Aman untuk dikonsumsi sehari-hari")
        recommendations.append("• Pertimbangkan sumber dengan kualitas lebih baik")
        recommendations.append("• Monitor kualitas secara berkala")
    
    else:  # "Layak Minum"
        recommendations.append("✅ AIR AMAN DAN BERKUALITAS BAIK")
        recommendations.append("• Memenuhi standar WHO untuk air minum")
        recommendations.append("• Aman untuk konsumsi jangka panjang")
        recommendations.append("")
        
        recommendations.append("**Saran:**")
        recommendations.append("• Simpan di tempat sejuk dan bersih")
        recommendations.append("• Hindari paparan sinar matahari langsung")
        recommendations.append("• Lakukan pengecekan berkala untuk konsistensi")
    
    return recommendations
