var ProgramResponsesPage = React.createClass({

    mixins: [UrlBuilderMixin],

    getInitialState: function() {
        return {
            participants: [],
            responses: [],
            numPages:1,
            curPage:this.props.cur_page,
            sortBy:this.props.sort_by,
            isLoading: false,
            isExporting: false,
            exportDidSucceed: false,
            showResultMsg: false,
            filteredUserId: this.props.filtered_user_id
        }
    },

    componentDidMount: function() {
        this.refreshData();

        this.setState({
            isExporting: this.props.program.export_status,
            exportPercentage: this.props.program.export_percentage
        });

        if (this.props.program.export_status == 1) { // Magic numbers, In Progress
            this.startProgressRefresh();
        }
    },

    updateExportProgress: function() {

        var url = "programs/" + this.props.program.id + "/export_status/";

        var wasExporting = this.state.isExporting;

        this.reactGetRequest(url).then(function(res) {

            if (this.isMounted()) {

                var isExporting = res.export_status == 1;

                this.setState({
                    isExporting: isExporting,
                    exportPercentage: res.export_percentage,
                    exportDidSucceed: res.export_status == 0
                });

                if (wasExporting && !isExporting) {
                    this.cancelProgressRefresh();
                    this.setState({
                        showResultMsg: true
                    })
                }
            }

        }.bind(this));

    },

    startProgressRefresh: function() {
        if (!this.timer) {
            this.timer = setInterval(this.updateExportProgress, 16000); //Increase check time to 16 seconds from 2
        }
    },

    cancelProgressRefresh: function() {
        clearInterval(this.timer);
        this.timer = null;
    },

    onSelectFilteredUser: function(key, value) {
        this.setState({
            filteredUserId: value
        }, function() {
            this.refreshData();
        });
    },

    refreshData: function() {

        this.setState({
            isLoading:true

        }, function() {

            var url = "programs/" + this.props.program.id + "/responses/?p=" + this.state.curPage + '&u=' + this.state.filteredUserId + '&s=' + this.state.sortBy;
            var getResponses = this.reactGetRequest(url);

            var getParticipants = this.reactGetRequest(["programs", this.props.program.id, "participants"]);

            $.when(getResponses, getParticipants).then(function(res1, res2) {

                if (this.isMounted()) {

                    var responses = res1[0];
                    var participants = res2[0];

                    participants.splice(0, 0, {username: 'All Users', id: -1});

                    this.setState({
                        participants: participants,
                        responses:responses.items,
                        numPages:responses.num_pages,
                        curPage:responses.cur_page,
                        isLoading:false
                    });
                }

            }.bind(this));

        }.bind(this));
    },

    onPageClicked: function(index, event) {

        this.setState({
            curPage: index
        }, function() {
            window.location = '/programs/' + this.props.program.id + '/responses/?p=' + this.state.curPage + '&s=' + this.state.sortBy + '&u=' + this.state.filteredUserId;
        }.bind(this));
    },

    onItemClicked: function (row, event) {
        window.location = '/programs/' + this.props.program.id + '/responses/' + row.id + '/?p=' + this.state.curPage;
    },

    onExportDataClicked: function() {

        this.setState({
            showExportDlg:true
        });
    },

    onDoExportCancelled: function() {

        this.setState({
            showExportDlg:false
        });
    },

    onDoExportClicked: function() {

        this.setState({
            showExportDlg:false,
            isExporting: true,
            exportDidSucceed: false,
            showResultMsg: false
        }, function() {

            var data = this.refs.form.getValues();

            var url = "programs/" + this.props.program.id + "/export_data/";

            this.startProgressRefresh();

            this.reactPostRequest(url, null, data).then(function(res) {

                if (this.isMounted()) {

                }

            }.bind(this));

        }.bind(this));
    },

    onSortingChanged: function(key) {

        this.setState({
            'sortBy': key
        }, function() {
            window.location = '/programs/' + this.props.program.id + '/responses/?p=' + this.state.curPage + '&s=' + this.state.sortBy;
        });
    },

    renderPagination: function() {

        if (this.state.numPages < 2) {
            return null;
        }

        var pageBuffer = 5;
        var numPages = this.state.numPages;
        var curPage = this.state.curPage;

        var items = [];

        if ((curPage - pageBuffer) > 2) {

            items.push(<li><a onClick={this.onPageClicked.bind(this, 1)}>1</a></li>);
            items.push(<li><a>...</a></li>);

            var foo = curPage-pageBuffer;
            for (var i=foo; i < curPage; i++) {
                items.push(<li><a onClick={this.onPageClicked.bind(this, i)}>{i}</a></li>);
            }

            items.push(<li className="active"><a onClick={this.onPageClicked.bind(this, curPage)}>{curPage}</a></li>);
        }
        else {
            for (var i=1; i < curPage; i++) {
                items.push(<li><a onClick={this.onPageClicked.bind(this, i)}>{i}</a></li>);
            }

            items.push(<li className="active"><a onClick={this.onPageClicked.bind(this, curPage)}>{curPage}</a></li>);
        }

        if (numPages - (curPage + pageBuffer) > 2) {

            for (var i=curPage+1; i < curPage+pageBuffer+1; i++) {
                items.push(<li><a onClick={this.onPageClicked.bind(this, i)}>{i}</a></li>);
            }

            items.push(<li><a>...</a></li>);
            items.push(<li><a onClick={this.onPageClicked.bind(this, numPages)}>{numPages}</a></li>);
        }
        else {
            for (var i=curPage+1; i < numPages+1; i++) {
                items.push(<li><a onClick={this.onPageClicked.bind(this, i)}>{i}</a></li>);
            }
        }

        return <ul className="pagination pagination-minimal">{items}</ul>;
    },

    render: function() {

        var resultMsg = this.state.exportDidSucceed ? <div className="alert alert-success">Your export completed successfully. Please check your email for download information.</div> : <div className="alert alert-warning">An error occurred while exporting your data. Please try again.</div>;
        var resultSection = this.state.showResultMsg ? resultMsg : null;

        var pagination = this.renderPagination();

        var progressStyle = {width: this.state.exportPercentage + '%'};
        var progress = this.state.isExporting ? (
            <div>
                <h5>Exporting data {this.state.exportPercentage}%...</h5>
                <p>You can safely navigate away from this page or close your browser. Your data will be emailed to your SEMA admin email address.</p>
                <div className="progress progress-striped active"><div className="progress-bar" role="progressbar" style={progressStyle}></div></div>
            </div>): null;

        return (
            <Page>

                <Column count="12">

                    <ProgramTabs
                        program={this.props.program}
                        selectedId="responses"/>

                    <ProgramHeader
                        program={this.props.program}
                        name="Responses">
                        <Button type="primary" small={true} onClick={this.onExportDataClicked} label="Export Data" disabled={this.state.isExporting}/>&nbsp;
                    </ProgramHeader>

                    {progress}
                    {resultSection}

                    <FormDropdown
                        name="filtered_user"
                        items={this.state.participants}
                        valueField="id"
                        labelField="username"
                        emptyLabel="Select User"
                        value={this.state.filteredUserId}
                        onValueChanged={this.onSelectFilteredUser}
                    />
                    <br/>

                    {pagination}

                    <DataTable
                        onSortingChanged={this.onSortingChanged}
                        ref='table'
                        isLoading={this.state.isLoading}
                        columns={[
                            {name: 'Participant ID', key: 'username'},
                            {name: 'Program Version', key: 'version'},
                            {name: 'Survey', key: 'survey_name'},
                            {name: 'Iteration', key: 'iteration'},
                            {name: 'Shown', key: 'delivery_timestamp', transform: function(value) { return moment(value).format('DD/MM/YY h:mm:ss a'); }},
                            {name: 'Completed', key: 'completed_timestamp', transform: function(value) {
                                var ts = moment(value);
                                if (ts.year() == 1970) {
                                    return "";
                                }
                                else {
                                    return ts.format('DD/MM/YY h:mm:ss a');
                                }
                            }},
                            {name: 'Uploaded', key: 'uploaded_timestamp', transform: function(value) { return moment(value).format('DD/MM/YY h:mm:ss a'); }}
                        ]}
                        items={this.state.responses}
                        onRowClicked={this.onItemClicked}
                    />

                    {pagination}
                </Column>

                <Dialog
                    show={this.state.showExportDlg}
                    title="Export Program Data"
                    onSaveClicked={this.onDoExportClicked}
                    onCancelClicked={this.onDoExportCancelled}
                    focusedField="email_address"
                    saveButtonLabel="Start Data Export"
                >
                    <h5>Please note</h5>
                    <p>The export process runs in the background on the server and may take some time depending on the volume of stored data.</p>
                    <p>Once it is started you can safely close your browser or navigate to a different page and the export process will continue running.</p>
                    <p>After completion your data will be emailed to your SEMA admin email address.</p>
                    <Form ref="form">
                    </Form>
                </Dialog>

            </Page>
        );
    }
});
