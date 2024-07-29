def parse_deal_stage(stage):
    if stage == "2350362":
        return "to delete (Lead Development Funnel)"
    elif stage == "2350321":
        return "Disqualified Lead (Lead Development Funnel)"
    elif stage == "2350318":
        return "Ready for Sales Pipeline (Lead Development Funnel)"
    elif stage == "qualifiedtobuy":
        return "10% - SQL (Sales pipeline)"
    elif stage == "fb38d038-f934-40e2-879b-bd267018a61a":
        return "30% - Requirements Analysis (Sales pipeline)"
    elif stage == "contractsent":
        return "50% - Project Development (Sales pipeline)"
    elif stage == "e36e5be6-4c90-45d6-9bfd-cfd6d9469ba8":
        return "70% - Negotiation (Sales pipeline)"
    elif stage == "894842":
        return "90% - Purchasing (Sales pipeline)"
    elif stage == "894843":
        return "100% - Won (Sales pipeline)"
    elif stage == "appointmentscheduled":
        return "0% - Lost (Sales pipeline)"
    else:
        return stage
    

def contact_lifecycle_stage_mapper(stage):
    if stage == "57677058":
        return "Marketing Lead"
    elif stage == "72332194":
        return "Unqualified Lead"
    elif stage == "68989508":
        return "Lead Dev Pipeline"
    elif stage == "70815292":
        return "Disqualified Lead"
    elif stage == "72329052":
        return "Lost"
    elif stage == "opportunity":
        return "Opportunity"
    elif stage == "lead":
        return "Lead"
    elif stage == "subscriber":
        return "Subscriber"
    elif stage == "marketingqualifiedlead":
        return "Marketing Qualified Lead"
    elif stage == "salesqualifiedlead":
        return "Sales Qualified Lead"
    elif stage == "81675095":
        return "Partner"
    elif stage == "customer":
        return "Customer"
    elif stage == "evangelist":
        return "Evangelist"
    elif stage == "other":
        return "Other"
    else:
        return stage
    
def reverse_deal_stage(stage):
    if stage == "to delete (Lead Development Funnel)":
        return "2350362"
    elif stage == "Disqualified Lead (Lead Development Funnel)":
        return "2350321"
    elif stage == "Ready for Sales Pipeline (Lead Development Funnel)":
        return "2350318"
    elif stage == "10% - SQL (Sales pipeline)":
        return "qualifiedtobuy"
    elif stage == "30% - Requirements Analysis (Sales pipeline)":
        return "fb38d038-f934-40e2-879b-bd267018a61a"
    elif stage == "50% - Project Development (Sales pipeline)":
        return "contractsent"
    elif stage == "70% - Negotiation (Sales pipeline)":
        return "e36e5be6-4c90-45d6-9bfd-cfd6d9469ba8"
    elif stage == "90% - Purchasing (Sales pipeline)":
        return "894842"
    elif stage == "100% - Won (Sales pipeline)":
        return "894843"
    elif stage == "0% - Lost (Sales pipeline)":
        return "appointmentscheduled"
    else:
        return stage