// JobPilot - Minimal JS (HTMX handles most interactions)

// Auto-close dialogs on outside click
document.addEventListener('click', (e) => {
    if (e.target.tagName === 'DIALOG') {
        e.target.close();
    }
});

// Format AI responses as HTML when received via HTMX
document.body.addEventListener('htmx:afterSwap', (e) => {
    // If the response is JSON, format it nicely
    const target = e.detail.target;
    try {
        const data = JSON.parse(target.textContent);
        let html = '';

        if (data.summary) {
            html += `<p>${data.summary}</p>`;
        }

        if (data.next_steps && data.next_steps.length) {
            html += '<h4>Next Steps</h4><ol>';
            data.next_steps.forEach(s => html += `<li>${s}</li>`);
            html += '</ol>';
        }

        if (data.risks && data.risks.length) {
            html += '<h4>Risks</h4><ul>';
            data.risks.forEach(r => html += `<li>${r}</li>`);
            html += '</ul>';
        }

        if (data.priority_suggestions && data.priority_suggestions.length) {
            html += '<h4>Priority Suggestions</h4><ul>';
            data.priority_suggestions.forEach(s => html += `<li>${s}</li>`);
            html += '</ul>';
        }

        if (data.top_priorities && data.top_priorities.length) {
            html += '<h4>Top Priorities</h4><ol>';
            data.top_priorities.forEach(p => html += `<li>${p}</li>`);
            html += '</ol>';
        }

        if (data.blockers && data.blockers.length) {
            html += '<h4>Blockers</h4><ul>';
            data.blockers.forEach(b => html += `<li>${b}</li>`);
            html += '</ul>';
        }

        if (data.recommendations && data.recommendations.length) {
            html += '<h4>Delegation Recommendations</h4><ul>';
            data.recommendations.forEach(r => {
                html += `<li><strong>${r.task_title}</strong> &rarr; ${r.recommended_member_name}<br><small>${r.reason}</small></li>`;
            });
            html += '</ul>';
        }

        if (html) target.innerHTML = html;
    } catch {
        // Not JSON, leave as-is
    }
});
