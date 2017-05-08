var ProgramQuestionSetsPage = React.createClass({

    mixins: [UrlBuilderMixin, ModelUtilsMixin],

    getInitialState: function() {
        return {
            questions: [],
            currentSet: null,
            selectedIndex: 0,
            selectedTab: "properties"
        };
    },

    componentDidMount: function() {
        this.refreshData();
    },

    refreshData: function() {

        var req = this.buildRequest(["programs", this.props.program.id, "sets"]);

        $.get(req.url, function (result) {

            if (this.isMounted()) {

                var selectedIndex = this.state.selectedIndex;

                if (this.state.selectedIndex >= result.length) {
                    selectedIndex = 0;
                }

                var selectedSet = result[selectedIndex];

                this.setState({
                    sets: result,
                    selectedIndex: selectedIndex,
                    selectedSet: selectedSet
                }, function() {

                });
            }
        }.bind(this));

    },

    onAddQuestionSet:function() {
        this.refs.form.setValues(QuestionSet(this.props.program_version.id));

        this.setState({
            isEditing:true
        });
    },

    onEditQuestionSet: function() {

        this.refs.form.setValues(this.state.selectedSet);

        this.setState({
            isEditing:true
        });
    },

    onSaveClicked: function() {

        var self = this;

        var data = this.refs.form.getValues();
        var req = this.buildRequest(["sets"], data.id);

        var set = $.ajax({
            type:req.method,
            url:req.url,
            data: JSON.stringify(data),
            dataType: 'json',
            contentType: "application/json",
            success: function(res) {

                self.setState({
                    isEditing:false
                }, function() {
                    this.refreshData();
                });

            }
        });
    },

    onCancelClicked: function() {
        this.setState({isEditing:false}, function() {
            this.refreshData();
        }.bind(this));
    },

    onItemClicked: function(itemData, index) {

        this.setState({
            selectedSet: itemData,
            selectedIndex: index
        });
    },

    onCloneQuestionSetClicked:function() {

        this.refs.confirmDlg.showWithMessage("Clone Question Set?" , "Are you sure you want to clone this question set?", "Cancel", "Clone", function() {

            this.reactPostRequest(["sets", this.state.selectedSet.id, "clone"], null, null)
                .done(function (res) {
                    this.refreshData();
                }.bind(this))
                .fail(function (res) {
                    alert("Unable to clone question set");
                });

        }.bind(this));
    },

    onArchiveQuestionSetClicked:function() {

        this.refs.confirmDlg.showWithMessage("Archive Question Set?" , "Are you sure you want to archive this question set?", "Cancel", "Archive", function() {

            this.reactPostRequest(["sets", this.state.selectedSet.id, "archive"], null, null)
                .done(function (res) {
                    this.refreshData();
                }.bind(this))
                .fail(function (res) {
                    alert("Unable to archive question set");
                });

        }.bind(this));
    },

    onAddTextQuestionClicked: function() {

        this.refs.questionForm.setValues(Question(this.props.program_version.id, this.state.selectedSet.id, 0));

        this.setState({
            currentOptions:[],
            currentPredicates:[],
            isEditingQuestion:true,
            questionType: 0 // Text Question
        });
    },

    onAddMultiQuestionClicked: function() {

        this.refs.questionForm.setValues(Question(this.props.program_version.id, this.state.selectedSet.id, 1));

        this.setState({
            currentOptions:[],
            currentPredicates:[],
            isEditingQuestion:true,
            questionType: 1 // MQ Question
        });
    },

    onAddRadioQuestionClicked: function() {

        this.refs.questionForm.setValues(Question(this.props.program_version.id, this.state.selectedSet.id, 2));

        this.setState({
            currentOptions:[],
            currentPredicates:[],
            isEditingQuestion:true,
            questionType: 2 // Radio Question
        });
    },

    onAddSliderQuestionClicked: function() {

        this.refs.questionForm.setValues(Question(this.props.program_version.id, this.state.selectedSet.id, 3));

        this.setState({
            currentOptions:[],
            currentPredicates:[],
            isEditingQuestion:true,
            questionType: 3 // Slider Question
        });
    },

    onSaveQuestionClicked: function() {

        var self = this;
        var data = this.refs.questionForm.getValues();

        var optionsValues = this.refs.optionsTable ? this.refs.optionsTable.getValues() : [];
        var req = this.buildRequest(["questions"], data.id);
        data.options = optionsValues;

        var predicates = this.refs.predicatesTable ? this.refs.predicatesTable.getValues() : [];
        data.predicates = predicates;

        this.setState({
            currentOptions:optionsValues
        }, function() {

            var question = $.ajax({
                type:req.method,
                url:req.url,
                data: JSON.stringify(data),
                dataType: 'json',
                contentType: "application/json",
                success: function(res) {

                    self.setState({
                        isEditingQuestion:false
                    }, function() {
                        this.refreshData();
                    });

                }
            });
        });
    },

    onCancelQuestionClicked: function() {

        this.setState({isEditingQuestion:false}, function() {
            this.refreshData();
        }.bind(this));
    },

    onDeleteQuestionClicked: function(questionId, index, event) {

        event.preventDefault();
        event.stopPropagation();

        if (this.props.program.is_locked) {
            return;
        }

        var self = this;

        this.refs.confirmDlg.showWithMessage("Delete" , "Are you sure you want to delete this question?", "Cancel", "Delete", function() {

            var req = self.buildRequest(["questions"], questionId);

            var question = $.ajax({
                type:'DELETE',
                url:req.url,
                dataType: 'json',
                contentType: "application/json",
                success: function(res) {

                    self.setState({
                        isEditingQuestion:false
                    }, function() {
                        self.refreshData();
                    });

                }
            });

        }, true);

    },

    onCloneQuestionClicked: function(questionId, index, event) {

        event.preventDefault();
        event.stopPropagation();

        if (this.props.program.is_locked) {
            return;
        }

        var self = this;

        var questions = this.state.selectedSet.questions;
        var question = questions[index];
        var newQuestion = Question(question.program_version, question.set, question.question_type);
        newQuestion.question_text = question.question_text;
        newQuestion.question_tag = question.question_tag + "-copy";

        var options = question.options.map(function(option) {
            return QuestionOption(option.label, option.value);
        });

        //
        newQuestion.options = options;

        //
        newQuestion.min_value = question.min_value;
        newQuestion.min_label = question.min_label;

        //
        newQuestion.max_value = question.max_value;
        newQuestion.max_label = question.max_label;

        //
        newQuestion.predicates = [];

        //
        questions.splice(index, 0, newQuestion);

        this.reactPostRequest(["questions"], null, newQuestion)
            .done(function(res) {
                this.refreshData();
            }.bind(this))
            .fail(function(res) {
                alert("Unable to clone question");
            });
    },


    onEditQuestionClicked: function(rowData, event) {

        this.refs.questionForm.setValues(rowData);

        // Do not allow predicate editing if this question is a jump target otherwise we might get cycles
        // We can fix this later with smarter cycle detection
        this.setState({
            currentOptions:rowData.options,
            currentPredicates:rowData.predicates,
            isEditingQuestion: true,
            questionType:rowData.question_type
        })
    },

    onAddOptionClicked: function() {

        if (this.props.program.is_locked) {
            return;
        }

        var options = this.state.currentOptions;
        var index = options.length+1;
        options.push(QuestionOption("Option " + index, index));
        this.setState({
            currentOptions:options
        });
    },

    onDeleteOptionClicked: function(optionId, index) {

        if (this.props.program.is_locked) {
            return;
        }

        var self = this;

        var options = this.state.currentOptions;

        options.splice(index, 1);

        self.setState({
            currentOptions: options
        }, function () {

        });
    },

    onCloneOptionClicked: function(optionId, index) {

        if (this.props.program.is_locked) {
            return;
        }

        var self = this;

        var options = this.state.currentOptions;
        var option = options[index];
        var newOption = QuestionOption(option.label + "", option.value);

        options.splice(index, 0, newOption);

        self.setState({
            currentOptions: options
        }, function () {

        });
    },

    currentQuestionCanBeSaved: function() {

        if (this.state.questionType == 1 || this.state.questionType == 2) {
            return this.state.currentOptions.length > 0
        }
        else {
            return true
        }
    },

    onAddPredicateClicked: function() {

        if (this.props.program.is_locked) {
            return;
        }

        var preds = this.state.currentPredicates;
        var index = preds.length+1;
        preds.push(ConditionalQuestionPredicate(null, -1, -1, "", null));
        this.setState({
            currentPredicates:preds
        });
    },

    onDeletePredicateClicked: function(optionId, index) {

        if (this.props.program.is_locked) {
            return;
        }

        var self = this;

        var preds = this.state.currentPredicates;

        preds.splice(index, 1);

        self.setState({
            currentPredicates: preds
        }, function () {

        });
    },

    questionSetSelectorFilter: function(item) {

        if (!this.state.sets || !this.state.currentPredicates) {
            return true;
        }

        var existing = this.state.currentPredicates.find(function(pred) {
            return pred.target_question_set == item.id;
        });

        return !existing;
    },

    render: function() {

        var disablePredicateEditing = (this.state.selectedSet && this.state.selectedSet.is_jump_target) || !this.props.program.feature_enable_conditional_question_sets;

        var availableQuestionSetsToLink = (this.state.selectedSet && this.state.sets) ? this.state.sets.filter(function(item) {

            return item.id != this.state.selectedSet.id;

        }, this) : [];

        var availableOptionsToLink = this.state.currentOptions ? this.state.currentOptions.filter(function(item) {

            //// Is there is already a predicate linked to this option?
            //var existing = this.state.currentPredicates.find(function(d) {
            //    return parseInt(d.target_value) == item.value;
            //});

            return true;

        }, this) : null;

        return (
            <Page>
                <Column count="12">

                    <ProgramTabs
                        program={this.props.program}
                        selectedId="questions"/>

                    <ProgramHeader
                        program={this.props.program}
                        name="Questions">
                        <Button type="primary" small={true} onClick={this.onAddQuestionSet} label="Create Question Set" disabled={this.props.program.is_locked}/>
                    </ProgramHeader>
                </Column>
                <Column count="12">
                    <Row>
                        <Column count="3">
                            <h5>Question Sets in Program</h5>
                            <DataList
                                dataIdField="id"
                                value={function(item, index) { return (index+1) + ". " + item.display_name }}
                                items={this.state.sets}
                                onItemClicked={this.onItemClicked}
                                selectedItemIndex={this.state.selectedIndex}
                            />
                        </Column>
                        <Column count="9">
                            <TabPanel selectedTab={this.state.selectedTab} onSelectionChange={function(tabId) {this.setState({selectedTab:tabId})}.bind(this)}>
                                <Tab label="Properties" id="properties">
                                    <Row>
                                        <Column count="3">
                                            <FormGroup label="Name">
                                                <br/>
                                                <FormTextValue value={this.getProperty(this.state.selectedSet, "display_name", "")}/>
                                            </FormGroup>
                                        </Column>
                                        <Column count="3">
                                            <FormGroup label="Randomise question order">
                                                <br/>
                                                <FormBooleanValue value={this.getPropertyAsBoolean(this.state.selectedSet, "randomise_question_order", false)}/>
                                            </FormGroup>
                                        </Column>
                                        <Column count="6">
                                            <ItemBar>
                                                <RightItems>
                                                    <Button small={true} onClick={this.onArchiveQuestionSetClicked} label="Archive" disabled={this.props.program.is_locked || (this.state.sets != null && this.state.sets.length == 1)}/>&nbsp;<Button small={true} onClick={this.onCloneQuestionSetClicked} label="Clone" disabled={this.props.program.is_locked}/>&nbsp;<Button type="primary" small={true} onClick={this.onEditQuestionSet} label="Edit" disabled={this.props.program.is_locked}/>&nbsp;
                                                </RightItems>
                                            </ItemBar>
                                        </Column>
                                    </Row>
                                    <Row>
                                        <Column count="12">
                                            { this.state.selectedSet && this.state.selectedSet.is_jump_target ? <p className="help"><i className="ss-help"></i> This Question Set is conditionally shown depending on answers given in another Question Set.</p> : null }
                                        </Column>
                                    </Row>
                                </Tab>
                                <Tab label="Included Questions" id="questions">
                                    <ItemBar>
                                        <RightItems>
                                            <Button small={true} onClick={this.onAddTextQuestionClicked} label="Add Text Question" disabled={this.props.program.is_locked}/>&nbsp;
                                            <Button small={true} onClick={this.onAddMultiQuestionClicked} label="Add Multi Choice Question" disabled={this.props.program.is_locked}/>&nbsp;
                                            <Button small={true} onClick={this.onAddRadioQuestionClicked} label="Add Radio Question" disabled={this.props.program.is_locked}/>&nbsp;
                                            <Button small={true} onClick={this.onAddSliderQuestionClicked} label="Add Slider Question" disabled={this.props.program.is_locked}/>&nbsp;
                                        </RightItems>
                                    </ItemBar>
                                    <hr/>
                                    <DataTable
                                        columns={[
                                            {name: 'Type', size: 1, value: function(rowData) {
                                                    return <span className="label label-primary">{QuestionTypeString(rowData.question_type)} {rowData.options.length > 0 ? "(" + rowData.options.length + ")" : null}</span>
                                                }
                                            },
                                            {name: 'Tag', key: "question_tag", size: 1, transform: function(item) { return <span className="label label-success">{item}</span> }},
                                            {name: 'Question Text', size:9, value: function(rowData) {

                                                var html = marked(rowData.question_text);

                                                return <div>
                                                    <div dangerouslySetInnerHTML={{__html:html}}></div>
                                                    <ul className="predicate-list">
                                                    {rowData.predicates.map(function(item) {
                                                        return <li key={item.id} className="predicate-label">&rarr; {item.desc}</li>
                                                    })}
                                                    </ul>
                                                </div>
                                            }},
                                            {name: '', value:function(rowData, index) {
                                                return <div>
                                                        <a href="#" disabled={this.props.program.is_locked} onClick={this.onCloneQuestionClicked.bind(this, rowData.id, index)}><i className="ss-icon" title="Clone"></i></a>&nbsp;&nbsp;&nbsp;&nbsp;
                                                        <a href="#" disabled={this.props.program.is_locked} onClick={this.onDeleteQuestionClicked.bind(this, rowData.id, index)}><i className="ss-icon" title="Delete"></i></a>
                                                    </div>
                                                    }.bind(this) , size:1},
                                        ]}
                                        items={this.state.selectedSet ? this.state.selectedSet.questions : []}
                                        onRowClicked={this.onEditQuestionClicked}
                                    />
                                </Tab>
                            </TabPanel>
                        </Column>
                    </Row>
                </Column>

                <ConfirmDialog
                    ref="confirmDlg"
                />

                <Dialog
                    show={this.state.isEditing}
                    title="Edit Question Set"
                    onSaveClicked={this.onSaveClicked}
                    onCancelClicked={this.onCancelClicked}
                    saveDisabled={this.props.program.is_locked}
                    focusedField="display_name"
                >
                    <Form ref="form">
                        <Row>
                            <Column count="6">
                                <FormInputField label="Question Set Name" name="display_name" disabled={this.props.program.is_locked}/>
                            </Column>

                            <Column count="6">
                                <FormCheckbox label="Randomise question order" name="randomise_question_order" disabled={this.props.program.is_locked}/>
                            </Column>

                            <Column count="6">
                            </Column>

                            <Column count="6">
                            </Column>

                        </Row>
                    </Form>
                </Dialog>
                <Dialog
                    show={this.state.isEditingQuestion}
                    title="Edit Question"
                    onSaveClicked={this.onSaveQuestionClicked}
                    onCancelClicked={this.onCancelQuestionClicked}
                    saveDisabled={this.props.program.is_locked || !this.currentQuestionCanBeSaved()}
                    focused="question_text"
                >
                    <Form
                        ref="questionForm"
                    >
                        <Row>
                            <Column count="9">
                                <FormInputField label="Text" name="question_text" isRequired={true} disabled={this.props.program.is_locked}/>
                            </Column>

                            <Column count="3">
                                <FormInputField label="Tag" name="question_tag" isRequired={true} disabled={this.props.program.is_locked}/>
                            </Column>
                        </Row>

                        <div className="help">
                            Formatting help: **text** = <strong>text</strong>, *text* = <em>text</em>
                        </div>

                        <StatePanel state={this.state.questionType ? this.state.questionType : 'default'}>

                            <State name="1,2">
                                <Row>
                                    <Column count="12">
                                        <hr/>
                                    </Column>
                                    <Column count="12">
                                        <ItemBar>
                                            <LeftItems>
                                                <FormCheckbox noGroup={true} label="Randomise option order" name="randomise_option_order" disabled={this.props.program.is_locked}/>
                                            </LeftItems>

                                            <RightItems>
                                                <Button type="primary" label="Add Option" small={true} onClick={this.onAddOptionClicked} disabled={this.props.program.is_locked}/>
                                            </RightItems>
                                        </ItemBar>
                                        <DataTable
                                            ref="optionsTable"
                                            disabled={this.props.program.is_locked}
                                            columns={[
                                                {name: 'Option', key: 'label', size:10, isEditable: true},
                                                {name: 'Value', key: 'value', size:2, isEditable: true},
                                                {name: '', value: function(rowData, index) {return <a href="#" onClick={this.onCloneOptionClicked.bind(this, rowData.id, index)}><i className="ss-icon" title="Clone"></i></a>}.bind(this)},
                                                {name: '', value: function(rowData, index) {return <a href="#" onClick={this.onDeleteOptionClicked.bind(this, rowData.id, index)}><i className="ss-icon" title="Delete"></i></a>}.bind(this)}
                                            ]}
                                            items={this.state.currentOptions ? this.state.currentOptions : []}
                                        />
                                    </Column>
                                </Row>
                            </State>

                            <State name="3">
                                <Row>
                                    <Column count="12">
                                        <hr/>
                                    </Column>
                                    <Column count="3">
                                        <FormInputField label="Min Value" name="min_value" isRequired={true} type="number" disabled={this.props.program.is_locked}/>
                                    </Column>

                                    <Column count="9">
                                        <FormInputField label="Min Label" name="min_label" isRequired={true} disabled={this.props.program.is_locked}/>
                                    </Column>
                                </Row>
                                <Row>
                                    <Column count="3">
                                        <FormInputField label="Max Value" name="max_value" isRequired={true} type="number" disabled={this.props.program.is_locked}/>
                                    </Column>

                                    <Column count="9">
                                        <FormInputField label="Max Label" name="max_label" isRequired={true} disabled={this.props.program.is_locked}/>
                                    </Column>
                                </Row>
                            </State>

                        </StatePanel>

                        <Row>
                            <Column count="12">

                                <hr/>

                                <ItemBar>
                                    <LeftItems>
                                        { disablePredicateEditing && this.props.program.feature_enable_conditional_question_sets ? <p className="help"><i className="ss-help"></i> Conditional Question Set editing has been disabled for this Question as its containing Question Set is the destination of another Question.</p> : null }
                                    </LeftItems>
                                    <RightItems>
                                        { disablePredicateEditing ? null : <Button type="primary" label="Add Predicate" small={true} onClick={this.onAddPredicateClicked} disabled={this.props.program.is_locked || disablePredicateEditing}/>}
                                    </RightItems>
                                </ItemBar>
                            </Column>
                        </Row>

                        <StatePanel state={this.state.questionType != undefined && !disablePredicateEditing ? this.state.questionType : 'default'}>

                            <State name="0">
                                <Row>
                                    <Column count="12">
                                        <DataTable
                                            ref="predicatesTable"
                                            disabled={this.props.program.is_locked}
                                            columns={[
                                                {name: 'Jump to:', key: 'target_question_set', size: 8, isEditable: true, useSelector: true, selectorKeyField: "id", selectorLabelField: "display_name", selectorItems:availableQuestionSetsToLink, selectorFilter: this.questionSetSelectorFilter},
                                                {name: 'When Answer contains', key: 'target_value', size: 4, isEditable: true},
                                                {name: '', value: function(rowData, index) {return <a href="#" onClick={this.onDeletePredicateClicked.bind(this, rowData.id, index)}><i className="ss-icon" title="Delete"></i></a>}.bind(this)}
                                            ]}
                                            items={this.state.currentPredicates ? this.state.currentPredicates : []}
                                        />
                                    </Column>
                                </Row>
                            </State>

                            <State name="1,2">
                                <Row>
                                    <Column count="12">
                                        <DataTable
                                            ref="predicatesTable"
                                            disabled={this.props.program.is_locked}
                                            columns={[
                                                {name: 'Jump to:', key: 'target_question_set', size: 8, isEditable: true, useSelector: true, selectorKeyField: "id", selectorLabelField: "display_name", selectorItems:availableQuestionSetsToLink, selectorFilter: this.questionSetSelectorFilter},
                                                {name: 'When Answer Is', key: 'target_value', size: 4, isEditable: true, useSelector: true, selectorKeyField: "value", selectorLabelField: "label", selectorItems:availableOptionsToLink},
                                                {name: '', value: function(rowData, index) {return <a href="#" onClick={this.onDeletePredicateClicked.bind(this, rowData.id, index)}><i className="ss-icon" title="Delete"></i></a>}.bind(this)}
                                            ]}
                                            items={this.state.currentPredicates ? this.state.currentPredicates : []}
                                        />
                                    </Column>
                                </Row>
                            </State>

                            <State name="3">
                                <Row>
                                    <Column count="12">
                                        <DataTable
                                            ref="predicatesTable"
                                            disabled={this.props.program.is_locked}
                                            columns={[
                                                {name: 'Jump to when answer is between:', key: 'target_question_set', size: 8, isEditable: true, useSelector: true, selectorKeyField: "id", selectorLabelField: "display_name", selectorItems:availableQuestionSetsToLink, selectorFilter: this.questionSetSelectorFilter},
                                                {name: 'Min (Incl.)', key: 'target_min_value_incl', size: 2, isEditable: true},
                                                {name: 'Max (Incl.)', key: 'target_max_value_incl', size: 2, isEditable: true},
                                                {name: '', value: function(rowData, index) {return <a href="#" onClick={this.onDeletePredicateClicked.bind(this, rowData.id, index)}><i className="ss-icon" title="Delete"></i></a>}.bind(this)}
                                            ]}
                                            items={this.state.currentPredicates ? this.state.currentPredicates : []}
                                        />
                                    </Column>
                                </Row>
                            </State>

                        </StatePanel>

                    </Form>
                </Dialog>

            </Page>
        );
    }
});