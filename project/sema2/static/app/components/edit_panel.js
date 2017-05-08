var State = React.createClass({

    render: function() {
        return <div>{this.props.children}</div>;
    }
});

var StatePanel = React.createClass({

    getDefaultProps: function() {
        return {
            activeState: null
        }
    },

    getInitialState: function () {
        return {
            activeState: this.props.activeState
        }
    },

    componentWillReceiveProps: function(newProps) {
        this.setState({activeState:newProps.activeState});
    },

    componentDidMount: function() {

    },

    render: function() {

        var res = null;

        React.Children.forEach(this.props.children, function(child) {

            var names = child.props.name.split(",");

            names.forEach(function(item) {

                if (item == this.props.state) {
                    res = child;
                }
            }.bind(this));

        }, this);

        var panelKey = "panel_" + this.props.state;

        return (
            <div key={panelKey}>{res}</div>
        );
    }
});