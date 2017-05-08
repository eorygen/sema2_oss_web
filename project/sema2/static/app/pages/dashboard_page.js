var ProgramDashboardPage = React.createClass({

    mixins: [UrlBuilderMixin, ModelUtilsMixin],

    getInitialState: function() {
        return {
            showDialog: false
        };
    },

    componentDidMount: function() {
        this.refreshResponseGraph();
    },

    refreshResponseGraph: function() {

    },

    editClicked: function() {

        this.refs.form.setValues(this.props.program);

        this.setState({
            showDialog: true
        });
    },

    onSaveClicked: function() {

        var data = this.refs.form.getValues();
        this.reactAddOrUpdateRequest(["programs"], data.id, data).then(function(res) {

            this.setState({
                showDialog: false
            }, function() {
                this.refreshData();
            }.bind(this));

        }.bind(this)).fail(function(err) {
            alert("Error saving program");
        });
    },

    onCancelClicked: function() {
        this.setState({
            showDialog: false
        });
    },

    render: function() {

        return (
            <Page>
                <Column count="12">

                    <ProgramTabs
                        program={this.props.program}
                        selectedId="dashboard"/>

                    <ProgramHeader
                        program={this.props.program}
                        name='Dashboard'>
                        <button className="btn btn-default btn-sm btn-primary" onClick={this.editClicked}>Edit</button>&nbsp;
                    </ProgramHeader>
                </Column>
                <Row>
                    <Column count="6">
                        <Panel title="Lowest Compliance">

                            <DataTable
                                ref='compliance_table'
                                columns={[
                                    {name: "Compliance", value: function(row) {
                                        return <Circle radius={20} width={2} id={row.email} value={Math.round(row.compliance)}/>
                                    }},
                                    {name: 'Email',  key: "email"}
                                ]}
                                items={this.props.program.top_compliance_list}
                            />

                        </Panel>
                    </Column>
                    <Column count="6">
                        <Panel title="Longest Sync Interval">

                            <DataTable
                                ref='sync_table'
                                columns={[
                                    {name: 'Interval',  key: "interval", transform: function(value) { return value ? moment(value).fromNow() : "N/A"; }},
                                    {name: 'Email',  key: "email"}
                                ]}
                                items={this.props.program.top_sync_interval_list}
                            />

                        </Panel>

                        <Panel title="Experimental Features">
                            Conditional Question Sets [{this.props.program.feature_enable_conditional_question_sets ? "Enabled" : "Disabled"}]
                        </Panel>
                    </Column>
                </Row>
                <Row>
                    <Column count="3">
                        <div className="panel panel-default">
                            <div className="panel-heading">Contact Info</div>
                            <ul className="list-group">
                                <li className="list-group-item">Program<br/>{this.getProperty(this.props.program, "display_name", "")}</li>
                                <li className="list-group-item">Contact<br/>{this.getProperty(this.props.program, "contact_name", "")}</li>
                                <li className="list-group-item">Phone<br/>{this.getProperty(this.props.program, "contact_phone_number", "")}</li>
                                <li className="list-group-item">Email<br/>{this.getProperty(this.props.program, "contact_email", "")}</li>
                            </ul>
                        </div>
                    </Column>
                </Row>

                <Dialog
                    show={this.state.showDialog}
                    title="Edit Program"
                    onSaveClicked={this.onSaveClicked}
                    onCancelClicked={this.onCancelClicked}
                    focused="display_name"
                >
                    <Form ref="form">
                        <Row>
                            <Column count="12">
                                <FormInputField label="Name" name="display_name"/>
                            </Column>
                            <Column count="12">
                                <FormInputField label="Description" name="description"/>
                            </Column>
                            <Column count="6">
                                <FormInputField label="Contact Name" name="contact_name"/>
                            </Column>
                            <Column count="6">
                                <FormInputField label="Phone Number" name="contact_phone_number"/>
                            </Column>
                            <Column count="6">
                                <FormInputField label="Email Address" name="contact_email"/>
                            </Column>
                            <Column count="6">

                            </Column>
                            <Column count="12">
                                <FormCheckbox noGroup={true} label="[EXPERIMENTAL] Enable Conditional Question Sets" name="feature_enable_conditional_question_sets"/>
                            </Column>
                        </Row>
                    </Form>
                </Dialog>

            </Page>);
    }
});