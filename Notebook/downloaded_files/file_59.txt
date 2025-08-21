from ehrql import Dataset, codelist_from_csv
from ehrql.tables.beta.core import medications
from ehrql.tables.beta.tpp import practice_registrations

subcutaneous_morphine_codelist = codelist_from_csv(
    "codelists/opensafely-morphine-subcutaneous-dmd.csv",
    column="dmd_id",
)

dataset = Dataset()

dataset.define_population(
    practice_registrations.where(
        practice_registrations.start_date.is_on_or_after("2018-01-01")
        & (
            practice_registrations.end_date.is_on_or_before("2021-12-31")
            | practice_registrations.end_date.is_null()
        )
    ).exists_for_patient()
)

dataset.num_subcutaneous_morphine_events = medications.where(
    medications.dmd_code.is_in(subcutaneous_morphine_codelist)
    & medications.date.is_on_or_between("2018-01-01", "2021-12-31")
).count_for_patient()
