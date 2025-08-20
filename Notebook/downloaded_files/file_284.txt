from datetime import date
from analysis.dataset_definition_pf_data_development import dataset

# Run the following command in the terminal to test the dataset definition dataset_definition_pf_data_development
# opensafely exec ehrql:v1 assure analysis/test_dataset_definition_pf_data_development.py
test_data = {
    # Expected in population
    # Testing `count_distinct_consultations_query`
    1: {
        "patients": {"date_of_birth": date(1950, 1, 1)},
        "clinical_events": [
            {
                # Community Pharmacy (CP) Blood Pressure (BP) Check Service
                # First before launch
                # This does not count as PF id or date
                "consultation_id": 1,
                "date": date(2024, 1, 1),
                "snomedct_code": "1659111000000107",
            },
            {
                # Pharmacy First service
                # First before launch
                "consultation_id": 2,
                "date": date(2024, 1, 1),
                "snomedct_code": "983341000000102",
            },
            {
                # Pharmacy First service
                # First after launch
                "consultation_id": 3,
                "date": date(2024, 2, 1),
                "snomedct_code": "983341000000102",
            },
            {
                # Community Pharmacist (CP) Consultation Service for minor illness
                # First after launch
                "consultation_id": 4,
                "date": date(2024, 2, 2),
                "snomedct_code": "1577041000000109",
            },
            {
                # Something else after PF launch
                # Counts as distinct id for 'post_all' selected events
                "consultation_id": 99,
                "date": date(2024, 2, 5),
                "snomedct_code": "999999999",
            },
        ],
        "expected_in_population": True,
        "expected_columns": {
            "pre_all_count_distinct_ids": 2,
            "pre_pfid_count_distinct_ids": 1,
            "pre_pfdate_count_distinct_ids": 2,
            "post_all_count_distinct_ids": 3,
            "post_pfid_count_distinct_ids": 2,
            "post_pfdate_count_distinct_ids": 2,
        },
    },
    # Expected in population
    # Testing `count_codes_query`
    2: {
        "patients": {"date_of_birth": date(1950, 1, 1)},
        "clinical_events": [
            {
                # Pharmacy First service
                # First before launch
                "consultation_id": 1,
                "date": date(2024, 1, 1),
                "snomedct_code": "983341000000102",
            },
            {
                # Pharmacy First service
                # First PF id and first PF date after launch
                "consultation_id": 2,
                "date": date(2024, 2, 2),
                "snomedct_code": "983341000000102",
            },
            {
                # Infected insect bite
                # Same consultation ID, same date
                "consultation_id": 2,
                "date": date(2024, 2, 2),
                "snomedct_code": "262550002",
            },
            {
                # Community Pharmacist (CP) Consultation Service for minor illness
                # Second PF id and second PF date after launch
                "consultation_id": 3,
                "date": date(2024, 2, 3),
                "snomedct_code": "1577041000000109",
            },
            {
                # Infected insect bite
                # Different consultation ID, same date
                "consultation_id": 4,
                "date": date(2024, 2, 3),
                "snomedct_code": "262550002",
            },
            {
                # Infected insect bite
                # Different consultation ID, different date
                "consultation_id": 4,
                "date": date(2024, 2, 4),
                "snomedct_code": "262550002",
            },
            {
                # Something else after PF launch
                # Should not impact any of the counts
                "consultation_id": 99,
                "date": date(2024, 2, 5),
                "snomedct_code": "999999999",
            },
        ],
        "expected_in_population": True,
        "expected_columns": {
            "pre_all_count_pf_events": 1,
            "pre_pfid_count_pf_events": 1,
            "pre_pfdate_count_pf_events": 1,
            "pre_all_count_pf_pathways": 0,
            "pre_pfid_count_pf_pathways": 0,
            "pre_pfdate_count_pf_pathways": 0,
            "post_all_count_pf_events": 2,
            "post_pfid_count_pf_events": 2,
            "post_pfdate_count_pf_events": 2,
            "post_all_count_pf_pathways": 2,
            "post_pfid_count_pf_pathways": 1,
            "post_pfdate_count_pf_pathways": 3,
        },
    },
}
