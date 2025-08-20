from ehrql import codelist_from_csv

diabetes_codelist = codelist_from_csv(
    "codelists/nhsd-primary-care-domain-refsets-dm_cod.csv",
    column="code",
    category_column="term"
)
diabetes_resolved_codelist = codelist_from_csv(
    "codelists/nhsd-primary-care-domain-refsets-dmres_cod.csv",
    column="code",
    category_column="term"
)