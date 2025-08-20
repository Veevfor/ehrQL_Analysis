from ehrql import Dataset, years, days, months, minimum_of, maximum_of, case, when
from ehrql.tables.core import patients
from ehrql.tables.tpp import practice_registrations, ons_deaths, clinical_events, clinical_events_ranges

import codelists

def make_dataset_fit(index_date, end_date):

    dataset = Dataset()

    reg_date = practice_registrations.where(practice_registrations.start_date.is_on_or_between(index_date, end_date)
                                                    ).sort_by(
                                                        practice_registrations.start_date
                                                    ).first_for_patient().start_date
    
    age_16_date = patients.date_of_birth + years(16)

    dataset.entry_date = maximum_of(reg_date, age_16_date, "2018-03-23")

    death_date = ons_deaths.date

    age_110_date = patients.date_of_birth + years(110)

    dereg_date = practice_registrations.sort_by(practice_registrations.end_date
                                              ).first_for_patient().end_date

    colorectal_ca_diag_date = clinical_events.where(clinical_events.snomedct_code.is_in(codelists.colorectal_diagnosis_codes_snomed)
                                                        ).sort_by(
                                                            clinical_events.date
                                                        ).first_for_patient().date
    
    dataset.exit_date = minimum_of(death_date, age_110_date, dereg_date, colorectal_ca_diag_date, "2023-10-22")

    dataset.death_date = death_date

    fit_test_first = clinical_events.where(clinical_events.snomedct_code.is_in(codelists.fit_codes)
            ).where(
                clinical_events.date.is_on_or_between(index_date, end_date)
            ).where(
                clinical_events.date.is_on_or_between(dataset.entry_date, dataset.exit_date)
            ).sort_by(
                clinical_events.date
            ).first_for_patient()
    
    fit_test_any_date = fit_test_first.date

    fit_test_prev = clinical_events.where(clinical_events.snomedct_code.is_in(codelists.fit_codes)
            ).where(
                clinical_events.date.is_on_or_between(fit_test_any_date - days(42), fit_test_any_date - days(1))
            ).exists_for_patient()
    
    dataset.fit_test_any = fit_test_first.exists_for_patient() & ~fit_test_prev
    dataset.fit_test_any_date = case(when(dataset.fit_test_any).then(fit_test_any_date))

    def fit_test_value(fit_date):
        return clinical_events_ranges.where(clinical_events_ranges.snomedct_code.is_in(codelists.fit_codes)
        ).where(
            clinical_events_ranges.date.is_on_or_after(fit_date)
        ).sort_by(
            clinical_events_ranges.date
        ).first_for_patient().numeric_value

    def fit_test_comparator(fit_date):
        return clinical_events_ranges.where(clinical_events_ranges.snomedct_code.is_in(codelists.fit_codes)
        ).where(
            clinical_events_ranges.date.is_on_or_after(fit_date)
        ).sort_by(
            clinical_events_ranges.date
        ).first_for_patient().comparator
    
    def fit_test_code(fit_date):
        return clinical_events.where(clinical_events.snomedct_code.is_in(codelists.fit_codes)
        ).where(
            clinical_events.date.is_on_or_after(fit_date)
        ).sort_by(
            clinical_events.date
        ).first_for_patient().snomedct_code

    def fit_test_positive(fit_date):
        return case(when((fit_test_value(fit_date)>=10) & (fit_test_comparator(fit_date)!="<")).then(True), 
                    when(fit_test_code(fit_date)=="389076003").then(True),
                    when(fit_test_code(fit_date)=="59614000").then(True),
                    otherwise=False)
    
    dataset.fit_test_any_positive = fit_test_positive(dataset.fit_test_any_date)

    dataset.fit_test_any_value = fit_test_value(dataset.fit_test_any_date)

    def symp_fit_6months(codelist, l_age, u_age):
        return clinical_events.where(clinical_events.snomedct_code.is_in(codelist)
        ).where(
            clinical_events.date.is_on_or_between(dataset.fit_test_any_date - months(6), dataset.fit_test_any_date)
        ).where(
            patients.age_on(clinical_events.date)>=l_age
        ).where(
            patients.age_on(clinical_events.date)<u_age
        ).sort_by(
            clinical_events.date
        ).first_for_patient().date
    
    dataset.ida_fit_date = symp_fit_6months(codelists.ida_codes, 16, 111)
    dataset.cibh_fit_date = symp_fit_6months(codelists.cibh_codes, 16, 111)
    dataset.prbleed_fit_date = symp_fit_6months(codelists.prbleeding_codes, 16, 111)
    dataset.wl_fit_date = symp_fit_6months(codelists.wl_codes, 16, 111)
    dataset.abdomass_fit_date = symp_fit_6months(codelists.abdomass_codes, 16, 111)
    dataset.abdopain_fit_date = symp_fit_6months(codelists.abdopain_codes, 16, 111)
    dataset.anaemia_fit_date = symp_fit_6months(codelists.anaemia_codes, 16, 111)
    dataset.prbleed_50_fit_date = symp_fit_6months(codelists.prbleeding_codes, 50, 111)
    dataset.wl_50_fit_date = symp_fit_6months(codelists.wl_codes, 50, 111)
    dataset.abdopain_50_fit_date = symp_fit_6months(codelists.abdopain_codes, 50, 111)
    dataset.anaemia_60_fit_date = symp_fit_6months(codelists.anaemia_codes, 60, 111)
    dataset.wl_abdopain_40_fit_date = minimum_of(symp_fit_6months(codelists.wl_codes, 40, 111), symp_fit_6months(codelists.abdopain_codes, 40, 111))
    dataset.prbleed_abdopain_fit_date = minimum_of(symp_fit_6months(codelists.prbleeding_codes, 16, 50), symp_fit_6months(codelists.abdopain_codes, 16, 50))
    dataset.prbleed_wl_fit_date = minimum_of(symp_fit_6months(codelists.prbleeding_codes, 16, 50), symp_fit_6months(codelists.wl_codes, 16, 50))

    dataset.lowerGI_any_symp_fit_date = minimum_of(dataset.ida_fit_date, dataset.cibh_fit_date, dataset.prbleed_fit_date, dataset.wl_fit_date, dataset.abdomass_fit_date, dataset.abdopain_fit_date, dataset.anaemia_fit_date)
    dataset.lowerGI_2ww_symp_fit_date = minimum_of(dataset.ida_fit_date, dataset.cibh_fit_date, dataset.abdomass_fit_date, dataset.prbleed_50_fit_date, dataset.wl_50_fit_date, dataset.abdopain_50_fit_date, dataset.anaemia_60_fit_date, dataset.wl_abdopain_40_fit_date, dataset.prbleed_abdopain_fit_date, dataset.prbleed_wl_fit_date)

    def symp_to_fit_days(symp_date):
        return (dataset.fit_test_any_date - symp_date).days
    
    dataset.ida_fit_days = symp_to_fit_days(dataset.ida_fit_date)
    dataset.cibh_fit_days = symp_to_fit_days(dataset.cibh_fit_date)
    dataset.prbleed_fit_days = symp_to_fit_days(dataset.prbleed_fit_date)
    dataset.wl_fit_days = symp_to_fit_days(dataset.wl_fit_date)
    dataset.abdomass_fit_days = symp_to_fit_days(dataset.abdomass_fit_date)
    dataset.abdopain_fit_days = symp_to_fit_days(dataset.abdopain_fit_date)
    dataset.anaemia_fit_days = symp_to_fit_days(dataset.anaemia_fit_date)
    
    dataset.prbleed_50_fit_days = symp_to_fit_days(dataset.prbleed_50_fit_date)
    dataset.wl_50_fit_days = symp_to_fit_days(dataset.wl_50_fit_date)
    dataset.abdopain_50_fit_days = symp_to_fit_days(dataset.abdopain_50_fit_date)
    dataset.anaemia_60_fit_days = symp_to_fit_days(dataset.anaemia_60_fit_date)
    dataset.wl_abdopain_40_fit_days = symp_to_fit_days(dataset.wl_abdopain_40_fit_date)
    dataset.prbleed_abdopain_fit_days = symp_to_fit_days(dataset.prbleed_abdopain_fit_date)
    dataset.prbleed_wl_fit_days = symp_to_fit_days(dataset.prbleed_wl_fit_date)

    dataset.lowerGI_any_fit_days = symp_to_fit_days(dataset.lowerGI_any_symp_fit_date)
    dataset.lowerGI_2ww_fit_days = symp_to_fit_days(dataset.lowerGI_2ww_symp_fit_date)

    lowerGI_any_num_fit = clinical_events.where(clinical_events.snomedct_code.is_in(codelists.colorectal_symptom_codes)
        ).where(
            clinical_events.date.is_on_or_between(dataset.fit_test_any_date - months(6), dataset.fit_test_any_date)
        ).date.count_episodes_for_patient(days(42))
    
    dataset.fit_lowerGI_any_num = lowerGI_any_num_fit

    dataset.ca_fit_date = clinical_events.where(clinical_events.snomedct_code.is_in(codelists.colorectal_diagnosis_codes_snomed)
        ).where(
            clinical_events.date.is_on_or_between(dataset.fit_test_any_date, dataset.fit_test_any_date + months(12))
        ).sort_by(
            clinical_events.date
        ).first_for_patient().date

    dataset.fit_to_ca_days = (dataset.ca_fit_date - dataset.fit_test_any_date).days

    return dataset
