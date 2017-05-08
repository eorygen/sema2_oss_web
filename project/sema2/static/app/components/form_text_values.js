var FormTextValue = React.createClass({

    mixins: [ModelUtilsMixin],

    componentDidMount: function() {

    },

    render: function() {

        return (
            <div className="well">{this.props.value}</div>
        );
    }
});

var FormNumberValue = React.createClass({

    mixins: [ModelUtilsMixin],

    componentDidMount: function() {
    },

    render: function() {

        return (
            <div className="well">{this.props.value.toString()}</div>
        );
    }
});

var FormBooleanValue = React.createClass({

    mixins: [ModelUtilsMixin],

    getDefaultProps: function() {
        return {
            default: "false",
            trueValue: "Yes",
            falseValue: "No"
        }
    },

    componentDidMount: function() {
    },

    render: function() {

        return (
            <div className="well">{this.props.value ? this.props.trueValue : this.props.falseValue}</div>
        );
    }
});

var FormOptionValue = React.createClass({

    mixins: [ModelUtilsMixin],

    getDefaultProps: function() {
        return {
            default: ""
        }
    },

    componentDidMount: function() {
    },

    render: function() {

        var value = this.props.options ? this.props.options[this.props.value] : this.props.default;
        return (
            <div className="well">{value}</div>
        );
    }
});
