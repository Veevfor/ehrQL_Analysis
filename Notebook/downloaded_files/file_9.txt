from ehrql import create_dataset, days, years, case, when
from ehrql.tables.beta.tpp import (
    patients,
    clinical_events,
    medications,
    practice_registrations,
    addresses,
)
from ehrql.codes import SNOMEDCTCode
from variable_lib_helper import (
    practice_registration_as_of,
    last_matching_event,
    last_matching_event_ctv3,
    last_matching_med,
)
import codelists


def generate_dataset(index_date):
    # Instantiate dataset
    dataset = create_dataset()

    # Extract prior events for further use in variable definitions below
    prior_events = clinical_events.where(
        clinical_events.date.is_on_or_before(index_date)
    )
    recent_meds = medications.where(
        medications.date.is_on_or_between(index_date - days(90), index_date)
    )

    # Demographic variables
    dataset.age = (index_date - patients.date_of_birth).years
    dataset.sex = patients.sex
    dataset.region = practice_registrations.for_patient_on(
        index_date
    ).practice_nuts1_region_name
    imd = addresses.for_patient_on(index_date).imd_rounded
    dataset.imd = case(
        when((imd >= 0) & (imd < 6569)).then(1),
        when((imd >= 6569) & (imd < 13138)).then(2),
        when((imd >= 13138) & (imd < 19706)).then(3),
        when((imd >= 19706) & (imd < 26275)).then(4),
        when((imd >= 26275) & (imd < 32844)).then(5),
        default=0,
    )
    dataset.ethnicity = (
        clinical_events.where(clinical_events.snomedct_code.is_in(codelists.ethnicity))
        .sort_by(clinical_events.date)
        .last_for_patient()
        .snomedct_code.to_category(codelists.ethnicity)
    )

    # Clinical stratifiers
    dataset.bmi = (
        prior_events.where(
            prior_events.snomedct_code.is_in(
                [SNOMEDCTCode("60621009"), SNOMEDCTCode("846931000000101")]
            )
        )
        # Exclude out-of-range values
        .where(
            (prior_events.numeric_value > 4.0) & (prior_events.numeric_value < 200.0)
        )
        # Exclude measurements taken when patient was younger than 16
        .where(prior_events.date >= patients.date_of_birth + years(16))
        .sort_by(prior_events.date)
        .last_for_patient()
        .numeric_value
    )
    dataset.cardiovascular_history = last_matching_event_ctv3(
        prior_events, codelists.chronic_cardiac_disease
    ).exists_for_patient()
    dataset.learning_difficulties = last_matching_event_ctv3(
        prior_events, codelists.learning_disabilites
    ).exists_for_patient()

    # CKD
    dataset.ckd35 = (
        prior_events.where(
            prior_events.snomedct_code.is_in(
                codelists.chronic_kidney_disease_stages_3_5_codes
            )
        )
        .sort_by(prior_events.date)
        .last_for_patient()
        .exists_for_patient()
    )
    dataset.ckd5 = (
        prior_events.where(
            prior_events.snomedct_code.is_in(
                codelists.chronic_kidney_disease_stage_5_codes
            )
        )
        .sort_by(prior_events.date)
        .last_for_patient()
        .exists_for_patient()
    )

    # Diabetes variables
    diabetes_resolved = last_matching_event(prior_events, codelists.dmres_cod).date

    last_t1dm = last_matching_event(prior_events, codelists.t1dm_cod).date
    dataset.t1dm = (diabetes_resolved < last_t1dm) | (
        last_t1dm.is_not_null() & diabetes_resolved.is_null()
    )

    last_t2dm = last_matching_event(prior_events, codelists.t2dm_cod).date
    dataset.t2dm = (diabetes_resolved < last_t2dm) | (
        last_t2dm.is_not_null() & diabetes_resolved.is_null()
    )

    # HbA1c
    dataset.hba1c = last_matching_event(prior_events, codelists.hba1c_cod).numeric_value
    dataset.hba1c_cat = case(
        when(dataset.hba1c <= 58).then("<=58"),
        when((dataset.hba1c > 58) & (dataset.hba1c <= 86)).then("58-86"),
        when(dataset.hba1c > 86).then(">86"),
        default="Missing",
    )
    dataset.hba1c_date = last_matching_event(prior_events, codelists.hba1c_cod).date

    # Medications
    dataset.dpp4_inhibitors = last_matching_med(recent_meds, codelists.dpp4_inhibitors)
    dataset.glp1s = last_matching_med(recent_meds, codelists.glp1s)
    dataset.glp1_combined_insulin = last_matching_med(
        recent_meds, codelists.glp1_combined_insulin
    )
    dataset.glp1_not_combined = last_matching_med(
        recent_meds, codelists.glp1_not_combined
    )
    dataset.insulin = last_matching_med(recent_meds, codelists.insulin)
    dataset.insulin_basal = last_matching_med(recent_meds, codelists.insulin_basal)
    dataset.insulin_mixed_biphasic = last_matching_med(
        recent_meds, codelists.insulin_mixed_biphasic
    )
    dataset.insulin_non_basal = (
        when(dataset.insulin_basal.is_null() & dataset.insulin_mixed_biphasic.is_null())
        .then(dataset.insulin)
        .otherwise(None)
    )
    dataset.metformin = last_matching_med(recent_meds, codelists.metformin)
    dataset.pioglitazone = last_matching_med(recent_meds, codelists.pioglitazone)
    dataset.sglt_2_inhibitors = last_matching_med(
        recent_meds, codelists.sglt_2_inhibitors
    )
    dataset.sulfonylureas = last_matching_med(recent_meds, codelists.sulfonylureas)

    # combine GLP-1s and insulin
    # for convenience of running downstream analysis code, we return the GLP-1
    #  dmd codes when the statement is true
    dataset.glp1s_and_insulin = (
        when(dataset.glp1s.is_not_null() & dataset.insulin.is_not_null())
        .then(dataset.glp1s)
        .otherwise(None)
    )

    dataset.glp1s_and_insulin_basal = (
        when(dataset.glp1s.is_not_null() & dataset.insulin_basal.is_not_null())
        .then(dataset.glp1s)
        .otherwise(None)
    )

    dataset.glp1s_and_insulin_non_basal = (
        when(dataset.glp1s.is_not_null() & dataset.insulin_non_basal.is_not_null())
        .then(dataset.glp1s)
        .otherwise(None)
    )

    dataset.glp1s_and_insulin_mixed_biphasic = (
        when(dataset.glp1s.is_not_null() & dataset.insulin_mixed_biphasic.is_not_null())
        .then(dataset.glp1s)
        .otherwise(None)
    )

    # Define population
    current_registration = practice_registration_as_of(index_date)
    dataset.define_population(
        (dataset.age < 110) & current_registration.exists_for_patient()
    )
    dataset.configure_dummy_dataset(population_size=1000)
    return dataset
