import csv
from ping3 import ping
import os
import platform

"""
    Author: Nathen Goldsborough
"""

def ping_check(ip_address, count=1):
    # return True
    for _ in range(count):
        
        delay = ping(ip_address, timeout=1)  # Timeout in seconds
        if delay is not None and delay is not False:  # Received a response
            print(f"Pinged: {ip_address}. Response received: {round(delay, 3)}ms")
            return True
        print(f"FATAL: Pinged: {ip_address}. No response received.")
    return False

def compare_csv_files(arp_file, ipam_file, output_file):
    arp_data = {}
    ipam_data = {}

    # Read the ARP table CSV file.
    try:
        with open(arp_file, 'r', encoding='utf-8') as arp_csv:
            arp_reader = csv.reader(arp_csv)
            # next(arp_reader, None)  # Skip the header row.  Handles empty files.
            for row in arp_reader:
                if len(row) == 2:
                    ip, mac = row
                    arp_data[ip] = mac.lower()  # Store MAC in lowercase
                elif row: #handling the case where row is not empty
                    print(f"Skipping invalid ARP entry: {row}")

    except FileNotFoundError:
        print(f"Error: ARP file not found at {arp_file}")
        return
    except Exception as e:
        print(f"Error reading ARP file: {e}")
        return

    # Read the ipam export CSV file.
    try:
        with open(ipam_file, 'r', encoding='utf-8') as ipam_csv:
            ipam_reader = csv.reader(ipam_csv)
            next(ipam_reader, None)  # Skip the header row. Handles empty files.
            for row in ipam_reader:
                if len(row) == 4:
                    ip, name, mac, comment = row
                    ipam_data[ip] = {
                        'mac': mac.lower(),  # Store MAC in lowercase
                        'name': name,
                        'comment': comment
                    }
                elif row: #handling the case where row is not empty
                    print(f"Skipping invalid ipam entry: {row}")
    except FileNotFoundError:
        print(f"Error: ipam file not found at {ipam_file}")
        return
    except Exception as e:
        print(f"Error reading ipam file: {e}")
        return

    # Prepare the output data.
    output_data = []
    for ip, arp_mac in arp_data.items():
        ping_successful = ping_check(ip)
        if ip in ipam_data:
            ipam_mac = ipam_data[ip]['mac']
            name = ipam_data[ip]['name']
            comment = ipam_data[ip]['comment']
            match = True
            mac_conflict = arp_mac != ipam_mac
            output_data.append({
                'IP': ip,
                'MAC': arp_mac,
                'Name': name,
                'Comment': comment,
                'Match': match,
                'MAC conflict': mac_conflict,
                'PING': ping_successful
            })
        else:
            output_data.append({
                'IP': ip,
                'MAC': '',
                'Name': '',
                'Comment': '',
                'Match': False,
                'MAC conflict': False,
                'PING': ping_successful
            })

    # Include entries that are only in ipam_data.
    for ip, data in ipam_data.items():
        if ip not in arp_data:
            ping_successful = ping_check(ip)
            output_data.append({
                'IP': ip,
                'MAC': data['mac'],
                'Name': data['name'],
                'Comment': data['comment'],
                'Match': False,
                'MAC conflict': False,
                'PING': ping_successful
            })
    # Write the output CSV file.
    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as output_csv:
            fieldnames = ['IP', 'MAC', 'Name', 'Comment', 'Match', 'MAC conflict', 'PING']
            writer = csv.DictWriter(output_csv, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(output_data)
        print(f"Successfully wrote output to {output_file}")
    except Exception as e:
        print(f"Error writing output file: {e}")

if __name__ == "__main__":
    # Example usage:
    arp_file = 'arp.csv'
    ipam_file = 'ipam.csv'
    output_file = 'output.csv'
    if compare_csv_files(arp_file, ipam_file, output_file):
        if platform.system() == 'Windows':
            try:
                os.startfile(output_file)
                print(f"Opened '{output_file}' with the default application.")
            except OSError as e:
                print(f"Error opening file on Windows: {e}")
                print(f"Please open '{output_file}' manually.")
        else:
            print(f"Not a Windows system. Please open '{output_file}' manually.")
