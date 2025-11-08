"""
Validation script for personal color analysis model.
Tests the model against the valid dataset and generates visualizations.

The model returns 12 detailed color types (3 subtypes per season):
- Spring: Warm Spring, Bright Spring, Light Spring
- Summer: Light Summer, True Summer, Soft Summer
- Autumn: Warm Autumn, Deep Autumn, Soft Autumn
- Winter: Cool Winter, Bright Winter, Deep Winter

The validation dataset has 4 main seasons (Fall, Spring, Summer, Winter).
This script automatically maps the 12 detailed types to the 4 main seasons.
"""
import base64
import csv
import requests
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from collections import defaultdict
from datetime import datetime
import json


# Configuration
API_BASE = "http://localhost:8000"
VALID_DIR = Path("data/valid")
CLASSES_FILE = VALID_DIR / "_classes.csv"
OUTPUT_DIR = Path("validation_results")

# Create output directory
OUTPUT_DIR.mkdir(exist_ok=True)

# Color mapping for seasons
SEASON_COLORS = {
    'spring': '#90EE90',  # Light green
    'summer': '#FFB6C1',  # Light pink
    'fall': '#FFA500',    # Orange
    'winter': '#ADD8E6'   # Light blue
}

# Season name mapping - 12 detailed types to 4 main seasons
# API uses 12-season model, ground truth has 4 seasons
SEASON_MAPPING = {
    # Spring variations -> spring (3 types)
    'warm spring': 'spring',
    'bright spring': 'spring',
    'light spring': 'spring',
    'clear spring': 'spring',
    'true spring': 'spring',
    'spring': 'spring',
    
    # Summer variations -> summer (3 types)
    'light summer': 'summer',
    'true summer': 'summer',
    'soft summer': 'summer',
    'cool summer': 'summer',
    'muted summer': 'summer',
    'summer': 'summer',
    
    # Autumn variations -> fall (3 types)
    'warm autumn': 'fall',
    'deep autumn': 'fall',
    'soft autumn': 'fall',
    'true autumn': 'fall',
    'muted autumn': 'fall',
    'warm fall': 'fall',
    'deep fall': 'fall',
    'soft fall': 'fall',
    'autumn': 'fall',
    'fall': 'fall',
    
    # Winter variations -> winter (3 types)
    'cool winter': 'winter',
    'bright winter': 'winter',
    'deep winter': 'winter',
    'clear winter': 'winter',
    'true winter': 'winter',
    'winter': 'winter'
}


def load_ground_truth():
    """Load ground truth labels from CSV file."""
    ground_truth = {}
    
    with open(CLASSES_FILE, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            filename = row['filename'].strip()
            # Find which class has value 1
            for season in ['fall', 'spring', 'summer', 'winter']:
                if row[f' {season}'].strip() == '1':
                    ground_truth[filename] = season
                    break
    
    return ground_truth


def image_to_base64(image_path):
    """Convert image file to base64 string."""
    with open(image_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode()
    return f"data:image/jpeg;base64,{image_data}"


def predict_image(image_base64):
    """Send image to API and get prediction."""
    try:
        response = requests.post(
            f"{API_BASE}/api/analyze/color",
            json={"image": image_base64},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Exception during prediction: {str(e)}")
        return None


def normalize_season(season_str):
    """
    Normalize season name to match ground truth format.
    Maps 12 detailed color types (e.g., 'Warm Spring', 'Cool Winter') to 4 main seasons.
    """
    season_lower = season_str.lower().strip()
    
    # Try exact match first
    if season_lower in SEASON_MAPPING:
        return SEASON_MAPPING[season_lower]
    
    # Try to extract season from compound names
    # e.g., "Warm Spring" -> "spring", "Deep Winter" -> "winter"
    for key in SEASON_MAPPING.keys():
        if key in season_lower:
            return SEASON_MAPPING[key]
    
    # If no match, try to extract the base season
    if 'spring' in season_lower:
        return 'spring'
    elif 'summer' in season_lower:
        return 'summer'
    elif 'autumn' in season_lower or 'fall' in season_lower:
        return 'fall'
    elif 'winter' in season_lower:
        return 'winter'
    
    # If still no match, return as-is (will be marked as error)
    print(f"⚠️  Warning: Unknown season format '{season_str}', returning as-is")
    return season_lower


def run_validation():
    """Run validation on the entire dataset."""
    print("=" * 70)
    print("PERSONAL COLOR ANALYSIS MODEL VALIDATION")
    print("=" * 70)
    
    # Load ground truth
    print("\n📋 Loading ground truth labels...")
    ground_truth = load_ground_truth()
    print(f"✓ Loaded {len(ground_truth)} images with labels")
    
    # Count samples per class
    class_counts = defaultdict(int)
    for label in ground_truth.values():
        class_counts[label] += 1
    
    print("\n📊 Dataset distribution:")
    for season, count in sorted(class_counts.items()):
        print(f"  {season.capitalize()}: {count} images")
    
    # Run predictions
    print("\n🔮 Running predictions...")
    predictions = {}
    confidences = {}
    failed_images = []
    undetermined_images = []  # Track images where model couldn't determine
    
    for idx, (filename, true_label) in enumerate(ground_truth.items(), 1):
        image_path = VALID_DIR / filename
        
        if not image_path.exists():
            print(f"⚠️  Image not found: {filename}")
            failed_images.append(filename)
            continue
        
        print(f"  [{idx}/{len(ground_truth)}] Processing {filename}...", end=' ')
        
        # Convert to base64 and predict
        try:
            image_b64 = image_to_base64(image_path)
            result = predict_image(image_b64)
            
            if result and 'season' in result:
                original_season = result['season']
                predicted_season = normalize_season(original_season)
                
                # Check if model returned "undetermined" or similar
                undetermined_keywords = ['undetermined', 'undeterminable', 'n/a', 'cannot determine', 
                                        'unable to determine', 'na', 'none', 'unknown']
                if predicted_season.lower() in undetermined_keywords:
                    print(f"⚠️  Model could not determine season (returned: {original_season})")
                    undetermined_images.append(filename)
                    continue
                
                # Only add valid predictions
                if predicted_season in ['fall', 'spring', 'summer', 'winter']:
                    predictions[filename] = predicted_season
                    confidences[filename] = result.get('confidence', 0.0)
                    
                    # Check if correct
                    is_correct = predicted_season == true_label
                    symbol = "✓" if is_correct else "✗"
                    
                    # Show mapping if detailed type was returned
                    if original_season.lower() != predicted_season:
                        print(f"{symbol} Predicted: {original_season} → {predicted_season} (confidence: {confidences[filename]:.2f})")
                    else:
                        print(f"{symbol} Predicted: {predicted_season} (confidence: {confidences[filename]:.2f})")
                else:
                    print(f"⚠️  Unexpected season format: {predicted_season} (from: {original_season})")
                    undetermined_images.append(filename)
            else:
                print("✗ Prediction failed")
                failed_images.append(filename)
        except Exception as e:
            print(f"✗ Error: {str(e)}")
            failed_images.append(filename)
    
    print(f"\n✓ Completed predictions for {len(predictions)}/{len(ground_truth)} images")
    if undetermined_images:
        print(f"⚠️  Undetermined predictions: {len(undetermined_images)} images")
        print(f"   (Model couldn't classify these due to image quality/lighting)")
    if failed_images:
        print(f"⚠️  Failed predictions: {len(failed_images)} (API errors)")
    
    # Calculate metrics
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    
    # Add statistics about undetermined
    total_processed = len(predictions) + len(undetermined_images) + len(failed_images)
    if undetermined_images:
        print(f"\n📊 Classification Coverage:")
        print(f"  Successfully classified: {len(predictions)}/{len(ground_truth)} ({len(predictions)/len(ground_truth)*100:.1f}%)")
        print(f"  Undetermined (poor image quality): {len(undetermined_images)}")
        print(f"  Failed (API errors): {len(failed_images)}")
    
    results = calculate_metrics(ground_truth, predictions, confidences, undetermined_images)
    
    # Generate visualizations
    print("\n📊 Generating visualizations...")
    generate_visualizations(ground_truth, predictions, confidences, results)
    
    # Save results to JSON
    save_results(results, predictions, confidences, ground_truth)
    
    print(f"\n✓ All results saved to {OUTPUT_DIR}/")
    print("\n" + "=" * 70)


def calculate_metrics(ground_truth, predictions, confidences, undetermined_images=[]):
    """Calculate validation metrics."""
    # Filter to only images that were successfully predicted
    common_images = set(ground_truth.keys()) & set(predictions.keys())
    
    if not common_images:
        print("⚠️  No successful predictions to evaluate!")
        return {
            'overall_accuracy': 0,
            'total_predictions': 0,
            'correct_predictions': 0,
            'class_metrics': {},
            'confusion_matrix': {},
            'avg_correct_confidence': 0,
            'avg_incorrect_confidence': 0,
            'undetermined_count': len(undetermined_images)
        }
    
    # Overall accuracy (on successfully classified images only)
    correct = sum(1 for img in common_images if ground_truth[img] == predictions[img])
    accuracy_on_classified = correct / len(common_images)
    
    print(f"\n📈 Accuracy (on classified images): {accuracy_on_classified:.2%} ({correct}/{len(common_images)})")
    
    # Calculate metrics including undetermined as errors
    total_attempted = len(common_images) + len(undetermined_images)
    accuracy_total = correct / total_attempted if total_attempted > 0 else 0
    classification_rate = len(common_images) / total_attempted if total_attempted > 0 else 0
    
    if undetermined_images:
        print(f"📉 Accuracy (counting undetermined as errors): {accuracy_total:.2%} ({correct}/{total_attempted})")
        print(f"📊 Classification rate: {classification_rate:.2%} ({len(common_images)}/{total_attempted} images classified)")
        print(f"   → {len(undetermined_images)} images couldn't be classified due to quality/lighting")
    
    # Per-class metrics
    seasons = ['fall', 'spring', 'summer', 'winter']
    class_metrics = {}
    
    # Confusion matrix
    confusion = {true_s: {pred_s: 0 for pred_s in seasons} for true_s in seasons}
    
    for img in common_images:
        true_label = ground_truth[img]
        pred_label = predictions[img]
        confusion[true_label][pred_label] += 1
    
    print("\n📊 Per-Class Metrics:")
    for season in seasons:
        # True positives, false positives, false negatives
        tp = confusion[season][season]
        fp = sum(confusion[other][season] for other in seasons if other != season)
        fn = sum(confusion[season][other] for other in seasons if other != season)
        tn = sum(confusion[other1][other2] 
                for other1 in seasons if other1 != season 
                for other2 in seasons if other2 != season)
        
        # Calculate metrics
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        class_metrics[season] = {
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'support': tp + fn
        }
        
        print(f"  {season.capitalize():8s} - Precision: {precision:.2%}, Recall: {recall:.2%}, F1: {f1:.2%}")
    
    # Average confidence for correct vs incorrect predictions
    correct_confidences = [confidences[img] for img in common_images if ground_truth[img] == predictions[img]]
    incorrect_confidences = [confidences[img] for img in common_images if ground_truth[img] != predictions[img]]
    
    avg_correct_conf = np.mean(correct_confidences) if correct_confidences else 0
    avg_incorrect_conf = np.mean(incorrect_confidences) if incorrect_confidences else 0
    
    print(f"\n📊 Confidence Analysis:")
    print(f"  Average confidence (correct predictions): {avg_correct_conf:.2%}")
    print(f"  Average confidence (incorrect predictions): {avg_incorrect_conf:.2%}")
    
    # Accuracy by confidence threshold
    print(f"\n📊 Accuracy by Confidence Threshold:")
    confidence_thresholds = [0.70, 0.80, 0.85, 0.90, 0.95]
    
    for threshold in confidence_thresholds:
        # Filter predictions with confidence >= threshold
        high_conf_images = [img for img in common_images if confidences[img] >= threshold]
        
        if high_conf_images:
            high_conf_correct = sum(1 for img in high_conf_images if ground_truth[img] == predictions[img])
            high_conf_accuracy = high_conf_correct / len(high_conf_images)
            coverage = len(high_conf_images) / len(common_images)
            
            print(f"  Confidence ≥ {threshold:.0%}: {high_conf_accuracy:.2%} accuracy "
                  f"({high_conf_correct}/{len(high_conf_images)} images, {coverage:.1%} coverage)")
        else:
            print(f"  Confidence ≥ {threshold:.0%}: No predictions above this threshold")
    
    return {
        'overall_accuracy': accuracy,
        'total_predictions': len(common_images),
        'correct_predictions': correct,
        'class_metrics': class_metrics,
        'confusion_matrix': confusion,
        'avg_correct_confidence': avg_correct_conf,
        'avg_incorrect_confidence': avg_incorrect_conf,
        'undetermined_count': len(undetermined_images)
    }


def generate_visualizations(ground_truth, predictions, confidences, results):
    """Generate visualization plots."""
    common_images = set(ground_truth.keys()) & set(predictions.keys())
    seasons = ['fall', 'spring', 'summer', 'winter']
    
    # Set style
    sns.set_style("whitegrid")
    plt.rcParams['figure.figsize'] = (15, 10)
    
    # Create figure with subplots
    fig = plt.figure(figsize=(20, 12))
    
    # 1. Confusion Matrix
    ax1 = plt.subplot(2, 3, 1)
    confusion = results['confusion_matrix']
    conf_matrix = np.array([[confusion[true_s][pred_s] for pred_s in seasons] for true_s in seasons])
    
    sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues', 
                xticklabels=[s.capitalize() for s in seasons],
                yticklabels=[s.capitalize() for s in seasons],
                ax=ax1, cbar_kws={'label': 'Count'})
    ax1.set_title('Confusion Matrix', fontsize=14, fontweight='bold')
    ax1.set_ylabel('True Label', fontsize=12)
    ax1.set_xlabel('Predicted Label', fontsize=12)
    
    # 2. Per-Class Metrics Bar Chart
    ax2 = plt.subplot(2, 3, 2)
    metrics_data = results['class_metrics']
    x = np.arange(len(seasons))
    width = 0.25
    
    precision_vals = [metrics_data[s]['precision'] for s in seasons]
    recall_vals = [metrics_data[s]['recall'] for s in seasons]
    f1_vals = [metrics_data[s]['f1'] for s in seasons]
    
    ax2.bar(x - width, precision_vals, width, label='Precision', color='#3498db')
    ax2.bar(x, recall_vals, width, label='Recall', color='#2ecc71')
    ax2.bar(x + width, f1_vals, width, label='F1-Score', color='#e74c3c')
    
    ax2.set_ylabel('Score', fontsize=12)
    ax2.set_title('Per-Class Metrics', fontsize=14, fontweight='bold')
    ax2.set_xticks(x)
    ax2.set_xticklabels([s.capitalize() for s in seasons])
    ax2.legend()
    ax2.set_ylim([0, 1.1])
    ax2.grid(axis='y', alpha=0.3)
    
    # 3. Class Distribution
    ax3 = plt.subplot(2, 3, 3)
    true_counts = [sum(1 for v in ground_truth.values() if v == s) for s in seasons]
    pred_counts = [sum(1 for v in predictions.values() if v == s) for s in seasons]
    
    x = np.arange(len(seasons))
    width = 0.35
    
    ax3.bar(x - width/2, true_counts, width, label='Ground Truth', color='#95a5a6')
    ax3.bar(x + width/2, pred_counts, width, label='Predictions', color='#9b59b6')
    
    ax3.set_ylabel('Count', fontsize=12)
    ax3.set_title('Class Distribution', fontsize=14, fontweight='bold')
    ax3.set_xticks(x)
    ax3.set_xticklabels([s.capitalize() for s in seasons])
    ax3.legend()
    ax3.grid(axis='y', alpha=0.3)
    
    # 4. Confidence Distribution
    ax4 = plt.subplot(2, 3, 4)
    correct_confs = [confidences[img] for img in common_images if ground_truth[img] == predictions[img]]
    incorrect_confs = [confidences[img] for img in common_images if ground_truth[img] != predictions[img]]
    
    ax4.hist(correct_confs, bins=20, alpha=0.7, label='Correct', color='#2ecc71', edgecolor='black')
    ax4.hist(incorrect_confs, bins=20, alpha=0.7, label='Incorrect', color='#e74c3c', edgecolor='black')
    ax4.set_xlabel('Confidence', fontsize=12)
    ax4.set_ylabel('Frequency', fontsize=12)
    ax4.set_title('Confidence Distribution', fontsize=14, fontweight='bold')
    ax4.legend()
    ax4.grid(axis='y', alpha=0.3)
    
    # 5. Accuracy by Season
    ax5 = plt.subplot(2, 3, 5)
    season_accuracies = []
    for season in seasons:
        season_images = [img for img in common_images if ground_truth[img] == season]
        if season_images:
            correct = sum(1 for img in season_images if predictions[img] == season)
            acc = correct / len(season_images)
        else:
            acc = 0
        season_accuracies.append(acc)
    
    colors = [SEASON_COLORS[s] for s in seasons]
    bars = ax5.bar(seasons, season_accuracies, color=colors, edgecolor='black', linewidth=1.5)
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax5.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1%}',
                ha='center', va='bottom', fontweight='bold')
    
    ax5.set_ylabel('Accuracy', fontsize=12)
    ax5.set_title('Accuracy per Season', fontsize=14, fontweight='bold')
    ax5.set_xticklabels([s.capitalize() for s in seasons])
    ax5.set_ylim([0, 1.1])
    ax5.grid(axis='y', alpha=0.3)
    
    # 6. Overall Summary
    ax6 = plt.subplot(2, 3, 6)
    ax6.axis('off')
    
    summary_text = f"""
    VALIDATION SUMMARY
    {'=' * 40}
    
    Total Images: {len(common_images)}
    Overall Accuracy: {results['overall_accuracy']:.2%}
    Correct Predictions: {results['correct_predictions']}
    
    Average Confidence:
      • Correct: {results['avg_correct_confidence']:.2%}
      • Incorrect: {results['avg_incorrect_confidence']:.2%}
    
    Best Performing Class: {max(results['class_metrics'].items(), key=lambda x: x[1]['f1'])[0].capitalize()}
    
    Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """
    
    ax6.text(0.1, 0.5, summary_text, fontsize=11, family='monospace',
            verticalalignment='center', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'validation_results.png', dpi=300, bbox_inches='tight')
    print(f"  ✓ Saved visualization: {OUTPUT_DIR / 'validation_results.png'}")
    plt.close()
    
    # Create a separate detailed confusion matrix
    create_detailed_confusion_matrix(confusion, seasons)


def create_detailed_confusion_matrix(confusion, seasons):
    """Create a detailed confusion matrix with percentages."""
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Calculate percentages
    conf_matrix = np.array([[confusion[true_s][pred_s] for pred_s in seasons] for true_s in seasons])
    conf_matrix_pct = conf_matrix.astype('float') / conf_matrix.sum(axis=1)[:, np.newaxis] * 100
    
    # Create annotations with both count and percentage
    annot = np.array([[f'{conf_matrix[i, j]}\n({conf_matrix_pct[i, j]:.1f}%)' 
                      for j in range(len(seasons))] 
                     for i in range(len(seasons))])
    
    sns.heatmap(conf_matrix, annot=annot, fmt='', cmap='YlOrRd',
                xticklabels=[s.capitalize() for s in seasons],
                yticklabels=[s.capitalize() for s in seasons],
                ax=ax, cbar_kws={'label': 'Count'},
                linewidths=1, linecolor='gray')
    
    ax.set_title('Detailed Confusion Matrix\n(Count and Percentage)', fontsize=16, fontweight='bold', pad=20)
    ax.set_ylabel('True Label', fontsize=14, fontweight='bold')
    ax.set_xlabel('Predicted Label', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'confusion_matrix_detailed.png', dpi=300, bbox_inches='tight')
    print(f"  ✓ Saved detailed confusion matrix: {OUTPUT_DIR / 'confusion_matrix_detailed.png'}")
    plt.close()


def save_results(results, predictions, confidences, ground_truth):
    """Save results to JSON file."""
    output_data = {
        'timestamp': datetime.now().isoformat(),
        'overall_metrics': {
            'accuracy': results['overall_accuracy'],
            'total_predictions': results['total_predictions'],
            'correct_predictions': results['correct_predictions']
        },
        'class_metrics': results['class_metrics'],
        'confusion_matrix': results['confusion_matrix'],
        'confidence_stats': {
            'avg_correct': results['avg_correct_confidence'],
            'avg_incorrect': results['avg_incorrect_confidence']
        },
        'predictions': [
            {
                'filename': filename,
                'ground_truth': ground_truth[filename],
                'prediction': predictions.get(filename, 'N/A'),
                'confidence': confidences.get(filename, 0.0),
                'correct': ground_truth[filename] == predictions.get(filename)
            }
            for filename in ground_truth.keys()
        ]
    }
    
    output_file = OUTPUT_DIR / 'validation_results.json'
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"  ✓ Saved results to: {output_file}")
    
    # Also save a summary text file
    summary_file = OUTPUT_DIR / 'validation_summary.txt'
    with open(summary_file, 'w') as f:
        f.write("=" * 70 + "\n")
        f.write("PERSONAL COLOR ANALYSIS MODEL - VALIDATION SUMMARY\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"Overall Accuracy: {results['overall_accuracy']:.2%}\n")
        f.write(f"Total Predictions: {results['total_predictions']}\n")
        f.write(f"Correct Predictions: {results['correct_predictions']}\n\n")
        f.write("Per-Class Metrics:\n")
        f.write("-" * 70 + "\n")
        for season, metrics in results['class_metrics'].items():
            f.write(f"{season.capitalize():10s} | ")
            f.write(f"Precision: {metrics['precision']:.2%} | ")
            f.write(f"Recall: {metrics['recall']:.2%} | ")
            f.write(f"F1: {metrics['f1']:.2%} | ")
            f.write(f"Support: {metrics['support']}\n")
    
    print(f"  ✓ Saved summary to: {summary_file}")


if __name__ == "__main__":
    try:
        run_validation()
    except KeyboardInterrupt:
        print("\n\n⚠️  Validation interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error during validation: {str(e)}")
        import traceback
        traceback.print_exc()

