from ehrql import Dataset
from ehrql.tables.beta.tpp import patients, practice_registrations, addresses

dataset = Dataset()

index_date = "2020-03-31"

has_registration = practice_registrations.for_patient_on(
    index_date
).exists_for_patient()

dataset.in_care_home = addresses.for_patient_on(index_date).care_home_is_potential_match

dataset.define_population(has_registration)
