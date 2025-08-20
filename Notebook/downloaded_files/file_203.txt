#def_funs
from ehrql.tables.tpp import ( 
    patients,
    addresses,
    apcs,
    clinical_events,
    medications,
    practice_registrations,
    ons_deaths,
   )

from ehrql import (
    days,
    months,
    years,
    create_dataset,
)


#from ehrql.tables.raw.tpp import (
# from ehrql.tables.raw.tpp import (
#     covid_therapeutics_raw,
#     isaric,
# )
index_startdate = "2021-12-16"  
index_enddate = "2022-02-10"

is_fem_male = patients.sex.is_in(["female", "male"])

is_alive = (
    patients.date_of_death.is_after(index_startdate)
    | patients.date_of_death.is_null()
)

index_startdate = "2021-12-16"  
index_enddate = "2022-02-10"

# is_registered = practice_registrations.spanning (  
#     index_startdate, index_enddate
# ).exists_for_patient()

# def get_registration_status(index_startdate):
#     return practice_registration_as_of(index_startdate).exists_for_patient() 


bmi_record = (
    clinical_events.where(
        clinical_events.snomedct_code.is_in(["60621009", "846931000000101"])
        # Ignore out-of-range values
        & (clinical_events.numeric_value > 4)
        & (clinical_events.numeric_value < 200)
        & (clinical_events.date >= patients.date_of_birth + years(16))
    )
    .sort_by(clinical_events.date)
    .last_for_patient()
)

def first_covid_therap_date(pre_df,covid_drug,start_date="2021-12-16",end_date="2022-02-10"):
    covid_treat=(
        pre_df
        .where(pre_df.intervention.is_in([covid_drug]) )
        .sort_by(pre_df.treatment_start_date)
    )
#Approved, Treatment Complete, Treatment Not Started, Treatment Stopped
    first_covid_therap = covid_treat.where(
    (covid_treat.treatment_start_date>=start_date) & 
    (covid_treat.treatment_start_date<=end_date) &
    (covid_treat.current_status.is_in(["Approved", "Treatment Complete"]))
    ).first_for_patient()

    return(
        first_covid_therap
        )

import operator
from functools import reduce

def any_of(conditions):
    return reduce(operator.or_, conditions)

# query if causes of death match a given codelist
def cause_of_death_matches(codelist):
    conditions = [
        getattr(ons_deaths, column_name).is_in(codelist)
        for column_name in (["underlying_cause_of_death"]+[f"cause_of_death_{i:02d}" for i in range(1, 16)])
    ]

    return any_of(conditions) 

