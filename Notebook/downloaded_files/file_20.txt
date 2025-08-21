from ehrql import INTERVAL, create_measures, months
from ehrql.tables.tpp import clinical_events, patients, practice_registrations

measures = create_measures()
measures.configure_dummy_data(population_size=10000)

# Dictionary of pharmacy first codes
pharmacy_first_event_codes = {
    # Community Pharmacist (CP) Consultation Service for minor illness (procedure)
    "consultation_service": ["1577041000000109"],
    # Pharmacy First service (qualifier value)
    "pharmacy_first_service": ["983341000000102"],
}

registration = practice_registrations.for_patient_on(INTERVAL.end_date)

# Select clinical events
selected_events = clinical_events.where(
    clinical_events.date.is_on_or_between(INTERVAL.start_date, INTERVAL.end_date)
)

# Count pharmacy first codes
pharmacy_first_code_counts = {}

for code_desc, code in pharmacy_first_event_codes.items():
    count_codes_query = selected_events.where(
        selected_events.snomedct_code.is_in(code)
    ).count_for_patient()
    pharmacy_first_code_counts[f"count_{code_desc}"] = count_codes_query

# Define intervals and measures
intervals = months(18).starting_on("2023-02-01")

for measures_name, code_counts in pharmacy_first_code_counts.items():
    measures.define_measure(
        name=measures_name,
        numerator=code_counts,
        group_by={"practice_region": registration.practice_nuts1_region_name},
        denominator=patients.exists_for_patient(),
        intervals=intervals,
    )
