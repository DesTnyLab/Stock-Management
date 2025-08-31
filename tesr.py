import requests

url = "https://webbackend.cdsc.com.np/api/meroShare/auth/"

payload = {
    "clientId": 146,            # Replace with your DP ID
    "username": "03910018",       # Must be string
    "password": "Destiny@MS69"  # Exact password
}

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:142.0) Gecko/20100101 Firefox/142.0",
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json",
    "Origin": "https://meroshare.cdsc.com.np",
    "Referer": "https://meroshare.cdsc.com.np/",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    # Authorization is not needed here; leave it out
}

response = requests.post(url, json=payload, headers=headers)

print(response.status_code)
print(response.headers['Authorization'])
