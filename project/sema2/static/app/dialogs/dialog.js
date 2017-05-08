/** @jsx React.DOM */

var Dialog = React.createClass({

    mixins: [BootstrapModalMixin],

    getDefaultProps: function () {
        return {
            saveButtonLabel: "Save",
            saveDisabled: false,
            autoDisableSaveButton: false
        }
    },

    getInitialState: function(evt) {
        return {
            saveTemporarilyDisabled: false
        }
    },

    _onCancelClicked: function(event) {

        if (this.props.onCancelClicked) {
            this.props.onCancelClicked(event.target);
        }
    },

    _onSaveClicked: function(event) {

        var self = this;

        if (this.props.onSaveClicked && !this.state.saveTemporarilyDisabled) {

            if (this.props.autoDisableSaveButton) {

                this.setState({
                    saveTemporarilyDisabled: true
                }, function() {
                    this.props.onSaveClicked(event.target);

                    setTimeout(function() {
                        self.setState({
                            saveTemporarilyDisabled: false
                        });
                    }, 1000);
                    
                }.bind(this));
            }
            else {
                this.props.onSaveClicked(event.target);
            }
        }
    },

    render: function() {

        var cancelButton = this.props.onCancelClicked ? <Button onClick={this._onCancelClicked} label="Cancel"/> : <Button onClick={this._onCancelClicked} label="Close"/>;
        var saveButton = this.props.onSaveClicked ? <Button type="primary" disabled={this.props.saveDisabled || this.state.saveTemporarilyDisabled} onClick={this._onSaveClicked}>{this.props.saveButtonLabel}</Button> : null;

        return <div className="modal fade">
            <div className="modal-dialog">
                <div className="modal-content">
                    <div className="modal-header">
                        <strong>{this.props.title}</strong>
                    </div>
                    <div className="modal-body">
                        <div className="container-fluid">
                        {this.props.children}
                        </div>
                    </div>
                    <div className="modal-footer">
                    {cancelButton}
                    {saveButton}
                    </div>
                </div>
            </div>
        </div>
    }
});