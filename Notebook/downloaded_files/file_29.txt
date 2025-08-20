from ehrql import create_dataset, get_parameter
from ehrql.tables.core import patients

year = get_parameter("year", default="2025")
index_date = f"{year}-01-01"

dataset = create_dataset()
dataset.age = patients.age_on(index_date)
dataset.define_population(dataset.age > 17)
