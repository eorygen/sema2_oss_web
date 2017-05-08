var LeftItems = React.createClass({

    render: function() {
        return (
            <div className="pull-left">
            {this.props.children}
            </div>
        );
    }
});

var RightItems = React.createClass({

    render: function() {
        return (
            <div className="pull-right">
            {this.props.children}
            </div>
        );
    }
});

var ItemBar = React.createClass({

    render: function() {
        return (
            <div className="clearfix">
            {this.props.children}
            </div>
        );
    }
});