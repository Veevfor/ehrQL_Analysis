import argparse
from ehrql import INTERVAL, Measures, codelist_from_csv, years
from ehrql.tables.tpp import clinical_events_ranges as ranges, clinical_events
from ehrql.tables.tpp import practice_registrations as registrations

parser = argparse.ArgumentParser()
parser.add_argument("--codelist")
parser.add_argument("--measure", type=str)
args = parser.parse_args()
index_date = "2018-01-01"

# Codelists
codelist = codelist_from_csv(args.codelist, column="code")
# Filter to codelist events during interval
codelist_events = ranges.where(
    ranges.snomedct_code.is_in(codelist) & ranges.date.is_during(INTERVAL)
)

# Stratification variables
region = registrations.for_patient_on(INTERVAL.start_date).practice_nuts1_region_name

# Presence of codelist (denominator)
codelist_event_count = codelist_events.count_for_patient()

# Booleans testing for presence of each field in clinical_events_ranges
if args.measure == "has_test_value":
    # Dont consider null and 0's as completed tests
    query = (clinical_events.numeric_value.is_not_null()) & (
        clinical_events.numeric_value != 0
    )
    # Use clinical_events instead of clinical_events_ranges for codelist_events
    codelist_events = clinical_events.where(
        clinical_events.snomedct_code.is_in(codelist)
        & clinical_events.date.is_during(INTERVAL)
    )
elif args.measure == "has_equality_comparator":
    query = ranges.comparator.is_in(["=", "~"])
elif args.measure == "has_differential_comparator":
    query = ranges.comparator.is_in([">=", ">", "<", "<="])
elif args.measure == "has_lower_bound":
    query = (ranges.lower_bound.is_not_null()) & (ranges.lower_bound > 0)
elif args.measure == "has_upper_bound":
    query = (ranges.upper_bound.is_not_null()) & (ranges.upper_bound > 0)

# Create filtered table query
count = codelist_events.where(query).count_for_patient()

# Measures
# --------------------------------------------------------------------------------------
measures = Measures()
measures.configure_dummy_data(population_size=1000, legacy=False)
measures.define_defaults(
    denominator=codelist_event_count,
    intervals=years(7).starting_on(index_date),
    group_by={"region": region},
)

measures.define_measure(
    name=args.measure,
    numerator=count,
)
