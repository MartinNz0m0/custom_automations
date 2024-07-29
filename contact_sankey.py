from hubspot import hubspot
from hubspot.crm.contacts import PublicObjectSearchRequest, ApiException
import datetime

import services
import hub_api_functions


def create_sankey_data():
    period = "month"
    year = 2024
    contacts = calculate()
    with_deals = []
    sankey_array = []
    for key in contacts.keys():
        sankey_data = {}
        for contact in contacts[key]:
            if contact['properties']['num_associated_deals']:
                with_deals.append(contact)
                
        # create sankey data with two dimensio sources and lifecycle stage in the end
        for contact in contacts[key]:
            analytics_source = contact['properties']['hs_analytics_source']
            marketing_source = contact['properties']['marketing_source__multiple_checkboxes_']
            lifecyclestage = services.contact_lifecycle_stage_mapper(contact['properties']['lifecyclestage'])
            
            if analytics_source not in sankey_data:
                sankey_data[analytics_source] = {}
            
            if marketing_source not in sankey_data[analytics_source]:
                sankey_data[analytics_source][marketing_source] = {}
                sankey_data[analytics_source][marketing_source]['life'] = {}
                sankey_data[analytics_source][marketing_source]['deal'] = {}
            
            if lifecyclestage not in sankey_data[analytics_source][marketing_source]['life']:
                sankey_data[analytics_source][marketing_source]['life'][lifecyclestage] = 0
                
            
            sankey_data[analytics_source][marketing_source]['life'][lifecyclestage] += 1
            
            # consider deal stages
            if contact in with_deals:
                hs_contact = hub_api_functions.get_user_by_id(contact['id'])
                if hs_contact.get('status') == 'success':
                    hs_contact = hs_contact.get('data')
                    if hs_contact.get('associations').get('deals'):
                        deals = hs_contact.get('associations').get('deals').get('results')
                        if deals:
                            deal_ids = [deal.get('id') for deal in deals if deal.get('type') == 'contact_to_deal']
                            deal_objs = [hub_api_functions.get_deal_by_id(deal_id) for deal_id in deal_ids]
                            recent_deal = max(deal_objs, key=lambda x: x.get('data').get('created_at'))
                            deal_stage = services.parse_deal_stage(recent_deal['data']['properties']['dealstage'])
                            # add to deal stages
                            if deal_stage not in sankey_data[analytics_source][marketing_source]:
                                sankey_data[analytics_source][marketing_source]['deal'][deal_stage] = {}
                                sankey_data[analytics_source][marketing_source]['deal'][deal_stage]['val'] = 0
                            sankey_data[analytics_source][marketing_source]['deal'][deal_stage]['life_stage'] = lifecyclestage
                            sankey_data[analytics_source][marketing_source]['deal'][deal_stage]['val'] += 1
            else:
                if lifecyclestage == "Unqualified Lead" or lifecyclestage == "Disqualified Lead":
                    if 'Unqualified' not in sankey_data[analytics_source][marketing_source]['deal']:
                        sankey_data[analytics_source][marketing_source]['deal']['Unqualified'] = {}
                        sankey_data[analytics_source][marketing_source]['deal']['Unqualified']['val'] = 0
                    sankey_data[analytics_source][marketing_source]['deal']['Unqualified']['life_stage'] = lifecyclestage
                    sankey_data[analytics_source][marketing_source]['deal']['Unqualified']['val'] += 1
                else:
                    if 'No Deal Created' not in sankey_data[analytics_source][marketing_source]['deal']:
                        sankey_data[analytics_source][marketing_source]['deal']['No Deal Created'] = {}
                        sankey_data[analytics_source][marketing_source]['deal']['No Deal Created']['val'] = 0
                    sankey_data[analytics_source][marketing_source]['deal']['No Deal Created']['life_stage'] = lifecyclestage
                    sankey_data[analytics_source][marketing_source]['deal']['No Deal Created']['val'] += 1
     
        # convert to array of arrays
        obj_life = {}
        obj_deal = {}
        for source in sankey_data:
            for target in sankey_data[source]:
                obj = {}
                for value in sankey_data[source][target]['life']:
                    tmp = f"{key}#{source}#{target}"
                    tmp_life = f"{key}#{target}#{value}"
                    
                    if tmp in obj:
                        obj[tmp]['value'] += sankey_data[source][target]['life'][value]
                    else:
                        obj[tmp] = {
                            "value": sankey_data[source][target]['life'][value]
                        }
                    if tmp_life in obj_life:
                        obj_life[tmp_life]['value'] += sankey_data[source][target]['life'][value]
                    else:
                        obj_life[tmp_life] = {
                            "value": sankey_data[source][target]['life'][value]
                        }
                for value in sankey_data[source][target]['deal'].keys():
                    life_stage = sankey_data[source][target]['deal'][value]['life_stage']
                    print(f"Deal: {value}, Life Stage: {life_stage}")
                    tmp_deal = f"{key}#{life_stage}#{value}"
                    if tmp_deal in obj_deal:
                        obj_deal[tmp_deal]['value'] += sankey_data[source][target]['deal'][value]['val']
                    else:
                        obj_deal[tmp_deal] = {
                            "value": sankey_data[source][target]['deal'][value]['val']
                        }
                for item in obj.keys():
                    sankey_array.append([item.split("#")[0], item.split("#")[1], item.split("#")[2], obj[item]['value']])
        for item in obj_life.keys():
            sankey_array.append([item.split("#")[0], item.split("#")[1], item.split("#")[2], obj_life[item]['value']])
        for item in obj_deal.keys():
            sankey_array.append([item.split("#")[0], item.split("#")[1], item.split("#")[2], obj_deal[item]['value']])
                    
        # # add rows for marketing sources vs lifecycle stage
        # for source in sankey_data:
        #     for target in sankey_data[source]:
        #         for value in sankey_data[source][target]['life']:
        #             sankey_array.append([key, target, value, sum(sankey_data[source][target]['life'].values())])
        #         for value in sankey_data[source][target]['deal']:
        #             sankey_array.append([key, next(iter(sankey_data[source][target]['life'])), value, sum(sankey_data[source][target]['deal'].values())])
            
    return {
        "data": sankey_array,
        "period": period,
        "year": year
    }

def calculate():
    res = {}
    month = datetime.datetime.now().month - 1 if datetime.datetime.now().month > 1 else 12
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
    res[f'{month} {year}'] = hub_api_functions.get_contacts_by_property(start_date, end_date)
    
    return res