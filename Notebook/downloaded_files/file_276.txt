from ehrql import Dataset, years, days, months, minimum_of, maximum_of, case, when
from ehrql.tables.core import patients, clinical_events
from ehrql.tables.tpp import practice_registrations, ons_deaths, opa, opa_proc, apcs

import codelists

index_date = "2020-01-21"
end_date = "2023-10-22"

dataset = Dataset()

lowerGI_2ww_ref = clinical_events.where(clinical_events.snomedct_code.is_in(codelists.colorectal_referral_codes)
            ).where(
                clinical_events.date.is_on_or_between(index_date, end_date)
            ).sort_by(
                clinical_events.date
            ).first_for_patient()

has_lowerGI_2ww = lowerGI_2ww_ref.exists_for_patient()

region = practice_registrations.for_patient_on(index_date).practice_nuts1_region_name 
region_east = case(
        when(region == "East").then(True),
        otherwise=False
)

dataset.define_population(
    has_lowerGI_2ww & region_east
)

dataset.lowerGI_2ww_date = lowerGI_2ww_ref.date

first_attendance_code = ["1", "3"]
colorectal_surg_clinic_code = ["104"]
gastro_clinic_code = ["301"]
gen_surg_clinic_code = ["100"]
#opcs_colonoscopy_code = ["H22", "H18", "H25", "H28"]

"""
colorectal_surg_clinic_21days = (
    opa.where(opa.treatment_function_code.is_in(colorectal_surg_clinic_code)
        ).where(
            opa.appointment_date.is_on_or_between(dataset.lowerGI_2ww_date, dataset.lowerGI_2ww_date + days(21))          
        ).where(
            opa.first_attendance.is_in(first_attendance_code)
        ).sort_by(
            opa.appointment_date
        ).first_for_patient()
)
"""

colorectal_surg_clinic_6weeks = (
    opa.where(opa.treatment_function_code.is_in(colorectal_surg_clinic_code)
        ).where(
            opa.appointment_date.is_on_or_between(dataset.lowerGI_2ww_date, dataset.lowerGI_2ww_date + days(42))          
        ).where(
            opa.first_attendance.is_in(first_attendance_code)
        ).sort_by(
            opa.appointment_date
        ).first_for_patient()
)

#dataset.colorectal_surg_clinic_21d = colorectal_surg_clinic_21days.exists_for_patient()
dataset.colorectal_surg_clinic_6w = colorectal_surg_clinic_6weeks.exists_for_patient()

"""
gastro_clinic_21days = (
    opa.where(opa.treatment_function_code.is_in(gastro_clinic_code)
        ).where(
            opa.appointment_date.is_on_or_between(dataset.lowerGI_2ww_date, dataset.lowerGI_2ww_date + days(21))          
        ).where(
            opa.first_attendance.is_in(first_attendance_code)
        ).sort_by(
            opa.appointment_date
        ).first_for_patient()
)
"""

gastro_clinic_6weeks = (
    opa.where(opa.treatment_function_code.is_in(gastro_clinic_code)
        ).where(
            opa.appointment_date.is_on_or_between(dataset.lowerGI_2ww_date, dataset.lowerGI_2ww_date + days(42))          
        ).where(
            opa.first_attendance.is_in(first_attendance_code)
        ).sort_by(
            opa.appointment_date
        ).first_for_patient()
)

#dataset.gastro_clinic_21d = gastro_clinic_21days.exists_for_patient()
dataset.gastro_clinic_6w = gastro_clinic_6weeks.exists_for_patient()

gen_surg_clinic_6weeks = (
    opa.where(opa.treatment_function_code.is_in(gen_surg_clinic_code)
        ).where(
            opa.appointment_date.is_on_or_between(dataset.lowerGI_2ww_date, dataset.lowerGI_2ww_date + days(42))          
        ).where(
            opa.first_attendance.is_in(first_attendance_code)
        ).sort_by(
            opa.appointment_date
        ).first_for_patient()
)

dataset.gen_surg_clinic_6w = gen_surg_clinic_6weeks.exists_for_patient()

"""
colonoscopy_21days = (
    opa_proc.where(opa_proc.primary_procedure_code.is_in(colonoscopy_code)
        ).where(
            opa_proc.appointment_date.is_on_or_between(dataset.lowerGI_2ww_date, dataset.lowerGI_2ww_date + days(21))
        ).sort_by(
            opa_proc.appointment_date
        ).first_for_patient()
)

opa_colonoscopy_6weeks = (
    opa_proc.where(opa_proc.primary_procedure_code.is_in(opcs_colonoscopy_code)
        ).where(
            opa_proc.appointment_date.is_on_or_between(dataset.lowerGI_2ww_date, dataset.lowerGI_2ww_date + days(42))
        ).sort_by(
            opa_proc.appointment_date
        ).first_for_patient()
)

dataset.colonoscopy_21d = colonoscopy_21days.exists_for_patient()
dataset.opa_colonoscopy_6w = opa_colonoscopy_6weeks.exists_for_patient()
"""
apcs_diagnostic_6weeks = (
    apcs.where(apcs.spell_core_hrg_sus.is_in(codelists.lowerGI_diagnostic_codes)
        ).where(
            apcs.admission_date.is_on_or_between(dataset.lowerGI_2ww_date, dataset.lowerGI_2ww_date + days(42))
        ).sort_by(
            apcs.admission_date
        ).first_for_patient()
)

dataset.apcs_diagnostic_6w = apcs_diagnostic_6weeks.exists_for_patient()

opa_diagnostic_6weeks = (
    opa.where(opa.hrg_code.is_in(codelists.lowerGI_diagnostic_codes)
        ).where(
            opa.appointment_date.is_on_or_between(dataset.lowerGI_2ww_date, dataset.lowerGI_2ww_date + days(42))
        ).sort_by(
            opa.appointment_date
        ).first_for_patient()
)

dataset.opa_diagnostic_6w = opa_diagnostic_6weeks.exists_for_patient()

dataset.lowergi_diagnostic_6w = (dataset.apcs_diagnostic_6w | dataset.opa_diagnostic_6w)

dataset.lowergi_referral_6w = (dataset.lowergi_diagnostic_6w | dataset.colorectal_surg_clinic_6w | dataset.gastro_clinic_6w | dataset.gen_surg_clinic_6w)


opa_1month = (
    opa.where(opa.appointment_date.is_on_or_between(dataset.lowerGI_2ww_date, dataset.lowerGI_2ww_date + months(1))
        ).where(
            opa.first_attendance.is_in(first_attendance_code)
        ).sort_by(
            opa.appointment_date
        ).first_for_patient()
)

dataset.opa_1m_tfc = opa_1month.treatment_function_code

"""
proc_1month = (
    opa_proc.where(opa_proc.appointment_date.is_on_or_between(dataset.lowerGI_2ww_date, dataset.lowerGI_2ww_date + months(1))
        ).sort_by(
            opa_proc.appointment_date
        ).first_for_patient()
)

dataset.proc_1m_opcs = proc_1month.primary_procedure_code
"""

apcs_6weeks = (
    apcs.where(apcs.admission_date.is_on_or_between(dataset.lowerGI_2ww_date, dataset.lowerGI_2ww_date + days(42))
        ).sort_by(
            apcs.admission_date
        ).first_for_patient()
)

dataset.apcs_6w_icd10 = apcs_6weeks.primary_diagnosis
dataset.apcs_6w_hrg = apcs_6weeks.spell_core_hrg_sus

gp_events_1month = (
    clinical_events.where(clinical_events.date.is_on_or_between(dataset.lowerGI_2ww_date + days(1), dataset.lowerGI_2ww_date + months(1))
        ).sort_by(
            clinical_events.date
        ).first_for_patient()
)

dataset.gp_events_snomed = gp_events_1month.snomedct_code