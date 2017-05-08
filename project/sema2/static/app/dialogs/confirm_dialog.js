/** @jsx React.DOM */

var ConfirmDialog = React.createClass({

    mixins: [BootstrapModalMixin],

    getInitialState: function () {
        return {
            successHandler: null
        }
    },

    showWithMessage: function(title, message, cancelLabel, confirmLabel, successHandler, isDanger) {

        this.setState({
            title: title,
            message: message,
            cancelLabel: cancelLabel,
            confirmLabel: confirmLabel,
            isDanger: isDanger,
            successHandler:successHandler
        }, function() {
            this.show();
        }.bind(this));
    },

    _onCancelClicked: function(event) {
        this.hide();
    },

    _onConfirmClicked: function(event) {

        this.hide();

        if (this.state.successHandler) {
            this.state.successHandler();
        }
    },

    render: function() {

        var cancelLabel = this.state.cancelLabel ? this.state.cancelLabel : "Cancel";
        var confirmLabel = this.state.confirmLabel ? this.state.confirmLabel : "Ok";

        var classes = "btn btn-primary";
        classes += this.state.isDanger ? " btn-danger" : "";

        var cancelButton = this.state.successHandler ? <button className="btn btn-default" onClick={this._onCancelClicked}>{cancelLabel}</button> : <button className="btn btn-default" onClick={this._onCancelClicked}>Close</button>;
        var confirmButton = this.state.successHandler ? <button className={classes} onClick={this._onConfirmClicked}>{confirmLabel}</button> : null;

        return <div className="modal fade">
            <div className="modal-dialog">
                <div className="modal-content">
                    <div className="modal-header">
                        <strong>{this.state.title}</strong>
                    </div>
                    <div className="modal-body">
                        {this.state.message}
                    </div>
                    <div className="modal-footer">
                    {cancelButton}
                    {confirmButton}
                    </div>
                </div>
            </div>
        </div>
    }
});