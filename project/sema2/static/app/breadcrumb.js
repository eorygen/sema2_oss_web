var Breadcrumb = React.createClass({

    render: function () {

        return (
            <ol className="breadcrumb">
            {this.props.items.map(function (item) {
                if (item.url) {
                    return <li key={item.url}>
                        <a href={item.url}>{item.name}</a>
                    </li>;
                }
                else {
                    return <li key={item.name}>
                        {item.name}
                    </li>;
                }
            }, this)}
            </ol>
        );
    }
});