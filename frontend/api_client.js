export function createApiClient(apiBaseUrl = '/api') {
    return {
        async initGame() {
            const response = await fetch(apiBaseUrl + '/game/init', { method: 'POST' });
            if (response.status === 401) throw new Error('Unauthorized');
            if (!response.ok) throw new Error('Failed to initialize game session');
            return response.json();
        },
        async guestLogin() {
            const response = await fetch(apiBaseUrl + '/guest', { method: 'POST' });
            if (!response.ok) throw new Error('Guest login failed');
            return response.json();
        },
        async logout() {
            await fetch(apiBaseUrl + '/logout', { method: 'POST' });
            window.location.href = '/';
        },
        async getAiSettings() {
            const response = await fetch(apiBaseUrl + '/settings/ai');
            if (!response.ok) throw new Error('Failed to load AI API settings');
            return response.json();
        },
        async saveAiSettings(data) {
            const response = await fetch(apiBaseUrl + '/settings/ai', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data),
            });
            if (!response.ok) {
                const payload = await response.json().catch(() => ({}));
                throw new Error(payload.detail || 'Failed to save AI API settings');
            }
            return response.json();
        },
        async testAiSettings(data) {
            const response = await fetch(apiBaseUrl + '/settings/ai/test', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data),
            });
            const payload = await response.json().catch(() => ({}));
            if (!response.ok) throw new Error(payload.detail || 'Failed to test AI API settings');
            return payload;
        },
        async saveAiProfile(data) {
            const response = await fetch(apiBaseUrl + '/settings/ai/profiles', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data),
            });
            const payload = await response.json().catch(() => ({}));
            if (!response.ok) throw new Error(payload.detail || 'Failed to save AI API profile');
            return payload;
        },
        async activateAiProfile(profileId) {
            const response = await fetch(apiBaseUrl + '/settings/ai/profiles/' + encodeURIComponent(profileId) + '/activate', { method: 'POST' });
            const payload = await response.json().catch(() => ({}));
            if (!response.ok) throw new Error(payload.detail || 'Failed to activate AI API profile');
            return payload;
        },
        async deleteAiProfile(profileId) {
            const response = await fetch(apiBaseUrl + '/settings/ai/profiles/' + encodeURIComponent(profileId), { method: 'DELETE' });
            const payload = await response.json().catch(() => ({}));
            if (!response.ok) throw new Error(payload.detail || 'Failed to delete AI API profile');
            return payload;
        },
        async clearAiSettings() {
            const response = await fetch(apiBaseUrl + '/settings/ai', { method: 'DELETE' });
            if (!response.ok) throw new Error('Failed to clear AI API settings');
            return response.json();
        },
    };
}
