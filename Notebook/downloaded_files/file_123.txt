from ehrql import case, when, months, INTERVAL, Measures, minimum_of, maximum_of
from ehrql.tables.tpp import (
    patients, 
    addresses,
    practice_registrations,
    clinical_events)

import codelists

from dataset_definition import make_dataset_lowerGI

from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("--start-date", type=str)
parser.add_argument("--intervals", type=int)

args = parser.parse_args()

start_date = args.start_date
intervals = args.intervals

##########

index_date = INTERVAL.start_date

dataset = make_dataset_lowerGI(index_date=index_date, end_date=INTERVAL.end_date)

dataset.elig_cohort = dataset.entry_date.is_on_or_before(INTERVAL.end_date) & dataset.exit_date.is_after(index_date) & patients.date_of_birth.is_not_null()

period_entry = maximum_of(index_date, dataset.entry_date)
period_exit = minimum_of(INTERVAL.end_date, dataset.exit_date)

follow_up_days = (period_exit - period_entry).days

dataset.elig_follow_up_days = case(
        when(dataset.elig_cohort).then(follow_up_days)
)

#dataset.fit_any = case(
        #when(dataset.fit_test_any).then(1),
        #otherwise=0
#)
dataset.ida = case(
        when(dataset.ida_symp).then(1),
        otherwise=0
)
dataset.cibh = case(
        when(dataset.cibh_symp).then(1),
        otherwise=0
)
dataset.abdomass = case(
        when(dataset.abdomass_symp).then(1),
        otherwise=0
)
dataset.prbleed_50 = case(
        when(dataset.prbleed_symp_50).then(1),
        otherwise=0
)
dataset.wl_50 = case(
        when(dataset.wl_symp_50).then(1),
        otherwise=0
)
dataset.abdopain_50 = case(
        when(dataset.abdopain_symp_50).then(1),
        otherwise=0
)
dataset.anaemia_60 = case(
        when(dataset.anaemia_symp_60).then(1),
        otherwise=0
)
#dataset.fit_6 = case(
        #when(dataset.fit_6_all_lowerGI).then(1),
        #otherwise=0
#)

##########

## Define demographic variables

imd = addresses.for_patient_on(dataset.entry_date).imd_rounded
imd5 = case(
        when((imd >=0) & (imd < int(32844 * 1 / 5))).then("1 (most deprived)"),
        when(imd < int(32844 * 2 / 5)).then("2"),
        when(imd < int(32844 * 3 / 5)).then("3"),
        when(imd < int(32844 * 4 / 5)).then("4"),
        when(imd < int(32844 * 5 / 5)).then("5 (least deprived)"),
        otherwise="unknown"
)

#########################

measures = Measures()
measures.configure_disclosure_control(enabled=False)

measures.define_defaults(intervals=months(intervals).starting_on(start_date))

#measures.define_measure(
    #name="fit_test_rate", 
    #numerator=dataset.fit_any,
    #denominator=dataset.elig_follow_up_days,
    #group_by={"imd": imd5}
    #)

measures.define_measure(
    name="ida_symp_rate", 
    numerator=dataset.ida,
    denominator=dataset.elig_follow_up_days,
    group_by={"imd": imd5}
    )

measures.define_measure(
    name="cibh_symp_rate", 
    numerator=dataset.cibh,
    denominator=dataset.elig_follow_up_days,
    group_by={"imd": imd5}
    )

measures.define_measure(
    name="abdomass_symp_rate", 
    numerator=dataset.abdomass,
    denominator=dataset.elig_follow_up_days,
    group_by={"imd": imd5}
    )

measures.define_measure(
    name="prbleed_symp_50_rate", 
    numerator=dataset.prbleed_50,
    denominator=dataset.elig_follow_up_days,
    group_by={"imd": imd5}
    )

measures.define_measure(
    name="wl_symp_50_rate", 
    numerator=dataset.wl_50,
    denominator=dataset.elig_follow_up_days,
    group_by={"imd": imd5}
    )

measures.define_measure(
    name="abdopain_symp_50_rate", 
    numerator=dataset.abdopain_50,
    denominator=dataset.elig_follow_up_days,
    group_by={"imd": imd5}
    )

measures.define_measure(
    name="anaemia_symp_60_rate", 
    numerator=dataset.anaemia_60,
    denominator=dataset.elig_follow_up_days,
    group_by={"imd": imd5}
    )

#measures.define_measure(
    #name="fit_6_rate", 
    #numerator=dataset.fit_6,
    #denominator=dataset.elig_follow_up_days,
    #group_by={"imd": imd5}
    #)

#measures.define_measure(
    #name="diag_6_rate", 
    #numerator=dataset.diag_6_all_lowerGI,
    #denominator=dataset.lowerGI_any_symp,
    #group_by={"imd": imd5}
    #)

#measures.define_measure(
    #name="ca_6_rate", 
    #numerator=dataset.ca_6_all_lowerGI,
    #denominator=dataset.lowerGI_any_symp,
    #group_by={"imd": imd5}
    #)