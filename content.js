// ── MAIN world script: intercepts fetch, uses postMessage to bridge ───────────
console.log("Sentinel-AI: Network Hook Active");

const _originalFetch = window.fetch.bind(window);
let currentSessionId = "";

// Listen for responses FROM the isolated bridge
window.addEventListener("message", (event) => {
    if (event.source !== window) return;
    if (event.data?.type === "SENTINEL_SESSION") {
        currentSessionId = event.data.sessionId || currentSessionId;
    }
});

// Helper: ask isolated world (bridge.js) to call backend
function askBridge(action, payload) {
    return new Promise((resolve) => {
        const requestId = Math.random().toString(36).slice(2);

        const handler = (event) => {
            if (event.source !== window) return;
            if (event.data?.type === "SENTINEL_RESPONSE" && event.data.requestId === requestId) {
                window.removeEventListener("message", handler);
                resolve(event.data.result);
            }
        };

        window.addEventListener("message", handler);

        window.postMessage({
            type:      "SENTINEL_REQUEST",
            action,
            requestId,
            payload:   { ...payload, session_id: currentSessionId },
        }, "*");

        // Timeout fallback (3s)
        setTimeout(() => {
            window.removeEventListener("message", handler);
            resolve(null);
        }, 3000);
    });
}

// ── Intercept window.fetch ────────────────────────────────────────────────────
window.fetch = async function (...args) {
    let [url, options] = args;

    const isChat = typeof url === "string" && (
        url.includes("/conversation") ||
        url.includes("/backend-api")  ||
        url.includes("/responses")
    );

    if (isChat && options?.body) {
        try {
            let body = JSON.parse(options.body);
            let originalText = null;

            // ChatGPT messages format
            if (body?.messages?.length > 0) {
                const lastMsg = body.messages[body.messages.length - 1];
                if (lastMsg?.content?.parts?.[0]) {
                    originalText = lastMsg.content.parts[0];
                }
            }

            // Responses API format
            if (!originalText && body?.input) {
                if (typeof body.input === "string") {
                    originalText = body.input;
                } else if (Array.isArray(body.input)) {
                    const last = body.input[body.input.length - 1];
                    originalText = last?.content?.[0]?.text || null;
                }
            }

            if (originalText && typeof originalText === "string" && originalText.trim()) {
                console.log("[Sentinel-AI] Intercepted:", originalText.slice(0, 80));

                const maskData = await askBridge("maskText", { text: originalText });

                if (maskData?.maskedText) {
                    currentSessionId = maskData.sessionId || currentSessionId;
                    console.log("[Sentinel-AI] Masked:", maskData.maskedText.slice(0, 80));
                    console.log("[Sentinel-AI] Entities:", maskData.itemsFound);

                    // Inject masked text back into request
                    if (body?.messages?.length > 0) {
                        body.messages[body.messages.length - 1].content.parts[0] = maskData.maskedText;
                    } else if (body?.input) {
                        if (typeof body.input === "string") {
                            body.input = maskData.maskedText;
                        } else if (Array.isArray(body.input)) {
                            const last = body.input[body.input.length - 1];
                            if (last?.content?.[0]?.text !== undefined) {
                                last.content[0].text = maskData.maskedText;
                            }
                        }
                    }

                    options = { ...options, body: JSON.stringify(body) };
                    args = [url, options];
                }
            }
        } catch (err) {
            console.error("[Sentinel-AI] Hook Error:", err);
        }
    }

    return _originalFetch(...args);
};

// ── MutationObserver: demask tokens in ChatGPT's rendered replies ─────────────
async function demaskNode(node) {
    if (!node?.textContent) return;
    if (!currentSessionId) return;
    if (!/<[A-Z_]+_\d+>/.test(node.textContent)) return;

    const data = await askBridge("demaskText", { text: node.textContent });
    if (data?.restoredText && data.tokensReplaced > 0) {
        node.textContent = data.restoredText;
        console.log("[Sentinel-AI] Demasked", data.tokensReplaced, "token(s)");
    }
}

const observer = new MutationObserver((mutations) => {
    for (const mutation of mutations) {
        for (const node of mutation.addedNodes) {
            if (node.nodeType === Node.TEXT_NODE) {
                demaskNode(node);
            } else if (node.nodeType === Node.ELEMENT_NODE) {
                const walker = document.createTreeWalker(node, NodeFilter.SHOW_TEXT);
                let t;
                while ((t = walker.nextNode())) demaskNode(t);
            }
        }
    }
});

observer.observe(document.body, { childList: true, subtree: true });
