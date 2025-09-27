import requests

# Replace with your Vercel deployment URL
url = "https://<your-vercel-app>/api/index"

payload = {"regions": ["apac", "emea"], "threshold_ms": 181}

response = requests.post(url, json=payload)

print("Status code:", response.status_code)
print("Response JSON:", response.json())
