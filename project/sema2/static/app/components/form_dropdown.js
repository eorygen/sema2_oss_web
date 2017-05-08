var FormDropdown = React.createClass({

    mixins: [ModelUtilsMixin],

    getDefaultProps: function() {
        return {
            items: [],
            valueField: 'value',
            labelField: 'label',
            emptyLabel: "[No item]",
            isValid: true,
            selectorFilter: null
        }
    },

    _onClick: function(index, event) {

        event.preventDefault();
        event.stopPropagation();

        var value = this.props.items[index][this.props.valueField];

        if (this.props.onValueChanged) {
            this.props.onValueChanged(this.props.name, value);
        }

        if (this.props.onNotifyValueChanged) {
            this.props.onNotifyValueChanged(this.props.name, value);
        }
    },

    render: function() {

        var value = this.props.getValue ? this.props.getValue(this.props.name) : this.props.value;

        var index = -1;
        for (var i=0; i < this.props.items.length; i++) {
            if (this.props.items[i][this.props.valueField] == value) {
                index = i;
                break;
            }
        }

        var name = index >= 0 ? this.props.items[index][this.props.labelField] : this.props.emptyLabel;

        if (this.props.disabled) {
            return <p>{name}</p>;
        }

        var selectorItems = [];

        if (this.props.selectionFilter) {
            selectorItems = this.props.items.filter(this.props.selectorFilter);
        }
        else {
            selectorItems = this.props.items;
        }

        return (
            <div className="btn-group btn-group-dropdown">
                <input name={this.props.name} type="hidden" value={value}/>
                <button id={this.props.name} type="button" className="btn btn-default dropdown-toggle" data-toggle="dropdown">{name}
                    <span className="ss-navigatedown pull-right"></span>
                </button>

                <ul className="dropdown-menu" role="menu">
                    <div className="arrow top"></div>
                    {selectorItems.map(function(item, index) {

                        var label = null;

                        if (this.props.labelFunc) {
                            label = this.props.labelFunc(item, index);
                        }
                        else {
                            label = item[this.props.labelField];
                        }

                        return <li key={index}><a href="#" onClick={this._onClick.bind(this, index)}>{label}</a></li>
                    }, this)}
                </ul>
            </div>
        );
    }
});
