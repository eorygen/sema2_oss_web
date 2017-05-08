var Button = React.createClass({

    getDefaultProps: function() {
        return {
            type: "default"
        }
    },

    _onClick: function(event) {

        event.preventDefault();
        event.stopPropagation();

        if (this.props.onClick) {
            this.props.onClick(event)
        }
    },

    render: function() {
        var classes = "btn btn-";
        classes += this.props.type ? this.props.type : "";
        classes += this.props.small ? " btn-sm" : "";

        var content = this.props.children ? this.props.children : this.props.label;

        return (
            <button className={classes} onClick={this._onClick} disabled={this.props.disabled}>{content}</button>
        );
    }
});