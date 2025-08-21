from ehrql import INTERVAL, create_measures, months, codelist_from_csv, case, when
from ehrql.tables.tpp import practice_registrations, clinical_events, patients

# Instantiate measures
measures = create_measures()

# Import codelists
dep_codelist = codelist_from_csv(
    "codelists/nhsd-primary-care-domain-refsets-depr_cod.csv",
    column="code",
)

depres_codelist = codelist_from_csv(
    "codelists/nhsd-primary-care-domain-refsets-depres_cod.csv",
    column="code",
)

# Important dates
# Quality Service Start Date
qs_start_date = "2023-04-01"

# Have their latest first or new episode of depression on or after 1 st April 2006
min_date = "2006-04-01"

# Inclusion criteria
has_registration = practice_registrations.spanning(
    INTERVAL.start_date, INTERVAL.end_date
).exists_for_patient()

# Create disease variables
# - depr_dat = Latest date of depression diagnosis
# - depres_dat = Latest depression resolved date
# - pat_age = Age at quality service start date
depr_dat = (
    (clinical_events.where(clinical_events.snomedct_code.is_in(dep_codelist)))
    .sort_by(clinical_events.date)
    .last_for_patient()
    .date
)
depres_dat = (
    clinical_events.where(clinical_events.snomedct_code.is_in(depres_codelist))
    .sort_by(clinical_events.date)
    .last_for_patient()
    .date
)
pat_age = patients.age_on(INTERVAL.start_date)


# Creating rules
dep1_reg_r1 = (depr_dat.is_on_or_after(min_date)) & (depres_dat.is_null())
dep1_reg_r2 = pat_age >= 18

# Define measures
dep_in_interval = depr_dat.is_during(INTERVAL)

# Stratification groups
age_band = case(
    when((pat_age >= 18) & (pat_age <= 21)).then("Young adult"),
    when((pat_age >= 22) & (pat_age <= 64)).then("Adult"),
    when(pat_age >= 65).then("Elderly"),
)

# Create measures
measures.define_measure(
    name="monthly_prevalence",
    numerator=dep_in_interval,
    denominator=has_registration & dep1_reg_r1 & dep1_reg_r2,
    intervals=months(12).starting_on(qs_start_date),
    group_by={
        "sex": patients.sex,
        "age": age_band,
    },
)
