
class AJAXError extends Error {
    constructor(message, status, url) {
        super(message);
        this.status = status;
        this.url = url;

        // work around for https://github.com/Rich-Harris/buble/issues/40
        this.name = this.constructor.name;
        this.message = message;
    }

    toString() {
        return `${this.name}: ${this.message} (${this.status}): ${this.url}`;
    }
}

function makeRequest(requestParameters) {
    const xhr = new window.XMLHttpRequest();

    xhr.open('GET', requestParameters.url, true);
    for (const k in requestParameters.headers) {
        xhr.setRequestHeader(k, requestParameters.headers[k]);
    }
    xhr.withCredentials = requestParameters.credentials === 'include';
    return xhr;
};

function getJSON(requestParameters, callback) {
    const xhr = makeRequest(requestParameters);
    xhr.setRequestHeader('Accept', 'application/json');
    xhr.onerror = function() {
        callback(new Error(xhr.statusText));
    };
    xhr.onload = function() {
        if (xhr.status >= 200 && xhr.status < 300 && xhr.response) {
            let data;
            try {
                data = JSON.parse(xhr.response);
            } catch (err) {
                return callback(err);
            }
            callback(null, data);
        } else {
            if (xhr.status === 401 && requestParameters.url.match(/mapbox.com/)) {
                callback(new AJAXError(`${xhr.statusText}: you may have provided an invalid Mapbox access token. See https://www.mapbox.com/api-documentation/#access-tokens`, xhr.status, requestParameters.url));
            } else {
                callback(new AJAXError(xhr.statusText, xhr.status, requestParameters.url));
            }
        }
    };
    xhr.send();
    return xhr;
};

function getSecondPart(str) {
  return str.split(' - ')[1];
}

function cleanLabel(str){
  str = str.charAt(0).toUpperCase() + str.slice(1);
  str = str.replace(/_/g,' ');
  str = str.replace(/ s /g, "'s ");
  return str;
}
