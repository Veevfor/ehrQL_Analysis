###<codelists.py> for repo: <prophy_effects_Sotro_Molnup>
##Description: This script extracts data for project 91:[Coverage, effectiveness and safety 
##of neutralising monoclonal antibodies or antivirals for non-hospitalised patients with COVID-19]
##   Date last updated: 10/05/2024 by  Qing Wen

from ehrql import codelist_from_csv 

# --- CODELISTS ---
covid_icd10_codes = ["U071", "U072", "U099","U109"]
#https://github.com/opensafely/documentation/discussions/1480

## HIGH RISK GROUPS ----
# dialysis
dialysis_codes = codelist_from_csv(
  "codelists/opensafely-dialysis.csv",
   column = "CTV3ID"
)
dialysis_icd10_codelist = codelist_from_csv(
    "codelists/ukrr-dialysis-icd10.csv",
    column="code"
)
dialysis_opcs4_codelist = codelist_from_csv(
    "codelists/ukrr-dialysis-opcs-4.csv",
    column="code"
)
# # kidney transplant
kidney_transplant_codes = codelist_from_csv(
  "codelists/opensafely-kidney-transplant.csv",
  column = "CTV3ID"
)
# kidney_tx_icd10_codelist=codelist(["Z940"], system="icd10")
kidney_tx_icd10_codelist = (["Z940"])

kidney_tx_opcs4_codelist = codelist_from_csv(
    "codelists/user-viyaasan-kidney-transplant-opcs-4.csv",
    # system="opcs4",
    column="code"
)

# ### Sickle cell disease
sickle_cell_disease_nhsd_snomed_codes = codelist_from_csv(
  "codelists/nhsd-sickle-spl-atriskv4-snomed-ct.csv",
   column = "code",
)

sickle_cell_disease_nhsd_icd10_codes = codelist_from_csv(
  "codelists/nhsd-sickle-spl-hes-icd-10.csv",
  column = "code",
)

# ### Solid cancer
non_haematological_cancer_opensafely_snomed_codes = codelist_from_csv(
  "codelists/opensafely-cancer-excluding-lung-and-haematological-snomed.csv",
  column = "id",
)
non_haematological_cancer_opensafely_snomed_codes_new = codelist_from_csv(
  "codelists/user-bangzheng-cancer-excluding-lung-and-haematological-snomed-new.csv",
  column = "code",
)
lung_cancer_opensafely_snomed_codes = codelist_from_csv(
  "codelists/opensafely-lung-cancer-snomed.csv", 
  column = "id"
)

chemotherapy_radiotherapy_opensafely_snomed_codes = codelist_from_csv(
  "codelists/opensafely-chemotherapy-or-radiotherapy-snomed.csv", 
  column = "id"
)

# ### Patients with a haematological diseases
haematopoietic_stem_cell_transplant_nhsd_snomed_codes = codelist_from_csv(
  "codelists/nhsd-haematopoietic-stem-cell-transplant-snomed.csv", 
  column = "code"
)

haematopoietic_stem_cell_transplant_nhsd_icd10_codes = codelist_from_csv(
  "codelists/nhsd-haematopoietic-stem-cell-transplant-icd-10.csv", 
  column = "code"
)

haematopoietic_stem_cell_transplant_nhsd_opcs4_codes = codelist_from_csv(
  "codelists/nhsd-haematopoietic-stem-cell-transplant-opcs4.csv", 
  column = "code"
)

haematological_malignancies_nhsd_snomed_codes = codelist_from_csv(
  "codelists/nhsd-haematological-malignancies-snomed.csv",
  column = "code"
)

haematological_malignancies_nhsd_icd10_codes = codelist_from_csv(
  "codelists/nhsd-haematological-malignancies-icd-10.csv", 
  column = "code"
)

## Patients with renal disease
## Immune-mediated inflammatory disorders (IMID)
immunosuppresant_drugs_dmd_codes = codelist_from_csv(
  "codelists/nhsd-immunosuppresant-drugs-pra-dmd.csv", 
  column = "code"
)

immunosuppresant_drugs_snomed_codes = codelist_from_csv(
  "codelists/nhsd-immunosuppresant-drugs-pra-snomed.csv", 
  column = "code"
)

oral_steroid_drugs_dmd_codes = codelist_from_csv(
  "codelists/nhsd-oral-steroid-drugs-pra-dmd.csv",
  column = "dmd_id",
)

oral_steroid_drugs_snomed_codes = codelist_from_csv(
  "codelists/nhsd-oral-steroid-drugs-snomed.csv", 
  column = "code"
)

## Primary immune deficiencies
immunosupression_nhsd_codes = codelist_from_csv(
  "codelists/nhsd-immunosupression-pcdcluster-snomed-ct.csv",
  column = "code",
)
immunosupression_nhsd_codes_new = codelist_from_csv(
  "codelists/user-bangzheng-nhsd-immunosupression-pcdcluster-snomed-ct-new.csv",
  column = "code",
)

## Solid organ transplant
solid_organ_transplant_codes = codelist_from_csv(
    "codelists/opensafely-solid-organ-transplantation-snomed.csv",
    column = "id",
)

solid_organ_transplant_nhsd_snomed_codes = codelist_from_csv(
  "codelists/nhsd-transplant-spl-atriskv4-snomed-ct.csv",
  column = "code",
)
solid_organ_transplant_nhsd_snomed_codes_new = codelist_from_csv(
  "codelists/user-bangzheng-nhsd-transplant-spl-atriskv4-snomed-ct-new.csv",
  column = "code",
)
solid_organ_transplant_nhsd_opcs4_codes = codelist_from_csv(
  "codelists/nhsd-transplant-spl-hes-opcs4.csv", 
  column = "code"
)

thymus_gland_transplant_nhsd_opcs4_codes = codelist_from_csv(
  "codelists/nhsd-transplant-thymus-gland-spl-hes-opcs4.csv", 
  column = "code"
)

replacement_of_organ_transplant_nhsd_opcs4_codes = codelist_from_csv(
  "codelists/nhsd-transplant-replacement-of-organ-spl-hes-opcs4.csv", 
  column = "code"
)

conjunctiva_transplant_nhsd_opcs4_codes = codelist_from_csv(
  "codelists/nhsd-transplant-conjunctiva-spl-hes-opcs4.csv", 
  column = "code"
)

conjunctiva_y_codes_transplant_nhsd_opcs4_codes = codelist_from_csv(
  "codelists/nhsd-transplant-conjunctiva-y-codes-spl-hes-opcs4.csv", 
  column = "code"
)

stomach_transplant_nhsd_opcs4_codes = codelist_from_csv(
  "codelists/nhsd-transplant-stomach-spl-hes-opcs4.csv", 
  column = "code"
)

ileum_1_transplant_nhsd_opcs4_codes = codelist_from_csv(
  "codelists/nhsd-transplant-ileum_1-spl-hes-opcs4.csv", 
  column = "code"
)

ileum_2_transplant_nhsd_opcs4_codes = codelist_from_csv(
  "codelists/nhsd-transplant-ileum_2-spl-hes-opcs4.csv", 
  column = "code"
)

ileum_1_y_codes_transplant_nhsd_opcs4_codes = codelist_from_csv(
  "codelists/nhsd-transplant-ileum_1-y-codes-spl-hes-opcs4.csv", 
  column = "code"
)

ileum_2_y_codes_transplant_nhsd_opcs4_codes = codelist_from_csv(
  "codelists/nhsd-transplant-ileum_2-y-codes-spl-hes-opcs4.csv", 
  column = "code"
)

## CLINICAL/DEMOGRAPHIC COVARIATES ----

ethnicity_codelist_with_categories = codelist_from_csv(
    "codelists/opensafely-ethnicity-snomed-0removed.csv",
    column = "snomedcode",
    category_column = "Grouping_6"
)

## OTHER COVARIATES ----
# Care home 
care_home_primis_snomed_codes = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-longres.csv", 
    column = "code")

# carehome_primis_codes = codelist_from_csv(
#   "codelists/primis-covid19-vacc-uptake-longres.csv", 
#   column = "code",
# )


## Pregnancy
pregnancy_primis_codes = codelist_from_csv(
  "codelists/primis-covid19-vacc-uptake-preg.csv",
  column = "code",
)

## Pregnancy or delivery
pregdel_primis_codes = codelist_from_csv(
  "codelists/primis-covid19-vacc-uptake-pregdel.csv",
  column = "code",
)

# SUS-HES mabs
#mabs_procedure_codes = ["X891", "X892"]  #system="opcs4"

# drugs_consider_risk_codes = codelist_from_csv(
#   "codelists/opensafely-nirmatrelvir-drug-interactions-3d3644f8-dmd.csv", 
#   system = "snomed", 
#   column = "dmd_id"
# )

# Chronic cardiac disease
chronic_cardiac_dis_codes = codelist_from_csv(
    "codelists/opensafely-chronic-cardiac-disease-snomed.csv",
    column="id"
)

# Chronic respiratory disease
chronic_respiratory_dis_codes = codelist_from_csv(
    "codelists/opensafely-chronic-respiratory-disease-snomed.csv",
    column="id"
)

# Diabetes
diabetes_codes = codelist_from_csv(
    "codelists/opensafely-diabetes-snomed.csv",
    #system="snomed",  #
    column="id"
)
# Hypertension
hypertension_codes = codelist_from_csv(
    "codelists/opensafely-hypertension-snomed.csv",
    #system="snomed",
    column="id"
)

# Dementia
dementia_nhsd_snomed_codes = codelist_from_csv(
  "codelists/nhsd-primary-care-domain-refsets-dem_cod.csv", 
#   system = "snomed", 
  column = "code",
)

# Learning disabilities
wider_ld_primis_snomed_codes = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-learndis.csv", 
#    system = "snomed", 
    column = "code"
)
 ## Autism
autism_nhsd_snomed_codes = codelist_from_csv(
  "codelists/nhsd-primary-care-domain-refsets-autism_cod.csv",
#  system = "snomed",
  column = "code",
)

## Serious mental illness
serious_mental_illness_nhsd_snomed_codes = codelist_from_csv(
  "codelists/nhsd-primary-care-domain-refsets-mh_cod.csv",
#  system = "snomed",
  column = "code",
)
## ELIGIBILITY CRITERIA VARIABLES ----
## Onset of symptoms of COVID-19
# covid_symptoms_snomed_codes = codelist_from_csv(
#   "codelists/user-MillieGreen-covid-19-symptoms.csv",
#   system = "snomed",
#   column = "code",
# )

## Require hospitalisation for COVID-19
# covid_icd10_codes = codelist_from_csv(
#   "codelists/opensafely-covid-identification.csv",
#   system = "icd10",
#   column = "icd10_code",
# )

## Housebound
housebound_opensafely_snomed_codes = codelist_from_csv(
    "codelists/opensafely-housebound.csv", 
#    system = "snomed", 
    column = "code"
)

no_longer_housebound_opensafely_snomed_codes = codelist_from_csv(
    "codelists/opensafely-no-longer-housebound.csv", 
 #   system = "snomed", 
    column = "code"
)

## Care home 
care_home_primis_snomed_codes = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-longres.csv", 
#    system = "snomed", 
    column = "code")

## Vaccination declined
# first_dose_declined = codelist_from_csv(
#   "codelists/opensafely-covid-19-vaccination-first-dose-declined.csv",
#   system = "snomed",
#   column = "code",
# )

## second_dose_declined = codelist_from_csv(
#   "codelists/opensafely-covid-19-vaccination-second-dose-declined.csv",
#   system = "snomed",
#   column = "code",
# )

# covid_vaccine_declined_codes = combine_codelists(
#   first_dose_declined, second_dose_declined
# )

# OTHER COVARIATES ----
# ## Shielded
# high_risk_primis_snomed_codes = codelist_from_csv(
#     "codelists/primis-covid19-vacc-uptake-shield.csv", 
#     system = "snomed", 
#     column = "code")

# not_high_risk_primis_snomed_codes = codelist_from_csv(
#     "codelists/primis-covid19-vacc-uptake-nonshield.csv", 
#     system = "snomed", 
#     column = "code")
    
