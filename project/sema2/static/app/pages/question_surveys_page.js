var ProgramSurveysPage = React.createClass({

    mixins: [UrlBuilderMixin, ModelUtilsMixin],

    getInitialState: function() {
        return {
            groups: [],
            addedSets: [],
            availableSets: [],
            selectedIndex:0,
            isEditing: false,
            currentSurvey: null,
            selectedTab: "properties"
        };
    },

    componentDidMount: function() {
        this.refreshData();
    },

    refreshData: function() {

        var self = this;

        var req = this.buildRequest(["programs", this.props.program.id, "surveys"]);
        var first = $.get(req.url);

        var setsReq = this.buildRequest(["programs", this.props.program.id, "sets"]);
        var second = $.get(setsReq.url);

        var schedules = this.reactGetRequest(["programs", this.props.program.id, "schedules"]);

        $.when(first, second, schedules).done(function(first, second, schedules) {

            var groups = first[0];
            var allSets = second[0];

            if (self.isMounted()) {

                self.setState({
                    groups: groups,
                    allSets: allSets,
                    schedules: schedules[0]
                }, function() {

                    if (self.state.selectedIndex >= 0) {
                        self.getDataForSurvey(self.state.selectedIndex);
                    }
                });
            }
        })

            .fail(function(){

            });
    },

    getDataForSurvey: function(surveyIndex) {

        if (this.state.groups.length == 0) {

            // Set all sets as available
            this.setState({
               availableSets: this.state.allSets
            });
        }
        else {

            var surveyId = this.state.groups[surveyIndex].id;

            var req = this.buildRequest(["surveys", surveyId]);

            $.get(req.url, function (result) {

                if (this.isMounted()) {

                    var addedSets = result.question_sets.sort(function (a, b) {
                        a.id - b.id
                    });
                    var availableSets = this.getAvailableSets(addedSets);

                    var groups = this.state.groups;
                    groups[surveyIndex].display_name = result.display_name;

                    this.setState({
                        groups: groups,
                        currentSurvey: result,
                        addedSets: addedSets,
                        availableSets: availableSets
                    }, function () {

                    });
                }

            }.bind(this));
        }
    },

    onSaveClicked: function() {

        this.saveCurrentSurvey();
        this.setState({isEditing:false});
    },

    onCancelClicked: function() {
        this.setState({isEditing:false}, function() {
            this.refreshData();
        }.bind(this));
    },

    saveCurrentSurvey: function() {

        var data = this.refs.form.getValues();

        this.reactAddOrUpdateRequest(["surveys"], data.id, data)
        .then(function(res) {

            var setIds = this.state.addedSets.map(function(item) { return item.id });

            this.reactAddOrUpdateRequest(["surveys", res.id, "selected_sets"], null, setIds)

            .then(function(res) {
                if (this.isMounted()) {
                    this.refreshData();
                }
            }.bind(this))
            .fail(function(err) {
                alert("Error setting question sets for survey");
            });

        }.bind(this))
        .fail(function(err) {
            alert("Error updating survey");
        });
    },

    getAvailableSets: function(addedSets) {

        var allSets = this.state.allSets.sort(function(a, b) {a.id - b.id});
        var addedIds = addedSets.map(function(item) {return item.id});
        var availableSets = [];
        for (var i = 0; i < allSets.length; i++) {
            if (addedIds.indexOf(allSets[i].id) == -1) {
                availableSets.push(allSets[i]);
            }
        }

        return availableSets;
    },

    onAddSurveyClicked:function() {

        this.refs.form.setValues(Survey(this.props.program_version.id));

        this.setState({
            isEditing:true
        });
    },

    onEditSurveyClicked:function() {
        this.refs.form.setValues(this.state.currentSurvey);
        this.setState({isEditing:true});
    },

    onCloneSurveyClicked:function() {

        this.refs.confirmDlg.showWithMessage("Clone Survey?" , "Are you sure you want to clone this survey?", "Cancel", "Clone", function() {

            this.reactPostRequest(["surveys", this.state.currentSurvey.id, "clone"], null, null)
                .done(function (res) {
                    this.refreshData();
                }.bind(this))
                .fail(function (res) {
                    alert("Unable to clone survey");
                });

        }.bind(this));
    },

    onArchiveSurveyClicked:function() {

        this.refs.confirmDlg.showWithMessage("Archive Survey?" , "Are you sure you want to archive this survey?", "Cancel", "Archive", function() {

            this.reactPostRequest(["surveys", this.state.currentSurvey.id, "archive"], null, null)
                .done(function (res) {
                    window.location.reload();
                }.bind(this))
                .fail(function (res) {
                    alert("Unable to archive survey");
                });

        }.bind(this));
    },

    onItemClicked: function(itemData, index) {
        this.setState({selectedIndex:index});
        this.getDataForSurvey(index);
    },

    addSelectedSets: function() {
        var newSets = this.refs.fromList.getSelectedItems();
        var addedSets = this.state.addedSets;

        addedSets = $.merge(addedSets, newSets);
        var availableSets = this.getAvailableSets(addedSets);

        this.setState({
            addedSets: addedSets,
            availableSets: availableSets
        });

        this.refs.fromList.clearSelectedItems();
    },

    removeSelectedSets: function() {
        var removedSets = this.refs.toList.getSelectedItems();
        var removedIds = removedSets.map(function(item) { return item.id });

        var addedSets = this.state.addedSets.filter(function(item) {
            return removedIds.indexOf(item.id) == -1;
        });

        var availableSets = this.getAvailableSets(addedSets);

        this.setState({
            addedSets: addedSets,
            availableSets: availableSets
        });

        this.refs.toList.clearSelectedItems();
    },

    triggeredQuestionSetList: function() {

        if (this.state.currentSet) {
            return [];
        }

        var currentSet = this.state.currentSet;
        var items = [];

        questionSet.questions.forEach(function(question) {
            question.predicates.forEach(function(pred) {
                items.push(pred.target_question_set_name);
            }, this);
        }, this);

        return items;
    },

    render: function() {

        var surveyStructureGraphUrl = this.state.currentSurvey ? "/api/1/surveys/" + this.state.currentSurvey.id + "/structure_graph/" : null;

        var availableTopLevelQuestionSets = this.state.availableSets.filter(function(item) {
            return !item.is_jump_target;
        });

        var disableSurveyList = this.state.groups.length == 0;
        var disableInputs = this.props.program.is_locked;

        var surveyList = (
            <TabPanel selectedTab={this.state.selectedTab} onSelectionChange={function(tabId) {this.setState({selectedTab:tabId})}.bind(this)}>
                <Tab label="Properties" id="properties">
                    <Row>
                        <Column count="3">
                            <FormGroup label="Name">
                                <br/>
                                <FormTextValue value={this.getProperty(this.state.currentSurvey, "display_name", "")}/>
                            </FormGroup>
                        </Column>
                        <Column count="3">
                            <FormGroup label="Randomise set order">
                                <br/>
                                <FormBooleanValue value={this.getProperty(this.state.currentSurvey, "randomise_set_order", "")}/>
                            </FormGroup>
                        </Column>
                        <Column count="2">
                            <FormGroup label="Trigger Mode">
                                <br/>
                                <FormOptionValue
                                    value={this.getProperty(this.state.currentSurvey, "trigger_mode", "")}
                                    options={
                                    {0: 'Scheduled', 1: 'Ad Hoc'}
                                        }/>
                            </FormGroup>
                        </Column>
                        <Column count="4">
                            <ItemBar>
                                <RightItems>
                                    <Button small={true} onClick={this.onArchiveSurveyClicked} label="Archive" disabled={disableInputs}/>&nbsp;<Button small={true} onClick={this.onCloneSurveyClicked} label="Clone" disabled={disableInputs}/>&nbsp;<Button type="primary" small={true} onClick={this.onEditSurveyClicked} label="Edit" disabled={disableInputs}/>&nbsp;
                                </RightItems>
                            </ItemBar>
                        </Column>
                    </Row>
                    <Row>
                        <Column count="3">
                            <FormGroup label="Max Iterations">
                                <br/>
                                <FormTextValue value={this.getProperty(this.state.currentSurvey, "max_iterations", "")}/>
                            </FormGroup>
                        </Column>
                        <Column count="3">
                            <FormGroup label="Schedule Name">
                                <br/>
                                <FormTextValue value={this.getProperty(this.state.currentSurvey, "schedule_name", "")}/>
                            </FormGroup>
                        </Column>
                    </Row>
                </Tab>
                <Tab label="Included Question Sets" id="questions">
                    <DataTable
                        columns={[
                            {name: 'Included Question Sets', value: function(rowData) {

                                var items = [];

                                rowData.questions.forEach(function(question) {
                                    question.predicates.forEach(function(pred) {
                                        items.push(<div key={pred.target_question_set_name}>- {pred.target_question_set_name}</div>);
                                    }, this);
                                }, this);

                                var conditionalBlock = items.length > 0 ?
                                (<div>
                                    <br/>
                                    <p className="help"><i className="ss-help"></i> This Question Set conditionally triggers the following Question Sets:</p>
                                    {items}
                                </div>) : null;

                                return (
                                <div>
                                    {rowData.display_name}
                                    {conditionalBlock}
                                </div>)
                            }}
                        ]}
                        items={this.state.addedSets}
                        onRowClicked={this.editSchedule}
                    />
                </Tab>
                <Tab label="Conditional Structure" id="structure">
                    {this.props.program.feature_enable_conditional_question_sets ? <img src={surveyStructureGraphUrl} width="100%"></img> : <p className="help"><i className="ss-help"></i> Conditional Questions Sets must be enabled in Program settings to enable the Conditional Structure view.</p>}
                </Tab>
            </TabPanel>
        );

        return (
            <Page>
                <Column count="12">

                    <ProgramTabs
                        program={this.props.program}
                        selectedId="surveys"/>

                    <ProgramHeader
                        program={this.props.program}
                        name="Surveys">
                        <Button type="primary" small={true} onClick={this.onAddSurveyClicked} label="Add New Survey" disabled={this.props.program.is_locked}/>&nbsp;
                    </ProgramHeader>
                </Column>
                <Column count="12">
                    <Row>
                        <Column count="3">
                            <h5>Surveys in Program</h5>
                            <DataList
                                dataIdField="id"
                                value={function(item, index) { return (index+1) + ". " + item.display_name }}
                                items={this.state.groups}
                                onItemClicked={this.onItemClicked}
                                selectedItemIndex={this.state.selectedIndex}
                            />
                        </Column>
                        <Column count="9">
                            {disableSurveyList ? null : surveyList}
                        </Column>
                    </Row>
                </Column>
                <ConfirmDialog
                    ref="confirmDlg"
                />

                <Dialog
                    show={this.state.isEditing}
                    title="Edit Survey"
                    onSaveClicked={this.onSaveClicked}
                    onCancelClicked={this.onCancelClicked}
                >
                    <Form ref="form">
                        <Row>
                            <Column count="8">
                                <FormInputField label="Display name" name="display_name"/>
                            </Column>
                            <Column count="4">
                                <FormCheckbox groupLabel="Randomise set order" label="Randomise" name="randomise_set_order"/>
                            </Column>
                        </Row>
                        <Row>
                            <Column count="4">
                                <FormGroup label="Trigger Mode" forField="trigger_mode">
                                    <br/>
                                    <FormDropdown
                                        name="trigger_mode"
                                        items={[
                                            {value: 0, label: "Scheduled", action:function() {}},
                                            {value: 1, label: "Ad Hoc", action:function() {}}
                                        ]}
                                    />
                                </FormGroup>
                            </Column>
                            <Column count="4">
                                <FormGroup label="Schedule" forField="schedule">
                                    <br/>
                                    <FormDropdown
                                        name="schedule"
                                        items={this.state.schedules}
                                        labelField="display_name"
                                        valueField="id"
                                    />
                                </FormGroup>
                            </Column>
                            <Column count="4">
                                <FormInputField label="Max iterations" name="max_iterations"/>
                            </Column>
                        </Row>
                        <hr/>
                        <Row>
                            <Column count="5">
                                <h5>Question Sets in Survey</h5>
                                <DataList
                                    ref="toList"
                                    items={this.state.addedSets}
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
                                    <button className="btn btn-default" onClick={this.addSelectedSets}><i className="ss-rewind"></i></button>&nbsp;
                                    <button className="btn btn-default" onClick={this.removeSelectedSets}><i className="ss-fastforward"></i></button>
                                </div>
                            </Column>
                            <Column count="5">
                                <h5>Available Question Sets</h5>
                                <DataList
                                    ref="fromList"
                                    items={availableTopLevelQuestionSets}
                                    dataIdField="id"
                                    dataNameField="display_name"
                                    allowMultiSelect={true}
                                />
                            </Column>
                        </Row>
                        <Row>
                            <Column count="12">
                                <br/>
                                <p className="help"><i className="ss-help"></i> Conditional Question Sets that are the destination of a conditional jump will automatically be bundled with the Survey and do not need to be added manually.</p>
                            </Column>
                        </Row>
                    </Form>
                </Dialog>
            </Page>
        );
    }
});