var FormCheckbox = React.createClass({

    mixins: [ModelUtilsMixin],

    getInitialState: function() {
        return {
            isValid: true
        }
    },

    componentWillReceiveProps: function(nextProps) {
        this.setInitialValue(nextProps);
    },

    componentDidMount: function() {
        this.setInitialValue(this.props);
    },

    _onChange: function(event) {

        var val = event.target.checked;

        if (this.props.onValueChanged != undefined) {
            this.props.onValueChanged(this.props.name, val);
        }

        if (this.props.onNotifyValueChanged) {
            this.props.onNotifyValueChanged(this.props.name, val);
        }

    },

    render: function() {

        var value = this.props.getValue ? this.props.getValue(this.props.name) : this.props.value;
        var isChecked = (value == true);

        var classes = "checkbox";

        if (isChecked) {
            classes += " checked";
        }

        var field = <label htmlFor={this.props.name}><input disabled={this.props.disabled} name={this.props.name} id={this.props.name} type="checkbox" checked={isChecked} onChange={this._onChange}/>&nbsp;&nbsp;{this.props.label}</label>;
        var res = null;

        var groupLabel = this.props.groupLabel ? this.props.groupLabel : this.props.label;

        if (!this.props.noGroup) {
            res = <FormGroup label={groupLabel} forField={this.props.name} isRequired={this.props.isRequired}><br/>{field}</FormGroup>
        }
        else {
            res = field;
        }

        return res;
    }
});
