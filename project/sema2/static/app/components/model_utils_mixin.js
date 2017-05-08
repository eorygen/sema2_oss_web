var ModelUtilsMixin = {

    getProperty:function(obj, prop, defaultValue) {

        if (obj == undefined || obj == null) {
            return defaultValue;
        }

        var parts = prop.split('.');

        if (parts.length == 1) {
            return obj[parts.pop()];
        }
        else {
            var last = parts.pop();
            var l = parts.length;
            var i = 1;
            var current = parts[0];

            while ((obj = obj[current]) && i < l) {
                current = parts[i];
                i++;
            }

            if (obj) {
                return obj[last];
            }
        }
    },

    setProperty:function(obj, prop, value) {

        var parts = prop.split('.');

        if (parts.length == 1) {
            obj[parts.pop()] = value;
        }
        else {
            var tmp = obj;
            var last = parts.pop();
            var l = parts.length;
            var i = 1;
            var current = parts[0];

            while ((tmp = tmp[current]) && i < l) {
                current = parts[i];
                i++;
            }

            if (tmp) {
                tmp[last] = value;
            }
        }

        return obj;
    },

    setInitialValue: function (props) {
        var property = props.property ? props.property : props.name;
        var value = props.value ? props.value : this.getProperty(props.object, property, props.default);
        this.setState({
            value: value
        })
    },

    getPropertyAsString:function(obj, prop, defaultValue) {

        var value = this.getProperty(obj, prop, defaultValue);

        if (value && typeof value != 'string') {
            value = value.toString();
        }

        return value;
    },

    getPropertyAsInt:function(obj, prop, defaultValue) {

        var value = this.getProperty(obj, prop, defaultValue);

        if (value && typeof value != 'int') {
            value = parseInt(value);
        }

        return value;
    },

    getPropertyAsBoolean:function(obj, prop, defaultValue) {

        var value = this.getProperty(obj, prop, defaultValue);
        return value ? true : false;
    }

}
