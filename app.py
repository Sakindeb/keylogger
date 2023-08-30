import os.path
import subprocess
import requests
from flask import Flask, render_template, request, jsonify
import psutil
import africastalking
import json

app = Flask(__name__)

#Africa's Talking API credentials
AFRICASTALKING_USERNAME = 'spaceity'
AFRICASTALKING_API_KEY = 'b07e0b95e54d9747c23eb69011ee85c7c842ac57254e5bc4590bfe683fecff32'

# Initialize Africa's Talking SMS
# This one also has the sms function
def initialize_sms():
    try:
        africastalking.initialize(username=AFRICASTALKING_USERNAME, api_key=AFRICASTALKING_API_KEY)
        return True
    except Exception as e:
        print(f"Error initializing Africa's Talking: {e}")
        return False

if initialize_sms():
    sms = africastalking.SMS
else:
    sms = None

# Replace with your API key from https://ipinfo.io/
IPINFO_API_KEY = '4a156323e54c50'

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


def check_master_password(password):
    return password == MASTER_PASSWORD


def check_existence():
    if os.path.exists(PASSWORD_FILE):
        pass
    else:
        file = open(PASSWORD_FILE, 'w')
        file.close()


def append_new(user_name, password, website):
    with open(PASSWORD_FILE, 'a') as file:
        file.write("---------------------------------\n")
        file.write("UserName:" + user_name + "\n")
        file.write("Password:" + encrypt_password(password) + "\n")
        file.write("Website:" + website + "\n")
        file.write("--------------------\n")


def read_passwords():
    with open(PASSWORD_FILE, 'r') as file:
        content = file.read()
    return content
def send_sms(phone_number, message):
    try:
        response = sms.send(message, [phone_number])
        print(response)
    except Exception as e:
        print(f"Error sending SMS: {e}")


@app.route('/api/network_stats')
def get_network_statistics():
    network_stats = psutil.net_io_counters(pernic=True)

    # Convert network_stats to a dictionary format for JSON response
    network_data = {}
    for interface, stats in network_stats.items():
        network_data[interface] = {
            'bytes_sent': stats.bytes_sent,
            'bytes_received': stats.bytes_recv,
            'packets_sent': stats.packets_sent,
            'packets_received': stats.packets_recv
        }

    return jsonify(network_data)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get user's name, phone number, and password from the form
        user_name = request.form['name']
        user_phone = request.form['phone']
        master_password = request.form['master_password']

        # Check the master password for validity
        if not check_master_password(master_password):
            return "Invalid master password. Password not saved."

        # Save the password details
        user_password = request.form['password']
        website = request.form['website']
        append_new(user_name, user_password, website)

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
        send_sms(user_phone, message)

        return render_template('result.html')
    
    # Get network statistics
    response = get_network_statistics()
    network_stats = json.loads(response.get_data(as_text=True))

    return render_template('index.html', network_stats=network_stats)


@app.route('/save_password', methods=['POST'])
def save_password():
    master_password = request.form['master_password']
    if not check_master_password(master_password):
        return "Invalid master password. Password not saved."

    user_name = request.form['name']
    password = request.form['password']
    website = request.form['website']

    append_new(user_name, password, website)

    return "Password saved successfully!"


@app.route('/get_passwords', methods=['POST'])
def get_passwords():
    master_password = request.form['master_password']
    if not check_master_password(master_password):
        return "Invalid master password. Passwords cannot be retrieved."

    passwords = read_passwords()
    return passwords


if __name__ == "__main__":
    check_existence()
    app.run(debug=True)
