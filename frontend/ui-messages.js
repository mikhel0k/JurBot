/**
 * Сообщения об ошибках API/сети не показываем пользователю подробно —
 * детали только в консоли (Application / DevTools).
 */
(function (global) {
    var NS = (global.JurBotUi = global.JurBotUi || {});

    NS.logError = function (context, info) {
        console.error('[JurBot]', context, info);
    };

    NS.clearHint = function (el) {
        if (el) el.textContent = '';
    };

    /** Залогировать тело ответа и вернуть распарсенный JSON или текст (для лога). */
    NS.logBadResponse = async function (context, response) {
        var text = '';
        try {
            text = await response.clone().text();
        } catch (e) {
            NS.logError(context + ' (read body)', e);
            NS.logError(context, { status: response.status });
            return null;
        }
        var parsed = text;
        try {
            parsed = JSON.parse(text);
        } catch (ignore) {}
        NS.logError(context, { status: response.status, body: parsed });
        return parsed;
    };
})(window);
