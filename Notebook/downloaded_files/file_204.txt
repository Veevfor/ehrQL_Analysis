from ehrql.tables.beta import tpp as schema


def first_matching_event(events, codelist, where=True):
    return (
        events.where(where)
        .where(events.snomedct_code.is_in(codelist))
        .sort_by(events.date)
        .first_for_patient()
    )


def last_matching_event(events, codelist, where=True):
    return (
        events.where(where)
        .where(events.snomedct_code.is_in(codelist))
        .sort_by(events.date)
        .last_for_patient()
    )


def last_matching_event_ctv3(events, codelist, where=True):
    return (
        events.where(where)
        .where(events.ctv3_code.is_in(codelist))
        .sort_by(events.date)
        .last_for_patient()
    )


def last_matching_med(events, codelist, where=True):
    return (
        events.where(where)
        .where(events.dmd_code.is_in(codelist))
        .sort_by(events.date)
        .last_for_patient()
        .dmd_code
    )


def _registrations_overlapping_period(start_date, end_date):
    regs = schema.practice_registrations
    return regs.where(
        regs.start_date.is_on_or_before(start_date)
        & (regs.end_date.is_after(end_date) | regs.end_date.is_null())
    )


def practice_registration_as_of(date):
    regs = _registrations_overlapping_period(date, date)
    return regs.sort_by(regs.start_date, regs.end_date).first_for_patient()


def get_events_on_or_between(events, codelist, start_date, end_date, where=True):
    return (
        events.where(where)
        .where(events.snomedct_code.is_in(codelist))
        .where(events.date.is_on_or_between(start_date, end_date))
    )
