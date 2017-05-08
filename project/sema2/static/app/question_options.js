var QuestionOptions = React.createClass({

    render: function() {

        return (
            <table className="table">
                <tbody>
                    {this.props.options.map(function(item) {
                        return <tr><input type=""
                    })}
                </tbody>
            </table>
        );
    }
});