# Task: Calulcate the monthly prevalence trends for the dementia QOF

# 1) Import the required functions from ehrql
from ehrql import codelist_from_csv
from ehrql import INTERVAL, case, create_measures, months, when

# 2) Import the tables of interest from TPP
from ehrql.tables.tpp import (
    patients,
    practice_registrations,
    clinical_events,
    addresses,
)

# 3) Import the codelists of interest
DEM_COD = codelist_from_csv(
    "codelists/nhsd-primary-care-domain-refsets-dm_cod.csv",
    column="code",
)

# 4) Create series for numerator and denominator for each interval
## Numerator - number of people with diagnosis of dementia before the end of elegible period
selected_events = clinical_events.where(
    clinical_events.date.is_on_or_before(INTERVAL.end_date)
)

latest_dementia_date = (
    selected_events.where(selected_events.snomedct_code.is_in(DEM_COD))
    .sort_by(selected_events.date)
    .last_for_patient()
    .date
)

# Simpler version

latest_dementia_date_dementia = (
    clinical_events.where(
        (clinical_events.date.is_on_or_before(INTERVAL.end_date))
        & (clinical_events.snomedct_code.is_in(DEM_COD))
    )
    .sort_by(clinical_events.date)
    .last_for_patient()
    .date
)


## Denominator - number of people with practice registration before the beginning of the interval
## and with no deregsotration or with reregistration after the end of each interval
has_registration_date = (
    practice_registrations.where(
        practice_registrations.start_date.is_on_or_before(INTERVAL.start_date)
        & (
            practice_registrations.end_date.is_null()
            | practice_registrations.end_date.is_on_or_after(INTERVAL.end_date)
        )
    )
    .sort_by(practice_registrations.start_date)
    .first_for_patient()
    .start_date
)

# Simpler
has_registration_date = practice_registrations.spanning(
    INTERVAL.start_date, INTERVAL.end_date
).exists_for_patient()

# Create measures framework
measures = create_measures()

measures.define_measure(
    name="dem_reg",
    numerator=latest_dementia_date.is_not_null(),
    denominator=has_registration_date.is_not_null(),
    intervals=months(12).starting_on("2023-04-01"),
)

# The output is a dataframe of measure name, interval_start,
# interval_end, ratio, numerator, denominator.

# Analyse dementia rates by subrgoup (socio-economic status)


imd_rounded = addresses.for_patient_on(INTERVAL.start_date).imd_rounded
max_imd = 32844

imd_quintile = case(
    when(imd_rounded < int(max_imd * 1 / 5)).then(1),
    when(imd_rounded < int(max_imd * 2 / 5)).then(2),
    when(imd_rounded < int(max_imd * 3 / 5)).then(3),
    when(imd_rounded < int(max_imd * 4 / 5)).then(4),
    when(imd_rounded <= max_imd).then(5),
)

measures.define_measure(
    name="dem_qof_monthy_imd",
    numerator=latest_dementia_date.is_not_null(),
    denominator=has_registration_date,
    group_by={"imd": imd_quintile},
    intervals=months(12).starting_on("2023-04-01"),
)
