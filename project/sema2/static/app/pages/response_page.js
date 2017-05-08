var ProgramResponsePage = React.createClass({

    mixins: [UrlBuilderMixin],

    getInitialState: function() {
        return {
            isLoading: false
        }
    },

    componentDidMount: function() {
    },

    render: function() {

        console.log(this.props.answer_set);
        console.log(this.props.answer_set.answers);

        var title = "Response ID: " + this.props.answer_set.id;
        var backUrl = "/programs/" + this.props.program.id + "/responses/?p=" + this.props.cur_page;

        return (
            <Column count="12">

                <ProgramTabs
                    program={this.props.program}
                    selectedId="responses"/>

                <ProgramHeader
                    program={this.props.program}
                    name={title}>
                </ProgramHeader>

                <a className="btn btn-stroke btn-sm" href={backUrl}><i className="ss-cursor"></i>&nbsp;&nbsp;Back to all Responses</a>
                <hr/>

                <div className="response-table">
                    <DataTable
                        ref='table'
                        isLoading={this.state.isLoading}
                        columns={[
                            {name: 'Type', key: 'linked_question.question_type', size:1, transform: function(item) { return <span className="label label-primary">{QuestionTypeString(item)}</span> }},
                            {name: 'Question Text', key: 'linked_question.question_text', size: 4},
                            {name: 'Answer', key: 'answer_display', size:5},
                            {name: 'Tag', key: 'linked_question.question_tag', size:1, transform: function(item) { return <span className="label label-success">{item}</span> }},
                            {name: 'Elapsed', key: 'reaction_time_ms', size:1, transform: function(item) { return item + " ms" } }
                        ]}
                        items={this.props.answer_set.answers}
                    />
                </div>
            </Column>
        );
    }
});