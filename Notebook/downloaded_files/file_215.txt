from ehrql import (
    days,
    case,
    when,
    minimum_of,
)
# Bring table definitions from the TPP backend 
from ehrql.tables.tpp import ( 
    patients, 
    practice_registrations, 
    addresses, 
    appointments, 
    occupation_on_covid_vaccine_record,
    sgss_covid_all_tests,
    apcs, 
    clinical_events, 
    ons_deaths,
)

# Codelists from codelists.py (which pulls all variables from the codelist folder)
from codelists import *


# Call functions from variable_helper_functions
from variable_helper_functions import (
    ever_matching_event_clinical_ctv3_before,
    first_matching_event_clinical_snomed_between,
    first_matching_event_apc_between,
    matching_death_between,
    last_matching_event_clinical_ctv3_before,
    last_matching_event_clinical_snomed_before,
    last_matching_med_dmd_before,
    last_matching_event_apc_before,
    last_matching_procedure_apc_before,
    last_matching_procedure_opa_before,
    filter_codes_by_category,
)


def generate_variables(index_date, end_date_exp, end_date_out):  

    ## Define individual variables first 
    ## Then define a dictionary with all exposures, outcomes, covariates, and other variables

    ## Inclusion/exclusion criteria------------------------------------------------------------------------

    ### Registered for a minimum of 6 months prior to index date
    inex_bin_6m_reg = (practice_registrations.spanning(
        index_date - days(180), index_date
        )).exists_for_patient()

    ### Alive on the index date
    inex_bin_alive = (((patients.date_of_death.is_null()) | (patients.date_of_death.is_after(index_date))) & 
    ((ons_deaths.date.is_null()) | (ons_deaths.date.is_after(index_date))))

    ### Project specific: No history of ESRD
    # Based on no history of kidney transplant, no history of dialysis, no coded ESRD
    # OPCS codes will likely need a new helper function

    inex_ever_esrd = (
        (last_matching_event_clinical_snomed_before(
            esrd_snomed, index_date
        ).exists_for_patient()) |
       (last_matching_event_apc_before(
            esrd_icd10, index_date
        ).exists_for_patient()) |
        (last_matching_event_clinical_snomed_before(
            dialysis_snomed, index_date
        ).exists_for_patient()) |
        (last_matching_event_apc_before(
            dialysis_icd10, index_date
        ).exists_for_patient())  |
        (last_matching_procedure_apc_before(
           dialysis_opcs, index_date
        ).exists_for_patient()) |
        (last_matching_procedure_opa_before(
           dialysis_opcs, index_date
        ).exists_for_patient()) |
        (last_matching_event_clinical_snomed_before(
            kidtrans_snomed, index_date
        ).exists_for_patient()) |
        (last_matching_event_apc_before(
            kidtrans_icd10, index_date
        ).exists_for_patient()) |
        (last_matching_procedure_apc_before(
            kidtrans_opcs, index_date
        ).exists_for_patient()) |
        (last_matching_procedure_opa_before(
            kidtrans_opcs, index_date
        ).exists_for_patient()) 
    )

    ## Censoring criteria----------------------------------------------------------------------------------

    ### Deregistered
    cens_date_dereg = (
        practice_registrations.where(practice_registrations.end_date.is_not_null())
        .where(practice_registrations.end_date.is_on_or_after(index_date))
        .sort_by(practice_registrations.end_date)
        .first_for_patient()
        .end_date
    )

    ## Exposures-------------------------------------------------------------------------------------------

    ### Covid
    tmp_exp_date_covid_sgss = (
        sgss_covid_all_tests.where(
            sgss_covid_all_tests.specimen_taken_date.is_on_or_between(index_date, end_date_exp)
        )
        .where(sgss_covid_all_tests.is_positive)
        .sort_by(sgss_covid_all_tests.specimen_taken_date)
        .first_for_patient()
        .specimen_taken_date
    )

    tmp_exp_date_covid_gp = (
        clinical_events.where(
            (clinical_events.ctv3_code.is_in(
                covid_primary_care_code + 
                covid_primary_care_positive_test +
                covid_primary_care_sequalae)) &
            clinical_events.date.is_on_or_between(index_date, end_date_exp)
        )
        .sort_by(clinical_events.date)
        .first_for_patient()
        .date
    )

    tmp_exp_date_covid_apc = (
        apcs.where(
            ((apcs.primary_diagnosis.is_in(covid_codes)) | 
             (apcs.secondary_diagnosis.is_in(covid_codes))) & 
            (apcs.admission_date.is_on_or_between(index_date, end_date_exp))
        )
        .sort_by(apcs.admission_date)
        .first_for_patient()
        .admission_date
    )

    tmp_exp_covid_death = matching_death_between(covid_codes, index_date, end_date_exp)

    tmp_exp_date_death = ons_deaths.date

    tmp_exp_date_covid_death = case(
        when(tmp_exp_covid_death).then(tmp_exp_date_death)
    )
    
    exp_date_covid=minimum_of(
        tmp_exp_date_covid_sgss, 
        tmp_exp_date_covid_gp,
        tmp_exp_date_covid_apc,
        tmp_exp_date_covid_death
    )

    
    ## Quality assurance-----------------------------------------------------------------------------------

    ### Prostate cancer
    qa_bin_prostate_cancer = (
        (last_matching_event_clinical_snomed_before(
            prostate_cancer_snomed, index_date
        ).exists_for_patient()) |
        (last_matching_event_apc_before(
            prostate_cancer_icd10, index_date
        ).exists_for_patient())
    )

    ### Pregnancy
    qa_bin_pregnancy = last_matching_event_clinical_snomed_before(
        pregnancy_snomed, index_date
    ).exists_for_patient()

    ### Year of birth
    qa_num_birth_year = patients.date_of_birth.year

    ## COCP or heart medication
    qa_bin_hrtcocp = last_matching_med_dmd_before(
        cocp_dmd + hrt_dmd, index_date
    ).exists_for_patient()


    ## Outcomes--------------------------------------------------------------------------------------------

    ### AKI
    tmp_out_date_aki_gp = (
        first_matching_event_clinical_snomed_between(
            aki_snomed, index_date, end_date_out
            ).date
    )
    tmp_out_date_aki_apc = (
        first_matching_event_apc_between(
            aki_icd10, index_date, end_date_out
            ).admission_date
    )
    tmp_out_date_aki_death = case(
        when(
            matching_death_between(aki_icd10, index_date, end_date_out)
            ).then(ons_deaths.date)
    )

    out_date_aki = minimum_of(
        tmp_out_date_aki_gp,
        tmp_out_date_aki_apc,
        tmp_out_date_aki_death
    )

    ### CKD
    tmp_out_date_ckd_gp = (
        first_matching_event_clinical_snomed_between(
            ckd34_snomed, index_date, end_date_out
            ).date
    )
    tmp_out_date_ckd_apc = (
        first_matching_event_apc_between(
            ckd34_icd10, index_date, end_date_out
            ).admission_date
    )
    tmp_out_date_ckd_death = case(
        when(
            matching_death_between(ckd34_icd10, index_date, end_date_out)
            ).then(ons_deaths.date)
    )

    out_date_ckd = minimum_of(
        tmp_out_date_ckd_gp,
        tmp_out_date_ckd_apc,
        tmp_out_date_ckd_death
    )

    ### ESRD   
    tmp_out_date_esrd_gp = (
        first_matching_event_clinical_snomed_between(
            esrd_snomed, index_date, end_date_out
            ).date
    )
    tmp_out_date_esrd_apc = (
        first_matching_event_apc_between(
            esrd_icd10, index_date, end_date_out
            ).admission_date
    )
    tmp_out_date_esrd_death = case(
        when(
            matching_death_between(esrd_icd10, index_date, end_date_out)
            ).then(ons_deaths.date)
    )

    out_date_esrd = minimum_of(
        tmp_out_date_esrd_gp,
        tmp_out_date_esrd_apc,
        tmp_out_date_esrd_death
    )

    ## Strata----------------------------------------------------------------------------------------------

    ### Region
    strat_cat_region = practice_registrations.for_patient_on(index_date).practice_nuts1_region_name

    ## Core covariates-------------------------------------------------------------------------------------

    ### Age
    cov_num_age = patients.age_on(index_date)

    ### Sex
    cov_cat_sex = patients.sex

    ### Ethnicity
    cov_cat_ethnicity = (
        clinical_events.where(
            clinical_events.ctv3_code.is_in(opensafely_ethnicity_codes_6)
        )
        .sort_by(clinical_events.date)
        .last_for_patient()
        .ctv3_code.to_category(opensafely_ethnicity_codes_6)
    )

    ### Deprivation
    cov_cat_imd = case(
        when((addresses.for_patient_on(index_date).imd_rounded >= 0) & 
                (addresses.for_patient_on(index_date).imd_rounded < int(32844 * 1 / 5))).then("1 (most deprived)"),
        when(addresses.for_patient_on(index_date).imd_rounded < int(32844 * 2 / 5)).then("2"),
        when(addresses.for_patient_on(index_date).imd_rounded < int(32844 * 3 / 5)).then("3"),
        when(addresses.for_patient_on(index_date).imd_rounded < int(32844 * 4 / 5)).then("4"),
        when(addresses.for_patient_on(index_date).imd_rounded < int(32844 * 5 / 5)).then("5 (least deprived)"),
        otherwise="unknown",
    )

    ### Smoking status
    tmp_most_recent_smoking_cat = (
        last_matching_event_clinical_ctv3_before(smoking_clear, index_date)
        .ctv3_code.to_category(smoking_clear)
    )
    tmp_ever_smoked = ever_matching_event_clinical_ctv3_before(
        (filter_codes_by_category(smoking_clear, include=["S", "E"])), index_date)

    cov_cat_smoking = case(
        when(tmp_most_recent_smoking_cat == "S").then("S"),
        when((tmp_most_recent_smoking_cat == "E") | ((tmp_most_recent_smoking_cat == "N") & (tmp_ever_smoked == True))).then("E"),
        when((tmp_most_recent_smoking_cat == "N") & (tmp_ever_smoked == False)).then("N"),
        otherwise="M"
    )

    ### Care home status
    cov_bin_carehome = (
        addresses.for_patient_on(index_date).care_home_is_potential_match |
        addresses.for_patient_on(index_date).care_home_requires_nursing |
        addresses.for_patient_on(index_date).care_home_does_not_require_nursing
    )

    ### Consultation rate in 2019
    tmp_cov_num_consrate2019 = appointments.where(
        appointments.status.is_in([
            "Arrived",
            "In Progress",
            "Finished",
            "Visit",
            "Waiting",
            "Patient Walked Out",
            ]) & appointments.start_date.is_on_or_between("2019-01-01", "2019-12-31")
            ).count_for_patient()    

    cov_num_consrate2019 = case(
        when(tmp_cov_num_consrate2019 <= 365).then(tmp_cov_num_consrate2019),
        otherwise=365,
    )

    ### Healthcare worker
    cov_bin_hcworker = occupation_on_covid_vaccine_record.where(
        (occupation_on_covid_vaccine_record.is_healthcare_worker == True)
    ).exists_for_patient()

    ### Dementia
    cov_bin_dementia = (
        (last_matching_event_clinical_snomed_before(
            dementia_snomed + dementia_vascular_snomed, index_date
        ).exists_for_patient()) |
        (last_matching_event_apc_before(
            dementia_icd10 + dementia_vascular_icd10, index_date
        ).exists_for_patient())
    )

    ### Liver disease
    cov_bin_liver_disease = (
        (last_matching_event_clinical_snomed_before(
            liver_disease_snomed, index_date
        ).exists_for_patient()) |
        (last_matching_event_apc_before(
            liver_disease_icd10, index_date
        ).exists_for_patient())
    )

    # Commented out as this is a project specific covariate
    # ### Chronic kidney disease (CKD)
    # cov_bin_ckd = (
    #     (last_matching_event_clinical_snomed_before(
    #         ckd_snomed, index_date
    #     ).exists_for_patient()) |
    #     (last_matching_event_apc_before(
    #         ckd_icd10, index_date
    #     ).exists_for_patient())
    # )

    ### Cancer
    cov_bin_cancer = (
        (last_matching_event_clinical_snomed_before(
            cancer_snomed, index_date
        ).exists_for_patient()) |
        (last_matching_event_apc_before(
            cancer_icd10, index_date
        ).exists_for_patient())
    )

    ### Hypertension (Also used for high vascular risk covariate)
    cov_bin_hypertension = (
        (last_matching_event_clinical_snomed_before(
            hypertension_snomed, index_date
        ).exists_for_patient()) |
        (last_matching_med_dmd_before(
            hypertension_drugs_dmd, index_date
        ).exists_for_patient()) |
        (last_matching_event_apc_before(
            hypertension_icd10, index_date
        ).exists_for_patient())
    )

    ### Diabetes (Also used for high vascular risk covariate) 
    cov_bin_diabetes = (
        (last_matching_event_clinical_snomed_before(
            diabetes_snomed, index_date
        ).exists_for_patient()) |
        (last_matching_med_dmd_before(
            diabetes_drugs_dmd, index_date
        ).exists_for_patient()) |
        (last_matching_event_apc_before(
            diabetes_icd10, index_date
        ).exists_for_patient())
    )

    ### Obesity 
    cov_bin_obesity = (
        (last_matching_event_clinical_snomed_before(
            bmi_obesity_snomed, index_date
        ).exists_for_patient()) |
        (last_matching_event_apc_before(
            bmi_obesity_icd10, index_date
        ).exists_for_patient())
    )

    ### COPD
    cov_bin_copd = (
        (last_matching_event_clinical_ctv3_before(
            copd_ctv3, index_date
        ).exists_for_patient()) |
        (last_matching_event_apc_before(
            copd_icd10, index_date
        ).exists_for_patient())
    )

    ### Acute myocardial infarction (AMI)
    cov_bin_ami = (
        (last_matching_event_clinical_snomed_before(
            ami_snomed, index_date
        ).exists_for_patient()) |
        (last_matching_event_apc_before(
            ami_icd10 + ami_prior_icd10, index_date
        ).exists_for_patient())
    )

    ### Depression
    cov_bin_depression = (
        (last_matching_event_clinical_snomed_before(
            depression_snomed, index_date
        ).exists_for_patient()) |
        (last_matching_event_apc_before(
            depression_icd10, index_date
        ).exists_for_patient())
    )

    ### Ischaemic stroke
    cov_bin_stroke_isch = (
        (last_matching_event_clinical_snomed_before(
            stroke_isch_snomed, index_date
        ).exists_for_patient()) |
        (last_matching_event_apc_before(
            stroke_isch_icd10, index_date
        ).exists_for_patient())
    )

    ## Project specific covariates-------------------------------------------------------------------------

    ### History of CKD (any stage)
    cov_bin_ckd = (
        (last_matching_event_clinical_snomed_before(
            ckd_snomed, index_date
        ).exists_for_patient()) |
        (last_matching_event_apc_before(
            ckd_icd10, index_date
        ).exists_for_patient())
    )

    ## Subgroups-------------------------------------------------------------------------------------------

    ### History of COVID-19
    tmp_sub_bin_covidhistory_sgss = (
        sgss_covid_all_tests.where(
            sgss_covid_all_tests.specimen_taken_date.is_before(index_date)
        )
        .where(sgss_covid_all_tests.is_positive)
        .exists_for_patient()
    )
    tmp_sub_bin_covidhistory_gp = (
        clinical_events.where(
            (clinical_events.ctv3_code.is_in(
                covid_primary_care_code + 
                covid_primary_care_positive_test + 
                covid_primary_care_sequalae)) &
            clinical_events.date.is_before(index_date)
        )
        .exists_for_patient()
    )
    tmp_sub_bin_covidhistory_apc = (
        apcs.where(
            ((apcs.primary_diagnosis.is_in(covid_codes)) | (apcs.secondary_diagnosis.is_in(covid_codes))) & 
            (apcs.admission_date.is_before(index_date))
        )
        .exists_for_patient()
    )

    sub_bin_covidhistory = (
        tmp_sub_bin_covidhistory_sgss |
        tmp_sub_bin_covidhistory_gp |
        tmp_sub_bin_covidhistory_apc
    )

    ### COVID-19 severity
    tmp_sub_date_covidhospital = (
        apcs.where(
            (apcs.primary_diagnosis.is_in(covid_codes)) & 
            (apcs.admission_date.is_on_or_after(exp_date_covid))
        )
        .sort_by(apcs.admission_date)
        .first_for_patient()
        .admission_date
    )

    sub_cat_covidhospital = case(
        when(
            (exp_date_covid.is_not_null()) &
            (tmp_sub_date_covidhospital.is_not_null()) &
            ((tmp_sub_date_covidhospital - exp_date_covid).days >= 0) &
            ((tmp_sub_date_covidhospital - exp_date_covid).days < 29)
            ).then("hospitalised"),
        when(exp_date_covid.is_not_null()).then("non_hospitalised"),
        when(exp_date_covid.is_null()).then("no_infection")
    )

# Start of Dictionary-----------------------------------------------------------------------------------------

    ## Combine the variables into the final dictionary
    dynamic_variables = dict(

# Inclusion/exclusion criteria--------------------------------------------------------------------------------
        inex_bin_6m_reg = inex_bin_6m_reg,
        inex_bin_alive  = inex_bin_alive,

    # History of End Stage Renal Disease 
        inex_ever_esrd  = inex_ever_esrd, 

# Censoring criteria------------------------------------------------------------------------------------------
        cens_date_dereg = cens_date_dereg,

# Exposures---------------------------------------------------------------------------------------------------
        exp_date_covid = exp_date_covid,

# Quality assurance-------------------------------------------------------------------------------------------
        qa_bin_prostate_cancer = qa_bin_prostate_cancer,
        qa_bin_pregnancy       = qa_bin_pregnancy,
        qa_num_birth_year      = qa_num_birth_year,
        qa_bin_hrtcocp         = qa_bin_hrtcocp,

# Outcomes----------------------------------------------------------------------------------------------------

        ### ---First recording of the outcome in during the study period
        out_date_aki         = out_date_aki,        # Acute Kidney Injury
        out_date_ckd         = out_date_ckd,        # Chronic Kidney Disease (but not ESRD)
        out_date_esrd        = out_date_esrd,       # End Stage Renal Disease

        ## Tmp GP
        tmp_out_date_aki_gp         = tmp_out_date_aki_gp,        # Acute Kidney Injury
        tmp_out_date_ckd_gp         = tmp_out_date_ckd_gp,        # Chronic Kidney Disease (but not ESRD)
        tmp_out_date_esrd_gp        = tmp_out_date_esrd_gp,       # End Stage Renal Disease

        ## Tmp APC
        tmp_out_date_aki_apc     = tmp_out_date_aki_apc,     # Acute Kidney Injury
        tmp_out_date_ckd_apc     = tmp_out_date_ckd_apc,     # Chronic Kidney Disease (but not ESRD)
        tmp_out_date_esrd_apc    = tmp_out_date_esrd_apc,    # End Stage Renal Disease

        ## Tmp Death 
        tmp_out_date_aki_death    = tmp_out_date_aki_death,   # Acute Kidney Injury
        tmp_out_date_ckd_death    = tmp_out_date_ckd_death,   # Chronic Kidney Disease (but not ESRD)
        tmp_out_date_esrd_death   = tmp_out_date_esrd_death,  # End Stage Renal Disease


### Strata----------------------------------------------------------------------------------------------------
        strat_cat_region = strat_cat_region,

### Core covariates-------------------------------------------------------------------------------------------
        cov_num_age           = cov_num_age,
        cov_cat_sex           = cov_cat_sex,

        cov_bin_ami           = cov_bin_ami,
        cov_bin_cancer        = cov_bin_cancer,
        cov_bin_carehome      = cov_bin_carehome,
        #cov_bin_ckd           = cov_bin_ckd,
        cov_num_consrate2019  = cov_num_consrate2019,
        cov_bin_copd          = cov_bin_copd,
        cov_bin_dementia = cov_bin_dementia,
        cov_bin_depression    = cov_bin_depression,
        cov_bin_diabetes      = cov_bin_diabetes,
        cov_cat_ethnicity     = cov_cat_ethnicity,
        cov_bin_hcworker      = cov_bin_hcworker,
        cov_bin_hypertension  = cov_bin_hypertension,
        cov_cat_imd           = cov_cat_imd,
        cov_bin_liver_disease = cov_bin_liver_disease,
        cov_bin_obesity       = cov_bin_obesity,
        cov_cat_smoking       = cov_cat_smoking,
        cov_bin_stroke_isch   = cov_bin_stroke_isch,

### Project specific covariates----------------------------------------------------------------------------------
        cov_bin_ckd            = cov_bin_ckd,
        
### Subgroups-----------------------------------------------------------------------------------------------------
        sub_bin_covidhistory  = sub_bin_covidhistory,
        sub_cat_covidhospital = sub_cat_covidhospital
    ) 
    
    return dynamic_variables