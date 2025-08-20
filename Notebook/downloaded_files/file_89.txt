#################################################################
# This code extracts all people who had an outpatient visit
#################################################################


from ehrql import create_dataset, case, when, years, days, weeks, show
from ehrql.tables.tpp import patients, practice_registrations, clinical_events, opa

dataset = create_dataset()
dataset.configure_dummy_data(population_size=10000)


# all outpatient visits - to measure before / after start of personalised follow-up
all_opa = opa.where(
        opa.appointment_date.is_on_or_after("2018-06-01")
        & opa.attendance_status.is_in(["5","6"])
    )

from analysis.variable_functions import opa_characteristics

dataset = opa_characteristics(all_opa)


###################################
    
# By treatment specialty (only include most common groups reported in public statistics)
trt_func = ["100","101","110","120","130","140","150","160","170","300","301","320","330","340","400","410","430","502"]

count_var = {}

for code in trt_func:

    count_var["any_pfu_" + code] = all_opa.where(
        all_opa.treatment_function_code.is_in([code])
        & all_opa.outcome_of_attendance.is_in(["4","5"]) 
        & all_opa.appointment_date.is_on_or_after("2022-06-01")
    ).exists_for_patient()

    count_var["any_opa_" + code] = all_opa.where(
        all_opa.treatment_function_code.is_in([code])
        & all_opa.appointment_date.is_on_or_after("2022-06-01")
    ).exists_for_patient()

    dataset.add_column(f"any_pfu_{code}", count_var["any_pfu_" + code])
    dataset.add_column(f"any_opa_{code}", count_var["any_opa_" + code])


######################################

# define population - everyone with an outpatient visit
dataset.define_population(
    (dataset.age >= 18) 
    & (dataset.age < 110) 
    & ((dataset.sex == "male") | (dataset.sex == "female"))
    & (patients.date_of_death.is_after(dataset.first_opa_date) | patients.date_of_death.is_null())
    & (practice_registrations.for_patient_on(dataset.first_opa_date).exists_for_patient())
    & dataset.first_opa_date.is_not_null()
)
