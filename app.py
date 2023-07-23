import subprocess
import requests
from flask import Flask, render_template, request
import africastalking


app = Flask(__name__)

# Replace with your Africa's Talking API credentials
AFRICASTALKING_USERNAME = 'spaceity'
AFRICASTALKING_API_KEY = 'b07e0b95e54d9747c23eb69011ee85c7c842ac57254e5bc4590bfe683fecff32'
def initialize_sms():
    try:
        # Replace 'YOUR_USERNAME' and 'YOUR_API_KEY' with your actual Africa's Talking credentials
        africastalking.initialize(username='spaceity', api_key='b07e0b95e54d9747c23eb69011ee85c7c842ac57254e5bc4590bfe683fecff32')
        return True
    except Exception as e:
        print(f"Error initializing Africa's Talking: {e}")
        return False

# Initialize Africa's Talking SMS
if initialize_sms():
    sms = africastalking.SMS
else:
    sms = None



IPINFO_API_KEY = '4a156323e54c50'  # Replace with your API key from https://ipinfo.io/

def run_command(command):
    result = subprocess.run(command, stdout=subprocess.PIPE, text=True, shell=True)
    return result.stdout

def filter_established_connections(output):
    lines = output.strip().split('\n')
    filtered_lines = [line for line in lines if "ESTABLISHED" in line]
    return '\n'.join(filtered_lines)

def extract_foreign_addresses(output):
    lines = output.strip().split('\n')
    foreign_addresses = []

    for line in lines:
        if "ESTABLISHED" in line:
            parts = line.split()
            foreign_address = parts[2].split(':')[0]  # Remove port number (if any)
            foreign_addresses.append(foreign_address)

    return foreign_addresses

def get_ipinfo_details(ip_address):
    url = f'https://ipinfo.io/{ip_address}?token={IPINFO_API_KEY}'
    response = requests.get(url)
    return response.json()

def send_sms(phone_number, message):
    africastalking.initialize(AFRICASTALKING_USERNAME, AFRICASTALKING_API_KEY)
    sms = africastalking.SMS
    try:
        response = sms.send(message, [phone_number])
        print(response)
    except Exception as e:
        print(f"Error sending SMS: {e}")
def get_ipinfo_details(ip_address):
    url = f'https://ipinfo.io/{ip_address}?token={IPINFO_API_KEY}'
    response = requests.get(url)
    return response.json()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get user's name and phone number from the form
        user_name = request.form['name']
        user_phone = request.form['phone']

        # Run netstat -ano command
        cmd_output = run_command('netstat -ano')

        # Filter the output to include only ESTABLISHED connections
        filtered_output = filter_established_connections(cmd_output)

        # Save the filtered output to a file
        with open('established_connections.txt', 'w') as file:
            file.write(filtered_output)

        # Extract foreign addresses
        foreign_addresses = extract_foreign_addresses(filtered_output)

        # Get IP details and save to another file
        with open('foreign_addresses_details.txt', 'w') as file:
            for ip_address in foreign_addresses:
                details = get_ipinfo_details(ip_address)
                file.write(f"{ip_address}: {details}\n")

        # Count the number of loggers
        with open('foreign_addresses_details.txt', 'r') as file:
            num_loggers = sum(1 for line in file)

        # Prepare the personalized SMS message
        message = f"Hey {user_name}! You have {num_loggers} logger(s) in your computer. Login to Safely to check them out."

        # Send the personalized SMS to the user's phone number
        try:
            response = sms.send(message, [user_phone])
            print(response)
        except Exception as e:
            print(f"Error sending SMS: {e}")

        return render_template('result.html')

    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)