var ProgramActivityPage = React.createClass({

    mixins: [UrlBuilderMixin],

    getInitialState: function() {
        return {
            isLoading: false,
            isExporting: false,
            filter: null
        }
    },

    componentDidMount: function() {
        this.refreshData();
    },

    refreshData: function() {

        var filter = this.state.filter ? this.state.filter : "";

        this.setState({
            isLoading:true

        }, function() {

            var url = "programs/" + this.props.program.id + "/activity/?filter=" + filter;
            var getActivity = this.reactGetRequest(url);

            $.when(getActivity).then(function(res1) {

                if (this.isMounted()) {

                    var activity = res1;

                    this.setState({
                        activity: activity,
                        isLoading:false
                    });
                }

            }.bind(this));

        }.bind(this));
    },

    onFilterAll() {
        this.setState({filter: null}, function() {
            this.refreshData();
        }.bind(this));
    },

    onFilterAdminOnly() {
        this.setState({filter: "admin"}, function() {
            this.refreshData();
        }.bind(this));
    },

    onFilterUserOnly() {
        this.setState({filter: "user"}, function() {
            this.refreshData();
        }.bind(this));
    },

    render: function() {

        return (
            <Page>

                <Column count="12">

                    <ProgramTabs
                        program={this.props.program}
                        selectedId="activity"/>

                    <ProgramHeader
                        program={this.props.program}
                        name="Activity">
                    </ProgramHeader>

                    <br/>

                    <a href="#all" onClick={this.onFilterAll}>All Events</a>
                    &nbsp; / &nbsp;
                    <a href="#admin" onClick={this.onFilterAdminOnly}>Admin Events</a>
                    &nbsp; / &nbsp;
                    <a href="#user" onClick={this.onFilterUserOnly}>User Events</a>

                    <br/>

                    <DataTable
                        ref='table'
                        isLoading={this.state.isLoading}
                        columns={[
                            {name: 'Timestamp', key: 'timestamp', transform: function(value) { return moment(value).format('DD/MM/YY h:mm:ss a'); }},
                            {name: 'Participant ID', key: 'username'},
                            {name: 'Description', key: 'description'}
                        ]}
                        items={this.state.activity}
                    />
                </Column>

            </Page>
        );
    }
});