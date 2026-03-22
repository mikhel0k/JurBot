(function () {
    var loc = window.location;
    var protocol = loc.protocol;
    var hostname = loc.hostname;
    var port = loc.port;
    if (protocol === 'http:' && (hostname === 'localhost' || hostname === '127.0.0.1') && port === '8000') {
        window.API_BASE = protocol + '//' + hostname + ':' + port;
    } else {
        window.API_BASE = 'http://localhost:8000';
    }
})();
