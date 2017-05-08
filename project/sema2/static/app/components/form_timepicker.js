var FormTimePicker = React.createClass({

    getDefaultProps: function() {
        return {
            isRequired: false
        }
    },

    getInitialState: function() {
        return {
            isValid: true
        }
    },

    componentDidMount: function() {
        var elem = $(React.findDOMNode(this.refs.field));
        elem.timepicker({timeFormat: 'g:i a', step:10});
        elem.on('changeTime', function() {
            this._setValue(elem.val());
            elem.blur();
        }.bind(this));
    },

    _setValue: function(val) {

        if (this.props.onValueChanged) {
            this.props.onValueChanged(this.props.name, val);
        }

        if (this.props.onNotifyValueChanged) {
            this.props.onNotifyValueChanged(this.props.name, val);
        }

        var isValid = false;

        if (this.props.isRequired && val.length != 0) {
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

    _onChange:function(event) {

        var val = event.target.value;
        this.setValue(val);
    },

    render: function() {

        var value = this.props.getValue ? this.props.getValue(this.props.name) : this.props.value;
        var valueVal = this.props.disabled ? "Default" : value;

        var placeholder = this.state.isValid ? this.props.placeholder : "This field is required";

        var field = <input ref="field" name={this.props.name} id={this.props.name} onChange={this._onChange} required={this.props.isRequired} type="text" className="form-control" value={valueVal} placeholder={placeholder} disabled={this.props.disabled}></input>;
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
        var value = this.props.getValue ? this.props.getValue(this.props.name) : this.props.value;
        return <input name={this.props.name} id={this.props.name} type="hidden" value={value}></input>
    }
});