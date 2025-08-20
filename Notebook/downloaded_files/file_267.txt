from ehrql import codelist_from_csv
from ehrql import create_dataset
from ehrql.tables.tpp import (
    clinical_events, 
    patients,
    practice_registrations,
)

# Hypertension codes
hyp_cod = codelist_from_csv(
    "codelists/nhsd-primary-care-domain-refsets-hyp_cod.csv",
    column="code"
)
# Hypertension resolved codes
hypres_cod = codelist_from_csv(
    "codelists/nhsd-primary-care-domain-refsets-hypres_cod.csv",
    column="code"
)

index_date = "2024-03-31"
dataset = create_dataset()

### variables ###

# date of the most recent hypertension diagnosis up to and including the achievement date
dataset.hyplat_dat = (
    clinical_events.where(clinical_events.snomedct_code.is_in(hyp_cod) & clinical_events.date.is_on_or_before(index_date))
    .sort_by(clinical_events.date)
    .last_for_patient()
    .date
)

# date of the most recent hypertension diagnosis resolved code recorded after the most recent hypertension diagnosis and up to and including the achievement date
dataset.hypres_dat = (
    clinical_events.where(clinical_events.snomedct_code.is_in(hypres_cod) & clinical_events.date.is_on_or_before(index_date))
    .sort_by(clinical_events.date)
    .last_for_patient()
    .date
)


### rules ###

# Pass to the next rule all patients from the specified population who meet both of the criteria below:
# Have a hypertension diagnosis in the patient record up to and including the achievement date.
# Latest hypertension diagnosis is not followed by a hypertension resolved code.
dataset.hyp_reg_r1 = dataset.hyplat_dat.is_not_null() & dataset.hypres_dat.is_null() | (dataset.hyplat_dat > dataset.hypres_dat)

### defining population ###
has_registration = practice_registrations.for_patient_on(index_date).exists_for_patient()
dataset.define_population(
    (has_registration) & dataset.hyp_reg_r1
    )
