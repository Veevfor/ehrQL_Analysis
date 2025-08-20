########################################################################################################
##<dadaset_definition.py> for repo: <prophy_effects_Sotro_Molnup>
##Description: This script extracts data for project 91:[Coverage, effectiveness and safety 
##of neutralising monoclonal antibodies or antivirals for non-hospitalised patients with COVID-19]
##Author(s): Qing Wen   Date last updated: 28/06/2024
########################################################################################################
from ehrql import(
    months,
    days,
    case,
    create_dataset,
    when,
    minimum_of,
)
from ehrql.tables.tpp import( 
    addresses,
    clinical_events,
    apcs,
    medications,
    patients,
    practice_registrations,
    ons_deaths,
    vaccinations,
    ethnicity_from_sus,
    covid_therapeutics,
)

# from ehrql.tables.raw.tpp import(
#     covid_therapeutics_raw,
# )

from ehrql.codes import *
#from ehrql.codes import CTV3Code, ICD10Code

## codelists #ethnicity_codelist,ethnicity
from codelists import( covid_icd10_codes, dialysis_codes,dialysis_icd10_codelist,
    dialysis_opcs4_codelist, kidney_transplant_codes, kidney_tx_icd10_codelist, kidney_tx_opcs4_codelist, solid_organ_transplant_codes,
    solid_organ_transplant_nhsd_snomed_codes, solid_organ_transplant_nhsd_snomed_codes_new, dialysis_opcs4_codelist,
    haematopoietic_stem_cell_transplant_nhsd_snomed_codes, haematopoietic_stem_cell_transplant_nhsd_icd10_codes, 
    haematological_malignancies_nhsd_snomed_codes, haematological_malignancies_nhsd_icd10_codes, sickle_cell_disease_nhsd_snomed_codes, 
    sickle_cell_disease_nhsd_icd10_codes, immunosupression_nhsd_codes, immunosupression_nhsd_codes_new, 
    immunosuppresant_drugs_dmd_codes, immunosuppresant_drugs_snomed_codes, oral_steroid_drugs_dmd_codes, 
    oral_steroid_drugs_snomed_codes, solid_organ_transplant_nhsd_opcs4_codes, replacement_of_organ_transplant_nhsd_opcs4_codes,
    thymus_gland_transplant_nhsd_opcs4_codes, conjunctiva_y_codes_transplant_nhsd_opcs4_codes, conjunctiva_transplant_nhsd_opcs4_codes, 
    stomach_transplant_nhsd_opcs4_codes, ileum_1_y_codes_transplant_nhsd_opcs4_codes, ileum_2_y_codes_transplant_nhsd_opcs4_codes,
    ileum_1_transplant_nhsd_opcs4_codes, ileum_2_transplant_nhsd_opcs4_codes, haematopoietic_stem_cell_transplant_nhsd_opcs4_codes, 
    haematopoietic_stem_cell_transplant_nhsd_opcs4_codes, pregnancy_primis_codes,pregdel_primis_codes, 
    non_haematological_cancer_opensafely_snomed_codes, non_haematological_cancer_opensafely_snomed_codes_new, 
    lung_cancer_opensafely_snomed_codes, chemotherapy_radiotherapy_opensafely_snomed_codes, care_home_primis_snomed_codes,
    ethnicity_codelist_with_categories,diabetes_codes,hypertension_codes,chronic_cardiac_dis_codes,chronic_respiratory_dis_codes,
    autism_nhsd_snomed_codes,wider_ld_primis_snomed_codes,serious_mental_illness_nhsd_snomed_codes, dementia_nhsd_snomed_codes,
    housebound_opensafely_snomed_codes,no_longer_housebound_opensafely_snomed_codes)

## def_funs files
from def_funs import(is_fem_male, bmi_record, first_covid_therap_date, cause_of_death_matches, any_of) 

index_startdate = "2021-12-16"  
index_enddate = "2022-02-10"

dataset = create_dataset()
dataset.configure_dummy_data(population_size = 3000)

##covid_therapeutics
had_covid_treat_df0 = (
    covid_therapeutics.where(covid_therapeutics.covid_indication.is_in(["non_hospitalised"])) \
    .where(covid_therapeutics.intervention.is_in(["Molnupiravir","Sotrovimab","Paxlovid" ,"Remdesivir","Casirivimab and imdevimab"]) & \
    (covid_therapeutics.current_status.is_in(["Approved", "Treatment Complete"]))) \
    .sort_by(covid_therapeutics.treatment_start_date) \
)

had_covid_m_s_treat_df = (
    had_covid_treat_df0
    .where(had_covid_treat_df0.intervention.is_in(["Molnupiravir","Sotrovimab"]) & \
        (had_covid_treat_df0.treatment_start_date>= index_startdate) &  \
        (had_covid_treat_df0.treatment_start_date<= index_enddate) \
    ).sort_by(had_covid_treat_df0.treatment_start_date).first_for_patient() \
)

had_first_covid_treat = had_covid_m_s_treat_df.exists_for_patient()
dataset.treat_date = had_covid_m_s_treat_df.treatment_start_date # first_covid_treat_date
dataset.had_first_covid_treat = had_first_covid_treat
dataset.first_covid_treat_interve= had_covid_m_s_treat_df.intervention
dataset.first_covid_treat_status= had_covid_m_s_treat_df.current_status
dataset.drug = case(
    when(dataset.first_covid_treat_interve.is_in(["Sotrovimab"])).then(1), otherwise = 0
)

#end_date_6mon, start_date_60d
dataset.end_date_6mon = dataset.treat_date + days(60) + months(6)
dataset.start_date_60d = dataset.treat_date + days(60)
treat_date = dataset.treat_date  
dataset.end_date_12mon = dataset.treat_date + days(60) + months(12)
dataset.end_date_24mon = dataset.treat_date + days(60) + months(24)
#dataset.treat_date = dataset.first_covid_treat_date 
dataset.if_old_covid_treat = (
    had_covid_treat_df0
    .sort_by(had_covid_treat_df0.treatment_start_date)
    .where(had_covid_treat_df0.treatment_start_date.is_before(treat_date))).exists_for_patient()

dataset.old_covid_treat = case(
    when(dataset.if_old_covid_treat).then(1), otherwise = 0
)

was_registered_treated = (
    practice_registrations.where(practice_registrations.start_date <= treat_date)
    .except_where(practice_registrations.end_date <= treat_date)
    .exists_for_patient()
)

is_adult = (patients.age_on(index_startdate) >= 18) & (
    patients.age_on(index_startdate) <= 110
)

is_alive = (
    patients.date_of_death.is_after(index_startdate)
    | patients.date_of_death.is_null()
)

dataset.define_population(
    is_fem_male
    & is_adult
    & is_alive
    & had_first_covid_treat
    & was_registered_treated
)

##covid_therapeutics
non_hospital_df = (  # #.where(covid_therapeutics.diagnosis.is_in(["Covid-19"]))
    covid_therapeutics.where(covid_therapeutics.covid_indication.is_in(["non_hospitalised"])) 
    .sort_by(covid_therapeutics.treatment_start_date) #current_status
)

first_molnupiravir = first_covid_therap_date(pre_df = non_hospital_df, covid_drug = "Molnupiravir")
dataset.first_molnupiravir_date = first_molnupiravir.treatment_start_date
dataset.first_molnupiravir_status = first_molnupiravir.current_status  
dataset.first_molnupiravir_interve= first_molnupiravir.intervention
#dataset.first_molnupiravir_diag = first_molnupiravir.diagnosis

first_sotrovimab = first_covid_therap_date(pre_df = non_hospital_df,covid_drug = "Sotrovimab")
dataset.first_sotrovimab_date = first_sotrovimab.treatment_start_date
dataset.first_sotrovimab_status = first_sotrovimab.current_status
dataset.first_sotrovimab_interve= first_sotrovimab.intervention

##main outcome variables-Any causes -hospital admission per primary_diagnosis
dataset.date_of_first_admis_af_treat = (
    apcs.where(apcs.admission_date.is_after(treat_date))
    .sort_by(apcs.admission_date).first_for_patient().admission_date
)
##############################################
def had_hosp_covid_pdiag_1stdate_df(enddate1, startdate1 =treat_date, where=True):
    return(
        apcs.where((apcs.primary_diagnosis.is_in(covid_icd10_codes)) &    #primary_diagnosis
        (apcs.admission_date.is_after(startdate1)) &
        (apcs.admission_date.is_on_or_before(enddate1)) & 
        (apcs.patient_classification.is_in(["1"])))   
    ).sort_by(apcs.admission_date).first_for_patient()


##covid_hospitalisation as per primary_diagnosis -OUTCOME
hosp_bf30d_covid_pdiag_1stdate_df = had_hosp_covid_pdiag_1stdate_df(enddate1= treat_date + days(30))
hosp_bf60d_covid_pdiag_1stdate_df = had_hosp_covid_pdiag_1stdate_df(enddate1= treat_date + days(60))  
#hosp_af60d_covid_pdiag_1stdate_df ##hosp_bf30d_covid_pdiag_1stdate_df ##hosp_bf60d_covid_pdiag_1stdate_df
hosp_af60d_covid_pdiag_1stdate_df = (  
    apcs.where((apcs.primary_diagnosis.is_in(covid_icd10_codes)) &    #primary_diagnosis
        (apcs.admission_date.is_after(treat_date + days(60))) &
        (apcs.admission_date.is_on_or_before(treat_date + days(60) + months(6))) & #  apcs.snomedct_code.is_in(covid_icd10_codes)
        (apcs.patient_classification.is_in(["1"]))   ## ordinary admissions only - exclude day cases and regular attenders
    ).sort_by(apcs.admission_date).first_for_patient()
)

hosp_60d_12m_covid_pdiag_1stdate_df = (  
    apcs.where((apcs.primary_diagnosis.is_in(covid_icd10_codes)) &    #primary_diagnosis
        (apcs.admission_date.is_after(treat_date + days(60))) &
        (apcs.admission_date.is_on_or_before(treat_date + days(60) + months(12))) & #  apcs.snomedct_code.is_in(covid_icd10_codes)
        (apcs.patient_classification.is_in(["1"]))   ## ordinary admissions only - exclude day cases and regular attenders
    ).sort_by(apcs.admission_date).first_for_patient()
)

hosp_60d_24m_covid_pdiag_1stdate_df = (  
    apcs.where((apcs.primary_diagnosis.is_in(covid_icd10_codes)) &    #primary_diagnosis
        (apcs.admission_date.is_after(treat_date + days(60))) &
        (apcs.admission_date.is_on_or_before(treat_date + days(60) + months(24))) & #  apcs.snomedct_code.is_in(covid_icd10_codes)
        (apcs.patient_classification.is_in(["1"]))   ## ordinary admissions only - exclude day cases and regular attenders
    ).sort_by(apcs.admission_date).first_for_patient()
)

def had_ccare_covid_pdiag_df(df, where=True): 
    return(
    df.admission_method.is_in(["21", "22", "23", "24", "25", "2A", "2B", "2C", "2D", "28"]) & \
    (df.days_in_critical_care>0))
###
##critical_care     
# ##added
ccare_bf30d_covid_pdiag = had_ccare_covid_pdiag_df(hosp_bf30d_covid_pdiag_1stdate_df)
ccare_bf60d_covid_pdiag = had_ccare_covid_pdiag_df(hosp_bf60d_covid_pdiag_1stdate_df)
#                
ccare_af60d_covid_pdiag = (
    hosp_af60d_covid_pdiag_1stdate_df.admission_method.is_in(["21", "22", "23", "24", "25", "2A", "2B", "2C", "2D", "28"]) & \
    (hosp_af60d_covid_pdiag_1stdate_df.days_in_critical_care>0))

ccare_60d_12m_covid_pdiag = (
    hosp_60d_12m_covid_pdiag_1stdate_df.admission_method.is_in(["21", "22", "23", "24", "25", "2A", "2B", "2C", "2D", "28"]) & \
    (hosp_60d_12m_covid_pdiag_1stdate_df.days_in_critical_care>0))

ccare_60d_24m_covid_pdiag = (
    hosp_60d_24m_covid_pdiag_1stdate_df.admission_method.is_in(["21", "22", "23", "24", "25", "2A", "2B", "2C", "2D", "28"]) & \
    (hosp_60d_24m_covid_pdiag_1stdate_df.days_in_critical_care>0))

######hosp_af60d_covid_pdiag_1stdate_df ##hosp_bf30d_covid_pdiag_1stdate_df ##hosp_bf60d_covid_pdiag_1stdate_df
##covid_hospitalisation as per primary_diagnosis (added)
dataset.hosp_covid_bf30d_date = hosp_bf30d_covid_pdiag_1stdate_df.admission_date #hosp_bf30d_covid_pdiag_1stdate_df
dataset.hosp_covid_bf30d_classfic = hosp_bf30d_covid_pdiag_1stdate_df.patient_classification #covid_pdiag_classfic
dataset.hosp_covid_bf30d_pdiag = hosp_bf30d_covid_pdiag_1stdate_df.primary_diagnosis #covid_pdiag
dataset.had_ccare_covid_bf30d = ccare_bf30d_covid_pdiag #had_ccare_covid_af60d_6mon_pdiag_date
##hosp_covid_bf30d_date,hosp_covid_bf30d_classfic,hosp_covid_bf30d_pdiag,had_ccare_covid_bf30d
##hosp_covid_bf60d_date,hosp_covid_bf60d_classfic,hosp_covid_bf60d_pdiag,had_ccare_covid_bf60d

#hosp_covid60d6m_date#had_ccare_covid60d6m#had_ccare_covid60d12m#had_ccare_covid60d24m
dataset.hosp_covid_bf60d_date = hosp_bf60d_covid_pdiag_1stdate_df.admission_date #hosp_bf60d_covid_pdiag_1stdate_df
dataset.hosp_covid_bf60d_classfic = hosp_bf60d_covid_pdiag_1stdate_df.patient_classification #covid_pdiag_classfic
dataset.hosp_covid_bf60d_pdiag = hosp_bf60d_covid_pdiag_1stdate_df.primary_diagnosis #covid_pdiag
dataset.had_ccare_covid_bf60d = ccare_bf60d_covid_pdiag #had_ccare_covid_af60d_6mon_pdiag_date


##covid_hospitalisation as per primary_diagnosis
dataset.hosp_covid60d6m_date = hosp_af60d_covid_pdiag_1stdate_df.admission_date #hosp_af60d_covid_pdiag_1stdate_df
dataset.hosp_covid60d6m_classfic = hosp_af60d_covid_pdiag_1stdate_df.patient_classification #hosp_af60d_covid_pdiag_classfic
dataset.hosp_covid60d6m_pdiag = hosp_af60d_covid_pdiag_1stdate_df.primary_diagnosis #hosp_af60d_covid_pdiag
dataset.had_ccare_covid60d6m = ccare_af60d_covid_pdiag #had_ccare_covid_af60d_6mon_pdiag_date

dataset.hosp_covid60d12m_date = hosp_60d_12m_covid_pdiag_1stdate_df.admission_date #
dataset.hosp_covid60d12m_classfic = hosp_60d_12m_covid_pdiag_1stdate_df.patient_classification #
dataset.hosp_covid60d12m_pdiag =hosp_60d_12m_covid_pdiag_1stdate_df.primary_diagnosis #
dataset.had_ccare_covid60d12m = ccare_60d_12m_covid_pdiag #

#hosp_covid60d12m_date,hosp_covid60d24m_date
dataset.hosp_covid60d24m_date = hosp_60d_24m_covid_pdiag_1stdate_df.admission_date #
dataset.hosp_covid60d24m_classfic = hosp_60d_24m_covid_pdiag_1stdate_df.patient_classification #
dataset.hosp_covid60d24m_pdiag =hosp_60d_24m_covid_pdiag_1stdate_df.primary_diagnosis #
dataset.had_ccare_covid60d24m = ccare_60d_24m_covid_pdiag #

##covid_critical_care-date
##ccare_covid_date =ccare_covid60d6m_date
dataset.ccare_covid60d6m_date = (  #primary_diagnosis
    apcs.where((apcs.primary_diagnosis.is_in(covid_icd10_codes)) &     
        (apcs.admission_date.is_after(treat_date + days(60))) & 
        (apcs.admission_date.is_on_or_before(treat_date + days(60) + months(6))) &   #  apcs.snomedct_code.is_in(covid_icd10_codes)
        (apcs.patient_classification.is_in(["1"])) & \
        (apcs.admission_method.is_in(["21", "22", "23", "24", "25", "2A", "2B", "2C", "2D", "28"])) & \
        (apcs.days_in_critical_care>0)).sort_by(apcs.admission_date).first_for_patient()).admission_date

##allcause_hospitalisation
hosp_allcause_af60d_6mon_df = ( 
    apcs.where(
    (apcs.admission_date.is_after(treat_date + days(60))) &
    (apcs.admission_date.is_on_or_before (treat_date + days(60) + months(6))) &
    (apcs.patient_classification.is_in(["1"]))
    ).sort_by(apcs.admission_date).first_for_patient()
) 

hosp_allcause_af60d_12mon_df = ( 
    apcs.where(
    (apcs.admission_date.is_after(treat_date + days(60))) &
    (apcs.admission_date.is_on_or_before (treat_date + days(60) + months(12))) &
    (apcs.patient_classification.is_in(["1"]))
    ).sort_by(apcs.admission_date).first_for_patient()
) 

hosp_allcause_af60d_24mon_df  = ( 
    apcs.where(
    (apcs.admission_date.is_after(treat_date + days(60))) &
    (apcs.admission_date.is_on_or_before (treat_date + days(60) + months(24))) &
    (apcs.patient_classification.is_in(["1"]))
    ).sort_by(apcs.admission_date).first_for_patient()
)

dataset.hosp_allcause60d6m_date = hosp_allcause_af60d_6mon_df.admission_date #hosp_allcause_af60d_6mon_pdiag_date
dataset.hosp_allcause60d6m_classfic = hosp_allcause_af60d_6mon_df.patient_classification
dataset.hosp_allcause60d6m_pdiag = hosp_allcause_af60d_6mon_df.primary_diagnosis
hosp_covid60d6m_date = dataset.hosp_covid60d6m_date #first hospitalise after 60days
hosp_allcause60d6m_date = dataset.hosp_allcause60d6m_date 

dataset.hosp_allcause60d12m_date = hosp_allcause_af60d_12mon_df.admission_date #hosp_allcause_af60d_6mon_pdiag_date
dataset.hosp_allcause60d12m_classfic = hosp_allcause_af60d_12mon_df.patient_classification
dataset.hosp_allcause60d12m_pdiag = hosp_allcause_af60d_12mon_df.primary_diagnosis
hosp_covid60d12m_date = dataset.hosp_covid60d12m_date #first hospitalise after 60days
hosp_allcause60d12m_date = dataset.hosp_allcause60d12m_date 

dataset.hosp_allcause60d24m_date = hosp_allcause_af60d_24mon_df.admission_date #hosp_allcause_af60d_6mon_pdiag_date
dataset.hosp_allcause60d24m_classfic = hosp_allcause_af60d_24mon_df.patient_classification
dataset.hosp_allcause60d24m_pdiag = hosp_allcause_af60d_24mon_df.primary_diagnosis
hosp_covid60d24m_date = dataset.hosp_covid60d24m_date #first hospitalise after 60days
hosp_allcause60d24m_date = dataset.hosp_allcause60d24m_date 

dataset.hospitalise_disc_covid = ( #covid_first discharge after 60days
    apcs.where(apcs.discharge_date.is_on_or_before(hosp_covid60d6m_date)
    ).sort_by(apcs.discharge_date).first_for_patient()).discharge_date

dataset.hospitalise_disc_allcause = (      #allcause-first discharge after 60days
    apcs.where(apcs.discharge_date.is_on_or_before(hosp_allcause60d6m_date)
    ).sort_by(apcs.discharge_date).first_for_patient()).discharge_date

##Death_date##
dataset.ons_dead_date = ons_deaths.date
dataset.underly_deathcause_code = ons_deaths.underlying_cause_of_death
dataset.death_cause_covid = cause_of_death_matches(covid_icd10_codes) #underlying or causes

##all-cause death 60d-6m #ons_dead_tr60d_6mon_covid_treat
dataset.was_allcause_death_60d_6m = (ons_deaths.date.is_after(treat_date + days(60)) & 
    ons_deaths.date.is_on_or_before(treat_date + days(60) + months(6)) 
)

#was_allcause_death_60d_6m, allcause_death_60d_6m(0,1) ,was_covid_death_60d_6m ,covid_death_60d_6m (0,1) 
dataset.allcause_death_60d_6m = case(
    when(dataset.was_allcause_death_60d_6m).then(1), otherwise = 0
)

##all-cause death 60d-12m #ons_dead_tr60d_12mon_covid_treat
dataset.was_allcause_death_60d_12m = (ons_deaths.date.is_after(treat_date + days(60)) & 
    ons_deaths.date.is_on_or_before(treat_date + days(60) + months(12)) 
)

#was_allcause_death_60d_12m, allcause_death_60d_12m(0,1) ,was_covid_death_60d_12m ,covid_death_60d_12m (0,1) 
dataset.allcause_death_60d_12m = case(
    when(dataset.was_allcause_death_60d_12m).then(1), otherwise = 0
)

##all-cause death 60d-24m #ons_dead_tr60d_24mon_covid_treat
dataset.was_allcause_death_60d_24m = (ons_deaths.date.is_after(treat_date + days(60)) & 
    ons_deaths.date.is_on_or_before(treat_date + days(60) + months(24)) 
)

#was_allcause_death_60d_12m, allcause_death_60d_12m(0,1) ,was_covid_death_60d_12m ,covid_death_60d_12m (0,1) 
dataset.allcause_death_60d_24m = case(
    when(dataset.was_allcause_death_60d_24m).then(1), otherwise = 0
)

#covid-death 60d-6m #ons_dead_tr60d_6mon_covid_treat2
dataset.was_covid_death_60d_6m = (ons_deaths.date.is_after(treat_date + days(60)) & 
    ons_deaths.date.is_on_or_before(treat_date + days(60) + months(6)) & (dataset.death_cause_covid)
)

dataset.covid_death_60d_6m = case(
    when(dataset.was_covid_death_60d_6m).then(1), otherwise = 0
)
###
#covid-death 60d-12m #ons_dead_tr60d_12mon_covid_treat2
dataset.was_covid_death_60d_12m = (ons_deaths.date.is_after(treat_date + days(60)) & 
    ons_deaths.date.is_on_or_before(treat_date + days(60) + months(12)) & (dataset.death_cause_covid)
)

dataset.covid_death_60d_12m = case(
    when(dataset.was_covid_death_60d_12m).then(1), otherwise = 0
)
###
#covid-death 60d-24m #ons_dead_tr60d_24mon_covid_treat2
dataset.was_covid_death_60d_24m = (ons_deaths.date.is_after(treat_date + days(60)) & 
    ons_deaths.date.is_on_or_before(treat_date + days(60) + months(24)) & (dataset.death_cause_covid)
)

dataset.covid_death_60d_24m = case(
    when(dataset.was_covid_death_60d_24m).then(1), otherwise = 0
)
###
#all-cause death <60d #ons_dead_trstart_60d_covid_treat
dataset.was_allcause_death_under60d = (ons_deaths.date.is_after(treat_date) & 
    ons_deaths.date.is_on_or_before(treat_date + days(60)))

dataset.allcause_death_under60d = case(
    when(dataset.was_allcause_death_under60d).then(1), otherwise = 0
)

#all-cause death <30d #ons_dead_trstart_30d_covid_treat
dataset.was_allcause_death_under30d = (ons_deaths.date.is_after(treat_date) & 
    ons_deaths.date.is_on_or_before(treat_date + days(30))) 

dataset.allcause_death_under30d = case(
    when(dataset.was_allcause_death_under30d).then(1), otherwise = 0
)
#####
#####
##censored
def had_covid_treat_excpt_drug_df(drug, enddate1, startdate1 =treat_date, where=True):
    return(
    had_covid_treat_df0
    .except_where(had_covid_treat_df0.intervention.is_in([drug])) \
    .where((had_covid_treat_df0.treatment_start_date > startdate1) &  \
    (had_covid_treat_df0.treatment_start_date <= enddate1))  \
    ).sort_by(had_covid_treat_df0.treatment_start_date)


had_covid_treat6m_excpt_molnu_df = had_covid_treat_excpt_drug_df(drug ="Molnupiravir", enddate1 =(treat_date + days(60) + months(6)))
had_covid_treat6m_excpt_sotro_df = had_covid_treat_excpt_drug_df(drug ="Sotrovimab", enddate1 =(treat_date + days(60) + months(6)))

had_covid_treat12m_excpt_molnu_df = had_covid_treat_excpt_drug_df(drug ="Molnupiravir", enddate1 =(treat_date + days(60) + months(12)))
had_covid_treat12m_excpt_sotro_df = had_covid_treat_excpt_drug_df(drug ="Sotrovimab", enddate1 =(treat_date + days(60) + months(12)))

had_covid_treat24m_excpt_molnu_df = had_covid_treat_excpt_drug_df(drug ="Molnupiravir", enddate1 =(treat_date + days(60) + months(24)))
had_covid_treat24m_excpt_sotro_df = had_covid_treat_excpt_drug_df(drug ="Sotrovimab", enddate1 =(treat_date + days(60) + months(24)))


##6month##
dataset.molnu_pt6m_censored_date = had_covid_treat6m_excpt_molnu_df.first_for_patient().treatment_start_date ##potential
dataset.sotro_pt6m_censored_date = had_covid_treat6m_excpt_sotro_df.first_for_patient().treatment_start_date
dataset.molnu_pt6m_censored_drug =had_covid_treat6m_excpt_molnu_df.first_for_patient().intervention
dataset.sotro_pt6m_censored_drug =had_covid_treat6m_excpt_sotro_df.first_for_patient().intervention
dataset.molnu_pt6m_censored_exist =had_covid_treat6m_excpt_molnu_df.exists_for_patient() 
dataset.sotro_pt6m_censored_exist =had_covid_treat6m_excpt_sotro_df.exists_for_patient() 
dataset.is_molnu_pt6m_censored =  ((dataset.molnu_pt6m_censored_exist ) & (dataset.first_covid_treat_interve.is_in(["Molnupiravir"])))
dataset.is_sotro_pt6m_censored =  ((dataset.sotro_pt6m_censored_exist ) & (dataset.first_covid_treat_interve.is_in(["Sotrovimab"])))

dataset.molnu_pt6m_censored = case(
    when(dataset.is_molnu_pt6m_censored).then(1), otherwise = 0
)

dataset.sotro_pt6m_censored = case(
    when(dataset.is_sotro_pt6m_censored).then(1), otherwise = 0
)
##12month##
dataset.molnu_pt12m_censored_date = had_covid_treat12m_excpt_molnu_df.first_for_patient().treatment_start_date ##potential
dataset.sotro_pt12m_censored_date = had_covid_treat12m_excpt_sotro_df.first_for_patient().treatment_start_date
dataset.molnu_pt12m_censored_drug =had_covid_treat12m_excpt_molnu_df.first_for_patient().intervention
dataset.sotro_pt12m_censored_drug =had_covid_treat12m_excpt_sotro_df.first_for_patient().intervention
dataset.molnu_pt12m_censored_exist =had_covid_treat12m_excpt_molnu_df.exists_for_patient() 
dataset.sotro_pt12m_censored_exist =had_covid_treat12m_excpt_sotro_df.exists_for_patient() 
dataset.is_molnu_pt12m_censored =  ((dataset.molnu_pt12m_censored_exist ) & (dataset.first_covid_treat_interve.is_in(["Molnupiravir"])))
dataset.is_sotro_pt12m_censored =  ((dataset.sotro_pt12m_censored_exist ) & (dataset.first_covid_treat_interve.is_in(["Sotrovimab"])))

dataset.molnu_pt12m_censored = case(
    when(dataset.is_molnu_pt12m_censored).then(1), otherwise = 0
)

dataset.sotro_pt12m_censored = case(
    when(dataset.is_sotro_pt12m_censored).then(1), otherwise = 0
)

#is_molnu_pt6m_censored, is_sotro_pt6m_censored, molnu_pt6m_censored, sotro_pt6m_censored, molnu_pt6m_censored_date, sotro_pt6m_censored_date,
#is_molnu_pt12m_censored, is_sotro_pt12m_censored, molnu_pt12m_censored, sotro_pt12m_censored, molnu_pt12m_censored_date, sotro_pt12m_censored_date,
#is_molnu_pt24m_censored, is_sotro_pt24m_censored, molnu_pt24m_censored, sotro_pt24m_censored, molnu_pt24m_censored_date, sotro_pt24m_censored_date,
    
############################
##24month##
dataset.molnu_pt24m_censored_date = had_covid_treat24m_excpt_molnu_df.first_for_patient().treatment_start_date ##potential
dataset.sotro_pt24m_censored_date = had_covid_treat24m_excpt_sotro_df.first_for_patient().treatment_start_date
dataset.molnu_pt24m_censored_drug =had_covid_treat24m_excpt_molnu_df.first_for_patient().intervention
dataset.sotro_pt24m_censored_drug =had_covid_treat24m_excpt_sotro_df.first_for_patient().intervention
dataset.molnu_pt24m_censored_exist =had_covid_treat24m_excpt_molnu_df.exists_for_patient() 
dataset.sotro_pt24m_censored_exist =had_covid_treat24m_excpt_sotro_df.exists_for_patient() 
dataset.is_molnu_pt24m_censored =  ((dataset.molnu_pt24m_censored_exist ) & (dataset.first_covid_treat_interve.is_in(["Molnupiravir"])))
dataset.is_sotro_pt24m_censored =  ((dataset.sotro_pt24m_censored_exist ) & (dataset.first_covid_treat_interve.is_in(["Sotrovimab"])))

dataset.molnu_pt24m_censored = case(
    when(dataset.is_molnu_pt24m_censored).then(1), otherwise = 0
)

dataset.sotro_pt24m_censored = case(
    when(dataset.is_sotro_pt24m_censored).then(1), otherwise = 0
)

####### comorbidities ####### 
#tpp-clinical_events, apcs.admission_date,tpp-medications
c_events = clinical_events  #tpp-clinical_events
c_events_bf_treat = c_events.where(c_events.date.is_on_or_before(treat_date))
c_events_bf6m = c_events.where(c_events.date.is_on_or_between(treat_date - months(6),treat_date))
c_events_bf12m = c_events.where(c_events.date.is_on_or_between(treat_date - months(12),treat_date))
c_events_bf24m = c_events.where(c_events.date.is_on_or_between(treat_date - months(24),treat_date))

apcs_diags_bf_treat = apcs.where(apcs.admission_date.is_on_or_before(treat_date))
apcs_diags_bf12m = apcs.where(apcs.admission_date.is_on_or_between(treat_date - months(12), treat_date))
apcs_diags_bf24m = apcs.where(apcs.admission_date.is_on_or_between(treat_date - months(24),treat_date))

pcmeds_bf_treat = medications.where(medications.date.is_on_or_before(treat_date)) #prescribed medications in primary care.
pcmeds_bf_3m = medications.where(medications.date.is_on_or_between(treat_date - months(3),treat_date)) 
pcmeds_bf_6m = medications.where(medications.date.is_on_or_between(treat_date - months(6),treat_date))
pcmeds_bf_12m = medications.where(medications.date.is_on_or_between(treat_date - months(12),treat_date))

def had_meds_lastdate(codelist1,codelist2,dt = pcmeds_bf_treat, where=True):
    return(
    dt.where(where)
    .where(dt.dmd_code.is_in(codelist1)|dt.dmd_code.is_in(codelist2))
    .sort_by(dt.date).last_for_patient().date
)

def had_meds_count(codelist1,codelist2,dt=pcmeds_bf_treat, where=True):
    return(
    dt.where(where)
    .where(dt.dmd_code.is_in(codelist1)|dt.dmd_code.is_in(codelist2))
    .count_for_patient()
)

#Immune-mediated inflammatory disorders (IMID)
dataset.immunosuppresant_drugs_nhsd = had_meds_lastdate (codelist1 = immunosuppresant_drugs_dmd_codes, 
    codelist2= immunosuppresant_drugs_snomed_codes, dt = pcmeds_bf_6m 
)

dataset.oral_steroid_drug_nhsd_3m_count = had_meds_count (codelist1 = oral_steroid_drugs_dmd_codes, 
    codelist2=oral_steroid_drugs_snomed_codes, dt = pcmeds_bf_3m
)  #replace oral_steroid_drugs_nhsd=. if oral_steroid_drug_nhsd_3m_count < 2 & oral_steroid_drug_nhsd_12m_count < 4

dataset.oral_steroid_drug_nhsd_12m_count = had_meds_count (codelist1 = oral_steroid_drugs_dmd_codes, 
    codelist2=oral_steroid_drugs_snomed_codes, dt = pcmeds_bf_12m
)

dataset.oral_steroid_drugs_nhsd = had_meds_lastdate (codelist1 = oral_steroid_drugs_dmd_codes, 
    codelist2= oral_steroid_drugs_snomed_codes, dt = pcmeds_bf_12m)
#.where((dataset.oral_steroid_drug_nhsd_3m_count >= 2) & (dataset.oral_steroid_drug_nhsd_12m_count >= 4))

dataset.oral_steroid_drugs_nhsd_check = ((dataset.oral_steroid_drugs_nhsd <=treat_date) & (dataset.oral_steroid_drug_nhsd_3m_count >= 2) & (dataset.oral_steroid_drug_nhsd_12m_count >= 4))
dataset.immunosuppresant_drugs_nhsd_ever = had_meds_lastdate (codelist1 = immunosuppresant_drugs_dmd_codes,
    codelist2=immunosuppresant_drugs_snomed_codes, dt = pcmeds_bf_treat
)

dataset.oral_steroid_drugs_nhsd_ever = had_meds_lastdate(codelist1 = oral_steroid_drugs_dmd_codes, 
    codelist2=oral_steroid_drugs_snomed_codes, dt = pcmeds_bf_treat
)
###minimum_of(
#dataset.imid_nhsd=minimum_of(dataset.oral_steroid_drugs_nhsd, dataset.immunosuppresant_drugs_nhsd)
#dataset.had_imid=(dataset.imid_nhsd <=treat_date)

dataset.had_imid=((dataset.oral_steroid_drugs_nhsd <dataset.immunosuppresant_drugs_nhsd) & (dataset.oral_steroid_drugs_nhsd<=treat_date) \
                  &(dataset.oral_steroid_drug_nhsd_3m_count >= 2) & (dataset.oral_steroid_drug_nhsd_12m_count >= 4) | \
                  (dataset.oral_steroid_drugs_nhsd > dataset.immunosuppresant_drugs_nhsd) &(dataset.immunosuppresant_drugs_nhsd<=treat_date))

dataset.had_imid_ever=((dataset.immunosuppresant_drugs_nhsd_ever <=treat_date)&(dataset.immunosuppresant_drugs_nhsd_ever>treat_date-days(365)))| \
                   ((dataset.oral_steroid_drugs_nhsd_ever <=treat_date)&(dataset.oral_steroid_drugs_nhsd_ever>treat_date-days(365)))

dataset.imid = case(
    when(dataset.had_imid).then(1), otherwise=0
)

dataset.imid_ever = case(
    when(dataset.had_imid_ever).then(1), otherwise=0
)

def had_c_event_ctv3snome_lastdate(codelist, dt=c_events_bf_treat, code_type='ctv3', where=True):
       # Determine which code type to filter on
    if code_type == 'snomedct':
        code_field = dt.snomedct_code
    elif code_type == 'ctv3':       
        code_field = dt.ctv3_code
    return (
        dt.where(where)
        .where(code_field.is_in(codelist) & (dt.date.is_on_or_before(treat_date)))
        .sort_by(dt.date)
        .last_for_patient().date
)

def had_apcs_diag_icd10_lastdate(codelist, dt = apcs_diags_bf_treat, code_type='icd10_prim', where=True): #Currently only use for primary diagnosis
    if code_type == 'icd10_prim':
        code_field = dt.primary_diagnosis
    elif code_type == 'icd10_sec':
        code_field = dt.secondary_diagnosis
    return (
    dt.where(where)
    .where(code_field.is_in(codelist) & (dt.admission_date.is_on_or_before(treat_date)))
    .sort_by(dt.admission_date)
    .last_for_patient().admission_date
)

##high-risk cohort
#on_or_before = "start_date",
dataset.dialysis_ctv3 = had_c_event_ctv3snome_lastdate(dialysis_codes) #tpp-clinical_events  #CTV3ID
dataset.dialysis_icd10 = had_apcs_diag_icd10_lastdate(dialysis_icd10_codelist) #tpp-apcs

##apcs_admis_alldiag_match  ##code_string = ICD10Code(code.replace(".", ""))._to_primitive_type()
def apcs_proc_match(codelist):
    code_strings = set()
    for code in codelist:
        code_string = ICD10Code(code.replace(".", ""))._to_primitive_type()
        code_strings.add(code_string)
    conditions = [
        apcs.all_procedures.contains(code_str)
        for code_str in code_strings
    ]
    return apcs.where(any_of(conditions)
)

def apcs_proc_bf_treat_lastdate(codelist=None, where=True):
    return (
    (apcs_proc_match(codelist) if codelist else apcs)
    .where(apcs.admission_date.is_on_or_before(treat_date))
    .where(where)
    .sort_by(apcs.admission_date)
    .last_for_patient()
    .admission_date
)

def apcs_proc_bf_treat_df(codelist=None, where=True): 
    return (
    (apcs_proc_match(codelist) if codelist else apcs)
    .where(apcs.admission_date.is_on_or_before(treat_date))
    .where(where)
    .sort_by(apcs.admission_date)
)

def apcs_proc_bf_treat_af01Feb20_lastdate(codelist=None, where=True):
    return (
    (apcs_proc_match(codelist) if codelist else apcs)
    .where(apcs.admission_date.is_on_or_before(treat_date) & apcs.admission_date.is_on_or_after("2020-02-01"))
    .where(where).sort_by(apcs.admission_date).last_for_patient().admission_date
)

def apcs_proc_bf_treat_af01Feb20_df(codelist=None, where=True): ##get dataframe-apcs.admission_date
    return (
    (apcs_proc_match(codelist) if codelist else apcs)
    .where(apcs.admission_date.is_on_or_before(treat_date) & apcs.admission_date.is_on_or_after("2020-02-01"))
    .where(where).sort_by(apcs.admission_date)
)

#on_or_before="start_date"
dataset.dialysis_procedure = apcs_proc_bf_treat_lastdate(codelist= dialysis_opcs4_codelist) ##use fun:apcs_proc_bf_treat_lastdate
#dataset.dialysis_procedure0 = apcs_proc_bf_treat_df(codelist= dialysis_opcs4_codelist).sort_by(apcs.admission_date).last_for_patient().admission_date ##use fun:apcs_proc_bf_treat_lastdate

dataset.had_dialysis =((dataset.dialysis_ctv3 <=treat_date) | (dataset.dialysis_icd10<=treat_date) | (dataset.dialysis_procedure<=treat_date))
dataset.dialysis = case(
    when(dataset.had_dialysis).then(1), otherwise=0
)

##kidney transplant
dataset.kidney_transplant_ctv3 = had_c_event_ctv3snome_lastdate(codelist=kidney_transplant_codes) #tpp-clinical_events #CTV3ID
dataset.kidney_transplant_icd10 = had_apcs_diag_icd10_lastdate (codelist=kidney_tx_icd10_codelist)

#kidney_transplant_procedure 
dataset.kidney_transplant_procedure = apcs_proc_bf_treat_lastdate(codelist= kidney_tx_opcs4_codelist)
#dataset.kidney_transplant_procedure = apcs_proc_bf_treat_df(codelist= kidney_tx_opcs4_codelist).sort_by(apcs.admission_date).last_for_patient().admission_date ##use fun:apcs_proc_bf_treat_lastdate

dataset.had_kidney_transplant =((dataset.kidney_transplant_ctv3<=treat_date) | (dataset.kidney_transplant_icd10<=treat_date) | (dataset.kidney_transplant_procedure<=treat_date))

dataset.kidney_transplant = case(
    when(dataset.had_kidney_transplant).then(1), otherwise = 0
)

##Solid organ transplant
dataset.solid_organ_transplant_snomed = had_c_event_ctv3snome_lastdate(  ##added 202404-30
    codelist = solid_organ_transplant_codes, code_type='snomedct')

dataset.solid_organ_transplant_nhsd_snomed = had_c_event_ctv3snome_lastdate(
    codelist = solid_organ_transplant_nhsd_snomed_codes, code_type='snomedct') #tpp-clinical_events  #snomedct
dataset.solid_organ_nhsd_snomed_new = had_c_event_ctv3snome_lastdate(
    codelist = solid_organ_transplant_nhsd_snomed_codes_new, code_type='snomedct') #tpp-clinical_events  #snomedct

dataset.solid_organ_transplant_nhsd_opcs4 =apcs_proc_bf_treat_af01Feb20_lastdate(codelist= solid_organ_transplant_nhsd_opcs4_codes)
dataset.transplant_all_y_codes_opcs4 =apcs_proc_bf_treat_af01Feb20_lastdate(codelist=replacement_of_organ_transplant_nhsd_opcs4_codes)

transplant_all_y_codes_opcs4_df =apcs_proc_bf_treat_af01Feb20_df(codelist=replacement_of_organ_transplant_nhsd_opcs4_codes)

dataset.transplant_all_y_codes_opcs4_count =apcs_proc_bf_treat_af01Feb20_df(codelist=replacement_of_organ_transplant_nhsd_opcs4_codes).count_for_patient()
#transplant_thymus_opcs4_df = apcs_proc_bf_treat_af01Feb20_df(codelist=thymus_gland_transplant_nhsd_opcs4_codes)

##between = ["transplant_all_y_codes_opcs4","transplant_all_y_codes_opcs4"],#is_on_or_before(treat_date)#"earliest": "2020-02-01
transplant_thymus_opcs4 = apcs_proc_bf_treat_af01Feb20_lastdate(codelist=thymus_gland_transplant_nhsd_opcs4_codes)

#dataset.transplant_thymus_opcs4_3 = transplant_thymus_opcs4(transplant_thymus_opcs4.is_on_or_between(transplant_all_y_codes_opcs4,transplant_all_y_codes_opcs4).last_for_patient()).admission_date
dataset.transplant_thymus_opcs4 = apcs_proc_bf_treat_af01Feb20_lastdate(codelist=thymus_gland_transplant_nhsd_opcs4_codes)
dataset.transplant_thymus_opcs4_count = apcs_proc_bf_treat_af01Feb20_df(codelist=thymus_gland_transplant_nhsd_opcs4_codes).count_for_patient()

dataset.transplant_thymus_opcs4_a =dataset.transplant_thymus_opcs4.is_on_or_between(dataset.transplant_all_y_codes_opcs4,dataset.transplant_all_y_codes_opcs4)
#dataset.transplant_thymus_opcs4_4 = dataset.transplant_thymus_opcs4.is_in(transplant_all_y_codes_opcs4_df)

dataset.transplant_conjunctiva_y_code_opcs4 = apcs_proc_bf_treat_af01Feb20_lastdate(codelist=conjunctiva_y_codes_transplant_nhsd_opcs4_codes)
dataset.transplant_conjunctiva_y_code_opcs4_count = apcs_proc_bf_treat_af01Feb20_df(codelist=conjunctiva_y_codes_transplant_nhsd_opcs4_codes).count_for_patient()
transplant_conjunctiva_y_code_opcs4_df = apcs_proc_bf_treat_af01Feb20_df(codelist=conjunctiva_y_codes_transplant_nhsd_opcs4_codes)

#between = ["transplant_conjunctiva_y_code_opcs4","transplant_conjunctiva_y_code_opcs4"],
dataset.transplant_conjunctiva_opcs4 =apcs_proc_bf_treat_af01Feb20_lastdate(codelist= conjunctiva_transplant_nhsd_opcs4_codes)
dataset.transplant_conjunctiva_opcs4_count =apcs_proc_bf_treat_af01Feb20_df(codelist= conjunctiva_transplant_nhsd_opcs4_codes).count_for_patient()
# dataset.transplant_conjunctiva_opcs4_a =dataset.transplant_conjunctiva_opcs4.is_on_or_between(
#     dataset.transplant_conjunctiva_y_code_opcs4,dataset.transplant_conjunctiva_y_code_opcs4)

# between = ["transplant_all_y_codes_opcs4","transplant_all_y_codes_opcs4"],
dataset.transplant_stomach_opcs4 = apcs_proc_bf_treat_af01Feb20_lastdate(codelist=stomach_transplant_nhsd_opcs4_codes)
dataset.transplant_stomach_opcs4_count =apcs_proc_bf_treat_af01Feb20_df(codelist=stomach_transplant_nhsd_opcs4_codes).count_for_patient()
#dataset.transplant_stomach_opcs4_a = dataset.transplant_stomach_opcs4.is_on_or_between(dataset.transplant_all_y_codes_opcs4,dataset.transplant_all_y_codes_opcs4) 


dataset.transplant_ileum_1_Y_codes_opcs4 = apcs_proc_bf_treat_af01Feb20_lastdate(codelist=ileum_1_y_codes_transplant_nhsd_opcs4_codes)
dataset.transplant_ileum_1_Y_codes_opcs4_count = apcs_proc_bf_treat_af01Feb20_df(codelist=ileum_1_y_codes_transplant_nhsd_opcs4_codes).count_for_patient()
transplant_ileum_1_Y_codes_opcs4_df = apcs_proc_bf_treat_af01Feb20_df(codelist=ileum_1_y_codes_transplant_nhsd_opcs4_codes)

#between = ["transplant_ileum_1_Y_codes_opcs4","transplant_ileum_1_Y_codes_opcs4"]
dataset.transplant_ileum_1_opcs4 = apcs_proc_bf_treat_af01Feb20_lastdate(codelist=ileum_1_transplant_nhsd_opcs4_codes) #not defined by transplant_ileum_1_Y_codes_opcs4
dataset.transplant_ileum_1_opcs4_count = apcs_proc_bf_treat_af01Feb20_df(codelist=ileum_1_transplant_nhsd_opcs4_codes).count_for_patient() #
#dataset.transplant_ileum_1_opcs4_a = dataset.transplant_ileum_1_opcs4.is_on_or_between(dataset.transplant_ileum_1_Y_codes_opcs4,dataset.transplant_ileum_1_Y_codes_opcs4) 

dataset.transplant_ileum_2_Y_codes_opcs4 = apcs_proc_bf_treat_af01Feb20_lastdate(codelist= ileum_2_y_codes_transplant_nhsd_opcs4_codes)
dataset.transplant_ileum_2_Y_codes_opcs4_count= apcs_proc_bf_treat_af01Feb20_df(codelist=ileum_2_y_codes_transplant_nhsd_opcs4_codes).count_for_patient()
transplant_ileum_2_Y_codes_opcs4_df= apcs_proc_bf_treat_af01Feb20_df(codelist=ileum_2_y_codes_transplant_nhsd_opcs4_codes)

#between = ["transplant_ileum_2_Y_codes_opcs4","transplant_ileum_2_Y_codes_opcs4"]
#"date": {"earliest": "2020-02-01"}
dataset.transplant_ileum_2_opcs4 = apcs_proc_bf_treat_af01Feb20_lastdate(codelist=ileum_2_transplant_nhsd_opcs4_codes)
dataset.transplant_ileum_2_opcs4_count = apcs_proc_bf_treat_af01Feb20_df(codelist=ileum_2_transplant_nhsd_opcs4_codes).count_for_patient()
#dataset.transplant_ileum_2_opcs4_a = dataset.transplant_ileum_2_opcs4.is_on_or_between(dataset.transplant_ileum_2_Y_codes_opcs4,dataset.transplant_ileum_2_Y_codes_opcs4) 

def proc_match(codelist, dt):
    code_strings = set()
    for code in codelist:
        code_string = ICD10Code(code.replace(".", ""))._to_primitive_type() #code.replace(".", "")
        code_strings.add(code_string)
    conditions = [
        dt.all_procedures.contains(code_str)
        for code_str in code_strings
    ]
    return dt.where(any_of(conditions))

def proc_bf_treat_af01Feb20_lastdate(dt, codelist=None, where=True):
    matched_data = proc_match(codelist, dt) if codelist else dt
    return (
        matched_data
        .where(dt.admission_date.is_on_or_before(treat_date) & dt.admission_date.is_on_or_after("2020-02-01"))
        .where(where).sort_by(dt.admission_date).last_for_patient().admission_date
    )

dataset.transplant_thymus_opcs4_2 = proc_bf_treat_af01Feb20_lastdate(
    dt=transplant_all_y_codes_opcs4_df, codelist=thymus_gland_transplant_nhsd_opcs4_codes
)

dataset.transplant_conjunctiva_opcs4_2 = proc_bf_treat_af01Feb20_lastdate(
    dt=transplant_conjunctiva_y_code_opcs4_df, codelist=conjunctiva_transplant_nhsd_opcs4_codes
)
dataset.transplant_stomach_opcs4_2 = proc_bf_treat_af01Feb20_lastdate(
    dt=transplant_all_y_codes_opcs4_df, codelist=stomach_transplant_nhsd_opcs4_codes
)
dataset.transplant_ileum_1_opcs4_2 = proc_bf_treat_af01Feb20_lastdate(
    dt=transplant_ileum_1_Y_codes_opcs4_df, codelist=ileum_1_transplant_nhsd_opcs4_codes
)
dataset.transplant_ileum_2_opcs4_2 = proc_bf_treat_af01Feb20_lastdate(
    dt=transplant_ileum_2_Y_codes_opcs4_df, codelist=ileum_2_transplant_nhsd_opcs4_codes
)

dataset.solid_organ_transplant_nhsd = minimum_of(
    dataset.solid_organ_transplant_nhsd_snomed, dataset.solid_organ_transplant_nhsd_opcs4,
    dataset.transplant_thymus_opcs4_2 , dataset.transplant_conjunctiva_opcs4_2, dataset.transplant_stomach_opcs4_2,
    dataset.transplant_ileum_1_opcs4_2,dataset.transplant_ileum_2_opcs4_2
)

dataset.solid_organ_transplant_nhsd_new = minimum_of(
    dataset.solid_organ_nhsd_snomed_new, dataset.solid_organ_transplant_nhsd_opcs4,
    dataset.transplant_thymus_opcs4_2 , dataset.transplant_conjunctiva_opcs4_2, dataset.transplant_stomach_opcs4_2,
    dataset.transplant_ileum_1_opcs4_2, dataset.transplant_ileum_2_opcs4_2
)

dataset.had_solid_organ_transplant =((dataset.solid_organ_transplant_nhsd<=treat_date) )

dataset.solid_organ_transplant = case(
    when(dataset.had_solid_organ_transplant).then(1), otherwise = 0
)

dataset.had_solid_organ_transplant_new =((dataset.solid_organ_transplant_nhsd_new<=treat_date) )

dataset.solid_organ_transplant_new = case(
    when(dataset.had_solid_organ_transplant_new).then(1), otherwise = 0
)

#Haematological diseases-between = ["start_date - 24 months", "start_date"],
#c_events_bf12m,apcs_diags_bf12m, #c_events_bf24m,apcs_diags_bf24m
#between = ["start_date - 12 months", "start_date"],
dataset.haematopoietic_stem_cell_snomed = had_c_event_ctv3snome_lastdate (dt = c_events_bf12m, 
    codelist = haematopoietic_stem_cell_transplant_nhsd_snomed_codes, code_type = 'snomedct'
) 

#between = ["start_date - 12 months", "start_date"],
dataset.haematopoietic_stem_cell_icd10  = had_apcs_diag_icd10_lastdate (dt = apcs_diags_bf12m, 
    codelist = haematopoietic_stem_cell_transplant_nhsd_icd10_codes
) 

def apcs_proc_12m_bf_treat_af01Feb20_lastdate (codelist=None, where=True): 
    return (
    (apcs_proc_match(codelist) if codelist else apcs) \
    .where(apcs.admission_date.is_on_or_between(treat_date- months(12),treat_date) & \
    apcs.admission_date.is_on_or_after("2020-02-01")) \
    .where(where).sort_by(apcs.admission_date).last_for_patient().admission_date \
)

# between = ["start_date - 12 months", "start_date"], #"date": {"earliest": "2020-02-01"},
dataset.haematopoietic_stem_cell_opcs4 = apcs_proc_12m_bf_treat_af01Feb20_lastdate(
    codelist=haematopoietic_stem_cell_transplant_nhsd_opcs4_codes) 

# between = ["start_date - 24 months", "start_date"],
dataset.haematological_malignancies_snomed = had_c_event_ctv3snome_lastdate(dt = c_events_bf24m, 
    codelist = haematological_malignancies_nhsd_snomed_codes, code_type = 'snomedct') #tpp-clinical_events  #snomedct

# between = ["start_date - 24 months", "start_date"],
dataset.haematological_malignancies_icd10 = had_apcs_diag_icd10_lastdate(dt = apcs_diags_bf24m, 
    codelist = haematological_malignancies_nhsd_icd10_codes) ##tpp-apcs

#on_or_before = "start_date",
dataset.sickle_cell_disease_nhsd_snomed = had_c_event_ctv3snome_lastdate(
    codelist = sickle_cell_disease_nhsd_snomed_codes, code_type = 'snomedct') #tpp-clinical_events  #snomedct
#on_or_before = "start_date",
dataset.sickle_cell_disease_nhsd_icd10  = had_apcs_diag_icd10_lastdate(codelist = sickle_cell_disease_nhsd_icd10_codes) 

## Haematological diseases-ever(on_or_before = "start_date")
dataset.haematopoietic_stem_cell_snomed_ever = had_c_event_ctv3snome_lastdate(
    codelist = haematopoietic_stem_cell_transplant_nhsd_snomed_codes, code_type = 'snomedct') #tpp-clinical_events  #snomedct
#on_or_before = "start_date",
dataset.haematopoietic_stem_cell_icd10_ever = had_apcs_diag_icd10_lastdate(
    codelist = haematopoietic_stem_cell_transplant_nhsd_icd10_codes) ##tpp-apcs

##on_or_before = "start_date", "earliest": "2020-02-01"},
dataset.haematopoietic_stem_cell_opcs4_ever = apcs_proc_bf_treat_af01Feb20_lastdate(
    codelist=haematopoietic_stem_cell_transplant_nhsd_opcs4_codes)
                          
#on_or_before = "start_date"
dataset.haematological_malignancies_snomed_ever = had_c_event_ctv3snome_lastdate(
    codelist = haematological_malignancies_nhsd_snomed_codes, 
    code_type='snomedct') #tpp-clinical_events  #snomedct
#on_or_before = "start_date"
dataset.haematological_malignancies_icd10_ever = had_apcs_diag_icd10_lastdate(
    codelist = haematological_malignancies_nhsd_icd10_codes) ##tpp-apcs

##minimum_of
dataset.haematological_disease_nhsd = minimum_of(
    dataset.haematopoietic_stem_cell_snomed, 
    dataset.haematopoietic_stem_cell_icd10, 
    dataset.haematopoietic_stem_cell_opcs4, 
    dataset.haematological_malignancies_snomed, 
    dataset.haematological_malignancies_icd10,
    dataset.sickle_cell_disease_nhsd_snomed, 
    dataset.sickle_cell_disease_nhsd_icd10)

dataset.haematological_disease_nhsd_ever = minimum_of(
    dataset.haematopoietic_stem_cell_snomed_ever, 
    dataset.haematopoietic_stem_cell_icd10_ever, 
    dataset.haematopoietic_stem_cell_opcs4_ever, 
    dataset.haematological_malignancies_snomed_ever, 
    dataset.haematological_malignancies_icd10_ever,
    dataset.sickle_cell_disease_nhsd_snomed, 
    dataset.sickle_cell_disease_nhsd_icd10)

dataset.had_haema_disease =((dataset.haematological_disease_nhsd<=treat_date) )
dataset.haema_disease  = case(
    when(dataset.had_haema_disease).then(1), otherwise = 0
)

dataset.had_haema_disease_ever =((dataset.haematological_disease_nhsd_ever<=treat_date) )
dataset.haema_disease_ever = case(
    when(dataset.had_haema_disease_ever).then(1), otherwise = 0
)

#on_or_before = "start_date"
##Primary immune deficiencies
dataset.immunosupression_nhsd = had_c_event_ctv3snome_lastdate(codelist=immunosupression_nhsd_codes, code_type='snomedct') #tpp-clinical_events  #snomedct
#on_or_before = "start_date",
dataset.immunosupression_nhsd_new  = had_c_event_ctv3snome_lastdate(codelist=immunosupression_nhsd_codes_new, code_type='snomedct') #tpp-clinical_events  #snomedct

dataset.had_immunosupression =((dataset.immunosupression_nhsd<=treat_date) )
dataset.immunosupression = case(
    when(dataset.had_immunosupression).then(1), otherwise = 0
)

dataset.had_immunosupression_new =((dataset.immunosupression_nhsd_new<=treat_date) )
dataset.immunosupression_new  = case(
    when(dataset.had_immunosupression_new).then(1), otherwise = 0
)

## Solid cancer
dataset.cancer_opensafely_snomed= c_events_bf6m.where(
        (c_events_bf6m.snomedct_code.is_in(non_haematological_cancer_opensafely_snomed_codes)) | \
        (c_events_bf6m.snomedct_code.is_in(lung_cancer_opensafely_snomed_codes)) | \
        (c_events_bf6m.snomedct_code.is_in(chemotherapy_radiotherapy_opensafely_snomed_codes))) \
        .sort_by(c_events_bf6m.date).last_for_patient().date

dataset.cancer_opensafely_snomed_new= c_events_bf6m.where(
        (c_events_bf6m.snomedct_code.is_in(non_haematological_cancer_opensafely_snomed_codes_new)) | \
        (c_events_bf6m.snomedct_code.is_in(lung_cancer_opensafely_snomed_codes)) | \
        (c_events_bf6m.snomedct_code.is_in(chemotherapy_radiotherapy_opensafely_snomed_codes))) \
        .sort_by(c_events_bf6m.date).last_for_patient().date

dataset.cancer_opensafely_snomed_ever= c_events_bf_treat.where(
        (c_events_bf_treat.snomedct_code.is_in(non_haematological_cancer_opensafely_snomed_codes_new)) | \
        (c_events_bf_treat.snomedct_code.is_in(lung_cancer_opensafely_snomed_codes)) | \
        (c_events_bf_treat.snomedct_code.is_in(chemotherapy_radiotherapy_opensafely_snomed_codes))) \
        .sort_by(c_events_bf_treat.date).last_for_patient().date

dataset.had_solid_cancer =((dataset.cancer_opensafely_snomed<=treat_date) )
dataset.solid_cancer = case(
    when(dataset.had_solid_cancer).then(1), otherwise = 0
)

dataset.had_solid_cancer_new =((dataset.cancer_opensafely_snomed_new<=treat_date) )
dataset.solid_cancer_new = case(
    when(dataset.had_solid_cancer_new).then(1), otherwise = 0
)

dataset.had_solid_cancer_ever =((dataset.cancer_opensafely_snomed_ever<=treat_date) )
dataset.solid_cancer_ever = case(
    when(dataset.had_solid_cancer_ever).then(1), otherwise = 0
)

## List of high-risk diseases
# highrisk_list = ["haematologic malignancy","Patients with a haematological diseases", "immune deficiencies", 
# "primary immune deficiencies",  "sickle cell disease", "solid cancer", "solid organ recipients", 
#"stem cell transplant recipient"
# ]

#covid_therapeutics-MOL1_high_risk_cohort-SOT02_risk_cohorts
therapeutics_df = (covid_therapeutics
    .where(covid_therapeutics.intervention.is_in(["Molnupiravir","Sotrovimab"])) # "Paxlovid" ,"Remdesivir","Casirivimab and imdevimab"
    .sort_by(covid_therapeutics.treatment_start_date).last_for_patient()
    )

#high_risk_MOL_last(=risk_cohort),high_risk_SOT02_last,high_risk_MOL_count,high_risk_SOT02_count
dataset.risk_cohort = therapeutics_df.risk_cohort  #risk_cohort 

dataset.is_codelist_highrisk = (dataset.imid + dataset.dialysis + dataset.kidney_transplant +dataset.solid_organ_transplant_new +dataset.haema_disease + dataset.immunosupression_new +
    dataset.solid_cancer_new)

dataset.highrisk_codelist = case(
    when(dataset.is_codelist_highrisk >=1).then(1), otherwise = 0
)
dataset.is_codelist_highrisk_ever = (dataset.imid_ever + dataset.dialysis + dataset.kidney_transplant +dataset.solid_organ_transplant_new +dataset.haema_disease_ever + dataset.immunosupression_new +
    dataset.solid_cancer_ever)

dataset.highrisk_codelist_ever = case(
    when(dataset.is_codelist_highrisk_ever >=1).then(1), otherwise = 0
)

##Pregnancy
#pregnancy record in last 36 weeks
dataset.preg_36wks_date = (
    c_events_bf_treat.where((c_events_bf_treat.snomedct_code.is_in(pregnancy_primis_codes)) & \
    (c_events_bf_treat.date.is_on_or_before(treat_date)) & \
        (c_events_bf_treat.date.is_on_or_between(treat_date - days(252), treat_date - days(1)))) 
        .sort_by(c_events_bf_treat.date)
        .last_for_patient().date
)

# if pregnancy has ended
dataset.is_pregdel = (
    c_events_bf_treat.where((c_events_bf_treat.snomedct_code.is_in(pregdel_primis_codes)) & \
    (c_events_bf_treat.date.is_on_or_before(treat_date)) & \
        (c_events_bf_treat.date.is_on_or_between(dataset.preg_36wks_date + days(1), treat_date - days(1)))) 
        .sort_by(c_events_bf_treat.date)
        .last_for_patient().exists_for_patient()    
)

is_pregdel = (
    c_events_bf_treat.where((c_events_bf_treat.snomedct_code.is_in(pregdel_primis_codes)) & \
    (c_events_bf_treat.date.is_on_or_before(treat_date)) & \
        (c_events_bf_treat.date.is_on_or_between(dataset.preg_36wks_date + days(1), treat_date - days(1)))) 
        .sort_by(c_events_bf_treat.date)
        .last_for_patient().exists_for_patient()  
)
dataset.pregnancy = case(
    when((patients.age_on(dataset.preg_36wks_date) <=50 ) & (patients.sex.is_in(["female"])) & (~(dataset.is_pregdel))).then("preg"),
    otherwise="Not preg",
)

## all_diagnoses-admission 
def apcs_admis_alldiag_match(codelist):  
    code_strings = set()
    for code in codelist:
        code_string = ICD10Code(code.replace(".", ""))._to_primitive_type()
        code_strings.add(code_string)
        conditions = [apcs.all_diagnoses.contains(code_str) 
        for code_str in code_strings]
    return apcs.where(any_of(conditions)
)

def apcs_admis_af_treat_alldiag_firstdate(codelist=None, where=True):
    return (
    (apcs_admis_alldiag_match(codelist) if codelist else apcs)
    .where(apcs.admission_date.is_on_or_after(treat_date))
    .where(apcs.patient_classification == "1")
    .where(where)
    .sort_by(apcs.admission_date)
    .first_for_patient()
    .admission_date
)

def apcs_admis_60daf_treat_alldiag_firstdate(codelist=None, where=True): #60days after treatment
    return (
    (apcs_admis_alldiag_match(codelist) if codelist else apcs)
    .where((apcs.admission_date.is_on_or_after(treat_date + days(60))) &
           (apcs.admission_date.is_on_or_before(treat_date + days(60) + months(6))))
    .where(apcs.patient_classification == "1")
    .where(where)
    .sort_by(apcs.admission_date)
    .first_for_patient()
    .admission_date
)

##hospitalisation as per all_diagnosis
# covid-related admission
#covid_first_admi_af_treat_alldiag_firstdate-hosp_af_treat_alldiag_date
dataset.hosp_af_treat_alldiag_date = apcs_admis_af_treat_alldiag_firstdate(
    codelist= covid_icd10_codes,   
)

##apcs_admis_60daf_treat_alldiag_firstdate -hosp_60daf_treat_alldiag_date
dataset.hosp_60daf_treat_alldiag_date = apcs_admis_60daf_treat_alldiag_firstdate(
    codelist= covid_icd10_codes,   
)

# covid-related admission to critical care
dataset.ccare_covid_first_af_treat_alldiag_date = apcs_admis_af_treat_alldiag_firstdate(codelist= covid_icd10_codes,
    where=(apcs.admission_method.is_in(
    ["21", "22", "23", "24", "25", "2A", "2B", "2C", "2D", "28"]
    )) & (apcs.days_in_critical_care>0),
)

##demographic
dataset.dob = patients.date_of_birth ##dob
dataset.dod = patients.date_of_death  #dod: date of death
dataset.sex = patients.sex

dataset.age_sstart = patients.age_on("2021-12-16")
dataset.age_sstart_group = case(
        when(dataset.age_sstart < 30).then("18-29"),
        when(dataset.age_sstart < 40).then("30-39"),
        when(dataset.age_sstart < 50).then("40-49"),
        when(dataset.age_sstart < 60).then("50-59"),
        when(dataset.age_sstart < 70).then("60-69"),
        when(dataset.age_sstart < 80).then("70-79"),
        when(dataset.age_sstart < 90).then("80-89"),
        when(dataset.age_sstart >= 90).then("90+"),
        otherwise="unknown",
)

##demographic - treatment day
dataset.age_treated = patients.age_on(treat_date)
dataset.age_treated_group = case(
        when(dataset.age_treated < 30).then("18-29"),
        when(dataset.age_treated < 40).then("30-39"),
        when(dataset.age_treated < 50).then("40-49"),
        when(dataset.age_treated < 60).then("50-59"),
        when(dataset.age_treated < 70).then("60-69"),
        when(dataset.age_treated < 80).then("70-79"),
        when(dataset.age_treated < 90).then("80-89"),
        when(dataset.age_treated >= 90).then("90+"),
        otherwise="unknown",
)
#ethnicity_snome,ethnicity_snome_cat,
## Ethnicity
dod_ons = ons_deaths.date

#ethnicity_from_sus
dataset.latest_ethnicity_code = (
    clinical_events.where(clinical_events.snomedct_code.is_in(ethnicity_codelist_with_categories))
    .where(clinical_events.date.is_on_or_before(dod_ons))
    .sort_by(clinical_events.date)
    .last_for_patient().snomedct_code
)

latest_ethnicity_group = dataset.latest_ethnicity_code.to_category(
    ethnicity_codelist_with_categories
)

# Add in code to extract ethnicity from SUS if it isn't present in primary care data. 
ethnicity_sus = ethnicity_from_sus.code

#dataset.ethnicity_combined
dataset.ethnicity = case(
  when((latest_ethnicity_group == "1") | ((latest_ethnicity_group.is_null()) & (ethnicity_sus.is_in(["A", "B", "C"])))).then("White"),
  when((latest_ethnicity_group == "2") | ((latest_ethnicity_group.is_null()) & (ethnicity_sus.is_in(["D", "E", "F", "G"])))).then("Mixed"),
  when((latest_ethnicity_group == "3") | ((latest_ethnicity_group.is_null()) & (ethnicity_sus.is_in(["H", "J", "K", "L"])))).then("Asian or Asian British"),
  when((latest_ethnicity_group == "4") | ((latest_ethnicity_group.is_null()) & (ethnicity_sus.is_in(["M", "N", "P"])))).then("Black or Black British"),
  when((latest_ethnicity_group == "5") | ((latest_ethnicity_group.is_null()) & (ethnicity_sus.is_in(["R", "S"])))).then("Chinese or Other Ethnic Groups"),
  otherwise="unknown", 
) 
 

spanning_addrs = addresses.where(addresses.start_date <= treat_date).except_where(
    addresses.end_date < treat_date
)

ordered_addrs = spanning_addrs.sort_by(
    case(when(addresses.has_postcode).then(1), otherwise = 0),
    addresses.start_date,
    addresses.end_date,
    addresses.address_id,
).last_for_patient()

# dataset.has_postcode = ordered_addrs.has_postcode
# dataset.addrs_type = ordered_addrs.address_type
# dataset.care_home = ordered_addrs.care_home_is_potential_match 
# dataset.care_home_nurse = ordered_addrs.care_home_requires_nursing 
# dataset.care_home_nonurse = ordered_addrs.care_home_does_not_require_nursing 

#######
# Care home based on primis codes/TPP address match
carehome_primis = clinical_events.where(
        clinical_events.snomedct_code.is_in(care_home_primis_snomed_codes)
    ).where(
        clinical_events.date.is_on_or_before(treat_date)
    ).exists_for_patient() 

carehome_tpp = addresses.for_patient_on(treat_date).care_home_is_potential_match 

carehome = case(
    when(carehome_primis).then(True),
    when(carehome_tpp).then(True),
    otherwise=False
)

dataset.care_home_primis = carehome

##max_imd = 32844
imd0 = addresses.for_patient_on(treat_date).imd_rounded
dataset.imd = case(
    when((imd0 >=0) & (imd0 < int(32844 * 1 / 5))).then("1 (most deprived)"),
    when(imd0 < int(32844 * 2 / 5)).then("2"),
    when(imd0 < int(32844 * 3 / 5)).then("3"),
    when(imd0 < int(32844 * 4 / 5)).then("4"),
    when(imd0 < int(32844 * 5 / 5)).then("5 (least deprived)"),
    otherwise="unknown"
)

# Index of Multiple Deprevation Rank (rounded down to nearest 100)
dataset.imd1 = addresses.for_patient_on(treat_date).imd_rounded #

##registrations

dataset.was_registered_treated = was_registered_treated
regd = practice_registrations.for_patient_on(treat_date)
dataset.region = regd.practice_nuts1_region_name
##STP
dataset.stp = regd.practice_stp

regd_end = practice_registrations.spanning(index_startdate, index_enddate
).sort_by(practice_registrations.end_date).first_for_patient()

dataset.dereg_date= regd_end.end_date

de_reg = (practice_registrations
    .where((practice_registrations.start_date.is_on_or_before(treat_date)) & (practice_registrations.start_date.is_not_null()) & 
    practice_registrations.end_date.is_after(treat_date))).sort_by(practice_registrations.end_date).first_for_patient()

dataset.dereg_date1 = de_reg.end_date

# registered_eligible = patients.registered_as_of("covid_test_positive_date"),
#   registered_treated = patients.registered_as_of("date_treated"),
# registered_eligible == 1 | registered_treated == 1,
##Rurality
dataset.rural_urban = addresses.for_patient_on(treat_date).rural_urban_classification

##bmi
dataset.bmi = bmi_record.numeric_value
dataset.bmi_date = bmi_record.date

##vaccination 
# first vaccine from during trials and up to treatment date
covid_vacc = (
    vaccinations.where((vaccinations.target_disease.is_in(["SARS-2 CORONAVIRUS"])) &
    (vaccinations.date.is_before(treat_date)) & (vaccinations.date.is_after("2020-06-08")))
    .sort_by(vaccinations.date)
)

#total_covid_vacc, covid_vacc1_date,covid_vacc2_date,covid_vacc3_date,covid_vacc4_date,covid_vacc_last_date
#vaccination count
dataset.total_covid_vacc = covid_vacc.count_for_patient()
#first-4 vaccination
dataset.covid_vacc1_date = covid_vacc.first_for_patient().date

dataset.covid_vacc2_date = covid_vacc.where(covid_vacc.date.is_after(dataset.covid_vacc1_date + days(19))
    ).sort_by(covid_vacc.date).first_for_patient().date

dataset.covid_vacc3_date = covid_vacc.where(covid_vacc.date.is_after(dataset.covid_vacc2_date + days(56))
    ).sort_by(covid_vacc.date).first_for_patient().date

dataset.covid_vacc4_date = covid_vacc.where(covid_vacc.date.is_after(dataset.covid_vacc3_date + days(56))
    ).sort_by(covid_vacc.date).first_for_patient().date

dataset.covid_vacc_last_date= covid_vacc.last_for_patient().date

dataset.total_covid_vacc_cat = case(
    when (dataset.total_covid_vacc ==1).then("One vaccination"),
    when (dataset.total_covid_vacc == 2).then("Two vaccinations"),
    when (dataset.total_covid_vacc >= 3).then("Three or more vaccinations"),
    otherwise = "unvaccinated",
)

##diabetes_codes,hypertension_codes,chronic_cardiac_dis_codes,chronic_respiratory_dis_codes,
##autism_nhsd_snomed_codes,wider_ld_primis_snomed_codes,serious_mental_illness_nhsd_snomed_codes, dementia_nhsd_snomed_codes 
def had_c_event_snome_exist(codelist, dt=c_events_bf_treat, code_type='snomedct', where=True):
    return (
        dt.where(where)
        .where(dt.snomedct_code.is_in(codelist) & (dt.date.is_on_or_before(treat_date)))
        .sort_by(dt.date)
        .exists_for_patient()
)
#had_diabetes,had_hypertension,had_chronic_cardiac_disease,had_chronic_respiratory_disease,
#had_autism,had_learning_disability,had_serious_mental_illness,had_dementia,had_housebound
# Diabetes
dataset.had_diabetes = had_c_event_snome_exist(codelist = diabetes_codes)
# Hypertension
dataset.had_hypertension = had_c_event_snome_exist(codelist = hypertension_codes)
# Chronic cardiac disease
dataset.had_chronic_cardiac_disease = had_c_event_snome_exist(codelist = chronic_cardiac_dis_codes)

# Chronic respiratory disease
dataset.had_chronic_respiratory_disease = had_c_event_snome_exist(codelist = chronic_respiratory_dis_codes)
 ## Autism
dataset.had_autism = had_c_event_snome_exist(codelist = autism_nhsd_snomed_codes)

# Learning disability
dataset.had_learning_disability = had_c_event_snome_exist(codelist = wider_ld_primis_snomed_codes)#, code_type='snomedct')#.exists_for_patient()

# Serious Mental Illness
dataset.had_serious_mental_illness = had_c_event_snome_exist(codelist = serious_mental_illness_nhsd_snomed_codes)#, code_type='snomedct')#.exists_for_patient()

## Dementia
dataset.had_dementia_poten = had_c_event_snome_exist(codelist = dementia_nhsd_snomed_codes)

dataset.had_dementia = ((dataset.had_dementia_poten) & ( dataset.age_treated > 39))

## Housebound #to be checked
#housebound_opensafely_snomed_codes,no_longer_housebound_opensafely_snomed_codes,care_home_primis_snomed_codes
#housebound_lastdate,no_longer_housebound_lastdate,moved_into_care_home_lastdate
dataset.had_housebound_poten = had_c_event_snome_exist(codelist = housebound_opensafely_snomed_codes)
dataset.housebound_lastdate = had_c_event_ctv3snome_lastdate(
    codelist = housebound_opensafely_snomed_codes, code_type='snomedct')

dataset.had_no_longer_housebound = had_c_event_snome_exist(codelist = no_longer_housebound_opensafely_snomed_codes)
dataset.no_longer_housebound_lastdate = had_c_event_ctv3snome_lastdate(
    codelist = no_longer_housebound_opensafely_snomed_codes, code_type='snomedct')

dataset.had_moved_into_care_home = had_c_event_snome_exist(codelist = care_home_primis_snomed_codes)
dataset.moved_into_care_home_lastdate = had_c_event_ctv3snome_lastdate(
    codelist = care_home_primis_snomed_codes, code_type='snomedct')

dataset.had_housebound=(dataset.housebound_lastdate > dataset.no_longer_housebound_lastdate ) & (dataset.housebound_lastdate>dataset.moved_into_care_home_lastdate)

  



