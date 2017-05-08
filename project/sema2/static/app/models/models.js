function Schedule(programVersionId) {

    return {
        display_name: "Schedule",
        start_time_hours: 9,
        start_time_minutes: 0,
        stop_time_hours: 17,
        stop_time_minutes: 0,
        program_version: programVersionId,
        interval_minutes: 120,
        expiry_minutes: 120,
        offset_plus_minus_minutes: 0,
        allow_monday: true,
        allow_tuesday: true,
        allow_wednesday: true,
        allow_thursday: true,
        allow_friday: true,
        allow_saturday: true,
        allow_sunday: true
    }
}

function Survey(programVersionId) {

    return {
        program_version: programVersionId,
        display_name: "New Survey",
        randomise_set_order: true,
        trigger_mode: 0,
        max_iterations: -1
    }
}

function ProgramModel() {

    return {
        display_name: "New Program",
        description: ""
    }
}

function QuestionSet(programVersionId) {

    return {
        program_version: programVersionId,
        display_name: "Default",
        randomise_question_order: false
    }
}


function Invite(programId, invitationType) {

    return {
        invitation_type: invitationType,
        program: programId,
        first_name: "",
        last_name: "",
        email_address: "",
        phone_number: "",
        welcome_message: "",
        require_email_confirmation: false
    }
}


function Question(programVersionId, setId, type) {

    return {
        set: setId,
        program_version: programVersionId,
        question_type: type,
        question_text: "",
        question_tag: "",
        min_value: 1,
        min_label: "Min",
        max_value: 5,
        max_label: "Max",
        question_set_id: null,
        trigger_value_min: -1,
        trigger_value_max: -1
    }
}

function QuestionTypeString(type) {

    switch(type) {
        case 0: return "Text"
        case 1: return "Multi Choice"
        case 2: return "Radio"
        case 3: return "Slider"
    }
}

function QuestionOption(label, value) {

    return {
        label: label,
        value: value
    }
}

function ProgramParticipantStatus(value) {

    switch(value) {
        case 0: return "Active"
        case 1: return "Stopped"
        case 2: return "Archived"
        case 3: return "Offline?"
    }
}

function ConditionalQuestionPredicate(target_question_set, target_min_value_incl, target_max_value_incl, target_value, target_option) {

    return {
        target_question_set: target_question_set,
        target_min_value_incl: target_min_value_incl,
        target_max_value_incl: target_max_value_incl,
        target_value: target_value,
        target_option: target_option
    }
}
