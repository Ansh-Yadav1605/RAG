import urllib.request
import json
import time
import sys

# Force UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

url = 'http://localhost:8000/ask'
headers = {'Content-Type': 'application/json'}

def test_query(q, expected_status):
    data = json.dumps({'query': q}).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers=headers, method='POST')
    try:
        with urllib.request.urlopen(req) as response:
            res = json.loads(response.read().decode('utf-8'))
            status = res.get('status')
            answer = res.get('data', {}).get('answer', '')
            print(f"Q: '{q}'")
            print(f"Expected: {expected_status}, Got: {status}")
            if status == expected_status:
                print(f"✅ PASS: {answer[:100]}...")
            else:
                print(f"❌ FAIL: {answer}")
            print('-' * 60)
            return status == expected_status
    except Exception as e:
        print(f"❌ Error testing query {q}: {e}")
        return False

tests = [
    # Factual Queries
    ('What is the expense ratio of HDFC Large Cap Fund?', 'success'),
    ('What is the benchmark index for HDFC Large Cap Fund?', 'success'),
    ('What is the minimum SIP amount for HDFC Mid-Cap Opportunities Fund?', 'success'),
    ('Who is the fund manager for HDFC Mid-Cap Opportunities Fund?', 'success'),
    ('What is the exit load for HDFC Small Cap Fund?', 'success'),
    ('What is the riskometer classification for HDFC Small Cap Fund?', 'success'),
    ('What is the minimum lump-sum amount for HDFC Gold ETF FoF?', 'success'),
    ('What category does HDFC Gold ETF FoF belong to?', 'success'),
    ('What is the AUM for HDFC Silver ETF FoF?', 'success'),
    ('What is the expense ratio for HDFC Silver ETF FoF?', 'success'),
    
    # Advisory Queries
    ('Should I invest in HDFC Large Cap Fund?', 'refused'),
    ('Which is better — HDFC Mid Cap or Small Cap?', 'refused'),
    ('Will this fund give good returns?', 'refused'),
    
    # Out of Scope Queries
    ('What is the weather today?', 'refused'),
    ('Tell me about SBI Bluechip Fund', 'refused')
]

if __name__ == '__main__':
    all_passed = True
    for q, expected in tests:
        passed = test_query(q, expected)
        if not passed:
            all_passed = False
        time.sleep(2)  # Avoid rate limiting
        
    if all_passed:
        print("🎉 ALL END-TO-END TESTS PASSED 🎉")
    else:
        print("⚠️ SOME TESTS FAILED")
