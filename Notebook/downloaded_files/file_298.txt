#################################################################
# This code extracts monthly counts of people on personalised
#   folloup pathways, stratified by relevant characteristics
#################################################################


from ehrql import months, INTERVAL, Measures
from ehrql.tables.tpp import (
    patients, 
    practice_registrations,
    opa)


# OPA checks
check_opa = opa.where(
        opa.appointment_date.is_on_or_between(INTERVAL.start_date, INTERVAL.end_date)
    ).sort_by(
        opa.appointment_date
    ).exists_for_patient()

#consult_medium = check_opa.consultation_medium_used
#attendance_status = check_opa.attendance_status
#first_attendance = check_opa.first_attendance


# For study
# All OP visits that were attended
all_opa = opa.where(
        opa.appointment_date.is_on_or_between(INTERVAL.start_date, INTERVAL.end_date)
        & opa.attendance_status.is_in(["5","6"])
    )

# All PIFU visits that were attended
all_pfu = opa.where(
        opa.appointment_date.is_on_or_between(INTERVAL.start_date, INTERVAL.end_date)
        & opa.attendance_status.is_in(["5","6"])
        & opa.outcome_of_attendance.is_in(["4","5"])
    )

# Any outpatient visit - total and personalised 
any_opa = all_opa.exists_for_patient()
any_pfu = all_pfu.exists_for_patient()


# Number of outpatient visits - total and personalised
count_opa = all_opa.opa_ident.count_distinct_for_patient()
count_pfu = all_pfu.opa_ident.count_distinct_for_patient()


# By treatment specialty (only include most common groups reported in public statistics)
trt_func = ["100","101","110","120","130","140","150","160","170","300","301","320","330","340","400","410","430","502"]

count_var = {}

for code in trt_func:

    count_var["any_opa_" + code] = all_opa.where(
        all_opa.treatment_function_code.is_in([code])
    ).exists_for_patient()

    count_var["any_pfu_" + code] = all_pfu.where(
        all_pfu.treatment_function_code.is_in([code])
    ).exists_for_patient()

    count_var["count_opa_" + code] = all_opa.where(
        all_opa.treatment_function_code.is_in([code])
    ).opa_ident.count_distinct_for_patient()
    
    count_var["count_pfu_" + code] = all_pfu.where(
        all_pfu.treatment_function_code.is_in([code])
    ).opa_ident.count_distinct_for_patient()


# Region
first_opa = all_opa.sort_by(
        all_opa.appointment_date
    ).first_for_patient()
region = practice_registrations.for_patient_on(first_opa.appointment_date).practice_nuts1_region_name


### Measures setup
measures = Measures()
measures.configure_disclosure_control(enabled=False)
measures.configure_dummy_data(population_size=1000)

denominator = (
        (patients.age_on(INTERVAL.start_date) >= 18) 
        & (patients.age_on(INTERVAL.start_date) < 110)
        & ((patients.sex == "male") | (patients.sex == "female"))
        & (patients.date_of_death.is_after(INTERVAL.start_date) | patients.date_of_death.is_null())
        & (practice_registrations.for_patient_on(INTERVAL.start_date).exists_for_patient())
    )

measures.define_defaults(
    intervals=months(48).starting_on("2022-01-01")
    )

########################

# Total outpatient visits
measures.define_measure(
    name="total_opa",
    numerator=check_opa,
    denominator=denominator,
    )

##################


# Number of people with an outpatient visit
measures.define_measure(
    name="count_opa",
    numerator=count_opa,
    denominator=denominator,
    )

measures.define_measure(
    name="patients_opa",
    numerator=any_opa,
    denominator=denominator,
    )

# Number of people with a personalised follow-up visit
measures.define_measure(
    name="count_pfu",
    numerator=count_pfu,
    denominator=denominator & any_opa,
    )

measures.define_measure(
    name="patients_pfu",
    numerator=any_pfu,
    denominator=denominator & any_opa,
    )

measures.define_measure(
    name="count_region_opa",
    numerator=count_opa,
    group_by={"region": region},
    denominator=denominator,
    )

measures.define_measure(
    name="count_region_pfu",
    numerator=count_pfu,
    group_by={"region": region},
    denominator=denominator & any_opa,
    )

measures.define_measure(
    name="patients_region_opa",
    numerator=any_opa,
    group_by={"region": region},
    denominator=denominator,
    )

measures.define_measure(
    name="patients_region_pfu",
    numerator=any_pfu,
    group_by={"region": region},
    denominator=denominator & any_opa,
    )


###########################################

for code in trt_func:
    measures.define_measure(
        name=f"any_opa_{code}",
        numerator=count_var["any_opa_" + code],
        denominator = denominator,
    )
    measures.define_measure(
        name=f"any_pfu_{code}",
        numerator=count_var["any_pfu_" + code],
        denominator = denominator & any_opa,
    )
    measures.define_measure(
        name=f"count_opa_{code}",
        numerator=count_var["count_opa_" + code],
        denominator = denominator,
    )
    measures.define_measure(
        name=f"count_pfu_{code}",
        numerator=count_var["count_pfu_" + code],
        denominator = denominator & any_opa,
    )
