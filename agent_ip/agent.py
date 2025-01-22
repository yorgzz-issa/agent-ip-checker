from flask import Flask, render_template, request, jsonify
import json
import re
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from functions import get_answer

app = Flask(__name__)

# Function to check IP reputation
def check_ip(ip_address):
    url = f"https://www.ipqualityscore.com/ip-reputation-check/lookup/{ip_address}"

    chrome_options = Options()
    chrome_options.add_argument("--headless")

    driver_path = 'chromedriver-win64/chromedriver.exe'
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "ip-lookup-report-wrapper"))
        )
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

        blacklist_check_text = content_data["ip_details"]["blacklist_check"]
        percentage_match = re.search(r"(\d+)%", blacklist_check_text)

        if percentage_match:
            percentage_value = percentage_match.group(1)
            additional_info = {
                "check_ip_reputation": content_data["check_ip_reputation"],
                "ip_details": content_data["ip_details"]
            }
            answer = get_answer(percentage_value, additional_info)
            content_data["answer"] = answer
        else:
            content_data["answer"] = "No percentage match found."

        return content_data
    except Exception as e:
        return {"error": str(e)}
    finally:
        driver.quit()

# Load existing IPs data
def load_existing_ips_data():
    if os.path.exists("ips/ips_data.json"):
        with open("ips/ips_data.json", "r") as json_file:
            return json.load(json_file)
    else:
        return {}

# Save IPs data
def save_ips_data(all_ips_data):
    with open("ips/ips_data.json", "w") as json_file:
        json.dump(all_ips_data, json_file, indent=4)

# Flask routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/check_ip', methods=['POST'])
def handle_check_ip():
    ip_address = request.form.get('ip_address')
    if not ip_address:
        return jsonify({"error": "IP address is required."}), 400

    result = check_ip(ip_address)
    return jsonify(result)

@app.route('/save_ips', methods=['POST'])
def handle_save_ips():
    all_ips_data = request.json
    save_ips_data(all_ips_data)
    return jsonify({"message": "IPs data saved successfully."})

if __name__ == "__main__":
    app.run(debug=True)
