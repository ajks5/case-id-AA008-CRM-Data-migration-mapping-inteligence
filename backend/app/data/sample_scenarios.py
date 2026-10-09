"""
Seeded Sample Scenarios for AA008 CRM Data Migration Mapping Intelligence.
Implements the 3 canonical scenarios from Product Bible §17:
1. Simple schema -> High direct-map coverage
2. Naming mismatch -> Alias-based mappings with evidence + transform
3. Relationship mismatch -> Target relationship cannot be safely derived -> REVIEW
"""

from typing import Dict, Any

SAMPLE_SCENARIOS: Dict[str, Dict[str, Any]] = {
    "simple_schema": {
        "id": "simple_schema",
        "name": "Scenario 1: Simple Schema (High Direct-Map)",
        "description": "Source and destination share standardized column names and compatible types. Results in high DIRECT_MAP coverage.",
        "expected_behavior": "High direct-map coverage (100% mapped, no human review required).",
        "request": {
            "source_schema": {
                "table_name": "legacy_contacts",
                "fields": [
                    {"name": "id", "data_type": "integer", "is_primary_key": True, "is_nullable": False},
                    {"name": "first_name", "data_type": "varchar", "is_nullable": False},
                    {"name": "last_name", "data_type": "varchar", "is_nullable": False},
                    {"name": "email", "data_type": "varchar", "is_nullable": False},
                    {"name": "phone", "data_type": "varchar", "is_nullable": True},
                    {"name": "created_at", "data_type": "datetime", "is_nullable": False}
                ],
                "relationships": []
            },
            "destination_schema": {
                "table_name": "crm_contacts",
                "fields": [
                    {"name": "id", "data_type": "integer", "is_primary_key": True, "is_required": True},
                    {"name": "first_name", "data_type": "string", "is_required": True},
                    {"name": "last_name", "data_type": "string", "is_required": True},
                    {"name": "email", "data_type": "string", "is_required": True},
                    {"name": "phone", "data_type": "string", "is_required": False},
                    {"name": "created_at", "data_type": "datetime", "is_required": True},
                    {"name": "status", "data_type": "string", "is_required": False, "default_value": "ACTIVE"}
                ],
                "relationships": []
            },
            "sample_rows": [
                {
                    "id": 101,
                    "first_name": "Alice",
                    "last_name": "Walker",
                    "email": "alice.walker@example.com",
                    "phone": "+1-555-0199",
                    "created_at": "2024-01-15T09:30:00Z"
                },
                {
                    "id": 102,
                    "first_name": "Robert",
                    "last_name": "Chen",
                    "email": "robert.c@example.org",
                    "phone": "+1-555-0142",
                    "created_at": "2024-02-20T14:15:00Z"
                }
            ],
            "relationship_metadata": [],
            "known_mapping_hints": {}
        }
    },
    "naming_mismatch": {
        "id": "naming_mismatch",
        "name": "Scenario 2: Naming Mismatch (Alias-Based Direct Map & Transform)",
        "description": "Legacy system uses abbreviations (cust_id, fname, lname, phone_num, email_addr, company_name, signup_date). Resolved via CRM alias dictionary and date type cast.",
        "expected_behavior": "DIRECT_MAP with alias evidence + TRANSFORM for string-to-datetime signup_date.",
        "request": {
            "source_schema": {
                "table_name": "old_customer_export",
                "fields": [
                    {"name": "cust_id", "data_type": "integer", "is_primary_key": True, "is_nullable": False},
                    {"name": "fname", "data_type": "varchar", "is_nullable": False},
                    {"name": "lname", "data_type": "varchar", "is_nullable": False},
                    {"name": "email_addr", "data_type": "varchar", "is_nullable": False},
                    {"name": "phone_num", "data_type": "varchar", "is_nullable": True},
                    {"name": "company_name", "data_type": "text", "is_nullable": True},
                    {"name": "signup_date", "data_type": "string", "is_nullable": False}
                ],
                "relationships": []
            },
            "destination_schema": {
                "table_name": "crm_contacts",
                "fields": [
                    {"name": "customer_id", "data_type": "integer", "is_primary_key": True, "is_required": True},
                    {"name": "first_name", "data_type": "string", "is_required": True},
                    {"name": "last_name", "data_type": "string", "is_required": True},
                    {"name": "email", "data_type": "string", "is_required": True},
                    {"name": "phone", "data_type": "string", "is_required": False},
                    {"name": "account_name", "data_type": "string", "is_required": False},
                    {"name": "created_at", "data_type": "datetime", "is_required": True}
                ],
                "relationships": []
            },
            "sample_rows": [
                {
                    "cust_id": 5001,
                    "fname": "Marcus",
                    "lname": "Brody",
                    "email_addr": "marcus@museum-edu.org",
                    "phone_num": "312-555-9011",
                    "company_name": "National Museum",
                    "signup_date": "2023-11-04"
                }
            ],
            "relationship_metadata": [],
            "known_mapping_hints": {}
        }
    },
    "relationship_mismatch": {
        "id": "relationship_mismatch",
        "name": "Scenario 3: Relationship Mismatch (Unresolvable Foreign Key)",
        "description": "Source provides flat unlinked leads with no account link. Destination enforces a mandatory foreign key account_id referencing crm_accounts.",
        "expected_behavior": "Flagged as REVIEW due to unresolvable mandatory relationship and missing source field (Rules 4 & 5).",
        "request": {
            "source_schema": {
                "table_name": "flat_web_leads",
                "fields": [
                    {"name": "lead_id", "data_type": "integer", "is_primary_key": True, "is_nullable": False},
                    {"name": "first_name", "data_type": "string", "is_nullable": False},
                    {"name": "last_name", "data_type": "string", "is_nullable": False},
                    {"name": "email", "data_type": "string", "is_nullable": False},
                    {"name": "company_raw", "data_type": "string", "is_nullable": True}
                ],
                "relationships": []
            },
            "destination_schema": {
                "table_name": "crm_contacts",
                "fields": [
                    {"name": "id", "data_type": "integer", "is_primary_key": True, "is_required": True},
                    {"name": "first_name", "data_type": "string", "is_required": True},
                    {"name": "last_name", "data_type": "string", "is_required": True},
                    {"name": "email", "data_type": "string", "is_required": True},
                    {
                        "name": "account_id",
                        "data_type": "integer",
                        "is_required": True,
                        "description": "Mandatory Foreign Key referencing crm_accounts.id"
                    }
                ],
                "relationships": [
                    {
                        "source_table": "crm_contacts",
                        "source_field": "account_id",
                        "target_table": "crm_accounts",
                        "target_field": "id",
                        "relationship_type": "many_to_one",
                        "is_required": True,
                        "description": "Each contact must be assigned to an existing CRM Account"
                    }
                ]
            },
            "sample_rows": [
                {
                    "lead_id": 901,
                    "first_name": "Diana",
                    "last_name": "Prince",
                    "email": "diana@themyscira.gov",
                    "company_raw": "Gateway Antiquities"
                }
            ],
            "relationship_metadata": [
                {
                    "source_table": "crm_contacts",
                    "source_field": "account_id",
                    "target_table": "crm_accounts",
                    "target_field": "id",
                    "relationship_type": "many_to_one",
                    "is_required": True,
                    "description": "Destination requires valid crm_accounts foreign key"
                }
            ],
            "known_mapping_hints": {}
        }
    }
}
