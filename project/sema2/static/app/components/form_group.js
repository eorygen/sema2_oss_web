var FormGroup = React.createClass({

    render: function() {

        var classes = "form-group";

        if (!this.props.isValid) {
            classes += " has-error";
        }
        else if (this.props.isRequired) {
            classes += " has-warning";
        }

        return (
            <div className={classes}>
                <label htmlFor={this.props.forField} className="control-label">{this.props.label}</label>
                {this.props.children}
            </div>
        );
    }
});
