from ehrql import create_dataset
from ehrql.codes import codelist_from_csv

from ehrql.tables.tpp import (
    clinical_events,
    patients,
    practice_registrations,
)

dataset = create_dataset()
# Quality Service Start Date
qs_start_date = '2024-04-01' 
# Fixed date used in DEPR1_REG and DEPCC01 logic.
# Depression register: Patients aged at least 18 years old whose latest
# unresolved episode of depression is since 1 st April 2006.
min_date = '2006-04-01'

# import codelists
dep_codelist = codelist_from_csv(
    'codelists/nhsd-primary-care-domain-refsets-depr_cod.csv',
    column='code')
depres_codelist = codelist_from_csv(
    'codelists/nhsd-primary-care-domain-refsets-depres_cod.csv',
    column='code')

# inclusion criteria
has_registration = (practice_registrations
                    .for_patient_on(qs_start_date)
                    .exists_for_patient())

# Create disease variables
# - DEPR_DAT = Latest date of depression diagnosis
# - DEPRES_DAT = Latest depression resolved date
# - PAT_AGE = Age at quality service start date

dataset.depr_dat = ((clinical_events.
                    where(clinical_events
                          .snomedct_code
                          .is_in(dep_codelist))
                          ).sort_by(clinical_events.date)
                          .last_for_patient()
                          .date)
dataset.depres_dat = (clinical_events
                      .where(clinical_events
                             .snomedct_code
                             .is_in(depres_codelist))
                             .sort_by(clinical_events.date)
                             .last_for_patient()
                             .date)
dataset.pat_age = (patients
                   .age_on(qs_start_date))

# --- Creating rules ---
# Have their latest first or new episode of depression on or after 1 st April 2006.
# Latest episode of depression is not followed by a depression resolved code.
# Must be aged 18 or over on the achievement date

dep1_reg_r1 = ((dataset.depr_dat.is_on_or_after(min_date))
               & (dataset.depres_dat.is_null()))
dep2_reg_r2 = dataset.pat_age >= 18

dataset.define_population(has_registration & dep1_reg_r1 & dep2_reg_r2)
