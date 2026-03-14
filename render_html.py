import html
from datetime import datetime

from models.claim_event import ClaimEvent
from models.claim_state import ClaimState
from models.claim_state_delta import ClaimStateDelta
from models.todo_item import TodoItem


def _fmt_dt(dt: datetime | None) -> str:
    if dt is None:
        return ""
    return dt.strftime("%Y-%m-%d %H:%M UTC")


def _esc(text: str) -> str:
    return html.escape(str(text))


def _category_class(category: str) -> str:
    return f"cat-{category}"


def _render_todo_row(item: TodoItem) -> str:
    return (
        f"<tr class='{_category_class(item.category)}' data-category='{_esc(item.category)}'>"
        f"<td class='mono'>{_esc(item.todo_item_id)}</td>"
        f"<td><span class='badge badge-{item.category}'>{_esc(item.category)}</span></td>"
        f"<td>{_esc(item.description)}</td>"
        f"<td>{_esc(item.owner)}</td>"
        f"<td><span class='badge badge-{item.status}'>{_esc(item.status)}</span></td>"
        f"<td>{_esc(item.urgency_type)}</td>"
        f"<td class='mono'>{_fmt_dt(item.created_at)}</td>"
        f"<td class='mono'>{_fmt_dt(item.terminal_at)}</td>"
        f"</tr>"
    )


def _render_todo_table(items: list[TodoItem], title: str) -> str:
    if not items:
        return f"<p class='empty'>{_esc(title)}: none</p>"
    return (
        f"<table>"
        f"<thead><tr>"
        f"<th>ID</th><th>Category</th><th>Description</th>"
        f"<th>Owner</th><th>Status</th><th>Urgency</th>"
        f"<th>Created</th><th>Terminal</th>"
        f"</tr></thead>"
        f"<tbody>{''.join(_render_todo_row(i) for i in items)}</tbody>"
        f"</table>"
    )


def _render_delta_section(delta: ClaimStateDelta) -> str:
    parts = []

    # Events added
    if delta.events.add:
        parts.append("<h4>Events Added</h4><ul>")
        for ev in delta.events.add:
            parts.append(
                f"<li><span class='mono'>{_esc(ev.claim_event_id)}</span> "
                f"— {_esc(ev.content[:120])}</li>"
            )
        parts.append("</ul>")

    # Open items added
    if delta.open_items.add:
        parts.append("<h4>Open Items Added</h4>")
        parts.append(_render_todo_table(delta.open_items.add, ""))

    # Open items deleted (moved to closed)
    if delta.open_items.delete:
        parts.append("<h4>Open Items Removed</h4><ul class='delete-list'>")
        for item_id in delta.open_items.delete:
            parts.append(f"<li><span class='mono'>{_esc(item_id)}</span></li>")
        parts.append("</ul>")

    # Closed items added
    if delta.closed_items.add:
        parts.append("<h4>Closed/Cancelled Items Added</h4>")
        parts.append(_render_todo_table(delta.closed_items.add, ""))

    # Open items updated
    if delta.open_items.update:
        parts.append("<h4>Open Items Updated</h4>")
        parts.append(_render_todo_table(delta.open_items.update, ""))

    if not parts:
        parts.append("<p class='empty'>No changes in this delta.</p>")

    return "".join(parts)


def _render_state_section(state: ClaimState) -> str:
    parts = []
    parts.append("<h4>Events</h4><ul>")
    for ev in state.events:
        parts.append(
            f"<li><span class='mono'>{_esc(ev.claim_event_id)}</span> "
            f"<span class='ts'>{_fmt_dt(ev.timestamp)}</span> "
            f"— {_esc(ev.content[:120])}</li>"
        )
    parts.append("</ul>")

    parts.append(f"<h4>Open Items ({len(state.open_items)})</h4>")
    parts.append(_render_todo_table(state.open_items, "Open items"))

    parts.append(f"<h4>Closed Items ({len(state.closed_items)})</h4>")
    parts.append(_render_todo_table(state.closed_items, "Closed items"))

    return "".join(parts)


def render_html(
    events: list[ClaimEvent],
    deltas: list[ClaimStateDelta],
    states: list[ClaimState],
) -> str:
    """Render a full HTML report showing event-by-event deltas and claim state."""
    event_sections = []
    for i, (event, delta, state) in enumerate(zip(events, deltas, states)):
        event_sections.append(
            f"""
            <div class="event-card">
                <div class="event-header" onclick="toggleSection('evt-{i}')">
                    <span class="event-id">{_esc(event.claim_event_id)}</span>
                    <span class="event-ts">{_fmt_dt(event.timestamp)}</span>
                    <span class="toggle" id="toggle-evt-{i}">&#9660;</span>
                </div>
                <div class="event-content">{_esc(event.content)}</div>
                <div class="event-body" id="evt-{i}">
                    <div class="split">
                        <div class="panel delta-panel">
                            <h3>Delta</h3>
                            {_render_delta_section(delta)}
                        </div>
                        <div class="panel state-panel">
                            <h3>State After</h3>
                            {_render_state_section(state)}
                        </div>
                    </div>
                </div>
            </div>
            """
        )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Claim State Delta Report</title>
<style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        background: #f0f2f5; color: #1a1a2e; padding: 24px;
        line-height: 1.5;
    }}
    h1 {{
        font-size: 1.6rem; margin-bottom: 24px; color: #1a1a2e;
        border-bottom: 2px solid #3a86ff; padding-bottom: 8px; display: inline-block;
    }}
    .event-card {{
        background: #fff; border-radius: 8px; margin-bottom: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1); overflow: hidden;
    }}
    .event-header {{
        display: flex; align-items: center; gap: 12px;
        padding: 12px 16px; background: #1a1a2e; color: #fff;
        cursor: pointer; user-select: none;
    }}
    .event-header:hover {{ background: #2a2a4e; }}
    .event-id {{
        font-family: 'Consolas', 'Fira Code', monospace;
        font-weight: 600; font-size: 0.95rem;
        background: rgba(255,255,255,0.15); padding: 2px 8px; border-radius: 4px;
    }}
    .event-ts {{ color: #a0a0c0; font-size: 0.85rem; }}
    .toggle {{ margin-left: auto; font-size: 0.8rem; transition: transform 0.2s; }}
    .toggle.collapsed {{ transform: rotate(-90deg); }}
    .event-content {{
        padding: 12px 16px; background: #f8f9fb; border-bottom: 1px solid #e4e7ec;
        font-size: 0.93rem; color: #444;
    }}
    .event-body {{ padding: 0; }}
    .event-body.hidden {{ display: none; }}
    .split {{ display: grid; grid-template-columns: 1fr 1fr; }}
    .panel {{ padding: 16px; overflow-x: auto; }}
    .delta-panel {{ background: #fefce8; border-right: 1px solid #e4e7ec; }}
    .state-panel {{ background: #f0fdf4; }}
    .panel h3 {{
        font-size: 0.95rem; margin-bottom: 12px; text-transform: uppercase;
        letter-spacing: 0.05em; color: #666;
    }}
    .panel h4 {{ font-size: 0.85rem; margin: 12px 0 6px; color: #333; }}
    .panel h4:first-child {{ margin-top: 0; }}
    table {{
        width: 100%; border-collapse: collapse; font-size: 0.82rem;
        margin-bottom: 8px;
    }}
    th {{
        text-align: left; padding: 6px 8px; background: rgba(0,0,0,0.05);
        font-weight: 600; font-size: 0.78rem; text-transform: uppercase;
        letter-spacing: 0.03em; color: #555; border-bottom: 2px solid #ddd;
    }}
    td {{ padding: 6px 8px; border-bottom: 1px solid #eee; vertical-align: top; }}
    .mono {{ font-family: 'Consolas', 'Fira Code', monospace; font-size: 0.82rem; }}
    .ts {{ color: #888; font-size: 0.82rem; }}
    .empty {{ color: #999; font-style: italic; font-size: 0.85rem; }}
    ul {{ padding-left: 20px; font-size: 0.88rem; }}
    li {{ margin-bottom: 4px; }}
    .delete-list li {{ color: #b91c1c; }}

    .badge {{
        display: inline-block; padding: 1px 7px; border-radius: 3px;
        font-size: 0.75rem; font-weight: 600; text-transform: uppercase;
        letter-spacing: 0.03em;
    }}
    .badge-treatment   {{ background: #dbeafe; color: #1e40af; }}
    .badge-employment  {{ background: #fef3c7; color: #92400e; }}
    .badge-financial   {{ background: #d1fae5; color: #065f46; }}
    .badge-compliance  {{ background: #ede9fe; color: #5b21b6; }}
    .badge-litigation  {{ background: #fee2e2; color: #991b1b; }}
    .badge-open        {{ background: #dbeafe; color: #1e40af; }}
    .badge-closed      {{ background: #d1fae5; color: #065f46; }}
    .badge-cancelled   {{ background: #fef3c7; color: #92400e; }}

    .filter-bar {{
        display: flex; flex-wrap: wrap; gap: 12px; align-items: center;
        margin-bottom: 16px; padding: 10px 16px;
        background: #fff; border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }}
    .filter-bar .filter-title {{
        font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.05em;
        color: #666; font-weight: 600; margin-right: 4px;
    }}
    .filter-btn {{
        border: 2px solid transparent; border-radius: 6px; padding: 4px 10px;
        cursor: pointer; background: #e5e7eb; font-size: 0.82rem;
        font-weight: 600; transition: opacity 0.15s, border-color 0.15s;
    }}
    .filter-btn.active {{ border-color: #3a86ff; opacity: 1; }}
    .filter-btn:not(.active) {{ opacity: 0.4; }}
    .filter-btn:hover {{ opacity: 0.85; }}

    @media (max-width: 900px) {{
        .split {{ grid-template-columns: 1fr; }}
        .delta-panel {{ border-right: none; border-bottom: 1px solid #e4e7ec; }}
    }}
</style>
</head>
<body>
<h1>Claim State Delta Report</h1>
<div class="filter-bar">
    <span class="filter-title">Categories:</span>
    <button class="filter-btn active" data-cat="all" onclick="filterCat('all')">All</button>
    <button class="filter-btn active" data-cat="treatment" onclick="filterCat('treatment')">
        <span class="badge badge-treatment">Treatment</span></button>
    <button class="filter-btn active" data-cat="employment" onclick="filterCat('employment')">
        <span class="badge badge-employment">Employment</span></button>
    <button class="filter-btn active" data-cat="financial" onclick="filterCat('financial')">
        <span class="badge badge-financial">Financial</span></button>
    <button class="filter-btn active" data-cat="compliance" onclick="filterCat('compliance')">
        <span class="badge badge-compliance">Compliance</span></button>
    <button class="filter-btn active" data-cat="litigation" onclick="filterCat('litigation')">
        <span class="badge badge-litigation">Litigation</span></button>
</div>
{"".join(event_sections)}
<script>
function toggleSection(id) {{
    const el = document.getElementById(id);
    const toggle = document.getElementById('toggle-' + id);
    el.classList.toggle('hidden');
    toggle.classList.toggle('collapsed');
}}
function filterCat(cat) {{
    const btns = document.querySelectorAll('.filter-btn');
    const allBtn = document.querySelector('.filter-btn[data-cat="all"]');
    const catBtns = Array.from(document.querySelectorAll('.filter-btn:not([data-cat="all"])'));

    if (cat === 'all') {{
        // If all are already active, do nothing; otherwise activate all
        catBtns.forEach(b => b.classList.add('active'));
        allBtn.classList.add('active');
    }} else {{
        const clicked = document.querySelector(`.filter-btn[data-cat="${{cat}}"]`);
        const activeNonAll = catBtns.filter(b => b.classList.contains('active'));

        // If everything is active (or "All" is on), solo this category
        // If only this one is active, go back to all
        // Otherwise toggle this category
        if (allBtn.classList.contains('active') || activeNonAll.length === catBtns.length) {{
            catBtns.forEach(b => b.classList.remove('active'));
            allBtn.classList.remove('active');
            clicked.classList.add('active');
        }} else if (activeNonAll.length === 1 && clicked.classList.contains('active')) {{
            catBtns.forEach(b => b.classList.add('active'));
            allBtn.classList.add('active');
        }} else {{
            clicked.classList.toggle('active');
            const nowActive = catBtns.filter(b => b.classList.contains('active'));
            if (nowActive.length === catBtns.length) {{
                allBtn.classList.add('active');
            }} else {{
                allBtn.classList.remove('active');
            }}
        }}
    }}

    const active = new Set(
        catBtns.filter(b => b.classList.contains('active')).map(b => b.dataset.cat)
    );
    document.querySelectorAll('tr[data-category]').forEach(row => {{
        row.style.display = active.has(row.dataset.category) ? '' : 'none';
    }});
}}
</script>
</body>
</html>"""
