import httpx
import time
import sys
import subprocess
import os

def test_flow():
    base_url = "http://127.0.0.1:8000"
    client_id = "test-evaluator-123"
    
    print(f"--- Starting Integration Test for {base_url} ---")

    # 1. Check Health
    print("Checking /health...")
    try:
        resp = httpx.get(f"{base_url}/health", timeout=5)
        print(f"Health Status: {resp.status_code} | {resp.json()}")
    except Exception as e:
        print(f"Health Check Failed: {e}")
        return

    # 2. Get Token
    print(f"\nRequesting token for client_id: {client_id}...")
    token_resp = httpx.post(
        f"{base_url}/auth/token",
        json={"client_id": client_id},
        timeout=10
    )
    if token_resp.status_code != 200:
        print(f"Token Request Failed: {token_resp.status_code} {token_resp.text}")
        return
    
    token_data = token_resp.json()
    token = token_data["access_token"]
    print(f"Token received! Expires in: {token_data['expires_in']}s")

    # 3. Analyze Sector
    sector = "pharmaceuticals"
    print(f"\nAnalyzing sector: {sector} (this will take 10-20s)...")
    headers = {"Authorization": f"Bearer {token}"}
    
    start_time = time.time()
    try:
        report_resp = httpx.get(
            f"{base_url}/analyze/{sector}",
            headers=headers,
            timeout=60
        )
        duration = time.time() - start_time
        
        if report_resp.status_code == 200:
            print(f"Success! Report generated in {duration:.2f}s")
            print("\n--- REPORT PREVIEW (First 500 chars) ---")
            print(report_resp.text[:500] + "...")
            print("--- END PREVIEW ---\n")
            
            # Save the report in test/results/
            results_dir = os.path.join(os.path.dirname(__file__), "results")
            os.makedirs(results_dir, exist_ok=True)
            
            filename = os.path.join(results_dir, f"test_{sector}_report.md")
            with open(filename, "w", encoding="utf-8") as f:
                f.write(report_resp.text)
            print(f"Full report saved to: {os.path.abspath(filename)}")
            
        else:
            print(f"Analysis Failed: {report_resp.status_code}")
            print(report_resp.text)
            
    except httpx.ReadTimeout:
        print("Error: Analysis timed out! (Gemini or Search took too long)")
    except Exception as e:
        print(f"Error during analysis: {e}")

if __name__ == "__main__":
    test_flow()
