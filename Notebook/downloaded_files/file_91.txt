# numpy for random seed - and set random seed
#import numpy as np 
#np.random.seed(209109) # random seed

#######################################################################################
# IMPORT
#######################################################################################
## Import ehrQL functions
from ehrql import (
    create_dataset,
    case,
    when
)

## Import TPP tables
from ehrql.tables.tpp import (
    clinical_events,
    patients,
    ons_deaths,
    medications,
    apcs,
    addresses,
    practice_registrations
)

## Import all codelists from codelists.py
from codelists import *

## Import the variable helper functions 
from variable_helper_functions import *

## json (for the dates)
import json

#######################################################################################
# IMPORT the dates
#######################################################################################
with open("output/study_dates.json") as f:
  study_dates = json.load(f)
studyend_date = study_dates["studyend_date"]
studystart_date = study_dates["studystart_date"]

#######################################################################################
# INITIALISE the dataset and set the dummy dataset size
#######################################################################################
dataset = create_dataset()
dataset.configure_dummy_data(population_size=10000)
dataset.define_population(patients.exists_for_patient())

#######################################################################################
#  Define the exposure start
#######################################################################################
## First baricitinib treatment, at hospital admission, after pandemic start
dataset.exp_date_bari_hosp_first = first_matching_event_bari_between("hospitalised_with", studystart_date, studyend_date).treatment_start_date 

## First baricitinib treatment, BUT hospital onset, after pandemic start (look into this in a second step)
dataset.exp_date_bari_hosp_onset_first = first_matching_event_bari_between("hospital_onset", studystart_date, studyend_date).treatment_start_date 

index_date = dataset.exp_date_bari_hosp_first

# second and third exposure dates
dataset.exp_date_bari_hosp_second = first_matching_event_bari_between("hospitalised_with", index_date, studyend_date).treatment_start_date 
second_date = dataset.exp_date_bari_hosp_second
dataset.exp_date_bari_hosp_third = first_matching_event_bari_between("hospitalised_with", second_date, studyend_date).treatment_start_date

#######################################################################################
#  QUALITY ASSURANCE variables
#######################################################################################
### demographic QA
dataset.qa_bin_is_female_or_male = patients.sex.is_in(["female", "male"]) 
dataset.qa_bin_was_adult = (patients.age_on(index_date) >= 18) & (patients.age_on(index_date) <= 110) 
dataset.qa_bin_was_alive = patients.is_alive_on(index_date)
dataset.qa_bin_known_imd = addresses.for_patient_on(index_date).exists_for_patient() # known deprivation
dataset.qa_bin_was_registered = practice_registrations.spanning(index_date - days(366), index_date).exists_for_patient() # see https://docs.opensafely.org/ehrql/reference/schemas/tpp/#practice_registrations.spanning. Calculated from 1 year = 365.25 days, taking into account leap year.
dataset.qa_num_birth_year = patients.date_of_birth
dataset.qa_date_of_death = ons_deaths.date
### clinical QA
## Pregnancy (over entire study period)
dataset.qa_bin_pregnancy = clinical_events.where(clinical_events.snomedct_code.is_in(pregnancy_snomed_clinical)).exists_for_patient()
## Combined oral contraceptive pill (over entire study period)
dataset.qa_bin_cocp = medications.where(medications.dmd_code.is_in(cocp_dmd)).exists_for_patient()
## Hormone replacement therapy (over entire study period)
dataset.qa_bin_hrt = medications.where(medications.dmd_code.is_in(hrt_dmd)).exists_for_patient()
## Prostate cancer (over entire study period)
### Primary care
prostate_cancer_snomed = clinical_events.where(clinical_events.snomedct_code.is_in(prostate_cancer_snomed_clinical)).exists_for_patient()
### HES APC
prostate_cancer_hes = apcs.where(apcs.all_diagnoses.contains_any_of(prostate_cancer_icd10)).exists_for_patient()
### ONS (stated anywhere on death certificate)
prostate_cancer_death = cause_of_death_matches(prostate_cancer_icd10)
# Combined: Any prostate cancer diagnosis
dataset.qa_bin_prostate_cancer = case(
    when(prostate_cancer_snomed).then(True),
    when(prostate_cancer_hes).then(True),
    when(prostate_cancer_death).then(True),
    otherwise=False
)

#######################################################################################
# Covariates
#######################################################################################
# Sex
dataset.cov_cat_sex = patients.sex
## Age at index_date
dataset.cov_num_age = patients.age_on(index_date)
# Ethnicity in 6 categories
dataset.ethnicity_cat = (
    clinical_events.where(clinical_events.ctv3_code.is_in(ethnicity_codes))
    .sort_by(clinical_events.date)
    .last_for_patient()
    .ctv3_code.to_category(ethnicity_codes))
## Index of Multiple Deprevation Rank (rounded down to nearest 100). 5 categories.
imd_rounded = addresses.for_patient_on(index_date).imd_rounded
dataset.cov_cat_deprivation_5 = case(
    when((imd_rounded >=0) & (imd_rounded < int(32844 * 1 / 5))).then("1 (most deprived)"),
    when(imd_rounded < int(32844 * 2 / 5)).then("2"),
    when(imd_rounded < int(32844 * 3 / 5)).then("3"),
    when(imd_rounded < int(32844 * 4 / 5)).then("4"),
    when(imd_rounded < int(32844 * 5 / 5)).then("5 (least deprived)"),
    otherwise="unknown")
## Practice registration info at index_date and derived region, STP and rural/urban
registered = practice_registrations.for_patient_on(index_date)
dataset.cov_cat_region = registered.practice_nuts1_region_name ## Region
dataset.cov_cat_stp = registered.practice_stp ## Practice
dataset.cov_cat_rural_urban = addresses.for_patient_on(index_date).rural_urban_classification ## Rurality
## Smoking status at index_date
tmp_most_recent_smoking_cat = last_matching_event_clinical_ctv3_before(smoking_clear, index_date).ctv3_code.to_category(smoking_clear)
tmp_ever_smoked = last_matching_event_clinical_ctv3_before(ever_smoking, index_date).exists_for_patient() # uses a different codelist with ONLY smoking codes
dataset.cov_cat_smoking_status = case(
    when(tmp_most_recent_smoking_cat == "S").then("S"),
    when(tmp_most_recent_smoking_cat == "E").then("E"),
    when((tmp_most_recent_smoking_cat == "N") & (tmp_ever_smoked == True)).then("E"),
    when(tmp_most_recent_smoking_cat == "N").then("N"),
    when((tmp_most_recent_smoking_cat == "M") & (tmp_ever_smoked == True)).then("E"),
    when(tmp_most_recent_smoking_cat == "M").then("M"),
    otherwise = "M")
## Care home resident at index_date, see https://github.com/opensafely/opioids-covid-research/blob/main/analysis/define_dataset_table.py
# Flag care home based on primis (patients in long-stay nursing and residential care)
tmp_care_home_code = last_matching_event_clinical_snomed_before(carehome, index_date).exists_for_patient()
# Flag care home based on TPP
tmp_care_home_tpp1 = addresses.for_patient_on(index_date).care_home_is_potential_match
tmp_care_home_tpp2 = addresses.for_patient_on(index_date).care_home_requires_nursing
tmp_care_home_tpp3 = addresses.for_patient_on(index_date).care_home_does_not_require_nursing
# combine
dataset.cov_bin_carehome_status = case(
    when(tmp_care_home_code).then(True),
    when(tmp_care_home_tpp1).then(True),
    when(tmp_care_home_tpp2).then(True),
    when(tmp_care_home_tpp3).then(True),
    otherwise = False)
## Treatment status at first hosp treatment with bari
dataset.cov_status_bari_hosp_first = first_matching_event_bari_between("hospitalised_with", studystart_date, studyend_date).current_status 

## Comorbidities ##
## Solid cancer
dataset.cov_solid_cancer_new = last_matching_event_clinical_snomed_between(non_haematological_cancer_opensafely_snomed_codes_new + lung_cancer_opensafely_snomed_codes + chemotherapy_radiotherapy_opensafely_snomed_codes, index_date - days(180), index_date).exists_for_patient()
dataset.cov_solid_cancer_ever = last_matching_event_clinical_snomed_before(non_haematological_cancer_opensafely_snomed_codes_new + lung_cancer_opensafely_snomed_codes + chemotherapy_radiotherapy_opensafely_snomed_codes, index_date).exists_for_patient()



