"""
Test script for user profile API endpoints.
Run this after starting the server to verify the profile functionality works.
"""
import requests
import base64
from pathlib import Path


API_BASE = "http://localhost:8000"


def test_user_profile_flow():
    """Test complete user profile flow."""
    print("=" * 60)
    print("Testing User Profile API")
    print("=" * 60)
    
    # Step 1: Register a test user
    print("\n1. Registering test user...")
    register_data = {
        "email": "profile_test@example.com",
        "password": "testpassword123"
    }
    
    response = requests.post(f"{API_BASE}/api/auth/register", json=register_data)
    if response.status_code in [200, 201]:
        print("✓ User registered successfully")
        token_data = response.json()
        token = token_data["access_token"]
    elif response.status_code == 400 and ("already exists" in response.text or "already registered" in response.text):
        # User already exists, try to login
        print("User already exists, logging in...")
        response = requests.post(f"{API_BASE}/api/auth/login", json=register_data)
        if response.status_code == 200:
            print("✓ User logged in successfully")
            token_data = response.json()
            token = token_data["access_token"]
        else:
            print(f"✗ Login failed: {response.status_code} - {response.text}")
            return
    else:
        print(f"✗ Registration failed: {response.status_code} - {response.text}")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Step 2: Check profile completeness (should be 0% initially)
    print("\n2. Checking initial profile completeness...")
    response = requests.get(f"{API_BASE}/api/user/profile/completeness", headers=headers)
    if response.status_code == 200:
        completeness = response.json()
        print(f"✓ Initial completeness: {completeness['completeness']}%")
        print(f"  Filled fields: {completeness['filled_fields']}/{completeness['total_fields']}")
    else:
        print(f"✗ Failed to get completeness: {response.status_code}")
    
    # Step 3: Try to get profile (should be 404 initially)
    print("\n3. Trying to get profile (should not exist yet)...")
    response = requests.get(f"{API_BASE}/api/user/profile", headers=headers)
    if response.status_code == 404:
        print("✓ Profile doesn't exist yet (expected)")
    elif response.status_code == 200:
        print("✓ Profile already exists")
        print(f"  Profile data: {response.json()}")
    else:
        print(f"✗ Unexpected response: {response.status_code}")
    
    # Step 4: Create profile with partial data
    print("\n4. Creating profile with partial data...")
    profile_data = {
        "height": 175.5,
        "weight": 70.0,
        "chest_size": 95.0,
        "waist_size": 80.0,
        "clothing_size": "M",
        "age": 25,
        "gender": "female",
        "preferred_style": "casual"
    }
    
    response = requests.post(
        f"{API_BASE}/api/user/profile",
        json=profile_data,
        headers=headers
    )
    
    if response.status_code == 201:
        print("✓ Profile created successfully")
        created_profile = response.json()
        print(f"  Profile ID: {created_profile['id']}")
    else:
        print(f"✗ Failed to create profile: {response.status_code} - {response.text}")
        return
    
    # Step 5: Check profile completeness again
    print("\n5. Checking updated profile completeness...")
    response = requests.get(f"{API_BASE}/api/user/profile/completeness", headers=headers)
    if response.status_code == 200:
        completeness = response.json()
        print(f"✓ Updated completeness: {completeness['completeness']}%")
        print(f"  Filled fields: {completeness['filled_fields']}/{completeness['total_fields']}")
        print(f"  Missing fields: {', '.join(completeness['missing_fields'])}")
    else:
        print(f"✗ Failed to get completeness: {response.status_code}")
    
    # Step 6: Get profile
    print("\n6. Getting profile...")
    response = requests.get(f"{API_BASE}/api/user/profile", headers=headers)
    if response.status_code == 200:
        print("✓ Profile retrieved successfully")
        profile = response.json()
        print(f"  Height: {profile.get('height')} cm")
        print(f"  Weight: {profile.get('weight')} kg")
        print(f"  Clothing size: {profile.get('clothing_size')}")
        print(f"  Age: {profile.get('age')}")
        print(f"  Gender: {profile.get('gender')}")
    else:
        print(f"✗ Failed to get profile: {response.status_code}")
    
    # Step 7: Update profile with image (if test image exists)
    print("\n7. Updating profile with additional data...")
    
    # Try to use a test image if it exists
    test_image_path = Path("images/image_test.JPG")
    if test_image_path.exists():
        print(f"  Found test image: {test_image_path}")
        with open(test_image_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode()
        
        update_data = {
            "hip_size": 98.0,
            "shoe_size": 39.0,
            "body_image": f"data:image/jpeg;base64,{image_data}"
        }
        
        print(f"  Sending update with image (size: {len(image_data)} bytes)...")
    else:
        print("  No test image found, updating without image")
        update_data = {
            "hip_size": 98.0,
            "shoe_size": 39.0
        }
    
    response = requests.post(
        f"{API_BASE}/api/user/profile",
        json=update_data,
        headers=headers
    )
    
    if response.status_code == 201:
        print("✓ Profile updated successfully")
        updated_profile = response.json()
        print(f"  Hip size: {updated_profile.get('hip_size')} cm")
        print(f"  Shoe size: {updated_profile.get('shoe_size')}")
        if updated_profile.get('body_image'):
            image_size = len(updated_profile.get('body_image'))
            print(f"  Body image saved: {image_size} characters (base64 string)")
    else:
        print(f"✗ Failed to update profile: {response.status_code} - {response.text}")
    
    # Step 8: Final completeness check
    print("\n8. Final completeness check...")
    response = requests.get(f"{API_BASE}/api/user/profile/completeness", headers=headers)
    if response.status_code == 200:
        completeness = response.json()
        print(f"✓ Final completeness: {completeness['completeness']}%")
        print(f"  Filled fields: {completeness['filled_fields']}/{completeness['total_fields']}")
        if completeness['missing_fields']:
            print(f"  Still missing: {', '.join(completeness['missing_fields'])}")
    else:
        print(f"✗ Failed to get completeness: {response.status_code}")
    
    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)
    
    # Optional: Uncomment to test deletion
    # print("\n9. Deleting profile...")
    # response = requests.delete(f"{API_BASE}/api/user/profile", headers=headers)
    # if response.status_code == 204:
    #     print("✓ Profile deleted successfully")
    # else:
    #     print(f"✗ Failed to delete profile: {response.status_code}")


if __name__ == "__main__":
    try:
        test_user_profile_flow()
    except requests.exceptions.ConnectionError:
        print("\n✗ Error: Could not connect to the API server.")
        print("Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"\n✗ Error occurred: {str(e)}")

