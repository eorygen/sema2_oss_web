var ProgramSchedulesPage = React.createClass({

    mixins: [UrlBuilderMixin, ModelUtilsMixin],

    getInitialState: function() {
        return {
            items: [],
            selectedIndex: 0,
            isEditing: false
        };
    },

    componentDidMount: function() {
        this.refreshData();
    },

    refreshData: function() {

        var req = this.buildRequest(["programs", this.props.program.id, "schedules"]);

        $.get(req.url, function (result) {

            if (this.isMounted()) {

                var selectedIndex = result.length > 0 ? 0 : -1;

                var moddedItems = result.map(function(item) {
                    return this.setStartEndTime(item);
                }.bind(this));

                this.setState({
                    selectedIndex:selectedIndex,
                    items: moddedItems
                });
            }
        }.bind(this));

    },

    onAddItemClicked:function() {

        var schedule = Schedule(this.props.program_version.id);
        schedule = this.setStartEndTime(schedule);

        this.refs.form.setValues(schedule);

        this.setState({
            isEditing:true
        });
    },

    onCancelClicked:function() {
        this.setState({isEditing:false});
    },

    onSaveClicked:function() {
        var data = this.refs.form.getValues();

        var startTime = moment(data.start_sending_at_full, "H:mm A");
        data.start_time_hours = startTime.hour();
        data.start_time_minutes = startTime.minute();

        var endTime = moment(data.stop_sending_at_full, "H:mm A");
        data.stop_time_hours = endTime.hour();
        data.stop_time_minutes = endTime.minute();

        var startMins = data.start_time_hours * 60 + data.start_time_minutes;
        var stopMins = data.stop_time_hours * 60 + data.stop_time_minutes;

        if (stopMins <= startMins) {
            alert("Invalid Schedule: Stop time '" + data.stop_sending_at_full + "' must be later than start time '" + data.start_sending_at_full + "'");
        }
        else {
            this.saveSchedule(data);
        }
    },

    setStartEndTime: function(rowData) {

        var startTime = moment({hour: rowData.start_time_hours, minute: rowData.start_time_minutes});
        var stopTime = moment({hour: rowData.stop_time_hours, minute: rowData.stop_time_minutes});

        rowData.start_sending_at_full = startTime.format("H:mm A");
        rowData.stop_sending_at_full = stopTime.format("H:mm A");

        return rowData;
    },

    editSchedule: function(rowData) {

        var schedule = this.setStartEndTime(rowData);
        this.refs.form.setValues(schedule);

        this.setState({
            isEditing:true
        });
    },

    onItemClicked: function(itemData, index) {

        this.setState({
            selectedIndex:index
        });
    },

    deleteSelectedSchedules: function() {
        var items = this.refs.schedulesTable.getSelectedItems();
        items.map(function(item) {
            this.deleteSchedule(item);
        }, this);
    },

    deleteSchedule: function(item) {

        var req = this.buildRequest(["schedules", item.id]);

        $.ajax({

            method: 'DELETE',
            url:req.url,
            contentType: 'application/json',
            dataType: 'json'

        }).done(function(res) {

            this.refreshData();

        }.bind(this)).fail(function() {

        });
    },

    saveSchedule: function(data) {

        var req = this.buildRequest(["schedules"], data.id);

        $.ajax({

            method: req.method,
            url:req.url,
            data: JSON.stringify(data),
            contentType: 'application/json',
            dataType: 'json'

        }).done(function(res) {

            this.setState({
                isEditing:false
            }, function() {

                this.refreshData();
            });

        }.bind(this)).fail(function() {
            alert("Error saving schedule information");
        });
    },

    render: function() {

        return (
        <Page>
            <Column count="12">

                <ProgramTabs
                    program={this.props.program}
                    selectedId="schedules"/>

                <ProgramHeader
                    program={this.props.program}
                    name='Schedules'>
                    <button disabled={this.props.program.is_locked} className="btn btn-default btn-sm btn-primary" onClick={this.onAddItemClicked}>Add New Schedule</button>&nbsp;
                </ProgramHeader>
            </Column>
            <Column count="12">
                <DataTable
                    ref="schedulesTable"
                    disabled={this.props.program.is_locked}
                    columns={[
                        {name: 'Name', key: 'display_name'},
                        {name: 'Start Time', key: 'start_sending_at_full'},
                        {name: 'End Time', key: 'stop_sending_at_full'},
                        {name: 'Interval (mins)', key: 'interval_minutes'},
                        {name: 'Expiry (mins)', key: 'expiry_minutes'},
                        {name: '± Random (mins)', key: 'offset_plus_minus_minutes'},
                        {name: 'Active', value: function(rowData) {
                            var str = "";
                            str += rowData['allow_monday'] ? "M" : "m";
                            str += rowData['allow_tuesday'] ? "T" : "t";
                            str += rowData['allow_wednesday'] ? "W" : "w";
                            str += rowData['allow_thursday'] ? "T" : "t";
                            str += rowData['allow_friday'] ? "F" : "f";
                            str += rowData['allow_saturday'] ? "S" : "s";
                            str += rowData['allow_sunday'] ? "S" : "s";
                            return str;
                        }}
                    ]}
                    items={this.state.items}
                    onRowClicked={this.editSchedule}
                    rowActionItems={[
                        {name: 'Delete', action:this.deleteSchedule}
                    ]}

                    tableActionItems={[
                        {name: 'Delete Selected', action:this.deleteSelectedSchedules}
                    ]}
                />
            </Column>
            <Dialog
                show={this.state.isEditing}
                title="Edit Schedule"
                item={this.schedule}
                onSaveClicked={this.onSaveClicked}
                onCancelClicked={this.onCancelClicked}
            >
                <Form ref="form">
                    <Row>
                        <Column count="6">
                            <FormInputField label="Name" name="display_name"/>
                        </Column>
                        <Column count="6">
                            <FormInputField label="Interval (Mins)" filter="numbers" name="interval_minutes"/>
                        </Column>
                        <Column count="6">
                            <FormTimePicker label="Start Sending At" name="start_sending_at_full"/>
                        </Column>
                        <Column count="6">
                            <FormTimePicker label="Stop Sending At" name="stop_sending_at_full"/>
                        </Column>
                        <Column count="6">
                            <FormInputField label="± Random (Mins)" name="offset_plus_minus_minutes" filter="numbers"/>
                        </Column>
                        <Column count="6">
                            <FormInputField label="Expiry (Mins)" name="expiry_minutes" filter="numbers"/>
                        </Column>
                    </Row>
                    <Row>
                        <Column count="4">
                            <FormGroup label="Active Days">
                                <br/>
                                <FormCheckbox noGroup={true} name="allow_monday" label="Monday"/><br/>
                                <FormCheckbox noGroup={true} name="allow_tuesday" label="Tuesday"/><br/>
                                <FormCheckbox noGroup={true} name="allow_wednesday" label="Wednesday"/><br/>
                            </FormGroup>
                        </Column>
                        <Column count="4">
                            <FormGroup label="Active Days">
                                <FormCheckbox noGroup={true} name="allow_thursday" label="Thursday"/><br/>
                                <FormCheckbox noGroup={true} name="allow_friday" label="Friday"/><br/>
                            </FormGroup>
                        </Column>
                        <Column count="4">
                            <FormGroup label="Active Days">
                                <br/>
                                <FormCheckbox noGroup={true} name="allow_saturday" label="Saturday"/><br/>
                                <FormCheckbox noGroup={true} name="allow_sunday" label="Sunday"/><br/>
                            </FormGroup>
                        </Column>
                    </Row>
                </Form>
            </Dialog>
        </Page>
        );
    }
});