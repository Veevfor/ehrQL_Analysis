from codelists import *
from ehrql import create_dataset
from ehrql.tables.tpp import patients, practice_registrations, clinical_events

dataset = create_dataset()

index_date = "2024-03-31"
has_registration = practice_registrations.for_patient_on(index_date).exists_for_patient()
'''
Extract the following columns:
1. age at achievement date
2. earliest diabetes resolved date
'''
dataset.age = patients.age_on(index_date)
prev_events = clinical_events.where(clinical_events.date.is_on_or_before(index_date))
dataset.dmlate_date = prev_events.where(clinical_events.snomedct_code.is_in(diabetes_codelist)).sort_by(clinical_events.date).last_for_patient().date
dataset.dmreso_date = prev_events.where(clinical_events.snomedct_code.is_in(diabetes_resolved_codelist)).sort_by(clinical_events.date).last_for_patient().date

'''
Filter each of the columns:
1. dmreso_date < dmlate_date or dmreso_date doesn't exist
2. age >= 17
'''
dataset.dm_reg_r1 = (
    ((dataset.dmlate_date > dataset.dmreso_date) | dataset.dmreso_date.is_null()) 
    & dataset.dmlate_date.is_not_null()
)
dataset.dm_reg_r2 = dataset.age >= 17

# Filter the dataset
dataset.define_population(has_registration & dataset.dm_reg_r1 & dataset.dm_reg_r2)
