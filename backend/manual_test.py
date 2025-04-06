import requests
import json
from datetime import datetime, timedelta

# Base URL - change as needed
BASE_URL = "http://localhost:8000"

# Test users
donor = {
    "name": "Manual Donor",
    "email": "manualdonor@example.com",
    "password": "password123",
    "user_type": "donor",
    "latitude": 37.7749,
    "longitude": -122.4194
}

recipient = {
    "name": "Manual Recipient",
    "email": "manualrecipient@example.com", 
    "password": "password123",
    "user_type": "recipient",
    "latitude": 37.7833,
    "longitude": -122.4167
}

# Function to print response in a readable format
def print_response(response, message=""):
    print(f"\n{'='*80}")
    print(f"{message} - Status Code: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)
    print(f"{'='*80}\n")

def run_manual_test():
    # 1. Register users
    print("\n🔍 STEP 1: REGISTERING USERS")
    
    print("\nRegistering donor...")
    response = requests.post(f"{BASE_URL}/users/register", json=donor)
    print_response(response, "Donor registration")
    
    print("\nRegistering recipient...")
    response = requests.post(f"{BASE_URL}/users/register", json=recipient)
    print_response(response, "Recipient registration")
    
    # 2. Login and get tokens
    print("\n🔍 STEP 2: LOGGING IN")
    
    print("\nDonor login...")
    response = requests.post(
        f"{BASE_URL}/users/token",
        data={"username": donor["email"], "password": donor["password"]}
    )
    print_response(response, "Donor login")
    donor_token = response.json()["access_token"]
    
    print("\nRecipient login...")
    response = requests.post(
        f"{BASE_URL}/users/token",
        data={"username": recipient["email"], "password": recipient["password"]}
    )
    print_response(response, "Recipient login")
    recipient_token = response.json()["access_token"]
    
    # 3. Get user profiles
    print("\n🔍 STEP 3: CHECKING USER PROFILES")
    
    print("\nDonor profile...")
    response = requests.get(
        f"{BASE_URL}/users/me",
        headers={"Authorization": f"Bearer {donor_token}"}
    )
    print_response(response, "Donor profile")
    
    print("\nRecipient profile...")
    response = requests.get(
        f"{BASE_URL}/users/me",
        headers={"Authorization": f"Bearer {recipient_token}"}
    )
    print_response(response, "Recipient profile")
    
    # 4. Create gatherings
    print("\n🔍 STEP 4: CREATING GATHERINGS")
    
    gathering1 = {
        "food_details": "Leftover catering food: 20 sandwiches, 5 salads",
        "available_from": (datetime.now() - timedelta(hours=1)).isoformat(),
        "available_to": (datetime.now() + timedelta(days=1)).isoformat(),
        "latitude": 37.7749,
        "longitude": -122.4194
    }
    
    print("\nCreating first gathering...")
    response = requests.post(
        f"{BASE_URL}/gatherings/",
        json=gathering1,
        headers={"Authorization": f"Bearer {donor_token}"}
    )
    print_response(response, "Create gathering")
    gathering1_id = response.json()["id"]
    
    gathering2 = {
        "food_details": "Birthday party leftovers: cake, pizza, drinks",
        "available_from": (datetime.now() - timedelta(hours=2)).isoformat(),
        "available_to": (datetime.now() + timedelta(hours=12)).isoformat(),
        "latitude": 37.7780,
        "longitude": -122.4184
    }
    
    print("\nCreating second gathering...")
    response = requests.post(
        f"{BASE_URL}/gatherings/",
        json=gathering2,
        headers={"Authorization": f"Bearer {donor_token}"}
    )
    print_response(response, "Create second gathering")
    gathering2_id = response.json()["id"]
    
    # 5. View gatherings as recipient
    print("\n🔍 STEP 5: VIEWING GATHERINGS AS RECIPIENT")
    
    print("\nAll available gatherings...")
    response = requests.get(
        f"{BASE_URL}/gatherings/",
        headers={"Authorization": f"Bearer {recipient_token}"}
    )
    print_response(response, "All gatherings")
    
    print("\nNearby gatherings...")
    response = requests.get(
        f"{BASE_URL}/gatherings/nearby?latitude={recipient['latitude']}&longitude={recipient['longitude']}",
        headers={"Authorization": f"Bearer {recipient_token}"}
    )
    print_response(response, "Nearby gatherings")
    
    print("\nSpecific gathering details...")
    response = requests.get(
        f"{BASE_URL}/gatherings/{gathering1_id}",
        headers={"Authorization": f"Bearer {recipient_token}"}
    )
    print_response(response, f"Gathering {gathering1_id} details")
    
    # 6. Claim a gathering
    print("\n🔍 STEP 6: CLAIMING A GATHERING")
    
    claim_data = {
        "gathering_id": gathering1_id
    }
    
    print("\nClaiming first gathering...")
    response = requests.post(
        f"{BASE_URL}/claims/",
        json=claim_data,
        headers={"Authorization": f"Bearer {recipient_token}"}
    )
    print_response(response, "Claim gathering")
    claim_id = response.json()["id"]
    
    # 7. Check that gathering is now taken
    print("\n🔍 STEP 7: VERIFYING GATHERING IS TAKEN")
    
    response = requests.get(
        f"{BASE_URL}/gatherings/{gathering1_id}",
        headers={"Authorization": f"Bearer {recipient_token}"}
    )
    print_response(response, "Gathering after claim")
    
    # 8. View claims as recipient
    print("\n🔍 STEP 8: VIEWING CLAIMS AS RECIPIENT")
    
    response = requests.get(
        f"{BASE_URL}/claims/my-claims",
        headers={"Authorization": f"Bearer {recipient_token}"}
    )
    print_response(response, "Recipient's claims")
    
    # 9. View claims as donor
    print("\n🔍 STEP 9: VIEWING CLAIMS AS DONOR")
    
    response = requests.get(
        f"{BASE_URL}/claims/for-my-gatherings",
        headers={"Authorization": f"Bearer {donor_token}"}
    )
    print_response(response, "Donor's gathering claims")
    
    # 10. Update claim to collected (by donor)
    print("\n🔍 STEP 10: MARKING CLAIM AS COLLECTED")
    
    response = requests.put(
        f"{BASE_URL}/claims/{claim_id}/status?status=collected",
        headers={"Authorization": f"Bearer {donor_token}"}
    )
    print_response(response, "Update claim to collected")
    
    # 11. Claim second gathering
    print("\n🔍 STEP 11: CLAIMING SECOND GATHERING")
    
    claim_data = {
        "gathering_id": gathering2_id
    }
    
    response = requests.post(
        f"{BASE_URL}/claims/",
        json=claim_data,
        headers={"Authorization": f"Bearer {recipient_token}"}
    )
    print_response(response, "Claim second gathering")
    claim2_id = response.json()["id"]
    
    # 12. Cancel second claim
    print("\n🔍 STEP 12: CANCELLING SECOND CLAIM")
    
    response = requests.put(
        f"{BASE_URL}/claims/{claim2_id}/status?status=cancelled",
        headers={"Authorization": f"Bearer {recipient_token}"}
    )
    print_response(response, "Cancel claim")
    
    # 13. Verify gathering is available again
    print("\n🔍 STEP 13: VERIFYING GATHERING IS AVAILABLE AGAIN")
    
    response = requests.get(
        f"{BASE_URL}/gatherings/{gathering2_id}",
        headers={"Authorization": f"Bearer {recipient_token}"}
    )
    print_response(response, "Gathering after cancellation")
    
    # 14. Check final state of claims
    print("\n🔍 STEP 14: CHECKING FINAL STATE OF CLAIMS")
    
    response = requests.get(
        f"{BASE_URL}/claims/my-claims",
        headers={"Authorization": f"Bearer {recipient_token}"}
    )
    print_response(response, "Final recipient claims")
    
    # 15. Try forbidden operations
    print("\n🔍 STEP 15: TESTING FORBIDDEN OPERATIONS")
    
    print("\nRecipient trying to create gathering (should fail)...")
    response = requests.post(
        f"{BASE_URL}/gatherings/",
        json=gathering1,
        headers={"Authorization": f"Bearer {recipient_token}"}
    )
    print_response(response, "Recipient create gathering attempt")
    
    print("\nDonor trying to view all gatherings (should fail)...")
    response = requests.get(
        f"{BASE_URL}/gatherings/",
        headers={"Authorization": f"Bearer {donor_token}"}
    )
    print_response(response, "Donor view all gatherings attempt")
    
    print("\nDonor trying to claim gathering (should fail)...")
    response = requests.post(
        f"{BASE_URL}/claims/",
        json={"gathering_id": gathering2_id},
        headers={"Authorization": f"Bearer {donor_token}"}
    )
    print_response(response, "Donor claim attempt")
    
    print("\n✅ Manual test completed!")

if __name__ == "__main__":
    run_manual_test()