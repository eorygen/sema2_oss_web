var Panel = React.createClass({

    componentDidMount: function() {

    },

    render: function() {

        var titleSection = (this.props.title != undefined) ? <div className="panel-heading">{this.props.title}</div> : null;

        return (
            <div className="panel panel-default" draggable="true">
                {titleSection}
                <div className="panel-body">
                {this.props.children}
                </div>
            </div>
        );
    }
});
