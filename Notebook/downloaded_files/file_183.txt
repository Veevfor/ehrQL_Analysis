#######################################################################################
# IMPORT
#######################################################################################
from ehrql import codelist_from_csv

#######################################################################################
# Codelists
#######################################################################################
# prostate
prostate_cancer_icd10 = codelist_from_csv("codelists/user-RochelleKnight-prostate_cancer_icd10.csv",column="code")
prostate_cancer_snomed_clinical = codelist_from_csv("codelists/user-RochelleKnight-prostate_cancer_snomed.csv",column="code")

# pregnancy
pregnancy_snomed_clinical = codelist_from_csv("codelists/user-RochelleKnight-pregnancy_and_birth_snomed.csv",column="code")

# combined oral contraceptive pill
cocp_dmd = codelist_from_csv("codelists/user-elsie_horne-cocp_dmd.csv",column="dmd_id")

# hormone replacement therapy
hrt_dmd = codelist_from_csv("codelists/user-elsie_horne-hrt_dmd.csv",column="dmd_id")

# ethnicity
ethnicity_codes = codelist_from_csv(
    "codelists/opensafely-ethnicity.csv",
    column="Code",
    category_column="Grouping_6",
)

## COVID-19
covid_primary_care_positive_test = codelist_from_csv("codelists/opensafely-covid-identification-in-primary-care-probable-covid-positive-test.csv", column="CTV3ID")
covid_primary_care_code = codelist_from_csv("codelists/opensafely-covid-identification-in-primary-care-probable-covid-clinical-code.csv", column="CTV3ID")
covid_primary_care_sequelae = codelist_from_csv("codelists/opensafely-covid-identification-in-primary-care-probable-covid-sequelae.csv", column="CTV3ID")
covid_codes = codelist_from_csv("codelists/user-RochelleKnight-confirmed-hospitalised-covid-19.csv", column="code") # only PCR-confirmed! => U071 (covid19 virus identified)

# smoking
smoking_clear = codelist_from_csv("codelists/opensafely-smoking-clear.csv",
    column="CTV3Code",
    category_column="Category",
)
ever_smoking = codelist_from_csv("codelists/user-alainamstutz-ever-smoking-bristol.csv",column="code")

# Patients in long-stay nursing and residential care
carehome = codelist_from_csv("codelists/primis-covid19-vacc-uptake-longres.csv",column="code")

### Solid cancer
non_haematological_cancer_opensafely_snomed_codes_new = codelist_from_csv("codelists/opensafely-cancer-excluding-lung-and-haematological-snomed.csv", column = "id")
lung_cancer_opensafely_snomed_codes = codelist_from_csv("codelists/opensafely-lung-cancer-snomed.csv", column = "id")
chemotherapy_radiotherapy_opensafely_snomed_codes = codelist_from_csv("codelists/opensafely-chemotherapy-or-radiotherapy-snomed.csv", column = "id")