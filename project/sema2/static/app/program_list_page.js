var ProgramListPage = React.createClass({

    mixins: [UrlBuilderMixin, ModelUtilsMixin, ],

    getInitialState: function() {
        return {
            items: [],
            showArchived: false
        };
    },

    componentDidMount: function() {
        this.refreshData();
    },

    refreshData: function() {

        var groupsReq = this.buildRequest(["programs"]);
        var url = groupsReq.url;

        $.get(url, function (result) {

            if (this.isMounted()) {

                this.setState({
                    items: result
                });
            }
        }.bind(this));

        var archivedUrl = groupsReq.url + '?archived_only=1';

        $.get(archivedUrl, function (result) {

            if (this.isMounted()) {

                this.setState({
                    archivedItems: result
                });
            }
        }.bind(this));

    },

    disableProgram: function(event) {
        event.stopPropagation();
        alert("dfdf");
    },

    onAddProgramClicked: function () {

        this.refs.form.setValues(ProgramModel());

        this.setState({
            showDialog: true
        });
    },

    onRowClicked: function(rowData) {
        window.location = "/programs/" + rowData.id + "/";
    },

    onEditProgramClicked: function(rowData) {

        this.refs.form.setValues(rowData);

        this.setState({
            showDialog: true
        });
    },

    onCloneProgramClicked: function(rowData) {

        var programId = rowData.id;

        this.refs.confirmDlg.showWithMessage("Clone Program?" , "Are you sure you want to clone this program?", "Cancel", "Clone", function() {

            this.reactPostRequest(["programs", programId, "clone"], null, null).then(function (res) {

                window.location.reload();

            }.bind(this)).fail(function (err) {
                alert("Error cloning program");
            });

        }.bind(this));
    },

    onArchiveProgramClicked: function(rowData) {

        var programId = rowData.id;

        this.refs.confirmDlg.showWithMessage("Archive Program?" , "Are you sure you want to archive this program?", "Cancel", "Archive", function() {

            this.reactPostRequest(["programs", programId, "archive"], null, null).then(function (res) {

                window.location.reload();

            }.bind(this)).fail(function (err) {
                alert("Error archiving program");
            });

        }.bind(this));
    },

    onRestoreProgramClicked: function(rowData) {

        var programId = rowData.id;

        this.refs.confirmDlg.showWithMessage("Restore Archived Program?" , "Are you sure you want to restore this program?", "Cancel", "Restore", function() {

            this.reactPostRequest(["programs", programId, "unarchive"], null, null).then(function (res) {

                window.location.reload();

            }.bind(this)).fail(function (err) {
                alert("Error restoring program");
            });

        }.bind(this));
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

    onShowArchivedChanged: function(name, val) {
        this.setState({
            showArchived: val
        }, function() {
            this.refreshData();
        });
    },

    render: function() {

        return (
            <Page>
                <Column count="12">
                    <Breadcrumb items={[
                        {name:"Home"}
                    ]}/>

                    <ProgramHeader name="Programs">
                        <Button label="Add Program" small={true} onClick={this.onAddProgramClicked}/>
                    </ProgramHeader>

                    <DataTable
                        columns={[
                            {name: 'Name', key: 'display_name'},
                            {name: 'Program Revision', key: 'revision_number', transform: function(value) { return "v"+value }},
                            {name: 'Description', key: 'description'},
                            {name: 'Editing State', key: 'is_locked', transform: function(value) { return value ? 'Published' : 'Draft'}}
                        ]}
                        dataUrl="/api/1/programs/"
                        onRowClicked={this.onRowClicked}
                        items={this.state.items}
                        rowActionItems={[
                            {action:this.onEditProgramClicked, name:'Edit'},
                            {action:this.onCloneProgramClicked, name:'Clone'},
                            {action:this.onArchiveProgramClicked, name:'Archive'}
                        ]}
                    />

                    <FormCheckbox name="show_archived" label="Show archived Programs" noGroup={true} value={this.state.showArchived} onValueChanged={this.onShowArchivedChanged}/>

                    {this.state.showArchived ? (
                        <Row>
                            <Column count="12">
                                <hr/>
                                <h4>Archived Programs</h4>

                                <DataTable
                                    columns={[
                                        {name: 'Name', key: 'display_name'},
                                        {name: 'Program Revision', key: 'revision_number', transform: function(value) { return "v"+value }},
                                        {name: 'Description', key: 'description'}
                                    ]}
                                    items={this.state.archivedItems}
                                    rowActionItems={[
                                        {action:this.onRestoreProgramClicked, name:'Restore'}
                                    ]}
                                />
                            </Column>
                        </Row>
                    ): null}

                </Column>

                <ConfirmDialog
                    ref="confirmDlg"
                />

                <Dialog
                    show={this.state.showDialog}
                    title="Add Program"
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
                        </Row>
                    </Form>
                </Dialog>

            </Page>
        );
    }
});