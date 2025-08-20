from pathlib import Path

from ehrql import create_dataset
from ehrql.codes import codelist_from_csv

from ehrql.tables.tpp import (
    clinical_events,
    patients,
    practice_registrations,
)

CODELIST_DIR = Path("codelists")

# Cluster name: DM_COD
# Description: Diabetes mellitus codes
# Refset ID: ^999004691000230108
dm_cod = codelist_from_csv(
    CODELIST_DIR / "nhsd-primary-care-domain-refsets-dm_cod.csv",
    column="code",
)

# Cluster name: DMRES_COD
# Description: Diabetes resolved codes
# Refset ID: ^999003371000230102
dm_res_cod = codelist_from_csv(
    CODELIST_DIR / "nhsd-primary-care-domain-refsets-dmres_cod.csv",
    column="code",
)


# Helper function for finding the last matching event
def last_matching_event(events, codelist, where=True):
    return (
        events.where(where)
        .where(events.snomedct_code.is_in(codelist))
        .sort_by(events.date)
        .last_for_patient()
    )


index_date = "2024-03-31"
dataset = create_dataset()

has_registration = practice_registrations.for_patient_on(
    index_date
).exists_for_patient()

# Extract prior events for further use in variable definitions below
prior_events = clinical_events.where(clinical_events.date.is_on_or_before(index_date))

# Field number: 4
# PAT_AGE: The age of the patient in full years at the achievement date.
dataset.pat_age = patients.age_on(index_date)

# Field number: 6
# DMLAT_DAT: Date of the most recent diabetes diagnosis up to and
# including the achievement date.
dataset.dmlat_dat = last_matching_event(prior_events, dm_cod).date

# Field number: 7
# DMRES_DAT: Date of the most recent diabetes diagnosis resolved code
# recorded after the most recent diabetes diagnosis and up to and
# including the achievement date.
dataset.dmres_dat = last_matching_event(prior_events, dm_res_cod).date

# DM_REG rule 1:
# Pass to the next rule all patients from the specified population who meet
# both of the criteria below:  Have a diabetes diagnosis in the patient record
# up to and including the achievement date. Latest diabetes diagnosis is not
# followed by a diabetes resolved code.
dataset.dm_reg_r1 = (dataset.dmres_dat < dataset.dmlat_dat) | (
    dataset.dmlat_dat.is_not_null() & dataset.dmres_dat.is_null()
)

# DM_REG rule 2:
# Reject patients passed to this rule who are aged under 17 years old on the
# achievement date.
dataset.dm_reg_r2 = dataset.pat_age < 17

dataset.define_population(has_registration & dataset.dm_reg_r1 & ~dataset.dm_reg_r2)
