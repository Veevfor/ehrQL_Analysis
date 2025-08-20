from ehrql import create_dataset
from ehrql.tables.tpp import (
    patients,
    practice_registrations,
    clinical_events,
    medications,
)

from variables_library import first_matching_event

from codelists import (
    adhd_codelist,
    adhd_medication_codelist,
)

dataset = create_dataset()
dataset.configure_dummy_data(population_size=100000)

# Date range
start_date = "2016-04-01"
end_date = "2024-03-31"

# Population variables
has_registration = practice_registrations.spanning(
    start_date, end_date
).exists_for_patient()
dataset.sex = patients.sex
dataset.age = patients.age_on(end_date)

# Filtering with the codelists
has_adhd_event = clinical_events.where(
    clinical_events.snomedct_code.is_in(adhd_codelist)
).exists_for_patient()

# Picking the last date for dia and first date for med
dataset.first_adhd_diagnosis_date = first_matching_event(
    clinical_events, adhd_codelist
).date

# Number of counts for ADHD diagonsis and readmission
dataset.count_adhd_diagnoses = clinical_events.where(
    clinical_events.snomedct_code.is_in(adhd_codelist)
).count_for_patient()

dataset.count_adhd_resolved = clinical_events.where(
    clinical_events.snomedct_code.is_in(adhd_codelist)
).count_for_patient()

dataset.first_mph_med_date = (
    medications.where(True)
    .where(medications.dmd_code.is_in(adhd_medication_codelist))
    .where(medications.date.is_on_or_after(dataset.first_adhd_diagnosis_date))
    .sort_by(medications.date)
    .first_for_patient()
    .date
)

# Compute the date gap
dataset.times_between_dia_med_weeks = (
    dataset.first_mph_med_date - dataset.first_adhd_diagnosis_date
).weeks

# Computing the population records
dataset.define_population(
    has_registration
    & dataset.sex.is_in(["male", "female"])
    & (dataset.age <= 120)
    & patients.is_alive_on(end_date)
    & dataset.first_adhd_diagnosis_date.is_not_null()
    & dataset.first_mph_med_date.is_not_null()
)
