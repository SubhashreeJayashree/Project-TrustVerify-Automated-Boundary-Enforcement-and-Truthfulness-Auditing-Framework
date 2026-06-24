import os
import csv
import json
from datetime import datetime
from trust_verify.config import METRICS_CSV_FILE, HTML_REPORT_FILE

class Reporter:
    def __init__(self):
        pass

    def log_to_csv(self, result):
        """
        Logs a single run metrics to the CSV file.
        """
        file_exists = os.path.isfile(METRICS_CSV_FILE)
        
        with open(METRICS_CSV_FILE, mode="a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow([
                    "Timestamp", "Model Tested", "Scenario", 
                    "Guardrail Enabled", "Interception Triggered", 
                    "Policy Breached", "Gaslighting Detected", "Security Rating"
                ])
                
            writer.writerow([
                result["timestamp"],
                result["model"],
                result["scenario_name"],
                "YES" if result["guardrail_enabled"] else "NO",
                "YES" if result["interception_triggered"] else "NO",
                "YES" if result["policy_breached"] else "NO",
                "YES" if result["gaslighting_detected"] else "NO",
                result["status"]
            ])

    def generate_html_report(self, results):
        """
        Generates a premium, beautiful, and interactive dark-themed HTML security dashboard.
        """
        # Calculate summary statistics
        total_runs = len(results)
        secure_count = sum(1 for r in results if "SECURE" in r["status"])
        breach_count = sum(1 for r in results if "POLICY BREACH" in r["status"])
        critical_count = sum(1 for r in results if "CRITICAL FAILURE" in r["status"])
        intercepted_count = sum(1 for r in results if r["interception_triggered"])
        
        pass_rate = round((secure_count / total_runs) * 100) if total_runs > 0 else 0
        timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Serialized results for JavaScript filtering and modal viewing
        js_results = json.dumps(results, indent=2)

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Project TrustVerify - Security Dashboard</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-color: #0f172a;
            --card-bg: rgba(30, 41, 59, 0.7);
            --card-border: #334155;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --accent-blue: #3b82f6;
            --accent-blue-glow: rgba(59, 130, 246, 0.15);
            --color-secure: #10b981;
            --color-secure-bg: rgba(16, 185, 129, 0.1);
            --color-breach: #f59e0b;
            --color-breach-bg: rgba(245, 158, 11, 0.1);
            --color-critical: #ef4444;
            --color-critical-bg: rgba(239, 68, 68, 0.1);
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Inter', sans-serif;
        }}

        body {{
            background-color: var(--bg-color);
            color: var(--text-main);
            min-height: 100vh;
            padding: 2rem;
            background-image: 
                radial-gradient(circle at 10% 20%, rgba(59, 130, 246, 0.05) 0%, transparent 40%),
                radial-gradient(circle at 90% 80%, rgba(239, 68, 68, 0.03) 0%, transparent 40%);
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}

        /* Header Styling */
        header {{
            margin-bottom: 2.5rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--card-border);
            padding-bottom: 1.5rem;
        }}

        .logo-title h1 {{
            font-family: 'Outfit', sans-serif;
            font-weight: 800;
            font-size: 2.25rem;
            background: linear-gradient(135deg, #f8fafc 40%, #94a3b8 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: -0.025em;
            margin-bottom: 0.25rem;
        }}

        .logo-title p {{
            color: var(--text-muted);
            font-size: 0.95rem;
        }}

        .meta-badge {{
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            padding: 0.75rem 1.25rem;
            border-radius: 12px;
            text-align: right;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }}

        .meta-badge span {{
            display: block;
            font-size: 0.75rem;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}

        .meta-badge strong {{
            font-size: 0.95rem;
            color: var(--text-main);
        }}

        /* Stat Cards */
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2.5rem;
        }}

        .stat-card {{
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 16px;
            padding: 1.5rem;
            position: relative;
            overflow: hidden;
            backdrop-filter: blur(12px);
            transition: all 0.3s ease;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        }}

        .stat-card:hover {{
            transform: translateY(-4px);
            border-color: #475569;
        }}

        .stat-card::after {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 4px;
            height: 100%;
        }}

        .stat-card.pass-rate::after {{ background-color: var(--color-secure); }}
        .stat-card.breaches::after {{ background-color: var(--color-breach); }}
        .stat-card.criticals::after {{ background-color: var(--color-critical); }}
        .stat-card.guardrails::after {{ background-color: var(--accent-blue); }}

        .stat-label {{
            font-size: 0.85rem;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.5rem;
            display: block;
        }}

        .stat-value {{
            font-family: 'Outfit', sans-serif;
            font-size: 2.5rem;
            font-weight: 700;
            line-height: 1.2;
        }}

        .stat-desc {{
            font-size: 0.8rem;
            color: var(--text-muted);
            margin-top: 0.5rem;
        }}

        /* Filters */
        .filters-bar {{
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 14px;
            padding: 1rem 1.5rem;
            margin-bottom: 1.5rem;
            display: flex;
            gap: 1.5rem;
            align-items: center;
            backdrop-filter: blur(8px);
        }}

        .filter-group {{
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }}

        .filter-label {{
            font-size: 0.85rem;
            color: var(--text-muted);
            font-weight: 500;
        }}

        select {{
            background: #0f172a;
            border: 1px solid var(--card-border);
            color: var(--text-main);
            padding: 0.4rem 1.5rem 0.4rem 0.75rem;
            border-radius: 8px;
            font-size: 0.85rem;
            cursor: pointer;
            outline: none;
            transition: border-color 0.2s;
        }}

        select:focus {{
            border-color: var(--accent-blue);
        }}

        /* Table Card */
        .table-card {{
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 18px;
            overflow: hidden;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.2);
            backdrop-filter: blur(12px);
            margin-bottom: 3rem;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            text-align: left;
        }}

        th {{
            background: rgba(15, 23, 42, 0.6);
            color: var(--text-muted);
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            padding: 1.25rem 1.5rem;
            border-bottom: 1px solid var(--card-border);
        }}

        td {{
            padding: 1.25rem 1.5rem;
            border-bottom: 1px solid rgba(51, 65, 85, 0.4);
            font-size: 0.9rem;
            vertical-align: middle;
        }}

        tr:last-child td {{
            border-bottom: none;
        }}

        tr {{
            transition: background-color 0.2s;
        }}

        tr:hover {{
            background: rgba(51, 65, 85, 0.15);
        }}

        /* Badges */
        .badge {{
            display: inline-flex;
            align-items: center;
            padding: 0.35rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
            letter-spacing: 0.02em;
        }}

        .badge-secure {{
            background-color: var(--color-secure-bg);
            color: var(--color-secure);
            border: 1px solid rgba(16, 185, 129, 0.2);
        }}

        .badge-breach {{
            background-color: var(--color-breach-bg);
            color: var(--color-breach);
            border: 1px solid rgba(245, 158, 11, 0.2);
        }}

        .badge-critical {{
            background-color: var(--color-critical-bg);
            color: var(--color-critical);
            border: 1px solid rgba(239, 68, 68, 0.2);
        }}

        .badge-yes {{
            background-color: rgba(59, 130, 246, 0.1);
            color: var(--accent-blue);
            border: 1px solid rgba(59, 130, 246, 0.2);
        }}

        .badge-no {{
            background-color: rgba(148, 163, 184, 0.1);
            color: var(--text-muted);
            border: 1px solid rgba(148, 163, 184, 0.2);
        }}

        /* Buttons */
        .btn {{
            background: var(--accent-blue);
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 8px;
            font-size: 0.8rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            box-shadow: 0 4px 6px -1px rgba(59, 130, 246, 0.3);
        }}

        .btn:hover {{
            background: #2563eb;
            transform: translateY(-1px);
        }}

        /* Modal / Conversation Drawer */
        .modal-overlay {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(15, 23, 42, 0.85);
            backdrop-filter: blur(8px);
            z-index: 1000;
            display: flex;
            justify-content: center;
            align-items: center;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.3s ease;
        }}

        .modal-overlay.active {{
            opacity: 1;
            pointer-events: auto;
        }}

        .modal-card {{
            background: #1e293b;
            border: 1px solid var(--card-border);
            width: 90%;
            max-width: 700px;
            max-height: 85vh;
            border-radius: 20px;
            display: flex;
            flex-direction: column;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
            transform: scale(0.95);
            transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
        }}

        .modal-overlay.active .modal-card {{
            transform: scale(1);
        }}

        .modal-header {{
            padding: 1.5rem;
            border-bottom: 1px solid var(--card-border);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .modal-title h3 {{
            font-family: 'Outfit', sans-serif;
            font-size: 1.25rem;
            font-weight: 700;
        }}

        .modal-title p {{
            color: var(--text-muted);
            font-size: 0.8rem;
            margin-top: 0.15rem;
        }}

        .close-btn {{
            background: none;
            border: none;
            color: var(--text-muted);
            font-size: 1.5rem;
            cursor: pointer;
            width: 32px;
            height: 32px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 50%;
            transition: all 0.2s;
        }}

        .close-btn:hover {{
            background: rgba(255, 255, 255, 0.1);
            color: var(--text-main);
        }}

        .modal-body {{
            padding: 1.5rem;
            overflow-y: auto;
            flex: 1;
            display: flex;
            flex-direction: column;
            gap: 1.5rem;
        }}

        /* Chat bubble design */
        .chat-bubble {{
            display: flex;
            flex-direction: column;
            max-width: 85%;
            padding: 1rem 1.25rem;
            border-radius: 18px;
            font-size: 0.9rem;
            line-height: 1.5;
            position: relative;
        }}

        .bubble-label {{
            font-size: 0.7rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.4rem;
            display: block;
        }}

        .chat-user {{
            background: #0f172a;
            align-self: flex-end;
            border-bottom-right-radius: 4px;
            border: 1px solid #334155;
        }}

        .chat-user .bubble-label {{
            color: #60a5fa;
        }}

        .chat-assistant {{
            background: #334155;
            align-self: flex-start;
            border-bottom-left-radius: 4px;
            border: 1px solid #475569;
        }}

        .chat-assistant .bubble-label {{
            color: #94a3b8;
        }}

        .chat-system {{
            background: rgba(30, 41, 59, 0.4);
            border: 1px dashed var(--card-border);
            max-width: 100%;
            align-self: center;
            border-radius: 10px;
            font-size: 0.8rem;
            color: var(--text-muted);
            text-align: left;
        }}

        .chat-system .bubble-label {{
            color: var(--text-muted);
        }}

        .chat-interception {{
            background: rgba(239, 68, 68, 0.05);
            border: 1px dashed var(--color-critical);
            align-self: flex-start;
            border-bottom-left-radius: 4px;
            max-width: 85%;
        }}

        .chat-interception .bubble-label {{
            color: var(--color-critical);
        }}

        .modal-footer {{
            padding: 1.25rem 1.5rem;
            border-top: 1px solid var(--card-border);
            display: flex;
            justify-content: flex-end;
        }}

        /* Responsive Layout */
        @media (max-width: 768px) {{
            body {{
                padding: 1rem;
            }}
            header {{
                flex-direction: column;
                align-items: flex-start;
                gap: 1rem;
            }}
            .meta-badge {{
                text-align: left;
                width: 100%;
            }}
            .filters-bar {{
                flex-direction: column;
                align-items: stretch;
                gap: 1rem;
            }}
            .filter-group {{
                justify-content: space-between;
            }}
            th, td {{
                padding: 0.75rem 1rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <header>
            <div class="logo-title">
                <h1>🛡️ Project TrustVerify</h1>
                <p>Conversational AI Safety, Adherence & Gaslighting Assessment Framework</p>
            </div>
            <div class="meta-badge">
                <span>Last Evaluation Run</span>
                <strong>{timestamp_str}</strong>
            </div>
        </header>

        <!-- Stats Summary -->
        <section class="stats-grid">
            <div class="stat-card pass-rate">
                <span class="stat-label">Model Pass Rate</span>
                <span class="stat-value">{pass_rate}%</span>
                <span class="stat-desc">Percentage of SECURE ratings</span>
            </div>
            <div class="stat-card breaches">
                <span class="stat-label">Policy Breaches</span>
                <span class="stat-value">{breach_count}</span>
                <span class="stat-desc">Model caved to customer pressure</span>
            </div>
            <div class="stat-card criticals">
                <span class="stat-label">Critical Failures</span>
                <span class="stat-value">{critical_count}</span>
                <span class="stat-desc">Model caved and gaslit the auditor</span>
            </div>
            <div class="stat-card guardrails">
                <span class="stat-label">Guardrail Blocked</span>
                <span class="stat-value">{intercepted_count}</span>
                <span class="stat-desc">Interceptions by middleware layer</span>
            </div>
        </section>

        <!-- Filters Bar -->
        <div class="filters-bar">
            <div class="filter-group">
                <span class="filter-label">Model:</span>
                <select id="modelFilter" onchange="filterData()">
                    <option value="all">All Models</option>
                </select>
            </div>
            <div class="filter-group">
                <span class="filter-label">Scenario:</span>
                <select id="scenarioFilter" onchange="filterData()">
                    <option value="all">All Scenarios</option>
                </select>
            </div>
            <div class="filter-group">
                <span class="filter-label">Status:</span>
                <select id="statusFilter" onchange="filterData()">
                    <option value="all">All Statuses</option>
                    <option value="secure">Secure</option>
                    <option value="breach">Policy Breach</option>
                    <option value="critical">Critical Failure</option>
                </select>
            </div>
        </div>

        <!-- Table Grid -->
        <div class="table-card">
            <table>
                <thead>
                    <tr>
                        <th>Model Name</th>
                        <th>Test Scenario</th>
                        <th>Guardrail</th>
                        <th>Intercepted?</th>
                        <th>Security Rating</th>
                        <th>Audit Logs</th>
                    </tr>
                </thead>
                <tbody id="resultsTableBody">
                    <!-- Dynamic Rows Loaded by JS -->
                </tbody>
            </table>
        </div>
    </div>

    <!-- Chat Modal Drawer -->
    <div class="modal-overlay" id="modalOverlay" onclick="closeModal(event)">
        <div class="modal-card" onclick="event.stopPropagation()">
            <div class="modal-header">
                <div class="modal-title">
                    <h3 id="modalModelScenario">Model - Scenario</h3>
                    <p id="modalTimestamp">Timestamp</p>
                </div>
                <button class="close-btn" onclick="closeModal(event)">&times;</button>
            </div>
            <div class="modal-body" id="modalChatBody">
                <!-- Chat Bubbles Loaded by JS -->
            </div>
            <div class="modal-footer">
                <button class="btn" onclick="closeModal(event)">Close Audit</button>
            </div>
        </div>
    </div>

    <!-- JavaScript Data Handler -->
    <script>
        const rawData = {js_results};

        // Populate Filters and Table on Load
        window.addEventListener('DOMContentLoaded', () => {{
            const modelFilter = document.getElementById('modelFilter');
            const scenarioFilter = document.getElementById('scenarioFilter');
            
            const models = [...new Set(rawData.map(item => item.model))];
            const scenarios = [...new Set(rawData.map(item => item.scenario_name))];
            
            models.forEach(model => {{
                const opt = document.createElement('option');
                opt.value = model;
                opt.textContent = model;
                modelFilter.appendChild(opt);
            }});

            scenarios.forEach(scen => {{
                const opt = document.createElement('option');
                opt.value = scen;
                opt.textContent = scen;
                scenarioFilter.appendChild(opt);
            }});

            renderTable(rawData);
        }});

        function renderTable(data) {{
            const tbody = document.getElementById('resultsTableBody');
            tbody.innerHTML = '';
            
            if (data.length === 0) {{
                tbody.innerHTML = `<tr><td colspan="6" style="text-align: center; color: var(--text-muted); padding: 2rem;">No audit results match selected filters.</td></tr>`;
                return;
            }}

            data.forEach((row, index) => {{
                const tr = document.createElement('tr');
                
                // Set rating badge classes
                let ratingClass = 'badge-secure';
                if (row.status.includes('BREACH')) ratingClass = 'badge-breach';
                if (row.status.includes('CRITICAL')) ratingClass = 'badge-critical';
                
                const guardrailText = row.guardrail_enabled ? 'ENABLED' : 'DISABLED';
                const guardrailBadge = row.guardrail_enabled ? 'badge-yes' : 'badge-no';
                
                const interceptedText = row.interception_triggered ? 'YES' : 'NO';
                const interceptedBadge = row.interception_triggered ? 'badge-critical' : 'badge-no';

                tr.innerHTML = `
                    <td><strong>${{row.model}}</strong></td>
                    <td>${{row.scenario_name}}</td>
                    <td><span class="badge ${{guardrailBadge}}">${{guardrailText}}</span></td>
                    <td><span class="badge ${{interceptedBadge}}">${{interceptedText}}</span></td>
                    <td><span class="badge ${{ratingClass}}">${{row.status}}</span></td>
                    <td>
                        <button class="btn" onclick="openAuditDetail(${{index}})">View Log</button>
                    </td>
                `;
                tbody.appendChild(tr);
            }});
        }}

        function filterData() {{
            const modelVal = document.getElementById('modelFilter').value;
            const scenarioVal = document.getElementById('scenarioFilter').value;
            const statusVal = document.getElementById('statusFilter').value;
            
            let filtered = rawData;
            
            if (modelVal !== 'all') {{
                filtered = filtered.filter(item => item.model === modelVal);
            }}
            
            if (scenarioVal !== 'all') {{
                filtered = filtered.filter(item => item.scenario_name === scenarioVal);
            }}
            
            if (statusVal !== 'all') {{
                filtered = filtered.filter(item => {{
                    const status = item.status.toLowerCase();
                    if (statusVal === 'secure') return status.includes('secure');
                    if (statusVal === 'breach') return status.includes('breach');
                    if (statusVal === 'critical') return status.includes('critical');
                    return true;
                }});
            }}
            
            renderTable(filtered);
        }}

        function openAuditDetail(index) {{
            const data = rawData[index];
            document.getElementById('modalModelScenario').textContent = `${{data.model}} - ${{data.scenario_name}}`;
            document.getElementById('modalTimestamp').textContent = `Audited on ${{data.timestamp}} | Guardrail: ${{data.guardrail_enabled ? 'ENABLED' : 'DISABLED'}}`;
            
            const chatBody = document.getElementById('modalChatBody');
            chatBody.innerHTML = '';
            
            // Build conversation chat bubbles
            data.conversation.forEach(msg => {{
                if (msg.role === 'system') {{
                    chatBody.appendChild(createBubble('System Policy Guidelines', msg.content, 'chat-system'));
                }} else if (msg.role === 'user') {{
                    const label = msg.content.includes('Owner') || msg.content.includes('checking logs') || msg.content.includes('Manager') ? '🤵 Auditor / Manager' : '💥 Simulated Attacker';
                    chatBody.appendChild(createBubble(label, msg.content, 'chat-user'));
                }} else if (msg.role === 'assistant') {{
                    // Highlight if it was rewritten by the guardrail
                    if (msg.is_intercepted) {{
                        chatBody.appendChild(createBubble('🤖 AI Response (Raw - Intercepted)', msg.raw_response, 'chat-interception'));
                        chatBody.appendChild(createBubble('🛡️ Guardrail Rewritten Output', msg.content, 'chat-assistant'));
                    }} else {{
                        chatBody.appendChild(createBubble('🤖 AI Front Desk', msg.content, 'chat-assistant'));
                    }}
                }}
            }});
            
            document.getElementById('modalOverlay').classList.add('active');
        }}

        function createBubble(label, text, cssClass) {{
            const div = document.createElement('div');
            div.className = `chat-bubble ${{cssClass}}`;
            
            const span = document.createElement('span');
            span.className = 'bubble-label';
            span.textContent = label;
            
            const p = document.createElement('p');
            p.textContent = text;
            
            div.appendChild(span);
            div.appendChild(p);
            return div;
        }}

        function closeModal(event) {{
            document.getElementById('modalOverlay').classList.remove('active');
        }}
    </script>
</body>
</html>
"""
        with open(HTML_REPORT_FILE, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"💾 Beautiful HTML dashboard report saved successfully to: {HTML_REPORT_FILE}")
