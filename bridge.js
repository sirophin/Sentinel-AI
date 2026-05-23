window.addEventListener("message", (event) => {
    if (event.source !== window || event.data?.type !== "SENTINEL_REQUEST") return;
    chrome.runtime.sendMessage(event.data, (response) => {
        window.postMessage({
            type: "SENTINEL_RESPONSE",
            requestId: event.data.requestId,
            result: response
        }, "*");
    });
});
