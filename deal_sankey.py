from hubspot import hubspot
from hubspot.crm.contacts import PublicObjectSearchRequest, ApiException
import os
import dotenv
import datetime
import time

import services
import hub_api_functions

dotenv.load_dotenv()

def create_sankey_data():
    deals = calculate_periodically("quarter", 2024)
    
    final = []
    
    for key in deals.keys():
        sankey_data = {}
        
        for deal in deals[key]:
            analytics_source = deal['properties']['hs_analytics_source']
            deal_amount = int(deal['properties']['amount']) if deal['properties']['amount'] else 0
            deal_stage = services.parse_deal_stage(deal['properties']['dealstage'])
            bdr_stage = ""
            sales_stage = ""
            if "Lead Development Funnel" in deal_stage:
                bdr_stage = deal_stage
            else:
                bdr_stage = "Ready for Sales Pipeline (Lead Development Funnel)"
                sales_stage = deal_stage
                
            if analytics_source not in sankey_data:
                sankey_data[analytics_source] = {}
                
            if bdr_stage not in sankey_data[analytics_source]:
                sankey_data[analytics_source][bdr_stage] = {}
                
            if sales_stage not in sankey_data[analytics_source][bdr_stage]:
                if sales_stage == "":
                        if bdr_stage == "Ready for Sales Pipeline":
                            sales_stage = "Moving into sales pipeline"
                        elif bdr_stage == "to delete":
                            sales_stage = "To delete"
                sankey_data[analytics_source][bdr_stage][sales_stage] = {
                    'val': 0,
                    'amnt': 0
                }
                
            sankey_data[analytics_source][bdr_stage][sales_stage]['val'] += 1
            sankey_data[analytics_source][bdr_stage][sales_stage]['amnt'] += deal_amount
        # convert to array of arrays
        obj = {}
        for source in sankey_data:
            for target in sankey_data[source]:
                tmp_obj = {}
                for value in sankey_data[source][target]:
                    tmp_str = f"{key}#{source}#{target}"
                    tmp_val = f"{key}#{target}#{value}"
   
                    if tmp_str in tmp_obj:
                        tmp_obj[tmp_str]['value'] += sankey_data[source][target][value]['val']
                        tmp_obj[tmp_str]['amount'] += sankey_data[source][target][value]['amnt']
                    else:
                        tmp_obj[tmp_str] = {
                            'value': sankey_data[source][target][value]['val'],
                            'amount': sankey_data[source][target][value]['amnt'],
                        }
                        
                    if tmp_val in obj:
                        obj[tmp_val]['value'] += sankey_data[source][target][value]['val']
                        obj[tmp_val]['amount'] += sankey_data[source][target][value]['amnt']
                    else:
                        obj[tmp_val] = {
                            'value': sankey_data[source][target][value]['val'],
                            'amount': sankey_data[source][target][value]['amnt']
                        }
                for item in tmp_obj.keys():
                    final.append([item.split('#')[0], item.split('#')[1], item.split('#')[2], tmp_obj[item]['value'], tmp_obj[item]['amount']])
        for item in obj.keys():
            final.append([item.split('#')[0], item.split('#')[1], item.split('#')[2], obj[item]['value'], obj[item]['amount']])
                    
    return final

def calculate():
    res = {}
    month = datetime.datetime.now().month - 1 if datetime.datetime.now().month > 1 else 12
    month = 4
    year = datetime.datetime.now().year
    start_date = datetime.datetime(year, month, 1)
    if month in [1, 3, 5, 7, 8, 10, 12]:
        end_date = datetime.datetime(year, month, 31)
    elif month == 2:
        end_date = datetime.datetime(year, month, 28)
    else:
        end_date = datetime.datetime(year, month, 30)
        
    month = start_date.strftime("%b")
    start_date = str(int(start_date.timestamp()*1000))
    end_date = str(int(end_date.timestamp()*1000))
    res[f'{month} {year}'] = hub_api_functions.get_all_deals(start_date, end_date)
    
    return res

def calculate_periodically(period, year):
    res = {}
    if period == "month":
        for month in range(1, 13):
            start_date = datetime.datetime(year, month, 1)
            if month in [1, 3, 5, 7, 8, 10, 12]:
                end_date = datetime.datetime(year, month, 31)
            elif month == 2:
                end_date = datetime.datetime(year, month, 28)
            else:
                end_date = datetime.datetime(year, month, 30)

            month = start_date.strftime("%b")
            start_date = str(int(start_date.timestamp()*1000))
            end_date = str(int(end_date.timestamp()*1000))
            res[f'{month} {year}'] = hub_api_functions.get_all_deals(start_date, end_date)
            time.sleep(4)
    elif period == "quarter":
        for i in range(1, 5):
            start_date = str(int(datetime.datetime(year, i*3-2, 1).timestamp()*1000))
            if i in [1, 4]:
                end_date = str(int(datetime.datetime(year, i*3, 31).timestamp()*1000))
            else:
                end_date = str(int(datetime.datetime(year, i*3, 30).timestamp()*1000))
            now = datetime.datetime.now()
            if year == now.year and i*3 > now.month:
                break
            res[f'Q{i} {year}'] = hub_api_functions.get_all_deals(start_date, end_date)
    elif period == "year":
        start_date = datetime.datetime(year, 1, 1)
        end_date = datetime.datetime(year, 12, 31)
        start_date = str(int(start_date.timestamp()*1000))
        end_date = str(int(end_date.timestamp()*1000))
        res[f'{year}'] = hub_api_functions.get_all_deals(start_date, end_date)
        
    return res