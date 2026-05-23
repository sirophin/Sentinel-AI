chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "maskText" || request.action === "demaskText") {
        fetch("http://127.0.0.1:8000/process", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ 
                action: request.action,
                text: request.payload.text, 
                session_id: request.payload.session_id 
            })
        })
        .then(res => res.json())
        .then(data => sendResponse(data))
        .catch(err => sendResponse({ error: err.message }));
        
        return true; // async response-க்காக அவசியம்
    }
});
