from hubspot import hubspot
from hubspot.crm.contacts import PublicObjectSearchRequest, ApiException
import datetime
import pandas as pd

import services
import hub_api_functions

def get_avg():
    df = pd.read_csv("Hubspot Data Tracker - loss_ratio.csv")
    groups = df.groupby("Stage")
    
    obj = {}
    for name, group in groups:
        obj[name] = group['Percent'].mean()
    return obj
        

def forecast_close_deals():
    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(days=60)
    start_date = str(int(start_date.timestamp()*1000))
    end_date = str(int(end_date.timestamp()*1000))
    avg_loss = get_avg()
    
    obj = {
        "totals": {}
    }
    for key in avg_loss.keys():
        stage_code = services.reverse_deal_stage(key)
        deals = hub_api_functions.get_all_deals(start_date, end_date, stage_code)
        num_deals = len(deals)
        obj["totals"][key] = num_deals
        
        if key == "10% - SQL (Sales pipeline)":
            obj["30% - Requirements Analysis (Sales pipeline)"] = num_deals * ((100 - avg_loss[key]) / 100)
        elif key == "30% - Requirements Analysis (Sales pipeline)":
            # obj["30% - Requirements Analysis (Sales pipeline)"] = obj["30% - Requirements Analysis (Sales pipeline)"] + num_deals
            obj["50% - Project Development (Sales pipeline)"] = (num_deals + obj["30% - Requirements Analysis (Sales pipeline)"]) * ((100 - avg_loss[key]) / 100)
        elif key == "50% - Project Development (Sales pipeline)":
            # obj["50% - Project Development (Sales pipeline)"] = obj["50% - Project Development (Sales pipeline)"] + num_deals
            obj["70% - Negotiation (Sales pipeline)"] = (num_deals + obj["50% - Project Development (Sales pipeline)"]) * ((100 - avg_loss[key]) / 100)
        elif key == "70% - Negotiation (Sales pipeline)":
            # obj["70% - Negotiation (Sales pipeline)"] = obj["70% - Negotiation (Sales pipeline)"] + num_deals
            obj["90% - Purchasing (Sales pipeline)"] = (num_deals + obj["70% - Negotiation (Sales pipeline)"]) * ((100 - avg_loss[key]) / 100)
        elif key == "90% - Purchasing (Sales pipeline)":
            # obj["90% - Purchasing (Sales pipeline)"] = obj["90% - Purchasing (Sales pipeline)"] + num_deals
            obj["100% - Won (Sales pipeline)"] = (num_deals + obj["90% - Purchasing (Sales pipeline)"]) * ((100 - avg_loss[key]) / 100)
    
    return obj
