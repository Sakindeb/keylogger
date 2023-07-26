import os
import africastalking
from datetime import datetime, date
import requests
import json

# Replace with your Africa's Talking API credentials
username = 'spaceity'
api_key = 'b07e0b95e54d9747c23eb69011ee85c7c842ac57254e5bc4590bfe683fecff32'

# Replace with your VirusTotal API key
vt_api_key = '7e33a905066287a26601f827c5b801dc16a65b0e3e602028a0df6ca061b5ce48'

# Initialize the Africa's Talking SDK
africastalking.initialize(username, api_key)
sms = africastalking.SMS

# Replace with the path to the directory where downloads are stored
download_directory = 'C:\\Users\\sakin\\Downloads'

def is_today(timestamp):
    file_date = datetime.fromtimestamp(timestamp).date()
    return file_date == date.today()

def get_today_downloaded_files(directory):
    if not os.path.exists(directory):
        return []

    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    today_files = [f for f in files if is_today(os.path.getmtime(os.path.join(directory, f)))]
    return today_files

def scan_file_with_vt(file_path):
    url = 'https://www.virustotal.com/api/v3/files'
    headers = {'x-apikey': vt_api_key}

    with open(file_path, 'rb') as file:
        files = {'file': file}
        response = requests.post(url, headers=headers, files=files)

    if response.status_code == 200:
        return response.json()
    else:
        return None

def save_results_to_file(file_name, results):
    with open(file_name, 'w') as output_file:
        json.dump(results, output_file, indent=4)

def send_message(phone_number, message):
    try:
        response = sms.send(message, [phone_number])
        print("Message sent successfully. Details:", response)
    except Exception as e:
        print("Error sending the message:", e)

if __name__ == "__main__":
    # Replace with the phone number of the user you want to send the message to
    user_phone_number = '+254115151539'

    today_files = get_today_downloaded_files(download_directory)
    if today_files:
        vt_results = {}
        for file in today_files:
            file_path = os.path.join(download_directory, file)
            scan_result = scan_file_with_vt(file_path)
            vt_results[file] = scan_result

        # Replace 'output_file.json' with the desired filename for the output results
        output_file_name = 'output_file.json'
        save_results_to_file(output_file_name, vt_results)

        message = f"Hey! You have {len(today_files)} downloaded files today. Check {output_file_name} for VirusTotal scan results!"
        send_message(user_phone_number, message)
    else:
        print("No downloaded files found.")
