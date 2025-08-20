
##########################
# extract patient information as at a fixed date, with vaccination dates ascertained retrospectively
##########################



from ehrql import Dataset
from ehrql.tables.beta.tpp import patients, clinical_events, practice_registrations, vaccinations, ons_deaths


index_date = "2023-09-01"

registered_patients = practice_registrations.for_patient_on(index_date)

# initialise dataset
dataset = Dataset()

# define dataset poppulation
dataset.define_population(registered_patients.exists_for_patient())

dataset.sex = patients.sex
dataset.age = patients.age_on(index_date)

dataset.registered = registered_patients.exists_for_patient()
dataset.region = registered_patients.practice_nuts1_region_name
dataset.stp = registered_patients.practice_stp
dataset.death_date = ons_deaths.sort_by(ons_deaths.date).first_for_patient().date


