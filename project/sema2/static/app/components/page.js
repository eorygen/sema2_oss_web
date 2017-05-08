var Page = React.createClass({

    render: function() {
        var classes = "pull-" + this.props.dir;

        return (
            <div>
            {this.props.children}
            </div>
        );
    }
});