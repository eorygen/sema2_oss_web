var ProgramAdminsPage = React.createClass({

    mixins: [UrlBuilderMixin],

    getInitialState: function() {
        return {
            items: []
        };
    },

    componentDidMount: function() {
        this.refreshData();
    },

    onRowClicked: function(rowData) {

    },

    onInviteTeamMember:function() {
        this.refs.inviteForm.setValues(Invite(this.props.program.id, 1));

        this.setState({
            showInviteForm:true
        })
    },

    onSaveClicked: function() {

        this.sendInvite()
            .then(function(res) {

                this.setState({showInviteForm:false}, function() {
                    alert("Your team member invitation was sent successfully");
                    this.refreshData();
                });

            }.bind(this))
            .fail(function(res) {
                alert("Unable to send invite. Please check all fields are filled.")
            });

    },

    onCancelClicked: function() {
        this.setState({showInviteForm:false});
    },

    sendInvite: function() {
        var data = this.refs.inviteForm.getValues();
        return this.reactPostRequest(["invitations"], null, data);
    },

    refreshData: function() {

        var req = this.buildRequest(["programs", this.props.program.id, "admins"]);

        $.get(req.url, function (result) {

            if (this.isMounted()) {

                this.setState({
                    items: result
                });
            }
        }.bind(this));

    },

    render: function() {

        return (
            <Column count="12">

                <ProgramTabs
                    program={this.props.program}
                    selectedId="admins"/>

                <ProgramHeader
                    program={this.props.program}
                    name="Team Members">
                    <button className="btn btn-default btn-sm btn-primary" onClick={this.onInviteTeamMember}>Invite New Team Member</button>&nbsp;
                </ProgramHeader>

                <DataTable
                    columns={[
                        {name: 'Username', key: 'username'},
                        {name: 'Email', key: 'email'},
                    ]}
                    items={this.state.items}
                    onRowClicked={this.onRowClicked}
                />

                <Dialog
                    show={this.state.showInviteForm}
                    title="Invite Team Member"
                    onSaveClicked={this.onSaveClicked}
                    onCancelClicked={this.onCancelClicked}
                    focused="first_name"
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
                        </Row>
                    </Form>
                </Dialog>

            </Column>
        );
    }
});