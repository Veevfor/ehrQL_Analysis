from ehrql import Dataset
from ehrql.tables.beta.core import patients

index_date = "2020-03-31"

dataset = Dataset()

dataset.age = patients.age_on(index_date)

dataset.define_population((dataset.age > 18))
