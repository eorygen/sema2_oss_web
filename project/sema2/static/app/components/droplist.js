//
var CheckListItem = React.createClass({

    render: function() {

        return (
            <div className="panel panel-default">
                <div className="panel-body">
                <label className="checkbox sr-only">
                    <input type="checkbox" value="" data-toggle="checkbox"></input>
                </label>
                </div>
            </div>
        );
    }
});

//
var CheckList = React.createClass({

    render: function() {

        var items = this.props.items.map(function(item, index) {
            return <CheckListItem key={index} data-id={index} item={item}/>
        });

        return (
            <div>
                {items}
            </div>
        );
    }
});