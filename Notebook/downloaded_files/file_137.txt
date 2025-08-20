from ehrql import create_dataset, codelist_from_csv
from ehrql.tables.beta.core import medications
from ehrql.tables.beta.tpp import practice_registrations


# Medications of interest
paxlovid_GP_codes = codelist_from_csv("codelists/user-bangzheng-paxlovid-dmd.csv", column="code")

dataset = create_dataset()

def paxlovid_prescriptions_between(start, end):
    return (
        medications
        .where(medications.dmd_code.is_in(paxlovid_GP_codes))
        .where(medications.date.is_on_or_between(start, end))
        .sort_by(medications.date)
        .count_for_patient()
    )

# Find prescription counts per patient per month May-August
dataset.may = paxlovid_prescriptions_between("2023-05-01", "2023-05-31")
dataset.june = paxlovid_prescriptions_between("2023-06-01", "2023-06-30")
dataset.july = paxlovid_prescriptions_between("2023-07-01", "2023-07-31")
dataset.august = paxlovid_prescriptions_between("2023-08-01", "2023-08-31")

# Define population as patients registered with a practice between the relevant dates
registered_at_start = practice_registrations.for_patient_on("2023-01-05").exists_for_patient()
registered_at_end = practice_registrations.for_patient_on("2023-08-30").exists_for_patient()
dataset.define_population(registered_at_start & registered_at_end)
