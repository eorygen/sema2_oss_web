var UrlBuilderMixin = {

    buildRequest: function(segments, objId) {

        var url = "/api/1/";

        if (Array.isArray(segments)) {
            segments.map(function (segment) {
                url += segment + "/";
            });
        }
        else {
            url += segments;
        }

        var method = 'POST';

        // Optionally add the id on the end
        if (objId != undefined && objId != null) {
            url += objId + "/";
            method = 'PUT';
        }

        return {method: method, url: url};
    },

    reactGetRequest: function(segments, objId) {
        return this.reactRequest("get", segments, objId, null);
    },

    reactPostRequest: function(segments, objId, data) {
        return this.reactRequest("post", segments, objId, data);
    },

    reactPutRequest: function(segments, objId, data) {
        return this.reactRequest("put", segments, objId, data);
    },

    reactAddOrUpdateRequest: function(segments, objId, data) {
        if (objId) {
            return this.reactPutRequest(segments, objId, data);
        }
        else {
            return this.reactPostRequest(segments, objId, data);
        }
    },

    reactRequest: function(method, segments, objId, data) {

        var req = this.buildRequest(segments, objId);

        var op = $.ajax({
            type:method.toUpperCase(),
            url:req.url,
            data: data ? JSON.stringify(data) : null,
            dataType: 'json',
            contentType: "application/json"
        });

        return op;
    }
};