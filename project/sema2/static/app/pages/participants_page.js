var ProgramParticipantsPage = React.createClass({

    mixins: [UrlBuilderMixin, ModelUtilsMixin],

    getInitialState: function() {
        return {
            invites: [],
            participantItems: [],
            showForm: false,
            showInfo: false,
            participantFilter: ""
        };
    },

    componentDidMount: function() {
        this.refreshData();

        this.timeout = null;
    },

    onUpdateFilter: function(e) {

        var self = this;

        this.setState({
            participantFilter: e.target.value
        }, function() {

            clearTimeout(this.timeout);
            setTimeout(function() {
                self.refreshData();
            }, 1500);
        }.bind(this));
    },

    onInviteParticipant:function(evt) {

        evt.preventDefault();
        
        this.refs.inviteForm.setValues(Invite(this.props.program.id, 0));

        this.setState({
            showForm:true
        })
    },

    debounce:function(func, wait, immediate) {
        var timeout;

        return function() {
            var context = this, args = arguments;
            var later = function() {
                timeout = null;
                if (!immediate) func.apply(context, args);
            };
            var callNow = immediate && !timeout;
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
            if (callNow) func.apply(context, args);
        };
    },

    refreshData: function() {

        this.setState({
            isLoading:true
        }, function() {

            var url = "programs/" + this.props.program.id + "/participants/?f=" + this.state.participantFilter;
            var getParticipants = this.reactGetRequest(url);

            var getInvites = this.reactGetRequest(["programs", this.props.program.id, "invites"]);
            var getSurveys = this.reactGetRequest(["programs", this.props.program.id, "surveys"]);

            $.when(getParticipants, getSurveys, getInvites).then(function(participants, surveys, invites) {

                if (this.isMounted()) {

                    var moddedParticipants = participants[0].map(function(item) {
                        return this.setStartEndTime(item);
                    }.bind(this));

                    this.setState({
                        isLoading:false,
                        allSurveys: surveys[0],
                        participantItems: moddedParticipants,
                        invites: invites[0]
                    });
                }

            }.bind(this));

        }.bind(this));
    },

    sendInvite: function() {
        var data = this.refs.inviteForm.getValues();
        return this.reactPostRequest(["invitations"], null, data);
    },

    onSaveClicked: function() {

        this.sendInvite()
            .then(function(res) {

                this.setState({showForm:false}, function() {
                    alert("Your invitation was sent successfully");
                    this.refreshData();
                });

            }.bind(this))
            .fail(function(res) {
                alert("Unable to send invite. Please check all fields are filled.")
            });

    },

    onCancelClicked: function() {
        this.setState({showForm:false});
    },

    // Participant Editing

    onRowClicked: function(rowData) {

        this.refs.form.setValues(rowData);

        this.setStartEndTime(rowData);

        this.refs.toList.clearSelectedItems();
        this.refs.fromList.clearSelectedItems();

        var addedSurveys = rowData.assigned_surveys.sort(function(a, b) {a.id - b.id});
        var availableSurveys = this.getAvailableSurveys(addedSurveys);

        this.setState({
            enableCustomTime:rowData.info.use_custom_start_stop_time,
            participant: rowData,
            addedSurveys: addedSurveys,
            availableSurveys: availableSurveys,
            showParticipantForm:true
        });
    },

    setStartEndTime: function(rowData) {

        var startTime = moment({hour: rowData.info.custom_start_hour, minute: rowData.info.custom_start_minute});
        var stopTime = moment({hour: rowData.info.custom_stop_hour, minute: rowData.info.custom_stop_minute});

        rowData.info.custom_start_time = startTime.format("H:mm A");
        rowData.info.custom_stop_time = stopTime.format("H:mm A");

        return rowData;
    },

    onParticipantSaveClicked: function() {

        var profile = this.refs.form.getValues();

        var startTime = moment(profile.info.custom_start_time, "H:mm A");
        profile.info.custom_start_hour = startTime.hour();
        profile.info.custom_start_minute = startTime.minute();

        var endTime = moment(profile.info.custom_stop_time, "H:mm A");
        profile.info.custom_stop_hour = endTime.hour();
        profile.info.custom_stop_minute = endTime.minute();

        var startMins = profile.info.custom_start_hour * 60 + profile.info.custom_start_minute;
        var stopMins = profile.info.custom_stop_hour * 60 + profile.info.custom_stop_minute;

        if (profile.info.use_custom_start_stop_time && stopMins <= startMins) {
            alert("Invalid Schedule: Stop time '" + profile.info.custom_stop_time + "' must be later than start time '" + profile.info.custom_start_time + "'");
        }
        else {

            var addedIds = this.state.addedSurveys.map(function (item) {
                return item.id;
            });

            profile.assigned_surveys = addedIds;
            profile.program = this.props.program.id;

            var profileReq = this.reactPutRequest(["participants", this.state.participant.id, "profile"], null, profile);

            profileReq.then(function (profile) {

                this.setState({showParticipantForm: false}, function () {
                    this.refreshData();
                }.bind(this));

            }.bind(this));
        }
    },

    onParticipantCancelClicked: function() {
        this.setState({
            showParticipantForm:false

        });
    },

    // Bulk Editing
    onBulkAssignClicked: function() {

        this.refs.toList.clearSelectedItems();
        this.refs.fromList.clearSelectedItems();

        var selected = this.refs.table.getSelectedItems();

        if (selected.length == 0) {
            alert("Please select a participant from the table");
        }
        else {

            var addedSurveys = [];
            var availableSurveys = this.getAvailableSurveys(addedSurveys);

            this.setState({
                addedSurveys: addedSurveys,
                availableSurveys: availableSurveys,
                showBulkAssignForm: true
            }, function() {
                this.refreshData();
            });
        }
    },

    onBulkAssignSaveClicked: function() {

        this.setState({showBulkAssignForm:false}, function() {
        });
    },

    onBulkAssignCancelClicked: function() {

        var addedIds = this.state.addedSurveys.map(function(item) {
            return item.id;
        });

        var selectedParticipants = this.refs.table.getSelectedItems();

        selectedParticipants.map(function(participant) {

            this.reactPutRequest(["participants", participant.id, "set_assigned_surveys"], null, addedIds).then(function(item) {

            }.bind(this));

        }.bind(this));

        this.setState({
            showBulkAssignForm:false
        });
    },

    // Survey Editing
    getAvailableSurveys: function(addedSurveys) {
        var allSurveys = this.state.allSurveys.sort(function(a, b) {a.id - b.id});
        var addedIds = addedSurveys.map(function(item) {return item.id});
        var availableSurveys = [];
        for (var i = 0; i < allSurveys.length; i++) {
            if (addedIds.indexOf(allSurveys[i].id) == -1) {
                availableSurveys.push(allSurveys[i]);
            }
        }

        return availableSurveys;
    },

    addSelectedSurveys: function(fromList) {
        var newSurveys = fromList.getSelectedItems();
        var addedSurveys = this.state.addedSurveys;

        addedSurveys = $.merge(addedSurveys, newSurveys);
        var availableSurveys = this.getAvailableSurveys(addedSurveys);

        this.setState({
            addedSurveys: addedSurveys,
            availableSurveys: availableSurveys
        });

        fromList.clearSelectedItems();
    },

    removeSelectedSurveys: function(toList) {
        var removedSurveys = toList.getSelectedItems();
        var removedIds = removedSurveys.map(function(item) { return item.id });

        var addedSurveys = this.state.addedSurveys.filter(function(item) {
            return removedIds.indexOf(item.id) == -1;
        });

        var availableSurveys = this.getAvailableSurveys(addedSurveys);

        this.setState({
            addedSurveys: addedSurveys,
            availableSurveys: availableSurveys
        });

        toList.clearSelectedItems();
    },

    onCustomTimeChanged: function(key, value) {
        this.setState({
            enableCustomTime:value
        });
    },

    onResetComplianceClicked: function() {

        var params = {
            user: this.state.participant.id
        };

        var resetComplianceReq = this.reactPostRequest(["programs", this.props.program.id, "reset_participant_compliance"], null, params);

        $.when(resetComplianceReq).then(function() {
            alert("Compliance reset successful");
        });
    },

    onResetIterationsClicked: function() {

        var data = this.refs.form.getValues();

        if (data.survey_to_reset != null) {

            var params = {
                user: this.state.participant.id,
                survey: data.survey_to_reset
            };

            var resetIterationsReq = this.reactPostRequest(["programs", this.props.program.id, "reset_participant_iterations"], null, params);

            $.when(resetIterationsReq).then(function () {
                alert("Iteration reset successful");
            });
        }
        else {
            alert("No survey has been selected.");
        }

    },

    onSurveyToResetChanged: function(name, item) {

        var params = {
            user: this.state.participant.id,
            survey: item
        };

        var surveyInfoReq = this.reactPostRequest(["programs", this.props.program.id, "get_survey_info"], null, params);

        $.when(surveyInfoReq).then(function (res) {
            this.setState({
                currentIteration: res.current_iteration,
                maxIterations: res.max_iterations
            });
        }.bind(this));
    },

    onInfoClicked: function(item, event) {

        event.stopPropagation();
        event.preventDefault();

        this.setState({
            showInfo:true,
            participant: item
        });
    },

    onInfoCancelClicked: function() {

        this.setState({
            showInfo:false
        })
    },

    onInviteConfirmClicked: function(id) {

        if (confirm("Are you sure you want to confirm this invitation?")) {

            var req = this.reactPostRequest(["invitations", id, "confirm"], null);
            $.when(req).then(function () {
                window.location.reload();
            });

        }
    },

    onInviteCancelClicked: function(id) {

        if (confirm("Are you sure you want to cancel this invitation?")) {

            var req = this.reactPostRequest(["invitations", id, "cancel"], null);
            $.when(req).then(function () {
                window.location.reload();
            });
        }
    },

    render: function() {

        var iterationsInfo = this.state.maxIterations ? <span className="label label-success">Iteration: {this.state.currentIteration} / {this.state.maxIterations}</span> : "";

        var inviteMessage = null;

        if (this.state.invites.length > 0) {

            var inviteList = this.state.invites.map(function (item) {

                var label = item.first_name + " " + item.last_name + " (username: " + item.username + " / email: " + item.email_address + ")";
                return <span>{label} [<a onClick={this.onInviteConfirmClicked.bind(this, item.id)}>Confirm</a>/<a onClick={this.onInviteCancelClicked.bind(this, item.id)}>Cancel</a>]&nbsp;&nbsp;</span>;

            }, this);

            inviteMessage = <div className="alert alert-primary">Waiting for enrollment confirmation by: <strong>{inviteList}</strong>.</div>
        }

        return (
            <Column count="12">

                <ProgramTabs
                    program={this.props.program}
                    selectedId="participants"/>

                <ProgramHeader
                    program={this.props.program}
                    name="Participants">
                    <form className="form-inline"><input className="form-control" onChange={this.onUpdateFilter} value={this.state.participantFilter} placeholder="Filter participants"></input> <button className="btn btn-default btn-sm btn-primary" onClick={this.onInviteParticipant}>Invite New Participant</button></form>
                </ProgramHeader>

                {inviteMessage}

                <DataTable
                    ref='table'
                    isLoading={this.state.isLoading}
                    columns={[
                        {name: 'Participant ID', key:"username"},
                        {name: "Compliance", value: function(row) {
                            return <a href="#" onClick={this.onInfoClicked.bind(this, row)}>
                                    <Circle radius={20} width={2} id={row.id} value={row.info.compliance_percentage}/>
                                </a>
                        }.bind(this)},
                        {name: "Status", key: 'info.program_participant_status', transform: function(value) { return <span className="label label-success">{ProgramParticipantStatus(value)}</span> }},
                        {name: "Uploaded", key: 'info.cached_last_upload_timestamp', transform: function(value) { return value ? moment(value).fromNow() : "N/A"; }},
                        {name: "Synced", key: 'info.cached_last_sync_timestamp', transform: function(value) { return value ? moment(value).fromNow() : "N/A"; }},
                        {name: 'Email', key: 'email'},
                        {name: 'Start Time', value: function(row) { return row.info.use_custom_start_stop_time ? row.info.custom_start_time : 'Default'}},
                        {name: 'Stop Time', value: function(row) { return row.info.use_custom_start_stop_time ? row.info.custom_stop_time  : 'Default'}},
                        {name: 'Assigned', value: function(row) { return row.assigned_surveys.length == 1 ? '1 survey' : row.assigned_surveys.length + ' surveys'}},
                        {name: 'Platform',  value: function(item) { return <span className="label label-success">{item.info.app_platform_name} {item.info.app_version_string} &nbsp;&nbsp;{item.info.is_running_latest_app_version ? '' : <i className="ss-upload"></i>}</span> }},
                    ]}
                    items={this.state.participantItems}
                    onRowClicked={this.onRowClicked}
                />

                <Dialog
                    show={this.state.showInfo}
                    onCancelClicked={this.onInfoCancelClicked}
                    title="Participant Info"
                >
                    <Form ref="infoForm">
                        <Row>
                            <Column count="4">
                                <FormGroup label="Uploaded Sets">
                                    <br/>
                                    <FormTextValue value={this.getProperty(this.state.participant, "info.cached_received_answer_set_count", "")}/>
                                </FormGroup>
                            </Column>
                            <Column count="4">
                                <FormGroup label="Answered Sets">
                                    <br/>
                                    <FormTextValue value={this.getProperty(this.state.participant, "info.cached_answered_answer_set_count", "")}/>
                                </FormGroup>
                            </Column>
                            <Column count="4">
                                <FormGroup label="Compliance %">
                                    <br/>
                                    <FormTextValue value={this.getProperty(this.state.participant, "info.compliance_percentage", "")}/>
                                </FormGroup>
                            </Column>
                        </Row>
                    </Form>
                </Dialog>

                <Dialog
                    show={this.state.showForm}
                    title="Invite Participant"
                    onSaveClicked={this.onSaveClicked}
                    onCancelClicked={this.onCancelClicked}
                    focused="first_name"
                    autoDisableSaveButton={true}
                >
                    <Form ref="inviteForm">
                        <Row>
                            <Column count="6">
                                <FormInputField label="First Name" name="first_name"/>
                            </Column>

                            <Column count="6">
                                <FormInputField label="Last Name" name="last_name"/>
                            </Column>

                            <Column count="6">
                                <FormInputField label="Email address" name="email_address"/>
                            </Column>
                            <Column count="6">
                                <FormInputField label="Phone Number" name="phone_number"/>
                            </Column>
                            <Column count="12">
                                <FormCheckbox noGroup={true} name="require_email_confirmation" label="Require email confirmation step" value={true}/><br/>
                            </Column>
                        </Row>
                    </Form>
                </Dialog>

                <Dialog
                    show={this.state.showParticipantForm}
                    title="Edit Participant"
                    onSaveClicked={this.onParticipantSaveClicked}
                    onCancelClicked={this.onParticipantCancelClicked}
                    focusedField="start_time"
                >
                    <Form ref="form">
                        <Row>
                            <Column count="4">
                                <FormGroup label="Custom Start/Stop">
                                    <FormCheckbox onValueChanged={this.onCustomTimeChanged} noGroup={true} name="info.use_custom_start_stop_time" label="Enabled"/><br/>
                                </FormGroup>
                            </Column>
                            <Column count="4">
                                <FormTimePicker label="Start Time" name="info.custom_start_time" disabled={!this.state.enableCustomTime}/>
                            </Column>
                            <Column count="4">
                                <FormTimePicker label="Stop Time" name="info.custom_stop_time" disabled={!this.state.enableCustomTime}/>
                            </Column>
                        </Row>

                        <Row>
                            <Column count="4">
                                <FormGroup label="Participant Status" forField="info.program_participant_status">
                                    <br/>
                                    <FormDropdown
                                        name="info.program_participant_status"
                                        items={[
                                            {value: 0, label: "Active", action:function() {}},
                                            {value: 1, label: "Stopped", action:function() {}},
                                            {value: 2, label: "Archived", action:function() {}}
                                        ]}
                                    />
                                </FormGroup>
                            </Column>
                            <Column count="4">
                            </Column>
                            <Column count="4">
                                <FormGroup label="Reset">
                                    <br/>
                                    <Button small={true} label="Reset Compliance" onClick={this.onResetComplianceClicked}/>
                                </FormGroup>
                            </Column>
                        </Row>

                        <hr/>

                        <Row>
                            <Column count="5">
                                <h5>Assigned Surveys</h5>
                                <DataList
                                    ref="toList"
                                    items={this.state.addedSurveys}
                                    dataIdField="id"
                                    dataNameField="display_name"
                                    allowMultiSelect={true}
                                />
                            </Column>
                            <Column count="2">
                                <h5></h5>
                                <div>
                                    <br/>
                                    <br/>
                                    <button className="btn btn-default" onClick={function() {this.addSelectedSurveys(this.refs.fromList)}.bind(this) }><i className="ss-rewind"></i></button>&nbsp;
                                    <button className="btn btn-default" onClick={function() {this.removeSelectedSurveys(this.refs.toList)}.bind(this) }><i className="ss-fastforward"></i></button>
                                </div>
                            </Column>
                            <Column count="5">
                                <h5>Available Surveys</h5>
                                <DataList
                                    ref="fromList"
                                    items={this.state.availableSurveys}
                                    dataIdField="id"
                                    dataNameField="display_name"
                                    allowMultiSelect={true}
                                />
                            </Column>
                        </Row>

                        <hr/>

                        <Row>
                            <Column count="5">
                                <FormGroup label="">
                                    <br/>
                                    <FormDropdown
                                        onValueChanged={this.onSurveyToResetChanged}
                                        name="survey_to_reset"
                                        valueField="uuid"
                                        labelField="display_name"
                                        emptyLabel="Select"
                                        items={this.state.allSurveys}
                                    />

                                    <br/>
                                    <br/>

                                    {iterationsInfo}
                                </FormGroup>
                            </Column>
                            <Column count="7">
                                <FormGroup label="">
                                    <br/>
                                    <Button small={true} label="Reset Iterations for selected Survey" onClick={this.onResetIterationsClicked}/>
                                </FormGroup>
                            </Column>
                        </Row>

                    </Form>
                </Dialog>

                <Dialog
                    show={this.state.showBulkAssignForm}
                    title="Bulk Assign Surveys"
                    onSaveClicked={this.onBulkAssignSaveClicked}
                    onCancelClicked={this.onBulkAssignCancelClicked}
                >
                    <Form ref="formBulk">
                        <div className="alert alert-primary">Assigned surveys will replace existing surveys for selected participants.</div>
                        <Row>
                            <Column count="5">
                                <h5>Assigned Surveys</h5>
                                <DataList
                                    ref="toList2"
                                    items={this.state.addedSurveys}
                                    dataIdField="id"
                                    dataNameField="display_name"
                                    allowMultiSelect={true}
                                />
                            </Column>
                            <Column count="2">
                                <h5></h5>
                                <div>
                                    <br/>
                                    <br/>
                                    <button className="btn btn-default" onClick={function() {this.addSelectedSurveys(this.refs.fromList2)}.bind(this) }><i className="ss-rewind"></i></button>&nbsp;
                                    <button className="btn btn-default" onClick={function() {this.removeSelectedSurveys(this.refs.toList2)}.bind(this) }><i className="ss-fastforward"></i></button>
                                </div>
                            </Column>
                            <Column count="5">
                                <h5>Available Surveys</h5>
                                <DataList
                                    ref="fromList2"
                                    items={this.state.availableSurveys}
                                    dataIdField="id"
                                    dataNameField="display_name"
                                    allowMultiSelect={true}
                                />
                            </Column>
                        </Row>
                    </Form>
                </Dialog>

            </Column>
        );
    }
});