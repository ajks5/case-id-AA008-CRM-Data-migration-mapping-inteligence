"""
Seeded alias dictionary for CRM Data Migration.
Provides standardized mapping synonyms across common legacy CRM formats.
"""

from typing import Dict, List, Optional

# Standard target field canonical name -> list of known synonyms / aliases
CRM_FIELD_ALIASES: Dict[str, List[str]] = {
    "customer_id": [
        "cust_id", "client_id", "cid", "account_num", "customer_number",
        "cust_code", "legacy_id", "user_id"
    ],
    "id": [
        "lead_id", "contact_id", "record_id", "pk_id", "identifier"
    ],
    "first_name": [
        "fname", "given_name", "first", "forename", "first_nm"
    ],
    "last_name": [
        "lname", "surname", "family_name", "last", "last_nm"
    ],
    "name": [
        "full_name", "contact_name", "client_name", "display_name"
    ],
    "email": [
        "email_addr", "email_address", "mail", "contact_email", "e_mail"
    ],
    "phone": [
        "phone_num", "phone_number", "telephone", "mobile", "cell", "tel", "contact_phone"
    ],
    "account_name": [
        "company_name", "company", "org_name", "organization", "client_company",
        "business_name", "employer"
    ],
    "account_id": [
        "company_id", "acc_id", "org_id", "client_account_id"
    ],
    "street_address": [
        "address", "address1", "street", "addr_line1", "address_line_1"
    ],
    "city": [
        "town", "municipality", "city_name"
    ],
    "state": [
        "province", "region", "state_code"
    ],
    "postal_code": [
        "zip", "zip_code", "postcode", "zipcode", "postal"
    ],
    "country": [
        "nation", "country_code", "country_name"
    ],
    "created_at": [
        "created_date", "creation_date", "date_created", "signup_date",
        "registered_at", "reg_date", "insert_timestamp"
    ],
    "updated_at": [
        "modified_date", "last_modified", "updated_date", "update_timestamp"
    ],
    "lead_source": [
        "source", "origin", "referral_source", "lead_origin", "acquisition_channel"
    ],
    "annual_revenue": [
        "revenue", "annual_sales", "turnover", "ann_revenue", "yearly_revenue"
    ],
    "status": [
        "active_status", "state", "lead_status", "account_status", "record_status"
    ],
}


def normalize_identifier(name: str) -> str:
    """Normalize identifier: lowercase, remove underscores/hyphens/spaces."""
    return name.lower().replace("_", "").replace("-", "").replace(" ", "")


def find_alias_match(target_field: str, source_field: str) -> Optional[str]:
    """
    Check if source_field is a known alias for target_field.
    Returns explanation string if matched, else None.
    """
    target_norm = target_field.lower().strip()
    source_norm = source_field.lower().strip()
    
    # Direct alias lookup
    if target_norm in CRM_FIELD_ALIASES:
        synonyms = [s.lower() for s in CRM_FIELD_ALIASES[target_norm]]
        if source_norm in synonyms:
            return f"Source field '{source_field}' matches known CRM alias for '{target_field}'"
        
        # Normalized match against synonyms
        source_compact = normalize_identifier(source_norm)
        for syn in synonyms:
            if normalize_identifier(syn) == source_compact:
                return f"Source field '{source_field}' normalized matches known alias '{syn}' for '{target_field}'"
                
    # Reverse lookup: if target_field is listed as alias of something that source_field is also part of
    for canonical, aliases in CRM_FIELD_ALIASES.items():
        all_names = [canonical] + aliases
        if target_norm in all_names and source_norm in all_names:
            return f"Both '{source_field}' and '{target_field}' belong to canonical synonym group '{canonical}'"
            
    return None
