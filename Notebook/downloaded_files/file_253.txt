from ehrql import create_dataset, case, create_measures, when, years, months
from ehrql.tables.tpp import (
    patients,
    practice_registrations,
    clinical_events,
    medications,
)

from variables_library import (
    first_matching_event,
    last_matching_event
)

from codelists import (
    adhd_codelist,
    adhdrem_codelist,
    adhd_medication_codelist,
)

dataset = create_dataset()
dataset.configure_dummy_data(population_size=10000)

# Date range
start_date_point = "2016-04-01"
end_date_point = "2025-04-01"

# Population variables
has_registration = practice_registrations.exists_for_patient()
dataset.has_registration = has_registration

dataset.sex = patients.sex

dataset.date_of_birth = patients.date_of_birth

# Picking the first date for dia and first date for med
dataset.first_adhd_diagnosis_date = first_matching_event(
    clinical_events, adhd_codelist
).date

dataset.last_mph_med_date = (
    medications.where(True)
    .where(medications.dmd_code.is_in(adhd_medication_codelist))
    .where(medications.date.is_on_or_after(dataset.first_adhd_diagnosis_date))
    .sort_by(medications.date)
    .last_for_patient()
    .date
)

dataset.year_of_medication = (dataset.last_mph_med_date).year
dataset.month_of_medication = (dataset.last_mph_med_date).month

#Computing the age at the point of medication
dataset.age = patients.age_on(dataset.last_mph_med_date)

dataset.age_band = case(
    when((dataset.age >= 0) & (dataset.age <= 9)).then("0 to 9"),
    when((dataset.age >= 10) & (dataset.age <= 17)).then("10 to 17"),
    when((dataset.age >= 18) & (dataset.age <= 24)).then("18 to 24"),
    when((dataset.age >= 25) & (dataset.age <= 34)).then("25 to 34"),
    when(dataset.age >= 35).then("35 and over"),
    when(dataset.age.is_null()).then("Missing"),
)

# Computing the population records
dataset.define_population(
    dataset.has_registration
    & dataset.sex.is_in(["male", "female"])
    & (dataset.age <= 120)
    & dataset.first_adhd_diagnosis_date.is_not_null()
    & dataset.last_mph_med_date.is_not_null()
    & (dataset.last_mph_med_date >= dataset.first_adhd_diagnosis_date)
)
