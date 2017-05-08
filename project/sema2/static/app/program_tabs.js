var ProgramTabs = React.createClass({

    mixins: [UrlBuilderMixin],

    propTypes: {
        selectedId: React.PropTypes.string
    },

    getInitialState: function() {
        return {
            unlocking: false
        }
    },

    buildProgramTabUrl:function(tab) {
        return "/programs/" + this.props.program.id + "/" + tab + "/";
    },

    createNewDraftVersionClicked:function() {
        this.setState({unlocking: true}, function() {

            this.reactPostRequest(["programs", this.props.program.id, "create_new_version"]).then(function(res) {

                window.location.reload();

            }.bind(this)).fail(function() {
                alert("Unable to create new program version.");
                location.reload();
            })

        });
    },

    publishCurrentDraftVersionClicked:function() {

        this.setState({unlocking: true}, function() {

            this.reactPostRequest(["programs", this.props.program.id, "publish_latest_draft"]).then(function (res) {
                window.location.reload();
            }.bind(this)).fail(function () {
                alert("An error occurred while attempting to publish this draft.");
                location.reload();
            })

        });
    },

    getInitialState:function() {

        return {
            items:[
                {id:"dashboard", url:this.buildProgramTabUrl("dashboard"), name:"Dashboard"},
                {id:"participants", url:this.buildProgramTabUrl("participants"), name:"Participants"},
                {id:"questions", url:this.buildProgramTabUrl("questions"), name:"Questions"},
                {id:"surveys", url:this.buildProgramTabUrl("surveys"), name:"Surveys"},
                {id:"schedules", url:this.buildProgramTabUrl("schedules"), name:"Schedules"},
                {id:"admins", url:this.buildProgramTabUrl("admins"), name:"Admins"},
                {id:"activity", url:this.buildProgramTabUrl("activity"), name:"Activity"},
                {id:"responses", url:this.buildProgramTabUrl("responses"), name:"Responses"}
            ]
        };
    },

    componentDidMount:function() {

    },

    render:function() {

        var editButton = this.props.program.is_locked ? <li className="pull-right"><Button type="primary" small={true} onClick={this.createNewDraftVersionClicked}><i className="ss-write"></i>&nbsp;&nbsp;Unlock &amp; Edit</Button></li> : <li className="pull-right"><Button type="danger" small={true} onClick={this.publishCurrentDraftVersionClicked}><i className="ss-uploadcloud"></i>&nbsp;&nbsp;Publish Changes</Button></li>;
        var infoBox = this.props.program.is_locked ? <div className="alert alert-primary"><strong>LOCKED</strong> Unlock the program to create a new version and enable editing.</div> : <div className="alert alert-danger"><strong>DRAFT</strong> This version must be published for participants to receive any changes.</div>;
        var progress = this.state.unlocking ? <div className="progress progress-striped active"><div className="progress-bar" role="progressbar" style={{width: "100%"}}></div></div> : null;

        return (
            <div className="clearfix">

                {infoBox}
                {progress}

                <ul id="main-tab-bar" className="nav nav-tabs">
                {this.state.items.map(function(item) {

                    var classes = "";
                    if (item.id == this.props.selectedId) {
                        classes = "active";
                    }
                    else if (item.disabled) {
                        classes = "disabled";
                        item.url = "#";
                    }

                    var item = <li key={item.id} id={item.id} className={classes}><a href={item.url}>{item.name}</a></li>;
                    return item;
                }, this)}
                {editButton}
                </ul>
            </div>
        );
    }
});