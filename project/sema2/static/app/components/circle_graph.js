var Circle = React.createClass({

    getDefaultProps: function() {
        return {
            width: 5,
            radius: 40,
            value: 90
        }
    },

    componentDidMount: function() {

        var myCircle = Circles.create({

            id:           'circles-' + this.props.id,
            radius:       this.props.radius,
            value:        this.props.value,
            maxValue:     100,
            width:        this.props.width,
            text:         function(value){ return value + '%';},
            colors:       ['#dddddd', '#2FB1E5'],
            duration:       400,
            wrpClass:     'circles-wrp',
            textClass:    'circles-text',
            styleWrapper: true,
            styleText:    true
        });
    },

    render: function() {

        var id = 'circles-' + this.props.id;

        return (
            <div ref="circle" className="circle" id={id}></div>
        );
    }
});