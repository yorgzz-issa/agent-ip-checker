import json
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from functions import get_answer
import os

def check_ip(ip_address, all_ips_data):
    url = f"https://www.ipqualityscore.com/ip-reputation-check/lookup/{ip_address}"

    # Set up Chrome options to run headlessly (without opening a browser window)
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode (no browser window)

    # Set the path to the ChromeDriver (replace with your actual path)
    driver_path = 'chromedriver-win64/chromedriver.exe'  # Corrected path

    # Initialize the WebDriver with the correct driver path
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Open the URL
    driver.get(url)

    # Wait for the element with the class 'ip-lookup-report-wrapper' to be present
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "ip-lookup-report-wrapper"))
        )
        print(f"Page for IP {ip_address} is fully loaded and the div is present.")
    except:
        print(f"Timed out waiting for the div for IP {ip_address}.")

    # Get the HTML content of the <div> with the class 'ip-lookup-report-wrapper'
    div_element = driver.find_element(By.XPATH, "//div[@class='ip-lookup-report-wrapper']")
    content_text = div_element.text

    content_data = {
        "ip_address": ip_address,
        "check_ip_reputation": content_text.split('\n')[0],  
        "ip_details": {
            "ip_address": content_text.split('\n')[1], 
            "proxy_vpn_check": content_text.split('\n')[2], 
            "ip_reputation_score": content_text.split('\n')[3],  
            "blacklist_check": content_text.split('\n')[4], 
            "blacklist_details": content_text.split('\n')[5], 
        }
    }
    additional_info = {
        "check_ip_reputation": content_data["check_ip_reputation"],
        "ip_details": {
            "ip_address": content_data["ip_details"]["ip_address"],
            "proxy_vpn_check": content_data["ip_details"]["proxy_vpn_check"],
            "ip_reputation_score": content_data["ip_details"]["ip_reputation_score"],
            "blacklist_details": content_data["ip_details"]["blacklist_details"]
        }
    }

    # Extract the percentage from the blacklist_check text (e.g., "0% - Clean IP")
    blacklist_check_text = content_data["ip_details"]["blacklist_check"]
    percentage_match = re.search(r"(\d+)%", blacklist_check_text)

    if percentage_match:
        percentage_value = percentage_match.group(1)  # Extract the matched percentage
        answer = get_answer(percentage_value, additional_info)  # Pass the value to get_answer
        content_data["answer"] = answer  # Add the answer to the data
        print(answer)
    else:
        print(f"No percentage match found in blacklist check text for IP {ip_address}.")

    # Add the IP data to the dictionary of all IPs
    all_ips_data[ip_address] = content_data

    # Close the driver after use
    driver.quit()

def load_existing_ips_data():
    # Load existing data from the JSON file if it exists
    if os.path.exists("ips/ips_data.json"):
        with open("ips/ips_data.json", "r") as json_file:
            return json.load(json_file)
    else:
        return {}

def save_ips_data(all_ips_data):
    # Save the structured data of all IPs into a JSON file
    with open("ips/ips_data.json", "w") as json_file:
        json.dump(all_ips_data, json_file, indent=4)

if __name__ == "__main__":
    all_ips_data = load_existing_ips_data()  # Load existing data before starting

    # Allow the user to enter multiple IP addresses
    while True:
        ip_address = input("Enter the IP address to check (or type 'done' to finish): ")
        if ip_address.lower() == 'done':
            break
        check_ip(ip_address, all_ips_data)

    # After processing all IPs, save the updated data to a JSON file
    save_ips_data(all_ips_data)
    print("All IP data has been saved to 'ips_data.json'.")
