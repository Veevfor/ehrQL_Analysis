
##########################
# extract patient information as at each vaccination date
##########################

from ehrql import Dataset
from ehrql.tables.beta.tpp import patients, medications, clinical_events, practice_registrations, vaccinations




covid_vaccinations = (
  vaccinations
  .where(vaccinations.target_disease.is_in(["SARS-2 CORONAVIRUS"]))
  .sort_by(vaccinations.date)
)



# initialise dataset
dataset = Dataset()

# define dataset poppulation
dataset.define_population(covid_vaccinations.exists_for_patient())


# Arbitrary date guaranteed to be before any events of interest
previous_vax_date = "1899-01-01"

for i in range(1, 10+1):

    current_vax = covid_vaccinations.where(covid_vaccinations.date>previous_vax_date).first_for_patient()
    registration = practice_registrations.for_patient_on(current_vax.date)

    setattr(dataset, f"covid_vax_{i}_date", current_vax.date)
    setattr(dataset, f"covid_vax_type_{i}", current_vax.product_name)
    setattr(dataset, f"age_{i}", patients.age_on(current_vax.date))
    setattr(dataset, f"registered_{i}", registration.exists_for_patient())
    setattr(dataset, f"deregistered_{i}_date", registration.end_date)
    setattr(dataset, f"region_{i}", registration.practice_nuts1_region_name)
    setattr(dataset, f"stp_{i}", registration.practice_stp)

    previous_vax_date = current_vax.date

