# To test dataset definition run the following command in the terminal:
# pytest tests/test_datasets.py
import os

import pandas as pd


# Load datasets
cwd = os.getcwd()
df_cohortextractor = pd.read_csv(f"{cwd}/output/dataset_cohortextractor_2022-09-25.csv")
df_ehrql = pd.read_csv(f"{cwd}/output/dataset_ehrql_2022-09-25.csv")


# Test dataset definition works as intended with dummy data
def test_dataset_definition():
    # arrange
    # act
    pt7 = df_ehrql.iloc[0].to_dict()

    # assert
    assert pt7 == {
        "patient_id": 7,
        "sex": "male",
        "age": 22,
        "has_died": "F",
        "care_home_tpp": "F",
        "care_home_code": "F",
        "msoa": "E02000010",
        "stp": "STP3",
        "region": "region_practice3",
        "registered": "T",
        "postest_01": "F",
        "postest_14": "F",
        "postest_ever": "T",
        "primary_care_covid_case_01": "F",
        "primary_care_covid_case_14": "F",
        "primary_care_covid_case_ever": "F",
        "covidemergency_01": "F",
        "covidemergency_14": "F",
        "covidemergency_ever": "F",
        "covidadmitted_01": "F",
        "covidadmitted_14": "F",
        "covidadmitted_ever": "T",
        "any_infection_or_disease_01": "F",
        "any_infection_or_disease_14": "F",
        "any_infection_or_disease_ever": "T",
        "included": "T",
    }


# Test that column names are identical across ehrQL and cohort extractor
def test_dataset_columns():
    # arrange
    # act
    cols_cohortextractor = df_cohortextractor.columns
    cols_ehrql = df_ehrql.columns

    # assert
    assert sorted(cols_cohortextractor) == sorted(cols_ehrql)
