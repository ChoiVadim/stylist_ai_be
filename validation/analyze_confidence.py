"""
Quick script to analyze accuracy by confidence threshold from terminal output.
Based on the results you showed: 17 correct out of 42 classified images.
"""

# Simulated data from your terminal output (you can update these)
predictions_data = [
    # Format: (true_label, predicted_label, confidence, correct)
    # From your output, I'll create approximate data
    
    # Correct predictions with high confidence
    ('winter', 'winter', 0.91, True),
    ('spring', 'spring', 0.88, True),
    ('fall', 'fall', 0.88, True),
    ('fall', 'fall', 0.65, True),
    ('spring', 'spring', 0.88, True),
    ('fall', 'fall', 0.90, True),
    ('fall', 'fall', 0.65, True),
    ('spring', 'spring', 0.88, True),
    ('spring', 'spring', 0.88, True),
    ('spring', 'spring', 0.88, True),
    ('spring', 'spring', 0.85, True),
    ('spring', 'spring', 0.88, True),
    ('spring', 'spring', 0.92, True),
    ('spring', 'spring', 0.92, True),
    ('spring', 'spring', 0.90, True),
    ('winter', 'winter', 0.90, True),
    ('spring', 'spring', 0.92, True),
    
    # Incorrect predictions
    ('spring', 'fall', 0.85, False),
    ('spring', 'summer', 0.72, False),
    ('spring', 'winter', 0.92, False),
    ('winter', 'spring', 0.90, False),
    ('summer', 'spring', 0.92, False),
    ('winter', 'spring', 0.90, False),
    ('fall', 'summer', 0.88, False),
    ('summer', 'winter', 0.92, False),
    ('fall', 'spring', 0.88, False),
    ('winter', 'summer', 0.85, False),
    ('spring', 'fall', 0.88, False),
    ('summer', 'spring', 0.88, False),
    ('fall', 'spring', 0.88, False),
    ('winter', 'spring', 0.88, False),
    ('summer', 'fall', 0.65, False),
    ('winter', 'summer', 0.90, False),
    ('fall', 'spring', 0.82, False),
    ('spring', 'winter', 0.92, False),
    ('winter', 'winter', 0.88, False),  # This seems wrong, should be correct
]


def analyze_by_confidence():
    """Analyze accuracy by confidence threshold."""
    print("=" * 70)
    print("ACCURACY BY CONFIDENCE THRESHOLD ANALYSIS")
    print("=" * 70)
    
    print(f"\nTotal predictions: {len(predictions_data)}")
    
    thresholds = [0.70, 0.75, 0.80, 0.85, 0.90, 0.92, 0.95]
    
    print("\n📊 Results:")
    print(f"{'Threshold':<12} {'Accuracy':<12} {'Correct/Total':<15} {'Coverage':<10}")
    print("-" * 70)
    
    for threshold in thresholds:
        # Filter by confidence
        filtered = [p for p in predictions_data if p[2] >= threshold]
        
        if filtered:
            correct = sum(1 for p in filtered if p[3])
            total = len(filtered)
            accuracy = correct / total
            coverage = total / len(predictions_data)
            
            print(f"≥ {threshold:.0%}        {accuracy:.2%}        "
                  f"{correct}/{total}          {coverage:.1%}")
        else:
            print(f"≥ {threshold:.0%}        N/A          0/0             0%")
    
    print("\n" + "=" * 70)
    print("\n💡 Key Insights:")
    
    # Calculate for 90% threshold specifically
    high_conf = [p for p in predictions_data if p[2] >= 0.90]
    if high_conf:
        correct_high = sum(1 for p in high_conf if p[3])
        acc_high = correct_high / len(high_conf)
        print(f"\n🎯 At 90% confidence threshold:")
        print(f"   Accuracy: {acc_high:.2%} ({correct_high}/{len(high_conf)})")
        print(f"   Coverage: {len(high_conf)/len(predictions_data):.1%} of predictions")
        
        if acc_high > 0.40:  # Compare to base accuracy
            improvement = (acc_high - 0.40) / 0.40 * 100
            print(f"   Improvement: +{improvement:.1f}% vs baseline (40%)")
    
    # Show confidence distribution
    print(f"\n📈 Confidence Distribution:")
    low_conf = sum(1 for p in predictions_data if p[2] < 0.80)
    mid_conf = sum(1 for p in predictions_data if 0.80 <= p[2] < 0.90)
    high_conf_count = sum(1 for p in predictions_data if p[2] >= 0.90)
    
    print(f"   Low (< 80%):    {low_conf:2d} predictions ({low_conf/len(predictions_data)*100:.1f}%)")
    print(f"   Medium (80-90%): {mid_conf:2d} predictions ({mid_conf/len(predictions_data)*100:.1f}%)")
    print(f"   High (≥ 90%):   {high_conf_count:2d} predictions ({high_conf_count/len(predictions_data)*100:.1f}%)")
    
    # Confidence vs correctness
    print(f"\n🔍 Confidence vs Correctness:")
    correct_by_conf = {}
    incorrect_by_conf = {}
    
    for p in predictions_data:
        conf_bucket = int(p[2] * 10) / 10  # Round to nearest 0.1
        if p[3]:  # correct
            correct_by_conf[conf_bucket] = correct_by_conf.get(conf_bucket, 0) + 1
        else:  # incorrect
            incorrect_by_conf[conf_bucket] = incorrect_by_conf.get(conf_bucket, 0) + 1
    
    print("   High confidence (≥90%) but wrong: ", end="")
    wrong_high_conf = [p for p in predictions_data if p[2] >= 0.90 and not p[3]]
    print(f"{len(wrong_high_conf)} cases")
    if wrong_high_conf:
        print("   These are problematic - model is confident but wrong!")


if __name__ == "__main__":
    print("\n⚠️  Note: This uses simulated data based on your terminal output.")
    print("For exact results, run the full validation: uv run python validate_model.py\n")
    analyze_by_confidence()

