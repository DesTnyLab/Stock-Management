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

headers['Authorization'] = response.headers['Authorization']

# req = requests.get("https://webbackend.cdsc.com.np/api/meroShare/bank/", headers=headers, verify=True)

# id = ""
# banks = req.json()
# for bank in banks:
#     print(f"Bank ID: {bank['id']}, Bank Name: {bank['name']}")
#     id = bank['id']

# r = requests.get(f"https://webbackend.cdsc.com.np/api/meroShare/bank/{id}",
#                   headers=headers, verify=True)

# print(r.json())
# # {
# #     "accountBranchId": 8474,
# # 	"accountNumber": "25707010131582",
# # 	"accountTypeId": 1,
# # 	"appliedKitta": "10",
# # 	"bankId": "48",
# # 	"boid": "03910018",
# # 	"companyShareId": "713",
# # 	"crnNumber": "R000642877",
# # 	"customerId": 2191239,
# # 	"demat": "1301120003910018",
# # 	"transactionPIN": "1069"
# # }


payload1 = {
	"accountBranchId": 8474,
	"accountNumber": "25707010131582",
	"accountTypeId": 1,
	"appliedKitta": "10",
	"bankId": "14",
	"boid": "03910018",
	"companyShareId": "713",
	"crnNumber": "R000642877",
	"customerId": 4312880,
	"demat": "1301120003910018",
	"transactionPIN": "1069"
}


# Now you can use this information to apply for shares

response = requests.post("https://webbackend.cdsc.com.np/api/meroShare/applicantForm/share/apply", json=payload1, headers=headers)

print(response.status_code)
print(response.json())
