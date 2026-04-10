(function () {
    var loc = window.location;
    var protocol = loc.protocol;
    var hostname = loc.hostname;
    var port = loc.port;
    if (protocol === 'file:') {
        console.warn(
            '[JurBot] Страница открыта как file:// — куки авторизации не отправляются на API, будет 401. ' +
                'Откройте: http://localhost:8000/ui/ (Docker/бэкенд) или поднимите фронт: cd frontend && python -m http.server 3000 → http://localhost:3000/'
        );
    }
    if (protocol === 'http:' && (hostname === 'localhost' || hostname === '127.0.0.1') && port === '8000') {
        window.API_BASE = protocol + '//' + hostname + ':' + port;
    } else {
        window.API_BASE = 'http://localhost:8000';
    }
})();
