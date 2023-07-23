import subprocess
import requests
import re
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

def extract_ip_org_from_file(file_path):
    ip_org_info = []
    with open(file_path, 'r') as file:
        for line in file:
            ip_org_match = re.search(r'(\d+\.\d+\.\d+\.\d+): {.*?\'org\': \'(.*?)\'.*?}', line)
            if ip_org_match:
                ip = ip_org_match.group(1)
                org = ip_org_match.group(2)
                ip_org_info.append((ip, org))
    return ip_org_info

def save_ip_org_to_file(ip_org_info, file_path):
    with open(file_path, 'w') as file:
        for ip, org in ip_org_info:
            file.write(f"{ip}, {org}\n")

def main():
    # Run netstat -ano command
    cmd_output = run_command('netstat -ano')

    # Filter the output to include only ESTABLISHED connections
    filtered_output = filter_established_connections(cmd_output)

    # Save the filtered output to a file
    filename_established = 'established_connections.txt'
    with open(filename_established, 'w') as file:
        file.write(filtered_output)

    print(f"Established connections saved to '{filename_established}'.")

    # Extract foreign addresses
    foreign_addresses = extract_foreign_addresses(filtered_output)

    # Get IP details and save to another file
    filename_foreign_addresses = 'foreign_addresses_details.txt'
    with open(filename_foreign_addresses, 'w') as file:
        for ip_address in foreign_addresses:
            details = get_ipinfo_details(ip_address)
            file.write(f"{ip_address}: {details}\n")
    # Extract IP and organization info from the file
        ip_org_info = extract_ip_org_from_file('foreign_addresses_details.txt')

        # Save IP and organization info to a separate file
        save_ip_org_to_file(ip_org_info, 'ip_organization_details.txt')

    print(f"Foreign addresses details saved to '{filename_foreign_addresses}'.")

if __name__ == "__main__":
    main()
