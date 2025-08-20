#################################################################
# This code extracts all people who had an outpatient visit
#################################################################


from ehrql import create_dataset, case, when, years, days, weeks, show
from ehrql.tables.tpp import patients, practice_registrations, clinical_events, opa

dataset = create_dataset()
dataset.configure_dummy_data(population_size=10000)


total_opa = opa.where(opa.appointment_date.is_on_or_between("2024-01-01","2024-12-31"))
total_opa_date = total_opa.appointment_date

attended_opa = opa.where(
    opa.appointment_date.is_on_or_between("2024-01-01","2024-12-31")
    & opa.attendance_status.is_in(["5","6"])
    )
attended_opa_date = attended_opa.appointment_date

rheum_opa = opa.where(
    opa.appointment_date.is_on_or_between("2024-01-01","2024-12-31")
    & opa.treatment_function_code.is_in(["410"])
)
rheum_opa_date = rheum_opa.appointment_date

rheum_attended_opa = opa.where(
    opa.appointment_date.is_on_or_between("2024-01-01","2024-12-31")
    & opa.attendance_status.is_in(["5","6"])
    & opa.treatment_function_code.is_in(["410"])
    )
rheum_attended_opa_date = rheum_attended_opa.appointment_date

dataset.count_same_day = total_opa_date.count_episodes_for_patient(days(0))
dataset.count_same_day_attended = attended_opa_date.count_episodes_for_patient(days(0))
dataset.count_same_day_rheum = rheum_opa_date.count_episodes_for_patient(days(0))
dataset.count_same_day_rheum_attended = rheum_attended_opa_date.count_episodes_for_patient(days(0))

dataset.count_all = total_opa.count_for_patient()
dataset.count_all_attended = attended_opa.count_for_patient()
dataset.count_rheum = rheum_opa.count_for_patient()
dataset.count_rheum_attended = rheum_attended_opa.count_for_patient()

first_opa = attended_opa.sort_by(
        opa.appointment_date
    ).first_for_patient()

first_rheum_opa = rheum_attended_opa.sort_by(
        opa.appointment_date
    ).first_for_patient()

first_pfu = attended_opa.where(
        attended_opa.outcome_of_attendance.is_in(["4","5"])   
    ).sort_by(
        attended_opa.appointment_date
    ).first_for_patient()

first_rheum_pfu = rheum_attended_opa.where(
        rheum_attended_opa.outcome_of_attendance.is_in(["4","5"])   
    ).sort_by(
        rheum_attended_opa.appointment_date
    ).first_for_patient()


dataset.any_opa = first_opa.exists_for_patient()
dataset.outcome_of_attendance = first_opa.outcome_of_attendance
dataset.treatment_function_code = first_opa.treatment_function_code  # specialty
dataset.attendance_status = first_opa.attendance_status
dataset.consultation_medium_used = first_opa.consultation_medium_used
dataset.first_attendance = first_opa.first_attendance
dataset.pfu = first_pfu.exists_for_patient()

dataset.rheum_any_opa = first_rheum_opa.exists_for_patient()
dataset.rheum_outcome_of_attendance = first_rheum_opa.outcome_of_attendance
dataset.rheum_treatment_function_code = first_rheum_opa.treatment_function_code  # specialty
dataset.rheum_attendance_status = first_rheum_opa.attendance_status
dataset.rheum_consultation_medium_used = first_rheum_opa.consultation_medium_used
dataset.rheum_first_attendance = first_rheum_opa.first_attendance
dataset.rheum_pfu = first_rheum_pfu.exists_for_patient()


dataset.rrr_date = first_opa.referral_request_received_date
dataset.rrr_year= dataset.rrr_date.year

dataset.rheum_rrr_date = first_rheum_opa.referral_request_received_date
dataset.rheum_rrr_year = dataset.rheum_rrr_date.year


###################################

# define population - everyone with an outpatient visit
dataset.define_population(
    (patients.age_on("2024-01-01") >= 18) 
    & (patients.age_on("2024-01-01") < 110) 
    & ((patients.sex == "male") | (patients.sex == "female"))
    & (patients.date_of_death.is_after("2024-01-01") | patients.date_of_death.is_null())
    & (practice_registrations.for_patient_on("2024-01-01").exists_for_patient())
    & attended_opa.exists_for_patient()
)