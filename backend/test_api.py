"""
Test script for the video downloader API
"""
import requests
import json

API_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("\n" + "="*60)
    print("Testing Health Endpoint")
    print("="*60)
    
    response = requests.get(f"{API_URL}/")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_download(url, platform_name):
    """Test download endpoint"""
    print("\n" + "="*60)
    print(f"Testing {platform_name} Download")
    print(f"URL: {url}")
    print("="*60)
    
    try:
        response = requests.post(
            f"{API_URL}/api/download",
            json={"url": url},
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS!")
            print(f"Title: {data.get('title')}")
            print(f"Platform: {data.get('platform')}")
            print(f"Duration: {data.get('duration')}")
            print(f"Formats: {len(data.get('formats', []))} available")
            
            for fmt in data.get('formats', [])[:3]:  # Show first 3 formats
                print(f"  - {fmt['label']} ({fmt['quality']})")
            
            return True
        else:
            print(f"❌ FAILED!")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    print("\n🚀 Starting API Tests...")
    
    # Test health
    if not test_health():
        print("\n❌ Health check failed! Server might not be running.")
        exit(1)
    
    # Test URLs
    test_urls = [
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "YouTube"),
        ("https://www.tiktok.com/@tiktok/video/7016451766833761541", "TikTok"),
    ]
    
    results = []
    for url, platform in test_urls:
        success = test_download(url, platform)
        results.append((platform, success))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    for platform, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{platform}: {status}")
    
    print("\n✅ Testing complete!")
