# This script creates a dataset file version of the measures file
# for testing purposes

import argparse
from ehrql import codelist_from_csv
from ehrql.tables.core import patients
from ehrql.tables.tpp import (
    clinical_events_ranges as ranges,
)
from ehrql import create_dataset

dataset = create_dataset()
parser = argparse.ArgumentParser()
parser.add_argument("--codelist")
args = parser.parse_args()
start_date = "2020-03-31"
end_date = "2021-03-31"

# Codelists
# --------------------------------------------------------------------------------------

# Codelists
codelist = codelist_from_csv(args.codelist, column="code")
codelist_events = ranges.where(
    ranges.snomedct_code.is_in(codelist)
    & ranges.date.is_on_or_between(start_date, end_date)
)

# Presence of codelist (denominator)
codelist_event_count = codelist_events.count_for_patient()

# Booleans
has_test_value = ((ranges.numeric_value.is_not_null()) & (ranges.numeric_value != 0))
#has_equality_comparator = ranges.comparator.is_in(["=", "~"])
#has_differential_comparator = ranges.comparator.is_not_null() & ~has_equality_comparator
#has_upper_bound = ranges.upper_bound.is_not_null()
#has_lower_bound = ranges.lower_bound.is_not_null()

dataset.has_test_value = codelist_events.where(has_test_value).count_for_patient()
dataset.define_population(patients.exists_for_patient())

