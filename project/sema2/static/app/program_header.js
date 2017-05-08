var ProgramHeader = React.createClass({

    getInitialState:function() {

        return {
        };
    },

    componentDidMount:function() {

    },

    render:function() {

        var foo = this.props.name;

        if (this.props.program) {
            foo = this.props.program.display_name + " (v" + this.props.program.revision_number + ")  ›  " + foo;
        }

        return (
            <div>
                <div className="clearfix">
                    <h4 className="pull-left tight-header">{foo}</h4>

                    <div className="pull-right">
                    {this.props.children}
                    </div>
                </div>
                <hr/>
            </div>
        );
    }
});