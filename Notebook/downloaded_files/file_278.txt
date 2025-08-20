from ehrql import codelist_from_csv


t1dm_cod = codelist_from_csv(
    "codelists/nhsd-primary-care-domain-refsets-dmtype1_cod.csv",
    column="code",
)

t2dm_cod = codelist_from_csv(
    "codelists/nhsd-primary-care-domain-refsets-dmtype2_cod.csv",
    column="code",
)

dmres_cod = codelist_from_csv(
    "codelists/nhsd-primary-care-domain-refsets-dmres_cod.csv",
    column="code",
)

hba1c_cod = codelist_from_csv(
    "codelists/opensafely-glycated-haemoglobin-hba1c-tests-numerical-value.csv",
    column="code",
)

ethnicity = codelist_from_csv(
    "codelists/opensafely-ethnicity-snomed-0removed.csv",
    column="snomedcode",
    category_column="Grouping_6",
)

chronic_cardiac_disease = codelist_from_csv(
    "codelists/opensafely-chronic-cardiac-disease.csv",
    column="CTV3ID",
)

learning_disabilites = codelist_from_csv(
    "codelists/opensafely-learning-disabilities.csv",
    column="CTV3Code",
)

dpp4_inhibitors = codelist_from_csv(
    "codelists/user-alex-walker-dpp-4-inhibitors-dmd.csv",
    column="dmd_id",
)

glp1s = codelist_from_csv(
    "codelists/user-alex-walker-glp1s-dmd.csv",
    column="dmd_id",
)

glp1_combined_insulin = codelist_from_csv(
    "codelists/user-Andrew-glp-1s-in-combination-with-insulin-dmd.csv",
    column="dmd_id",
)

glp1_not_combined = codelist_from_csv(
    "codelists/user-Andrew-glp-1s-excluding-those-combined-insulin-dmd.csv",
    column="dmd_id",
)

insulin = codelist_from_csv(
    "codelists/user-alex-walker-insulin-dmd.csv",
    column="dmd_id",
)

insulin_basal = codelist_from_csv(
    "codelists/user-Andrew-insulin-long-acting-basal-dmd.csv",
    column="dmd_id",
)

insulin_mixed_biphasic = codelist_from_csv(
    "codelists/user-Andrew-mixed-biphasic-insulin-dmd.csv",
    column="dmd_id",
)

metformin = codelist_from_csv(
    "codelists/user-alex-walker-metformin-dmd.csv",
    column="dmd_id",
)

pioglitazone = codelist_from_csv(
    "codelists/user-alex-walker-pioglitazone-dmd.csv",
    column="dmd_id",
)

sglt_2_inhibitors = codelist_from_csv(
    "codelists/user-alex-walker-sglt-2-inhibitors-dmd.csv",
    column="dmd_id",
)

sulfonylureas = codelist_from_csv(
    "codelists/user-alex-walker-sulfonylureas-dmd.csv",
    column="dmd_id",
)

# Chronic kidney disease codes-stages 3 - 5
chronic_kidney_disease_stages_3_5_codes = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-ckd35.csv",
    column="code",
)
# Chronic kidney disease codes-stages 3 - 5
chronic_kidney_disease_stage_5_codes = codelist_from_csv(
    "codelists/nhsd-primary-care-domain-refsets-ckd5_cod.csv",
    column="code",
)
