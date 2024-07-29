from hubspot import hubspot
from hubspot.crm.contacts import PublicObjectSearchRequest, ApiException
import os
import dotenv
import datetime

dotenv.load_dotenv


# crm search for contacts
def search_contacts(start_date, end_date, operator, value, property_name="marketing_source__multiple_checkboxes_", add_filter=None):
    api_client = hubspot.HubSpot(access_token=os.environ["HS"])
        
    value_key = 'values' if operator in ["IN", "NOT IN"] else 'value'
    public_object_search_request = PublicObjectSearchRequest(
        filter_groups = [
            {
                "filters": [
                    {
                        value_key: value,
                        "propertyName": property_name,
                        "operator": operator
                    },
                    {
                        "propertyName": "createdate",
                        "operator": "BETWEEN",
                        "highValue": end_date,
                        "value": start_date
                        
                    }
                ]
            }
        ], limit=100
    )
    if add_filter:
        public_object_search_request.filter_groups[0]['filters'].append(add_filter)
    
    try:
        api_response = api_client.crm.contacts.search_api.do_search(public_object_search_request=public_object_search_request)
        res = api_response.to_dict()
        # return res['total'] # for a total count
        return res['results'] # for a list of contacts
    except ApiException as e:
        print("Exception when calling search_api->do_search: %s\n" % e)
        

# get a user by id, with properties and properties with history
def get_user_by_id(user_id:int) -> dict:
    try:
        api_client = hubspot.HubSpot(access_token=os.environ["HS"])
        properties = [
            "email",
            "hs_analytics_first_url",
        ]
        properties_with_history = [
            "hs_analytics_last_url"
        ]
        contact_fetched = api_client.crm.contacts.basic_api.get_by_id(user_id, properties=properties, properties_with_history=properties_with_history)
        contact = contact_fetched.to_dict()
        return {
            "status": "success",
            "data": contact
        }
    except Exception as e:
        print(f"Error fetching company from user: {e}")
        return {
            "status": "error",
            "message": str(e),
            "data": None
        }
        

# get all contacts for a certain time period and property value        
def get_contacts_by_property(start_date, end_date):
    api_client = hubspot.HubSpot(access_token=os.environ["HS"])
  
    public_object_search_request = PublicObjectSearchRequest(
        filter_groups = [
            {
                "filters": [
                    {
                        # "value": "Book Demo",
                        "propertyName": "marketing_source__multiple_checkboxes_",
                        "operator": "HAS_PROPERTY"
                    },
                    {
                        "propertyName": "createdate",
                        "operator": "BETWEEN",
                        "highValue": end_date,
                        "value": start_date
                        
                    }
                ]
            }
        ], limit=100, properties=["email", "marketing_source__multiple_checkboxes_", "hs_analytics_source", "lifecyclestage", "num_associated_deals"]
    )
    
    try:
        api_response = api_client.crm.contacts.search_api.do_search(public_object_search_request=public_object_search_request)
        res = api_response.to_dict()
        return res['results']
    except ApiException as e:
        print("Exception when calling search_api->do_search: %s\n" % e)
        
        
# get company from user id         
def get_company_from_user(user_id:int) -> dict:
    try:
        api_client = hubspot.HubSpot(access_token=os.environ["HS"])
        properties = [
            "email",
            "associatedcompanyid"
        ]
        contact_fetched = api_client.crm.contacts.basic_api.get_by_id(user_id, properties=properties)
        contact = contact_fetched.to_dict()
        company_id = contact.get('properties').get('associatedcompanyid')
        if company_id:
            return get_company_by_id(company_id)
        else:
            return {
                "status": "error",
                "message": "No company found",
                "data": None
            }
    except Exception as e:
        print(f"Error fetching company from user: {e}")
        return {
            "status": "error",
            "message": str(e),
            "data": None
        }
        
# get company by id        
def get_company_by_id(id):
    try:
        api_client = hubspot.HubSpot(access_token=os.environ["HS"])
        properties = [
            "website",
            "name",
            "linkedin_page"
            ]
        associations = [
            "deals"
        ]
        company_fetched = api_client.crm.companies.basic_api.get_by_id(id, properties=properties, associations=associations)
        res = company_fetched.to_dict()
        
        # this will sort the deal associations by most recent
        if res.get('associations'):
            deals = res.get('associations').get('deals').get('results')
            if deals:
                deal_ids = [deal.get('id') for deal in deals if deal.get('type') == 'company_to_deal']
                deal_objs = [get_deal_by_id(deal_id) for deal_id in deal_ids]
                recent_deal = max(deal_objs, key=lambda x: x.get('data').get('created_at'))
                res['deals'] = recent_deal['data']
                    
        return {
            "status": "success",
            "data": res
        }
    except Exception as e:
        print(f"Error fetching company by id: {e}")
        return {
            "status": "error",
            "message": str(e),
            "data": None
        }
        
# update company property - linkedin example
def update_company_linkedin(linkedin, company_id):
    try:
        api_client = hubspot.HubSpot(access_token=os.environ["HS"])
        properties = {
            "properties": {
            "linkedin_page": linkedin
        }
        }
        company_fetched = api_client.crm.companies.basic_api.update(company_id, properties)
        return {
            "status": "success",
            "data": company_fetched.to_dict()
        }
    except Exception as e:
        print(f"Error updating company: {e}")
        return {
            "status": "error",
            "message": str(e),
            "data": None
        }


# get a deal by its id
def get_deal_by_id(id):
    try:
        api_client = hubspot.HubSpot(access_token=os.environ["HS"])
        properties = [
            "dealname",
            "amount",
            "hubspot_owner_id"
            ]
        with_his = ["dealstage"]
        deal_fetched = api_client.crm.deals.basic_api.get_by_id(id, properties=properties, properties_with_history=with_his)
        res = deal_fetched.to_dict()
        return {
            "status": "success",
            "data": res
        }
    except Exception as e:
        print(f"Error fetching deal by id: {e}")
        return {
            "status": "error",
            "message": str(e),
            "data": None
        }


# get deals for certain time period and deal stage
def get_all_deals(start_date, end_date, stage):
    api_client = hubspot.HubSpot(access_token=os.environ["HS"])
    
    public_object_search_request = PublicObjectSearchRequest(
        filter_groups = [
            {
                "filters": [
                    {
                        "propertyName": "createdate",
                        "operator": "BETWEEN",
                        "value": start_date,
                        "highValue": end_date
                    },
                    {
                        "propertyName": "dealstage",
                        "operator": "EQ",
                        "value": stage
                    }
                ]
            }
        ], limit=100, properties=["dealname", "dealstage" ,"closedate", "amount", "hs_analytics_source"]
    )
    
    try:
        api_response = api_client.crm.deals.search_api.do_search(public_object_search_request=public_object_search_request)
        res = api_response.to_dict()
        return res['results']
    except ApiException as e:
        print("Exception when calling crm.deals.search_api.do_search: %s\n" % e)
        return None