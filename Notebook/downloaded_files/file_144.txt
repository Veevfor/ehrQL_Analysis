# This script extracts numeric, upper and lower bound values for testing if there are proxy null values
# Args: --codelist [codelist]

import argparse
from ehrql import codelist_from_csv
from ehrql.tables.core import patients
from ehrql.tables.tpp import (
    practice_registrations as registrations,
    clinical_events_ranges
)
from ehrql import create_dataset

dataset = create_dataset()
parser = argparse.ArgumentParser()
parser.add_argument("--codelist")
args = parser.parse_args()
start_date = "2018-01-01"
end_date = "2024-01-01"

# Codelists
# --------------------------------------------------------------------------------------

# Codelists
codelist = codelist_from_csv(args.codelist, column="code")

codelist_events = clinical_events_ranges.where(
    clinical_events_ranges.snomedct_code.is_in(codelist)
    & clinical_events_ranges.date.is_on_or_between(start_date, end_date)
)

# Extract numeric values for codelist
dataset.codelist_event_count = codelist_events.count_for_patient()
dataset.numeric_value = codelist_events.sort_by(codelist_events.date).first_for_patient().numeric_value
dataset.upper_bound = codelist_events.sort_by(codelist_events.date).first_for_patient().upper_bound
dataset.lower_bound = codelist_events.sort_by(codelist_events.date).first_for_patient().lower_bound

dataset.configure_dummy_data(population_size=1000)
dataset.define_population(patients.exists_for_patient())
