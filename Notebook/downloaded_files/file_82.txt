from ehrql import create_dataset, months, days
from ehrql.tables.tpp import patients, clinical_events

from datetime import date

from codelists import pharmacy_first_clinical_pathways_cod

dataset = create_dataset()
dataset.configure_dummy_data(population_size=1000)

dataset.define_population(patients.exists_for_patient())

# Dictionary of pharmacy first codes
pharmacy_first_events_dict = {
    # Community Pharmacist (CP) Consultation Service for minor illness (procedure)
    "comm_pharm_consultation_service": ["1577041000000109"],
    # Pharmacy First service (qualifier value)
    "pharm_first_service": ["983341000000102"],
}

pharmacy_first_event_codes = [
    code for codelist in pharmacy_first_events_dict.values() for code in codelist
]

# https://www.england.nhs.uk/primary-care/pharmacy/pharmacy-first/
# For further projects we should review if choosing the actual start date
# will give us the most accurate cut-off in OpenSAFELY
pharmacy_first_launch_date = date(2024, 2, 1)

# Time interval for selecting medications pre and post Pharmacy First launch date
time_interval = months(6)

pharmacy_first_ids = clinical_events.where(
    clinical_events.snomedct_code.is_in(pharmacy_first_event_codes)
).consultation_id

pharmacy_first_dates = clinical_events.where(
    clinical_events.snomedct_code.is_in(pharmacy_first_event_codes)
).date

# Select clinical events pre and post PF launch date
selected_all_events_pre = clinical_events.where(
    clinical_events.date.is_on_or_between(
        pharmacy_first_launch_date - time_interval,
        pharmacy_first_launch_date - days(1),
    )
).sort_by(clinical_events.date)

selected_pfid_events_pre = selected_all_events_pre.where(
    clinical_events.consultation_id.is_in(pharmacy_first_ids)
)

selected_pfdate_events_pre = selected_all_events_pre.where(
    clinical_events.date.is_in(pharmacy_first_dates)
)

selected_all_events_post = clinical_events.where(
    clinical_events.date.is_on_or_between(
        pharmacy_first_launch_date, pharmacy_first_launch_date + time_interval
    )
).sort_by(clinical_events.date)

selected_pfid_events_post = selected_all_events_post.where(
    clinical_events.consultation_id.is_in(pharmacy_first_ids)
)

selected_pfdate_events_post = selected_all_events_post.where(
    clinical_events.date.is_in(pharmacy_first_dates)
)

selected_events_dict = {
    "pre_all": selected_all_events_pre,
    "pre_pfid": selected_pfid_events_pre,
    "pre_pfdate": selected_pfdate_events_pre,
    "post_all": selected_all_events_post,
    "post_pfid": selected_pfid_events_post,
    "post_pfdate": selected_pfdate_events_post,
}

pf_codelists_dict = {
    "pf_events": pharmacy_first_event_codes,
    "pf_pathways": pharmacy_first_clinical_pathways_cod,
}

# Count distinct pharmacy first consultations per patient
for time_interval_desc, selected_events in selected_events_dict.items():
    count_distinct_consultations_query = (
        selected_events.consultation_id.count_distinct_for_patient()
    )
    dataset.add_column(
        f"{time_interval_desc}_count_distinct_ids",
        count_distinct_consultations_query,
    )

# Count pharmacy first codes
for code_desc, code in pf_codelists_dict.items():
    for time_interval_desc, selected_events in selected_events_dict.items():
        count_codes_query = selected_events.where(
            selected_events.snomedct_code.is_in(code)
        ).count_for_patient()
        dataset.add_column(f"{time_interval_desc}_count_{code_desc}", count_codes_query)
