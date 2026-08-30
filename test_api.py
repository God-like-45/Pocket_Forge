import requests
import time
import json

response = requests.post("http://127.0.0.1:8000/api/v1/upload-chapter", json={
    "chapter_text": "The massive starship shook as the photon torpedoes hit the shields. 'Evasive maneuvers!' yelled Commander Riker. The klaxons blared."
})
job = response.json()
job_id = job["id"]
print(f"Started job {job_id}")

while True:
    status_resp = requests.get(f"http://127.0.0.1:8000/api/v1/status/{job_id}")
    status = status_resp.json()
    print("Status:", status["status"])
    if status["status"] == "Completed":
        print(json.dumps(status["script_json"], indent=2))
        break
    elif status["status"] == "Failed":
        print("Failed!")
        break
    time.sleep(2)
