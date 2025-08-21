# Import functions that will be used for dataset definition
from ehrql import create_dataset
from ehrql import codelist_from_csv
from ehrql import Path

# Import the tables of the variables which you need to define the dataset
from ehrql.tables.tpp import patients, practice_registrations, clinical_events

## could use from ehrql.tables.core or from ehrql.tables.emis

# Create an empty dataset - we will be adding columns to this, based on which we will filter data
dataset = create_dataset()

# Create objects containing codelists - these will be used to define the dataset
codelist_path = Path("codelists")
dm_cod = codelist_from_csv(
    codelist_path / "nhsd-primary-care-domain-refsets-dm_cod.csv",
    column="code",
)
dmres_cod = codelist_from_csv(
    codelist_path / "nhsd-primary-care-domain-refsets-dmres_cod.csv",
    column="code",
)

# Simpler:
dm_cod = codelist_from_csv(
    "codelists/nhsd-primary-care-domain-refsets-dm_cod.csv",
    column="code",
)
dmres_cod = codelist_from_csv(
    "codelists/nhsd-primary-care-domain-refsets-dmres_cod.csv",
    column="code",
)

# Create index date
index_date = "2024-03-31"

# Create a boolean vector for which patients were registered up until the index date
registered = practice_registrations.for_patient_on(index_date).exists_for_patient()

# However, unless we add this information to the dataset, we won't be able to filter based on it, using dataset.define_population
##So first, we need to add a column to the dataset which defines which patients are registered
dataset.registered = practice_registrations.for_patient_on(
    index_date
).exists_for_patient()

# Derive patient age from the DOB and add to the dataset
dataset.pat_age = patients.age_on(index_date)

# Derive latest dates for Dx DM and Dx DM res for each patient, and add them to the dataset

## Select the latest date with the diabetes code and add it to the dataset
dataset.latest_dm = (
    clinical_events.where(clinical_events.snomedct_code.is_in(dm_cod))
    .sort_by(clinical_events.date)
    .last_for_patient()
    .date
)


## Select the latest date with the diabetes resolved code and add it to the dataset
dataset.latest_dmres = (
    clinical_events.where(clinical_events.snomedct_code.is_in(dmres_cod))
    .sort_by(clinical_events.date)
    .last_for_patient()
    .date
)

# Define the dataset (=cohort) - using the rules

##Rule 1
### Has a diabetes diagnosis before the index date
### Latest diabetes diagnosis is not followed by a diabetes resolved code.

dm_reg_r1 = (
    (dataset.latest_dm.is_not_null())
    & (dataset.latest_dm < index_date)
    & ((dataset.latest_dmres < dataset.latest_dm) | dataset.latest_dmres.is_null())
)

##Rule 2
### Needs to be minimim 17 years old on the index date

dm_reg_r2 = dataset.pat_age >= 17

# Create the population
dataset.define_population(registered & dm_reg_r1 & dm_reg_r2)
