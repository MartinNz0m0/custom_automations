from hubspot import hubspot
from hubspot.crm.contacts import PublicObjectSearchRequest, ApiException
import datetime
import time

import hub_api_functions


def process(start_date, end_date):
    total_contacts = hub_api_functions.search_contacts(start_date, end_date, "HAS_PROPERTY", None)
    # time.sleep(1) # HS API rate limit
    total_demos = hub_api_functions.search_contacts(start_date, end_date, "IN", ["Book Demo", "Book Demo DE"])
    time.sleep(1)
    total_ebooks = hub_api_functions.search_contacts(start_date, end_date, "IN", ["E-book", "E-book DE"])
    # time.sleep(1)
    total_event = hub_api_functions.search_contacts(start_date, end_date, "IN", ["Event", "Event DE"])
    # time.sleep(1)
    total_sales_pipeline = hub_api_functions.search_contacts(start_date, end_date, "HAS_PROPERTY", None, add_filter={
        "propertyName": "lifecyclestage",
        "operator": "IN",
        "values": ["68989508", "salesqualifiedlead", "72329052", "opportunity", "customer"]
    })
    time.sleep(1)
    total_sales_pipeline_demo = hub_api_functions.search_contacts(start_date, end_date, "IN", ["Book Demo", "Book Demo DE"], add_filter={
        "propertyName": "lifecyclestage",
        "operator": "IN",
        "values": ["68989508", "salesqualifiedlead", "72329052", "opportunity", "customer"]
    })
    # time.sleep(1)
    total_sales_pipeline_form = hub_api_functions.search_contacts(start_date, end_date, "IN", ["Book Demo", "Book Demo DE", "E-book", "E-book DE"], add_filter={
        "propertyName": "lifecyclestage",
        "operator": "IN",
        "values": ["68989508", "salesqualifiedlead", "72329052", "opportunity", "customer"]
    })
    # time.sleep(1)
    total_sales_pipeline_event = hub_api_functions.search_contacts(start_date, end_date, "IN", ["Event", "Event DE"], add_filter={
        "propertyName": "lifecyclestage",
        "operator": "IN",
        "values": ["68989508", "salesqualifiedlead", "72329052", "opportunity", "customer"]
    })
    time.sleep(1)
    total_unqualified = hub_api_functions.search_contacts(start_date, end_date, "HAS_PROPERTY", None, add_filter={
        "propertyName": "lifecyclestage",
        "operator": "IN",
        "values": ["72332194", "70815292"]
    })
    # time.sleep(1)
    unqualified_demo = hub_api_functions.search_contacts(start_date, end_date, "IN", ["Book Demo", "Book Demo DE"], add_filter={
        "propertyName": "lifecyclestage",
        "operator": "IN",
        "values": ["72332194", "70815292"]
    })
    time.sleep(1)
    unqualified_ebook = hub_api_functions.search_contacts(start_date, end_date, "IN", ["E-book", "E-book DE"], add_filter={
        "propertyName": "lifecyclestage",
        "operator": "IN",
        "values": ["72332194", "70815292"]
    })
    if type(total_sales_pipeline_form) == tuple:
        total_sales_pipeline_form = total_sales_pipeline_form[0]
    if total_contacts == 0:
        return {
            "total_contacts": 0,
            "total_demos": 0,
            "total_ebooks": 0,
            "total_event": 0,
            "total_sales_pipeline": 0,
            "total_unqualified": 0,
            "demo_percentage": "0%", 
            "ebook_percentage": "0%",
            "event_percentage": "0%",
            "sales_pipeline_percentage": "0%",
            "unqualified_percentage": "0%"
        }
    without_event = (total_demos+total_ebooks)
    object_res = {
        "total_contacts": total_contacts,
        "total_demos": total_demos,
        "total_ebooks": total_ebooks,
        "total_event": total_event,
        "total_sales_pipeline": total_sales_pipeline,
        "total_sales_pipeline_demo": total_sales_pipeline_demo,
        "total_sales_pipeline_form": total_sales_pipeline_form,
        "total_sales_pipeline_event": total_sales_pipeline_event,
        "total_unqualified": total_unqualified,
        "demo_percentage": f"{float(round((total_demos/total_contacts)*100,2))}%", 
        "ebook_percentage": f"{float(round((total_ebooks/total_contacts)*100,2))}%",
        "event_percentage": f"{float(round((total_event/total_contacts)*100,2))}%",
        "total_contact_pipeline": f"{float(round((total_sales_pipeline/total_contacts)*100,2))}%",
        "demo_pipeline_percentage": f"{float(round((total_sales_pipeline/total_demos)*100,2))}%" if total_demos > 0 else "0%",
        "demo_pipeline_percentage (Demo only)": f"{float(round((total_sales_pipeline_demo/total_demos)*100,2))}%" if total_demos > 0 else "0%",
        "form_pipeline_percentage": f"{float(round((total_sales_pipeline/without_event)*100,2))}%" if without_event > 0 else "0%",
        "form_pipeline_percentage (Demo & Ebook)": f"{float(round((total_sales_pipeline_form/without_event)*100,2))}%" if without_event > 0 else "0%",
        "event_pipeline_percentage": f"{float(round((total_sales_pipeline_event/total_event)*100,2))}%" if total_event > 0 else "0%",
        "unqualified_percentage": f"{float(round((total_unqualified/total_contacts)*100,2))}%" if total_contacts > 0 else "0%",
        "unqualified_demo_percentage": f"{float(round((unqualified_demo/total_demos)*100,2))}%" if total_demos > 0 else "0%",
        "unqualified_ebook_percentage": f"{float(round((unqualified_ebook/total_ebooks)*100,2))}%" if total_ebooks > 0 else "0%"
    }
    return object_res
        
def calculate(period:str="year", year:int=2023):
    res = {}
    if period == "year":
        years = [2021, 2022, 2023, 2024]
        for year in years:
            start_date = str(int(datetime.datetime(year, 1, 1).timestamp()*1000))
            end_date = str(int(datetime.datetime(year, 12, 31).timestamp()*1000))
            # time.sleep(4)
            res[year] = process(start_date, end_date)
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
            res[f"Q{i} {year}"] = process(start_date, end_date)
    elif period == "month":
        for i in range(1, 13):
            start_date = str(int(datetime.datetime(year, i, 1).timestamp()*1000))
            if i in [1, 3, 5, 7, 8, 10, 12]:
                end_date = str(int(datetime.datetime(year, i, 31).timestamp()*1000))
            elif i == 2:
                end_date = str(int(datetime.datetime(year, i, 28).timestamp()*1000))
            else:
                end_date = str(int(datetime.datetime(year, i, 30).timestamp()*1000))
            now = datetime.datetime.now()
            if year == now.year and i > now.month:
                break
            month = datetime.datetime(year, i, 1).strftime("%b")
            res[f"{month} {year}"] = process(start_date, end_date)
    return res
        
def handle_data():
    total_demos = 0
    final = []
    period = "quarter"
    year = 2024
    res = calculate(period, year)
    print(res)
    for item in res.keys():
        print(item, "\n")
        resp = [item]
        total_demos += res[item]["total_demos"]
        resp.extend([res[item][sub_item] for sub_item in res[item].keys()])
        final.append(resp)
    avg_demo = total_demos/len(res.keys())
    print(f"Average Demos: {avg_demo}")
    return {
        "data": final,
        "average_demos": avg_demo,
        "period": period,
        "year": year
    }