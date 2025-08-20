from datetime import date
from analysis.dataset_definition_med_status_data_development import dataset

# Run the following command in the terminal to test the dataset definition dataset_definition_med_status_data_development
# opensafely exec ehrql:v1 assure analysis/test_dataset_definition_med_status_data_development.py
test_data = {
    # Expected in population (pre-launch patient with PF ID and PF MED)
    1: {
        "patients": {"date_of_birth": date(1950, 1, 1)},
        "clinical_events": [
            {
                # Community Pharmacy (CP) Blood Pressure (BP) Check Service
                # Before launch
                "consultation_id": 1,
                "date": date(2024, 1, 1),
                "snomedct_code": "1659111000000107",
            },
        ],
        "medications_raw": [
            {
                # Before Pharmacy first launch
                "consultation_id": 1,
                "date": date(2024, 1, 2),
                "dmd_code": "20129711000001103",
                "medication_status": 3,
            },
        ],
        "expected_in_population": True,
        "expected_columns": {
            "pre_any_status3": 1,
            "post_any_status3": 0,
            "pre_pfmed_status3": 1,
            "pre_pfmedid_status3": 1,
            "pre_any_pfid_status3": 1,
            "pre_date_pfid_status3": 0,
        },
    },
    # Expected in population (post-launch patient with PF ID and PF MED)
    2: {
        "patients": {"date_of_birth": date(1950, 1, 1)},
        "clinical_events": [
            {
                # Community Pharmacy (CP) Blood Pressure (BP) Check Service
                # Before launch
                "consultation_id": 1,
                "date": date(2024, 4, 1),
                "snomedct_code": "1659111000000107",
            },
        ],
        "medications_raw": [
            {
                # Before Pharmacy first launch
                "consultation_id": 1,
                "date": date(2024, 4, 2),
                "dmd_code": "20129711000001103",
                "medication_status": 3,
            },
        ],
        "expected_in_population": True,
        "expected_columns": {
            "pre_any_status3": 0,
            "post_any_status3": 1,
            "pre_pfmed_status3": 0,
            "post_pfmed_status3": 1,
            "pre_pfmedid_status3": 0,
            "post_pfmedid_status3": 1,
            "pre_any_pfid_status3": 0,
            "post_any_pfid_status3": 1,
            "pre_date_pfid_status3": 0,
            "post_date_pfid_status3": 0,
        },
    },
    # Expected in population (post-launch patient with no PF ID but has PF MED)
    3: {
        "patients": {"date_of_birth": date(1950, 1, 1)},
        "clinical_events": [
            {
                # Not a Pharmacy First Consultation
                # Before launch
                "consultation_id": 1,
                "date": date(2024, 4, 1),
                "snomedct_code": "Non-PF Consultation",
            },
        ],
        "medications_raw": [
            {
                # Pharmacy First Medication
                "consultation_id": 1,
                "date": date(2024, 4, 2),
                "dmd_code": "20129711000001103",
                "medication_status": 3,
            },
        ],
        "expected_in_population": True,
        "expected_columns": {
            "pre_any_status3": 0,
            "post_any_status3": 1,
            "pre_pfmed_status3": 0,
            "post_pfmed_status3": 1,
            "pre_pfmedid_status3": 0,
            "post_pfmedid_status3": 0,
            "pre_any_pfid_status3": 0,
            "post_any_pfid_status3": 0,
            "pre_date_pfid_status3": 0,
            "post_date_pfid_status3": 0,
        },
    },
    # Expected in population (post-launch patient with PF ID but with same-day prescribed non-PF MED)
    4: {
        "patients": {"date_of_birth": date(1950, 1, 1)},
        "clinical_events": [
            {
                # Community Pharmacy (CP) Blood Pressure (BP) Check Service
                # Post launch
                "consultation_id": 1,
                "date": date(2024, 4, 1),
                "snomedct_code": "1659111000000107",
            },
        ],
        "medications_raw": [
            {
                # Pharmacy First Medication
                "consultation_id": 1,
                "date": date(2024, 4, 1),
                "dmd_code": "Non-PF Medication",
                "medication_status": 3,
            },
        ],
        "expected_in_population": True,
        "expected_columns": {
            "pre_any_status3": 0,
            "post_any_status3": 1,
            "pre_pfmed_status3": 0,
            "post_pfmed_status3": 0,
            "pre_pfmedid_status3": 0,
            "post_pfmedid_status3": 0,
            "pre_any_pfid_status3": 0,
            "post_any_pfid_status3": 1,
            "pre_date_pfid_status3": 0,
            "post_date_pfid_status3": 1,
        },
    },
}
