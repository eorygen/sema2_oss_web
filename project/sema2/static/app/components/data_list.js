var DataList = React.createClass({

    mixins: [DataWidgetMixin],

    propTypes: {
        items: React.PropTypes.array.isRequired,
        dataIdField: React.PropTypes.string.isRequired,
        dataNameField: React.PropTypes.string,
        selectedItemIndex: React.PropTypes.number,
        allowMultiSelect: React.PropTypes.bool,
        transform: React.PropTypes.func
    },

    getDefaultProps: function() {
        return {
            items: [],
            selectedItemIndex: 0
        }
    },

    getInitialState: function() {
        return {
            selectedItems: {},
            selectedItemIndex: 0
        }
    },

    componentDidMount:function() {

        this.selectItemAtIndex(this.props, this.props.selectedItemIndex, false);
    },

    componentWillReceiveProps: function(nextProps) {

        this.selectItemAtIndex(nextProps, nextProps.selectedItemIndex, false);
    },

    _onItemClicked: function(index) {

        this.selectItemAtIndex(this.props, index, true);
    },

    selectItemAtIndex: function(props, index, doClick) {

        if (index >= 0 && index < props.items.length) {

            var item = props.items[index];

            if (doClick && props.onItemClicked) {
                props.onItemClicked(item, index);
            }

            var selectedItems = this.state.selectedItems;

            if (!props.allowMultiSelect) {
                selectedItems = {};
            }

            if (selectedItems['key-' + index] == null) {
                selectedItems['key-' + index] = item;
            }
            else {
                delete selectedItems['key-' + index];
            }

            this.setState({selectedItems: selectedItems});
        }
    },

    getSelectedItems: function() {

        selectedItems = this.state.selectedItems;
        var items = [];

        for (var property in selectedItems) {
            if (selectedItems.hasOwnProperty(property)) {
                items.push(selectedItems[property]);
            }
        }

        return items;
    },

    clearSelectedItems: function() {
        this.setState({selectedItems:{}});
    },

    itemRows: function() {

        var idField = this.props.dataIdField;
        var nameField = this.props.dataNameField;
        var selectedItems = this.state.selectedItems;

        return (
            <div className="list-group">
                    {this.props.items.map(function(row, index) {
                        var keyVal = this.getProperty(row, idField);
                        var nameVal = null;

                        if (this.props.value) {
                            nameVal = this.props.value(row, index);
                        }
                        else {
                            nameVal = this.getProperty(row, nameField);

                            if (this.props.transform) {
                                nameVal = this.props.transform(nameVal, index);
                            }
                        }

                        var isSelected = selectedItems['key-' + index] != null;
                        var classes = isSelected ? "list-group-item active" : "list-group-item";
                        return (
                            <a key={keyVal} className={classes} onClick={this._onItemClicked.bind(this, index)}>
                                {nameVal}
                            </a>
                        );
                    }, this)}
            </div>);
    },

    emptyRow: function() {

        return (
            <div className="list-group">
                <a className="list-group-item empty">No items.</a>
            </div>);
    },

    render: function () {

        var isEmpty = this.props.items.length == 0;
        var listBody = isEmpty ? this.emptyRow() : this.itemRows();

        return listBody;
    }
});