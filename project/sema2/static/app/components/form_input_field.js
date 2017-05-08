var FormInputField = React.createClass({

    mixins: [ModelUtilsMixin],

    getInitialState: function() {
        return {
            isValid: true
        }
    },

    componentDidMount: function() {
    },

    _onChange:function(event) {

        var val = event.target.value;

        if (this.props.filter == 'numbers') {
            val = val.replace(/[^0-9]/g,'');
        }

        if (this.props.type == 'number') {
            val = parseInt(val);
            if (isNaN(val)) {
                val = 0;
            }
        }

        if (this.props.onValueChanged) {
            this.props.onValueChanged(this.props.name, val);
        }

        if (this.props.onNotifyValueChanged) {
            this.props.onNotifyValueChanged(this.props.name, val);
        }

        var isValid = false;

        if (this.props.required && val && val.length != 0) {
            isValid = true;
        }
        else {
            isValid = false;
        }

        if (isValid != this.state.isValid) {
            if (this.props.onValidStateChanged) {
                this.props.onValidStateChanged(isValid);
            }

            if (this.props.onNotifyValidStateChanged) {
                this.props.onNotifyValidStateChanged(isValid);
            }
        }

        this.setState({
            isValid: isValid
        });
    },

    render: function() {

        var value = this.props.getValue ? this.props.getValue(this.props.name) : this.props.value;
        var placeholder = this.state.isValid ? this.props.placeholder : "This field is required";

        var field = <input name={this.props.name} id={this.props.name} onChange={this._onChange} disabled={this.props.disabled} required={this.props.isRequired} type="text" className="form-control" value={value} placeholder={placeholder}></input>;
        var res = null;

        if (!this.props.noGroup) {
            res = <FormGroup label={this.props.label} forField={this.props.name} isRequired={this.props.isRequired}>{field}</FormGroup>
        }
        else {
            res = field;
        }

        return res;
    }
});

var FormHiddenField = React.createClass({

    render: function() {
        return <input name={this.props.name} id={this.props.name} type="hidden" value={this.props.value}></input>
    }
});