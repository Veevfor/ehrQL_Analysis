from datetime import date
from dm_reg_dataset_milan import dataset

# Patient data for the FY23/24 with index date = "2024-03-31"
# Run the tests with the following command:
# opensafely exec ehrql:v1 assure analysis/test_dm_reg_dataset_milan.py

test_data = {
    # Correctly not expected in population
    # No clinical events
    1: {
        "patients": {"date_of_birth": date(1950, 1, 1)},
        "practice_registrations": [
            {
                "start_date": date(2010, 1, 1),
            },
        ],
        "clinical_events": [{}],
        "expected_in_population": False,
    },
    # Correctly not expected in population
    # Diagnosis after the index date
    2: {
        "patients": {"date_of_birth": date(1950, 1, 1)},
        "practice_registrations": [
            {
                "start_date": date(2010, 1, 1),
            },
        ],
        "clinical_events": [
            {
                # First diabetes diagnosis (DM_COD)
                "date": date(2024, 8, 1),
                "snomedct_code": "73211009",
            },
        ],
        "expected_in_population": False,
    },
    # Correctly not expected in population
    # Younger than 17yo at index date
    3: {
        "patients": {"date_of_birth": date(2010, 1, 1)},
        "practice_registrations": [
            {
                "start_date": date(2010, 1, 1),
            },
        ],
        "clinical_events": [
            {
                # First diabetes diagnosis (DM_COD)
                "date": date(2022, 8, 1),
                "snomedct_code": "73211009",
            },
        ],
        "expected_in_population": False,
    },
    # Correctly not expected in population
    # Not registered at index date
    4: {
        "patients": {"date_of_birth": date(1960, 1, 1)},
        "practice_registrations": [
            {
                "start_date": date(1960, 1, 1),
                "end_date": date(2020, 1, 1),
            },
        ],
        "clinical_events": [
            {
                # First diabetes diagnosis (DM_COD)
                "date": date(2022, 8, 1),
                "snomedct_code": "73211009",
            },
        ],
        "expected_in_population": False,
    },
    # Correctly not expected in population
    # Diabetes diagnosis resolved before index date
    5: {
        "patients": {"date_of_birth": date(1960, 1, 1)},
        "practice_registrations": [
            {
                "start_date": date(1960, 1, 1),
            },
        ],
        "clinical_events": [
            {
                # First diabetes diagnosis (DM_COD)
                "date": date(2000, 6, 1),
                "snomedct_code": "73211009",
            },
            {
                # Diabetes diagnosis resolved (DMRES_COD)
                "date": date(2023, 1, 1),
                "snomedct_code": "315051004",
            },
        ],
        "expected_in_population": False,
    },
    # Correctly expected in population
    # Diabetes diagnosis resolved before index date
    6: {
        "patients": {"date_of_birth": date(1960, 1, 1)},
        "practice_registrations": [
            {
                "start_date": date(1960, 1, 1),
            },
        ],
        "clinical_events": [
            {
                # First diabetes diagnosis (DM_COD)
                "date": date(2000, 6, 1),
                "snomedct_code": "73211009",
            },
        ],
        "expected_in_population": True,
        "expected_columns": {
            "pat_age": 64,
            "dmlat_dat": date(2000, 6, 1),
            "dmres_dat": None,
            "dm_reg_r1": True,
            "dm_reg_r2": False,
        },
    },
    # Correctly not expected in population
    # Code not form DM_COD codelist
    7: {
        "patients": {"date_of_birth": date(1960, 1, 1)},
        "practice_registrations": [
            {
                "start_date": date(1960, 1, 1),
            },
        ],
        "clinical_events": [
            {
                # Code not in the codelist
                "date": date(2000, 6, 1),
                "snomedct_code": "1111111111",
            },
        ],
        "expected_in_population": False,
    },
}
