/** @jsx React.DOM */

var Form = React.createClass({

    mixins: [ModelUtilsMixin],

    getInitialState: function() {
        return {
            values: {}
        }
    },

    componentDidMount: function() {

        if (this.props.focused) {
            console.log(this.props.focused);

            var elem = $(React.findDOMNode(this));
            var field = elem.find('input[name="' + this.props.focused + '"]');

            setTimeout(function() {
                console.log(field);
                field.focus();
            }.bind(this));
        }
    },

    _onNotifyValidStateChanged: function() {

    },

    _onNotifyValueChanged: function(key, value) {

        this.setValue(key, value);

        if (this.props.onValueChanged) {
            this.props.onValueChanged(key, value);
        }
    },

    cloneChildren: function (children) {

        return React.Children.map(children, function (child) {

            var newChildren = null;

            if (child.props && child.props.children) {
                newChildren = this.cloneChildren(child.props.children);
            }

            if (child.props && child.props.name && !child.props.onNotifyValueChanged) {

                var newProps = child.props;

                $.extend(newProps, {
                    onNotifyValueChanged: this._onNotifyValueChanged,
                    onNotifyValidStateChanged: this._onNotifyValidStateChanged,
                    getValue: this.getValue
                });
            }

            var newChild = child;

            if (child.type) {
                newChild = React.cloneElement(child, newProps, newChildren);
            }

            //console.log(newChild.props);

            return newChild;

        }.bind(this));
    },

    setValue: function(key, value) {
        var values = this.state.values;
        values = this.setProperty(values, key, value);
        this.setState({values:values});
    },

    getValue: function(key) {
        var value = this.getProperty(this.state.values, key);
        return value;
    },

    setValues: function(obj) {
        this.setState({values:obj});
    },

    getValues: function(existingData) {
        var obj = this.state.values;

        if (existingData != undefined) {
            obj = $.extend(existingData, obj);
        }

        return obj;
    },

    render: function() {

        var children = this.cloneChildren(this.props.children);
        return <form onSubmit={function(event) {event.preventDefault();}} className="form">{children}</form>
    }
});