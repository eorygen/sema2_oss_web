var Tab = React.createClass({

    render: function() {
        return <div>{this.props.children}</div>;
    }
});

var TabPanel = React.createClass({

    getDefaultProps: function() {
        return {
            type: 'tabs'
        }
    },

    componentDidMount: function() {
    },

    _onClick: function (tabId, event) {
        event.preventDefault();

        if (this.props.onSelectionChange) {
            this.props.onSelectionChange(tabId);
        }
    },

    render: function() {

        var tabs = [];
        var activeChild = null;

        React.Children.forEach(this.props.children, function(child) {

            var classes = "";

            if (child.props.id == this.props.selectedTab) {
                activeChild = child;
                classes = "active";
            }

            tabs.push(<li key={child.props.id} id={child.props.id} onClick={this._onClick.bind(this, child.props.id)} className={classes}><a href="#">{child.props.label}</a></li>)

        }, this);

        var classes = this.props.type ? "nav nav-" + this.props.type : "nav nav-tabs";

        return (
            <div>
                <ul id="main-tab-bar" className={classes}>
                {tabs}
                </ul>
                <div>{activeChild}</div>
            </div>
        );
    }
});