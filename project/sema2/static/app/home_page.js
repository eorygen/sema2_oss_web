var HomePage = React.createClass({

    mixins: [UrlBuilderMixin, ModelUtilsMixin],

    getInitialState: function() {
        return {
            items: []
        };
    },

    componentDidMount: function() {

    },

    render: function() {

        var welcome = this.props.showWelcome ? <div className="alert alert-primary">Welcome aboard! To start using the apps simply click the link below for your phone platform.</div> : <span/>;

        return (
            <Page>
                <Column count="12">
                    <Breadcrumb items={[
                        {name:"Home"}
                    ]}/>

                    <ProgramHeader name="Home">
                    </ProgramHeader>

                    <div className="clearfix">
                        <ul id="main-tab-bar" className="nav nav-tabs">
                            <li className="active"><a href="#">Apps</a></li>
                        </ul>
                    </div>

                {welcome}
                    <h5>Download the SEMA app for your mobile device</h5>

                    <div className="list-group">

                        <a href="https://itunes.apple.com/au/app/sema/id1068685403?mt=8" className="list-group-item">
                            <div className="pull-left"><i className="ss-download"></i></div>
                            <div className="media-body">
                                <h4 className="list-group-item-heading">SEMA for iOS</h4>
                                <p className="list-group-item-text">Download SEMA for iOS</p>
                            </div>
                        </a>

                        <a href="http://play.google.com/store/apps/details?id=com.orygenapps.sema" className="list-group-item">
                            <div className="pull-left"><i className="ss-download"></i></div>
                            <div className="media-body">
                                <h4 className="list-group-item-heading">SEMA for Android</h4>
                                <p className="list-group-item-text">Download SEMA for Android</p>
                            </div>
                        </a>
                    </div>
                </Column>
            </Page>
        );
    }
});