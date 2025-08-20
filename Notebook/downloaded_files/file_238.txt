from ehrql import create_measures, months
from ehrql.tables.core import patients

from analysis.dataset_definition import on_register, dataset

measures = create_measures()

measures.define_measure(
    name="prt_or_mal",
    numerator=dataset.prt_or_mal,
    denominator=on_register,
    group_by={
        "sex": patients.sex
    },
    intervals=months(12).starting_on("2025-01-01"),
)

measures.define_measure(
    name="ace_or_arb",
    numerator=dataset.ace_or_arb,
    denominator=on_register,
    group_by={
        "sex": patients.sex
    },
    intervals=months(12).starting_on("2025-01-01"),
)
