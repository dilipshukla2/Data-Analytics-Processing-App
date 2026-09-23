# processor/services.py
import math
import uuid
import time
from .models import FinalReport

# ==============================================================================
# ⚙️ CONFIGURATION: LOAD CONTROL VARIABLE
# Change this single value to increase or decrease the overall CPU load.
# 50,000,000 = ~1.5 to 2 minutes per step (Standard Mac/PC)
# 100,000,000 = ~3 to 4 minutes per step (Increase this if more load is needed)
# ==============================================================================
HEAVY_LOAD_ITERATIONS = 80000000


def simulate_heavy_cpu_load(iterations=HEAVY_LOAD_ITERATIONS):
    """
    Simulates heavy CPU load. 
    Prints progress every 10 million iterations to show active processing in the terminal.
    """
    print(f"🚀 Starting heavy computation: {iterations:,} iterations...")
    start_time = time.time()
    
    result = 0.0
    for i in range(1, iterations):
        # Complex mathematical operations to maximize CPU usage
        result += math.sqrt(i) * math.log(i + 1)
        result += math.sin(i) * math.cos(i)
        result += math.pow(i, 0.5) / (i + 1)
        
        # Print progress every 10 million iterations
        if i % 10000000 == 0:
            elapsed = time.time() - start_time
            print(f"   ⏳ Progress: {i:,}/{iterations:,} | Elapsed: {elapsed:.2f}s | Partial result: {result:.4f}")
    
    elapsed_time = time.time() - start_time
    print(f"✅ Computation completed in {elapsed_time:.2f} seconds\n")
    return result


def step1_ingest_and_clean(raw_data):
    print("\n" + "="*60)
    print("=== STEP 1: Data Ingestion & Cleaning ===")
    print("="*60)
    
    # HEAVY CPU LOAD (Uses the global configuration variable)
    simulate_heavy_cpu_load(HEAVY_LOAD_ITERATIONS)
    
    # Clean data: keep only valid records
    cleaned_data = [item for item in raw_data if item.get('is_valid', False)]
    
    print(f"📊 Step 1 Complete: {len(raw_data)} -> {len(cleaned_data)} records after cleaning")
    return cleaned_data


def step2_transform_and_aggregate(cleaned_data):
    print("\n" + "="*60)
    print("=== STEP 2: Data Transformation & Aggregation ===")
    print("="*60)
    
    # HEAVY CPU LOAD
    simulate_heavy_cpu_load(HEAVY_LOAD_ITERATIONS)
    
    # Aggregate calculations
    total_value = sum(item.get('value', 0) for item in cleaned_data)
    avg_value = total_value / len(cleaned_data) if cleaned_data else 0
    
    aggregated_result = {
        "total_records": len(cleaned_data),
        "aggregated_value": total_value,
        "average_value": avg_value,
        "original_data": cleaned_data
    }
    
    print(f"📊 Step 2 Complete: Aggregated value = {total_value:.2f}, Average = {avg_value:.2f}")
    return aggregated_result


def step3_calculate_score(aggregated_data):
    print("\n" + "="*60)
    print("=== STEP 3: Risk Scoring & Analysis ===")
    print("="*60)
    
    # HEAVY CPU LOAD
    simulate_heavy_cpu_load(HEAVY_LOAD_ITERATIONS)
    
    # Complex scoring calculation
    base_score = aggregated_data['aggregated_value'] * 1.5
    volatility_factor = len(aggregated_data['original_data']) * 0.01
    risk_score = base_score * (1 + volatility_factor)
    
    # Add scoring metrics to data
    aggregated_data['risk_score'] = risk_score
    aggregated_data['volatility_factor'] = volatility_factor
    aggregated_data['base_score'] = base_score
    
    print(f"📊 Step 3 Complete: Risk Score = {risk_score:.2f}")
    return aggregated_data


def step4_save_to_db(scored_data):
    print("\n" + "="*60)
    print("=== STEP 4: Final Storage & Report Generation ===")
    print("="*60)
    
    # HEAVY CPU LOAD
    simulate_heavy_cpu_load(HEAVY_LOAD_ITERATIONS)
    
    # Generate unique report ID
    report_id = str(uuid.uuid4())
    
    # Save final processed data to database
    report = FinalReport.objects.create(
        report_id=report_id,
        processed_data=scored_data
    )
    
    print(f"💾 Step 4 Complete: Report saved with ID = {report_id}")
    print("="*60 + "\n")
    return report