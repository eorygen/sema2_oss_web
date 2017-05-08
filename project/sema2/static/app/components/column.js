var Column = React.createClass({

    getDefaultProps: function() {
        return {
            count:1
        }
    },

    render: function() {
        var classes = "col-md-" + this.props.count;

        if (this.props.vcenter == true) {
            classes += " vertical-center"
        }

        return (
            <div className={classes}>
            {this.props.children}
            </div>
        );
    }
});