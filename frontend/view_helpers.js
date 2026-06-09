function escapeHtml(text) {
    return String(text || '').replace(/[&<>]/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[char]));
}

function joinCleanList(value, fallback = '') {
    const items = Array.isArray(value) ? value : [value];
    const text = items
        .map(item => String(item || '').trim())
        .filter(Boolean)
        .join('、');
    return text || fallback;
}

function formatLegacyStateEffectLine(line) {
    const rawLine = String(line || '');
    const prefix = '状态变化：';
    const index = rawLine.indexOf(prefix);
    if (index === -1) return rawLine;
    const rawEffect = rawLine.slice(index + prefix.length).trim();
    if (!rawEffect.startsWith('{')) return rawLine;
    const entries = Array.from(rawEffect.matchAll(/[\'"]([^\'"]+)[\'"]\s*:\s*(-?\d+)/g))
        .map(match => {
            const value = Number(match[2]);
            return match[1] + ' ' + (value > 0 ? '+' : '') + value;
        });
    return entries.length ? rawLine.slice(0, index + prefix.length) + entries.join('、') : rawLine;
}

function parseLegacyPreludeEvent(text) {
    const raw = String(text || '').trim();
    if (!raw.startsWith('{') || !raw.includes('event')) return null;
    const pickText = (key) => {
        const match = raw.match(new RegExp('[\\\'"]' + key + '[\\\'"]\\s*:\\s*[\\\'"]([^\\\'"]*)[\\\'"]'));
        return match ? match[1] : '';
    };
    const pickNumber = (key) => {
        const match = raw.match(new RegExp('[\\\'"]' + key + '[\\\'"]\\s*:\\s*(\\d+)'));
        return match ? match[1] : '';
    };
    const event = pickText('event') || pickText('text') || pickText('summary') || pickText('description');
    if (!event) return null;
    return {
        age: pickNumber('age') || pickText('age'),
        year: pickNumber('year') || pickText('year'),
        event,
        impact: pickText('impact') || pickText('effect') || pickText('influence'),
    };
}

function normalizePreludeEvent(item) {
    if (item && typeof item === 'object' && !Array.isArray(item)) {
        return {
            age: item.age || '',
            year: item.year || '',
            event: item.event || item.text || item.summary || item.description || JSON.stringify(item),
            impact: item.impact || item.effect || item.influence || '',
        };
    }
    const legacy = parseLegacyPreludeEvent(item);
    if (legacy) return legacy;
    return { age: '', year: '', event: String(item || ''), impact: '' };
}

function renderPreludeEvent(item, compact = false) {
    const event = normalizePreludeEvent(item);
    const meta = [
        event.age ? event.age + '岁' : '',
        event.year ? event.year + '年' : '',
    ].filter(Boolean).join(' · ');
    return '<article class=\'prelude-event-card' + (compact ? ' compact' : '') + '\'>' +
        (meta ? '<span class=\'prelude-event-meta\'>' + escapeHtml(meta) + '</span>' : '') +
        '<p>' + escapeHtml(event.event) + '</p>' +
        (event.impact ? '<small>影响：' + escapeHtml(event.impact) + '</small>' : '') +
        '</article>';
}

function renderText(text) {
    return String(text || '').split('\n').map(line => {
        line = formatLegacyStateEffectLine(line);
        if (line.startsWith('# ')) return '<h1>' + escapeHtml(line.slice(2)) + '</h1>';
        if (line.startsWith('## ')) return '<h2>' + escapeHtml(line.slice(3)) + '</h2>';
        if (line.startsWith('- ')) {
            const body = line.slice(2);
            if (parseLegacyPreludeEvent(body)) return renderPreludeEvent(body, true);
            return '<p class=\'bullet-line\'>• ' + escapeHtml(body) + '</p>';
        }
        return line ? '<p>' + escapeHtml(line) + '</p>' : '';
    }).join('');
}

export { escapeHtml, joinCleanList, formatLegacyStateEffectLine, parseLegacyPreludeEvent, normalizePreludeEvent, renderPreludeEvent, renderText };
