"""
Quick validation test - validates only first 5 images for demonstration.
For full validation, use validate_model.py
"""
import sys
sys.path.append('.')

from validate_model import (
    load_ground_truth, image_to_base64, predict_image,
    normalize_season, VALID_DIR
)
from pathlib import Path


def quick_test():
    """Run a quick test on first 5 images."""
    print("=" * 70)
    print("QUICK VALIDATION TEST (5 images)")
    print("=" * 70)
    
    # Load ground truth
    print("\n📋 Loading ground truth...")
    ground_truth = load_ground_truth()
    
    # Take first 5 images
    test_images = list(ground_truth.items())[:5]
    
    print(f"✓ Testing {len(test_images)} images\n")
    
    # Run predictions
    correct = 0
    total = 0
    
    for idx, (filename, true_label) in enumerate(test_images, 1):
        image_path = VALID_DIR / filename
        
        if not image_path.exists():
            print(f"⚠️  [{idx}] Image not found: {filename}")
            continue
        
        print(f"[{idx}/{len(test_images)}] Testing {filename}")
        print(f"  True label: {true_label}")
        
        try:
            # Convert and predict
            image_b64 = image_to_base64(image_path)
            result = predict_image(image_b64)
            
            if result and 'season' in result:
                predicted = normalize_season(result['season'])
                confidence = result.get('confidence', 0.0)
                
                is_correct = predicted == true_label
                symbol = "✅" if is_correct else "❌"
                
                print(f"  Prediction: {predicted} (confidence: {confidence:.2%})")
                print(f"  Result: {symbol} {'CORRECT' if is_correct else 'INCORRECT'}\n")
                
                if is_correct:
                    correct += 1
                total += 1
            else:
                print(f"  ❌ Prediction failed\n")
        
        except Exception as e:
            print(f"  ❌ Error: {str(e)}\n")
    
    # Summary
    if total > 0:
        accuracy = correct / total
        print("=" * 70)
        print(f"QUICK TEST RESULTS: {correct}/{total} correct ({accuracy:.1%})")
        print("=" * 70)
        print("\n💡 For full validation with graphics, run:")
        print("   uv run python validate_model.py")
    else:
        print("⚠️  No successful predictions")


if __name__ == "__main__":
    try:
        quick_test()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

