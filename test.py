import requests
  
# Making a get request 
response = requests.get('http://127.0.0.1:5001/device?device_id=123456')
main_token=response.json() 
  
 
