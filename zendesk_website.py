from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from hubspot import hubspot
from hubspot.crm.contacts import PublicObjectSearchRequest, ApiException
from fake_useragent import UserAgent
import datetime
import time

import hub_api_functions

def run():
    start_date = str(int(datetime.datetime(2024, 1, 1).timestamp()*1000))
    end_date = str(int(datetime.datetime(2024, 1, 31).timestamp()*1000))
    contacts = hub_api_functions.get_contacts_by_property(start_date, end_date)
    response = []
    website_count = 0
    checked_websites = []
    for contact in contacts:
        if 'hs_email_domain' in contact['properties'] and contact['properties']['hs_email_domain'] is not None:
            if contact['properties']['hs_email_domain'] not in ["gmail.com", "yahoo.com", "hotmail.com", "salesforce.com", "outlook.com", "", "zendesk.com"]:
                website_count += 1
                if contact['properties']['hs_email_domain'] in checked_websites:
                    print('Website already checked')
                    continue
                res = scrape_site(contact['properties']['hs_email_domain'])
                checked_websites.append(contact['properties']['hs_email_domain'])
                if res['status'] == 'success':
                    response.append({
                        'website': contact['properties']['hs_email_domain'],
                        'has_zendesk': res['has_zendesk']
                    })
            continue
        else:
            print('No website found for contact')
            continue
    return {
        'total_contacts_checked': len(contacts),
        'contacts_with_website': website_count,
        'zendesk_count': len([x for x in response if x['has_zendesk'] == True]),    
        'zendeck_websites': [x['website'] for x in response if x['has_zendesk'] == True],
    
    }
    
def scrape_site(website:str) -> dict:
    
    website = website.split('.')[0]
    website = f"https://{website}.zendesk.com"
    dr = webdriver.Chrome()
    dr.get(website)
    time.sleep(5)
    if "help-center-closed" in dr.current_url:
        return {
            'status': 'success',
            'has_zendesk': False
        }
    html = BeautifulSoup(dr.page_source, 'html.parser')
    links = html.find_all('link', attrs={'rel': 'stylesheet'})
    has_zendesk = False
    for link in links:
        if 'zdassets.com' in link['href']:
            has_zendesk = True
            break
    return {
        'status': 'success',
        'has_zendesk': has_zendesk
    }