export function applyPatch(doc, patch) {
    for (const op of patch || []) {
        const parts = op.path.split('/').slice(1).map(part => part.replace(/~1/g, '/').replace(/~0/g, '~'));
        let target = doc;
        for (const part of parts.slice(0, -1)) target = target[part];
        const key = parts[parts.length - 1];
        if (op.op === 'remove') {
            if (Array.isArray(target)) target.splice(Number(key), 1);
            else delete target[key];
        } else if (op.op === 'add' && Array.isArray(target)) {
            if (key === '-') target.push(op.value);
            else target.splice(Number(key), 0, op.value);
        } else {
            target[key] = op.value;
        }
    }
    return doc;
}

export function createSocketManager({ apiBaseUrl = '/api', appState, onStateChanged }) {
    return {
        socket: null,
        connect() {
            return new Promise((resolve, reject) => {
                if (this.socket && this.socket.readyState === WebSocket.OPEN) {
                    resolve();
                    return;
                }
                const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                const wsUrl = protocol + '//' + window.location.host + apiBaseUrl + '/ws';
                this.socket = new WebSocket(wsUrl);
                this.socket.onopen = () => resolve();
                this.socket.onmessage = (event) => {
                    const message = JSON.parse(event.data);
                    if (message.type === 'full_state') {
                        appState.gameState = message.data;
                    } else if (message.type === 'patch' && appState.gameState) {
                        appState.gameState = applyPatch(appState.gameState, message.patch);
                    }
                    onStateChanged?.(message);
                };
                this.socket.onclose = () => setTimeout(() => this.connect(), 3000);
                this.socket.onerror = (error) => reject(error);
            });
        },
        sendAction(action) {
            if (this.socket && this.socket.readyState === WebSocket.OPEN) {
                this.socket.send(JSON.stringify({ action }));
            }
        },
    };
}
