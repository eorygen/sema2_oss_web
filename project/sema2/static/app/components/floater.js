var Floater = React.createClass({

    getDefaultProps: function() {
        return {
            dir: 'left'
        }
    },

    render: function() {
        var classes = "pull-" + this.props.dir;

        return (
            <div className={classes}>
            {this.props.children}
            </div>
        );
    }
});