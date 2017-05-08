var DataTableActionsMenu = React.createClass({

    handleClick: function(event) {
        event.stopPropagation();
    },

    handleItemClick: function(item, rowData, event) {

        event.stopPropagation();

        if (!this.props.disabled) {
            item.action(this.props.rowData);
        }
    },

    render: function () {

        return (
            <div className="btn-group btn-group-dropdown pull-right">
                <button type="button" disabled={this.props.disabled} className="btn btn-sm btn-default dropdown-toggle" data-toggle="dropdown" onClick={this.handleClick}>Actions<span className="ss-navigatedown pull-right"></span></button>
                <ul className="dropdown-menu" role="menu">
                    <div className="arrow top"></div>
                {this.props.items.map(function(item) {
                    if (item.action != undefined) {
                        return <li key={item.name}><a onClick={this.handleItemClick.bind(this, item, this.props.rowData)}>{item.name}</a></li>;
                    }
                    else {
                        return <li key={item.name}><a href={item.url}>{item.name}</a></li>;
                    }
                }, this)}
                </ul>
            </div>
        );
    }
});

var DataTableRow = React.createClass({

    mixins: [DataWidgetMixin],

    _onRowClicked: function(event) {

        if (this.props.onRowClicked && !this.props.disabled) {
            this.props.onRowClicked(this.props.rowData);
        }
    },

    rowActionsMenu: function(showActionsColumn) {

        if (showActionsColumn) {

            if (this.props.rowActionItems != undefined) {
                return <td><DataTableActionsMenu disabled={this.props.disabled} rowData={this.props.rowData} items={this.props.rowActionItems}/></td>;
            }
            else {
                return <td></td>;
            }
        }
        else {
            return null;
        }
    },

    onChangeField: function(key, event) {
        this.props.onChangeField(this.props.index, key, $(event.target).val());
    },

    onChangeSelectorField: function(key, name, value) {
        this.props.onChangeField(this.props.index, key, value);
    },

    render: function () {

        var cb = this.props.showActionsColumn ? <td><label onClick={this.props.onToggleRow} className="checkbox" htmlFor="checkbox1"><span className="icons"><span className="first-icon"></span><span className="second-icon ss-check"></span></span><input type="checkbox" value="" id="checkbox1" data-toggle="checkbox"></input></label></td> : null;

        return (
            <tr onClick={this._onRowClicked}>
            {cb}
            {this.props.columns.map(function(column, index) {

                var value = null;

                if (column.value) {
                    value = column.value(this.props.rowData, this.props.index, index);
                }
                else {
                    value = this.getProperty(this.props.rowData, column.key);
                }

                if (column.transform) {
                    value = column.transform(value);
                }

                var elem = value;

                if (this.props.tableIsEditable || column.isEditable) {

                    if (column.useSelector) {
                        elem = <FormDropdown disabled={this.props.disabled} name={column.name} items={column.selectorItems} labelField={column.selectorLabelField} valueField={column.selectorKeyField} value={value} onValueChanged={this.onChangeSelectorField.bind(this, column.key)} selectorFilter={column.selectorFilter} />
                    }
                    else {
                        elem = <input type="text" disabled={this.props.disabled} className="form-control" value={value} placeholder={column.name} onChange={this.onChangeField.bind(this, column.key)}></input>
                    }
                }
                else if (column.disableHtmlEscaping) {
                    elem = <span dangerouslySetInnerHTML={{__html:elem}}/>
                }

                return <td key={index}>{elem}</td>;

            }, this)}
            {this.rowActionsMenu(this.props.showActionsColumn)}
            </tr>
        );
    }
});

var DataTable = React.createClass({

    propTypes: {
        items: React.PropTypes.array,
        columns: React.PropTypes.array,
        dataUrl: React.PropTypes.string
    },

    getDefaultProps: function() {
        return {
            items: [],
            allowMultiSelect:false
        }
    },

    getInitialState: function() {
        return {
            selectedItems: {},
            items: this.props.items
        }
    },

    componentWillReceiveProps: function(nextProps) {
        this.setState({items: nextProps.items});
    },

    selectItemAtIndex: function(props, index, doClick, suppressUpdate) {

        if (index >= 0 && index < props.items.length) {

            var item = props.items[index];

            if (doClick && props.onItemClicked) {
                props.onItemClicked(item, index);
            }

            var selectedItems = this.state.selectedItems;

            if (selectedItems['key-' + index] == null) {
                selectedItems['key-' + index] = item;
            }
            else {
                delete selectedItems['key-' + index];
            }

            if (!suppressUpdate) {
                this.setState({selectedItems: selectedItems});
            }
        }
    },

    getValues: function() {
        return this.state.items;
    },

    getSelectedItems: function() {

        var selectedItems = this.state.selectedItems;
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

    componentDidMount:function() {

    },

    onSelectAllClicked: function() {

        this.state.items.map(function(item, index) {
        }, this);
    },

    onToggleRow: function(index, event) {
        event.stopPropagation();
        this.selectItemAtIndex(this.props, index, true);
    },

    onChangeField: function(index, key, value) {
        var items = this.state.items;
        items[index][key] = value;
        this.setState({items:items});
    },

    onHeaderItemClicked: function(key) {

        if (this.props.onSortingChanged(key)) {
            this.props.onSortingChanged(key);
        }
    },

    tableRows: function(showActionsColumn) {

        var selectedItems = this.state.selectedItems;

        return (<tbody>
                    {this.state.items.map(function(row, index) {
                        var isSelected = selectedItems['key-' + index] != null;
                        var rowId = row['id'];
                        return <DataTableRow key={index} disabled={this.props.disabled} index={index} isEditable={this.props.isEditable} selected={isSelected} onToggleRow={this.onToggleRow.bind(this, index)} onChangeField={this.onChangeField} columns={this.props.columns} rowData={row} onRowClicked={this.props.onRowClicked} rowActionItems={this.props.rowActionItems} showActionsColumn={showActionsColumn}/>
                    }, this)}
        </tbody>);
    },

    emptyRow: function() {
        var width = 100 + '%';
        var colCount = this.props.columns.length + 2;
        var message = this.props.isLoading ? <div>Loading data...<br/><div className="progress progress-striped active">
					  <div className="progress-bar" role="progressbar" style={{width: width}}>
					  </div>
					</div></div> : "No items.";
        return <tbody><tr><td colSpan={colCount}>{message}</td></tr></tbody>;
    },

    tableActionsMenu: function(showActionsColumn) {

        if (showActionsColumn) {

            if (this.props.tableActionItems) {
                return <th>
                    <DataTableActionsMenu disabled={this.props.disabled} items={this.props.tableActionItems}/>
                </th>
            }
            else {
                return <th></th>
            }
        }
        else {
            return null;
        }
    },

    render: function () {

        var isEmpty = this.state.items == null || this.state.items.length == 0 || this.props.isLoading;

        var showActionsColumn = (this.props.tableActionItems != null) || (this.props.rowActionItems != null);
        var tableBody = isEmpty ? this.emptyRow() : this.tableRows(showActionsColumn);
        var cb = showActionsColumn ? <th><label onClick={this.onSelectAllClicked} className="checkbox" htmlFor="checkbox1"><span className="icons"><span className="first-icon"></span><span className="second-icon ss-check"></span></span><input type="checkbox" value="" id="checkbox1" data-toggle="checkbox"></input></label></th> : null;

        return (
            <table className="table table-striped table-compact">
                <thead>
                {cb}
                {this.props.columns.map(function(item) {
                    var classes = "";

                    if (item.size) {
                        classes += "col-md-" + item.size;
                    }

                    return <th key={item.key} className={classes} onClick={this.onHeaderItemClicked.bind(this, item.key)}>{item.name}</th>;
                }, this)}
                {this.tableActionsMenu(showActionsColumn)}
                </thead>
                {tableBody}
            </table>
        );
    }
});