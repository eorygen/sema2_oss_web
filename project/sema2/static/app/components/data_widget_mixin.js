var DataWidgetMixin = {

    getProperty:function(obj, prop) {

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
    }
}
