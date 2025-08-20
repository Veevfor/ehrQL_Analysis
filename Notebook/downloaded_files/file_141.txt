from ehrql import create_dataset, months, days
from ehrql.tables.tpp import patients, clinical_events
from ehrql.tables.raw.tpp import medications

from datetime import date

from codelists import *

dataset = create_dataset()
dataset.configure_dummy_data(population_size=1000)

dataset.define_population(patients.exists_for_patient())

# https://www.england.nhs.uk/primary-care/pharmacy/pharmacy-first/
pharmacy_first_launch_date = date(2024, 2, 1)

# Time interval for selecting medications pre and post Pharmacy First launch date
time_interval = months(6)

pharmacy_first_ids = clinical_events.where(
    clinical_events.snomedct_code.is_in(pharmacy_first_event_codes)
).consultation_id

pharmacy_first_dates = clinical_events.where(
    clinical_events.snomedct_code.is_in(pharmacy_first_event_codes)
).date

# Select medications
# Pre launch, any medication
selected_medications_any_pre = medications.where(
    medications.date.is_on_or_between(
        pharmacy_first_launch_date - time_interval,
        pharmacy_first_launch_date - days(1),
    )
).sort_by(medications.date)

# Pre launch, pharmacy first medication (pfmed)
selected_medications_pfmed_pre = (
    medications.where(
        medications.date.is_on_or_between(
            pharmacy_first_launch_date - time_interval,
            pharmacy_first_launch_date - days(1),
        )
    )
    .where(medications.dmd_code.is_in(pharmacy_first_med_codes))
    .sort_by(medications.date)
)

# Pre launch, pharmacy first id (pdid) identified through clinical events
# and pharmacy first medication (pfmed)
selected_medications_pfmed_pfid_pre = (
    medications.where(
        medications.date.is_on_or_between(
            pharmacy_first_launch_date - time_interval,
            pharmacy_first_launch_date - days(1),
        )
    )
    .where(medications.dmd_code.is_in(pharmacy_first_med_codes))
    .where(medications.consultation_id.is_in(pharmacy_first_ids))
    .sort_by(medications.date)
)

# Pre launch, pharmacy first id, any medication
selected_medications_anymed_pfid_pre = (
    medications.where(
        medications.date.is_on_or_between(
            pharmacy_first_launch_date - time_interval,
            pharmacy_first_launch_date - days(1),
        )
    )
    .where(medications.consultation_id.is_in(pharmacy_first_ids))
    .sort_by(medications.date)
)

# Pre launch, pharmacy first id, same day medication
selected_medications_pfdate_pfid_pre = (
    medications.where(
        medications.date.is_on_or_between(
            pharmacy_first_launch_date - time_interval,
            pharmacy_first_launch_date - days(1),
        )
    )
    .where(medications.consultation_id.is_in(pharmacy_first_ids))
    .where(medications.date.is_in(pharmacy_first_dates))
    .sort_by(medications.date)
)

# Post launch, any medication
selected_medications_any_post = medications.where(
    medications.date.is_on_or_between(
        pharmacy_first_launch_date, pharmacy_first_launch_date + time_interval
    )
).sort_by(medications.date)

# Post launch, pharmacy first medication (pfmed)
selected_medications_pfmed_post = (
    medications.where(
        medications.date.is_on_or_between(
            pharmacy_first_launch_date, pharmacy_first_launch_date + time_interval
        )
    )
    .where(medications.dmd_code.is_in(pharmacy_first_med_codes))
    .sort_by(medications.date)
)

# Post launch, pharmacy first id (pdid) identified through clinical events
# and pharmacy first medication (pfmed)
selected_medications_pfmed_pfid_post = (
    medications.where(
        medications.date.is_on_or_between(
            pharmacy_first_launch_date, pharmacy_first_launch_date + time_interval
        )
    )
    .where(medications.dmd_code.is_in(pharmacy_first_med_codes))
    .where(medications.consultation_id.is_in(pharmacy_first_ids))
    .sort_by(medications.date)
)

# Post launch, pharmacy first id, any medication
selected_medications_anymed_pfid_post = (
    medications.where(
        medications.date.is_on_or_between(
            pharmacy_first_launch_date, pharmacy_first_launch_date + time_interval
        )
    )
    .where(medications.consultation_id.is_in(pharmacy_first_ids))
    .sort_by(medications.date)
)

# Post launch, pharmacy first id, same day medication
selected_medications_pfdate_pfid_post = (
    medications.where(
        medications.date.is_on_or_between(
            pharmacy_first_launch_date, pharmacy_first_launch_date + time_interval
        )
    )
    .where(medications.consultation_id.is_in(pharmacy_first_ids))
    .where(medications.date.is_in(pharmacy_first_dates))
    .sort_by(medications.date)
)

# Pre launch, pharmacy first med, same day as pf consultation
selected_medications_pfmed_pfdate_pre = (
    medications.where(
        medications.date.is_on_or_between(
            pharmacy_first_launch_date - time_interval,
            pharmacy_first_launch_date - days(1),
        )
    )
    .where(medications.dmd_code.is_in(pharmacy_first_med_codes))
    .where(medications.date.is_in(pharmacy_first_dates))
    .sort_by(medications.date)
)

# Post launch, pharmacy first med, same day as pf consultation
selected_medications_pfmed_pfdate_post = (
    medications.where(
        medications.date.is_on_or_between(
            pharmacy_first_launch_date, pharmacy_first_launch_date + time_interval
        )
    )
    .where(medications.dmd_code.is_in(pharmacy_first_med_codes))
    .where(medications.date.is_in(pharmacy_first_dates))
    .sort_by(medications.date)
)

# Pre launch, any med, same day as pf consultation
selected_medications_anymed_pfdate_pre = (
    medications.where(
        medications.date.is_on_or_between(
            pharmacy_first_launch_date - time_interval,
            pharmacy_first_launch_date - days(1),
        )
    )
    .where(medications.date.is_in(pharmacy_first_dates))
    .sort_by(medications.date)
)

# Post launch, any med, same day as pf consultation
selected_medications_anymed_pfdate_post = (
    medications.where(
        medications.date.is_on_or_between(
            pharmacy_first_launch_date, pharmacy_first_launch_date + time_interval
        )
    )
    .where(medications.date.is_in(pharmacy_first_dates))
    .sort_by(medications.date)
)

selected_medications_dict = {
    "pre_anymed": selected_medications_any_pre,
    "pre_anypfid": selected_medications_anymed_pfid_pre,
    "pre_anypfdate": selected_medications_anymed_pfdate_pre,
    "pre_pfmed": selected_medications_pfmed_pre,
    "pre_pfmedid": selected_medications_pfmed_pfid_pre,
    "pre_pfmedpfdate": selected_medications_pfmed_pfdate_pre,
    "post_anymed": selected_medications_any_post,
    "post_anypfid": selected_medications_anymed_pfid_post,
    "post_anypfdate": selected_medications_anymed_pfdate_post,
    "post_pfmed": selected_medications_pfmed_post,
    "post_pfmedid": selected_medications_pfmed_pfid_post,
    "post_pfmedpfdate": selected_medications_pfmed_pfdate_post,
}

# Count all medication status
# This will add 6 x 28 = 168 new columns
for desc, selected_medications in selected_medications_dict.items():
    for status in range(29):
        count_med_status_query = selected_medications.where(
            selected_medications.medication_status.is_in([status])
        ).count_for_patient()
        dataset.add_column(f"{desc}_status{status}", count_med_status_query)
