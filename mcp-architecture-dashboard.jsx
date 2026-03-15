import { useState } from "react";

const VENDORS = {
  prisma: {
    name: "Prisma Access",
    subtitle: "Strata Cloud Manager",
    color: "#F97316",
    accent: "#FB923C",
    bg: "#431407",
    icon: "🛡️",
    phase: 1,
    weeks: "1–3",
    gap: "None exist",
    gapLevel: "critical",
    maturity: 0,
    sdk: "pan-scm-sdk",
    sdkLang: "Python",
    auth: "OAuth2 Client Credentials",
    authDetail: "15-min token TTL → proactive refresh at 13 min",
    rateLimit: "Undocumented (token TTL is primary constraint)",
    apiBase: "api.strata.paloaltonetworks.com",
    commitModel: "Candidate → Push (async job)",
    uniqueChallenge: "Commit model requires explicit push; never auto-commit",
    tools: {
      tier1: [
        { name: "prisma_list_security_rules", desc: "Security policy rules by folder", type: "read" },
        { name: "prisma_list_nat_rules", desc: "NAT policy visibility", type: "read" },
        { name: "prisma_list_addresses", desc: "Address objects for rule analysis", type: "read" },
        { name: "prisma_list_security_profiles", desc: "Anti-spyware, WildFire, DNS profiles", type: "read" },
        { name: "prisma_list_url_categories", desc: "URL filtering config", type: "read" },
        { name: "prisma_list_edls", desc: "External dynamic lists / threat feeds", type: "read" },
      ],
      tier2: [
        { name: "prisma_list_remote_networks", desc: "Remote network configurations", type: "read" },
        { name: "prisma_list_service_connections", desc: "Service connection status", type: "read" },
        { name: "prisma_list_bandwidth_alloc", desc: "Bandwidth across locations", type: "read" },
        { name: "prisma_get_job", desc: "Config push job monitoring", type: "read" },
      ],
      tier3: [
        { name: "prisma_create_security_rule", desc: "Rule CRUD operations", type: "write" },
        { name: "prisma_move_security_rule", desc: "Rule reordering", type: "write" },
        { name: "prisma_push_candidate_config", desc: "Explicit commit action", type: "write" },
        { name: "prisma_create_address", desc: "Object creation", type: "write" },
      ],
    },
  },
  meraki: {
    name: "Cisco Meraki",
    subtitle: "Dashboard API v1",
    color: "#06B6D4",
    accent: "#22D3EE",
    bg: "#083344",
    icon: "🌐",
    phase: 2,
    weeks: "3–5",
    gap: "4+ community servers",
    gapLevel: "covered",
    maturity: 4,
    sdk: "meraki (official)",
    sdkLang: "Python",
    auth: "API Key or OAuth2",
    authDetail: "Key: no expiry; OAuth: 60-min tokens with refresh",
    rateLimit: "10 req/s per org (token bucket + burst)",
    apiBase: "api.meraki.com/api/v1",
    commitModel: "Immediate (no staging)",
    uniqueChallenge: "1,225 endpoints; rate limiting is the primary constraint",
    tools: {
      tier1: [
        { name: "meraki_get_device_availabilities", desc: "Org-wide device up/down", type: "read" },
        { name: "meraki_get_uplink_loss_latency", desc: "WAN health across MX appliances", type: "read" },
        { name: "meraki_get_network_events", desc: "Event log search", type: "read" },
        { name: "meraki_get_vpn_statuses", desc: "Site-to-site VPN health", type: "read" },
        { name: "meraki_get_switch_port_statuses", desc: "Per-switch diagnostics", type: "read" },
        { name: "meraki_get_clients", desc: "Client connectivity data", type: "read" },
      ],
      tier2: [
        { name: "meraki_ping_device", desc: "Ping from Meraki device", type: "read" },
        { name: "meraki_traceroute_device", desc: "Traceroute from device", type: "read" },
        { name: "meraki_cable_test", desc: "Physical layer diagnostics", type: "read" },
        { name: "meraki_get_config_changes", desc: "Audit trail of changes", type: "read" },
      ],
      tier3: [
        { name: "meraki_update_ssid", desc: "SSID configuration", type: "write" },
        { name: "meraki_update_switch_port", desc: "Port configuration", type: "write" },
        { name: "meraki_update_firewall_rules", desc: "L3/L7 firewall rules", type: "write" },
        { name: "meraki_create_action_batch", desc: "Bulk config via action batches", type: "write" },
      ],
    },
  },
  mist: {
    name: "Juniper Mist",
    subtitle: "Cloud REST API",
    color: "#A855F7",
    accent: "#C084FC",
    bg: "#2E1065",
    icon: "📡",
    phase: 3,
    weeks: "5–7",
    gap: "2 early-stage servers",
    gapLevel: "partial",
    maturity: 2,
    sdk: "mistapi",
    sdkLang: "Python",
    auth: "Static API Token",
    authDetail: "No expiry; org-level or user-level tokens",
    rateLimit: "5,000 req/hour per token",
    apiBase: "api.mist.com/api/v1 (5 regions)",
    commitModel: "Immediate (no staging)",
    uniqueChallenge: "5 regional endpoints; SLE metrics are the key differentiator",
    tools: {
      tier1: [
        { name: "mist_get_device_stats", desc: "AP/switch/gateway health", type: "read" },
        { name: "mist_get_sle_summary", desc: "AI-driven SLE metrics (Marvis)", type: "read" },
        { name: "mist_get_client_stats", desc: "Client connectivity data", type: "read" },
        { name: "mist_search_org_devices", desc: "Fleet-wide device discovery", type: "read" },
        { name: "mist_get_alarms", desc: "Active + Marvis anomaly alerts", type: "read" },
        { name: "mist_get_site_events", desc: "Event logs for forensics", type: "read" },
      ],
      tier2: [
        { name: "mist_list_wlans", desc: "WLAN profile listing", type: "read" },
        { name: "mist_get_inventory", desc: "Device lifecycle management", type: "read" },
        { name: "mist_get_rf_templates", desc: "RF template configs", type: "read" },
        { name: "mist_get_device_config_cmd", desc: "Generated CLI config", type: "read" },
      ],
      tier3: [
        { name: "mist_update_wlan", desc: "WLAN profile changes", type: "write" },
        { name: "mist_manage_nac_rules", desc: "802.1X / Access Assurance", type: "write" },
        { name: "mist_manage_wxlan", desc: "Microsegmentation policies", type: "write" },
        { name: "mist_manage_security_policies", desc: "WAN security for SRX/SSR", type: "write" },
      ],
    },
  },
};

const ARCH_LAYERS = [
  { label: "LLM Agent", sub: "Claude / GPT / Codex", color: "#818CF8", icon: "🤖" },
  { label: "MCP Protocol", sub: "stdio | streamable-http", color: "#60A5FA", icon: "🔌" },
  { label: "FastMCP Server", sub: "Python 3.11+ / FastMCP ≥2.5.1", color: "#34D399", icon: "⚡" },
  { label: "Tool Functions", sub: "@mcp.tool() decorators", color: "#FBBF24", icon: "🔧" },
  { label: "Vendor SDK", sub: "meraki / mistapi / pan-scm-sdk", color: "#F472B6", icon: "📦" },
  { label: "REST API", sub: "Vendor cloud endpoints", color: "#FB923C", icon: "🌍" },
];

const SAFETY_LAYERS = [
  { num: "1", label: "Read-only Default", desc: "Only list_* and get_* tools registered at startup", color: "#22C55E" },
  { num: "2", label: "Explicit Write Enable", desc: "--enable-write-tools --write-tools \"pattern\"", color: "#EAB308" },
  { num: "3", label: "Destructive Hints", desc: "destructiveHint=True triggers LLM permission dialog", color: "#F97316" },
  { num: "4", label: "Platform Safety", desc: "Prisma: no auto-commit · Meraki: action batch review · Mist: template validation", color: "#EF4444" },
];

function GapBadge({ level }) {
  const styles = {
    critical: { bg: "rgba(239,68,68,0.15)", border: "rgba(239,68,68,0.4)", text: "#FCA5A5", label: "NO MCP SERVER" },
    partial: { bg: "rgba(234,179,8,0.15)", border: "rgba(234,179,8,0.4)", text: "#FDE68A", label: "EARLY STAGE" },
    covered: { bg: "rgba(34,197,94,0.15)", border: "rgba(34,197,94,0.4)", text: "#86EFAC", label: "COMMUNITY" },
  };
  const s = styles[level];
  return (
    <span style={{ background: s.bg, border: `1px solid ${s.border}`, color: s.text, padding: "2px 8px", borderRadius: 4, fontSize: 10, fontWeight: 700, letterSpacing: "0.08em" }}>
      {s.label}
    </span>
  );
}

function ToolPill({ tool }) {
  const isWrite = tool.type === "write";
  return (
    <div style={{
      display: "flex", alignItems: "center", gap: 8, padding: "6px 10px",
      background: isWrite ? "rgba(239,68,68,0.08)" : "rgba(34,197,94,0.08)",
      border: `1px solid ${isWrite ? "rgba(239,68,68,0.2)" : "rgba(34,197,94,0.2)"}`,
      borderRadius: 6, fontSize: 12,
    }}>
      <span style={{
        width: 6, height: 6, borderRadius: "50%", flexShrink: 0,
        background: isWrite ? "#EF4444" : "#22C55E",
      }} />
      <code style={{ color: "#E2E8F0", fontFamily: "'JetBrains Mono', 'Fira Code', monospace", fontSize: 11, whiteSpace: "nowrap" }}>{tool.name}</code>
      <span style={{ color: "#94A3B8", fontSize: 11, marginLeft: "auto" }}>{tool.desc}</span>
    </div>
  );
}

export default function MCPDashboard() {
  const [activeTab, setActiveTab] = useState("overview");
  const [activeVendor, setActiveVendor] = useState("prisma");
  const vendor = VENDORS[activeVendor];

  const tabs = [
    { id: "overview", label: "Overview" },
    { id: "architecture", label: "Architecture" },
    { id: "vendors", label: "Vendor Deep Dive" },
    { id: "roadmap", label: "Roadmap" },
  ];

  return (
    <div style={{
      fontFamily: "'IBM Plex Sans', 'SF Pro Display', system-ui, sans-serif",
      background: "#0B0F1A",
      color: "#E2E8F0",
      minHeight: "100vh",
      overflow: "auto",
    }}>
      {/* Subtle grid pattern */}
      <div style={{
        position: "fixed", inset: 0, zIndex: 0, opacity: 0.03,
        backgroundImage: "linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)",
        backgroundSize: "40px 40px",
        pointerEvents: "none",
      }} />

      <div style={{ position: "relative", zIndex: 1, maxWidth: 1100, margin: "0 auto", padding: "24px 20px 60px" }}>
        {/* Header */}
        <div style={{ marginBottom: 32 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 6 }}>
            <div style={{
              width: 10, height: 10, borderRadius: "50%", background: "#22C55E",
              boxShadow: "0 0 8px rgba(34,197,94,0.6)",
              animation: "pulse 2s ease-in-out infinite",
            }} />
            <span style={{ fontSize: 11, color: "#94A3B8", fontWeight: 600, letterSpacing: "0.12em", textTransform: "uppercase" }}>
              Network Automation MCP Architecture
            </span>
          </div>
          <h1 style={{
            fontSize: 32, fontWeight: 800, margin: 0, lineHeight: 1.1,
            background: "linear-gradient(135deg, #E2E8F0 0%, #94A3B8 100%)",
            WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent",
          }}>
            MCP Server Blueprint
          </h1>
          <p style={{ color: "#64748B", fontSize: 14, margin: "8px 0 0", maxWidth: 600 }}>
            Building AI-native network orchestration for Juniper Mist, Cisco Meraki, and Palo Alto Prisma Access — using the Zscaler MCP server as the reference architecture.
          </p>
        </div>

        {/* Tab Nav */}
        <div style={{
          display: "flex", gap: 2, marginBottom: 28, background: "rgba(255,255,255,0.03)",
          borderRadius: 10, padding: 3, border: "1px solid rgba(255,255,255,0.06)",
          width: "fit-content",
        }}>
          {tabs.map(t => (
            <button key={t.id} onClick={() => setActiveTab(t.id)} style={{
              padding: "8px 18px", borderRadius: 8, border: "none", cursor: "pointer",
              fontSize: 13, fontWeight: 600, transition: "all 0.2s",
              background: activeTab === t.id ? "rgba(255,255,255,0.1)" : "transparent",
              color: activeTab === t.id ? "#F1F5F9" : "#64748B",
              boxShadow: activeTab === t.id ? "0 1px 3px rgba(0,0,0,0.3)" : "none",
            }}>
              {t.label}
            </button>
          ))}
        </div>

        {/* === OVERVIEW TAB === */}
        {activeTab === "overview" && (
          <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
            {/* Vendor Cards */}
            <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 16 }}>
              {Object.entries(VENDORS).map(([key, v]) => (
                <div key={key} style={{
                  background: `linear-gradient(135deg, ${v.bg} 0%, #0B0F1A 100%)`,
                  border: `1px solid ${v.color}33`,
                  borderRadius: 12, padding: 20, position: "relative", overflow: "hidden",
                  cursor: "pointer", transition: "all 0.2s",
                }} onClick={() => { setActiveVendor(key); setActiveTab("vendors"); }}>
                  <div style={{
                    position: "absolute", top: -20, right: -20, fontSize: 80, opacity: 0.06,
                  }}>{v.icon}</div>
                  <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 12 }}>
                    <span style={{ fontSize: 22 }}>{v.icon}</span>
                    <div>
                      <div style={{ fontSize: 16, fontWeight: 700, color: v.accent }}>{v.name}</div>
                      <div style={{ fontSize: 11, color: "#64748B" }}>{v.subtitle}</div>
                    </div>
                  </div>
                  <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 10 }}>
                    <GapBadge level={v.gapLevel} />
                    <span style={{ fontSize: 11, color: "#94A3B8" }}>{v.gap}</span>
                  </div>
                  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8, fontSize: 11 }}>
                    <div style={{ color: "#64748B" }}>SDK</div>
                    <div style={{ color: "#CBD5E1", fontFamily: "monospace", fontSize: 10 }}>{v.sdk}</div>
                    <div style={{ color: "#64748B" }}>Auth</div>
                    <div style={{ color: "#CBD5E1", fontSize: 10 }}>{v.auth}</div>
                    <div style={{ color: "#64748B" }}>Phase</div>
                    <div style={{ color: v.accent, fontWeight: 700 }}>Phase {v.phase} · Weeks {v.weeks}</div>
                  </div>
                  <div style={{
                    marginTop: 12, fontSize: 11, color: "#64748B", textAlign: "center",
                    padding: "4px 0", borderTop: "1px solid rgba(255,255,255,0.05)",
                  }}>
                    Click for deep dive →
                  </div>
                </div>
              ))}
            </div>

            {/* Ecosystem Comparison Table */}
            <div style={{
              background: "rgba(255,255,255,0.02)", border: "1px solid rgba(255,255,255,0.06)",
              borderRadius: 12, overflow: "hidden",
            }}>
              <div style={{ padding: "14px 20px", borderBottom: "1px solid rgba(255,255,255,0.06)", fontSize: 14, fontWeight: 700 }}>
                MCP Ecosystem Maturity
              </div>
              <div style={{ padding: "0 4px" }}>
                {[
                  { name: "Zscaler", servers: "1 official", stars: 5, note: "Reference impl · 83 tools" },
                  { name: "Cisco Meraki", servers: "4+ community", stars: 4, note: "Most mature ecosystem" },
                  { name: "Juniper Mist", servers: "2 community", stars: 2, note: "Early stage, functional" },
                  { name: "Palo Alto PAN-OS", servers: "2 community", stars: 2, note: "Firewall only, not SCM" },
                  { name: "Prisma Access / SCM", servers: "None", stars: 0, note: "HIGHEST-VALUE GAP" },
                  { name: "Fortinet", servers: "1 community", stars: 1, note: "FortiGate only" },
                ].map((row, i) => (
                  <div key={i} style={{
                    display: "grid", gridTemplateColumns: "160px 120px 120px 1fr",
                    alignItems: "center", padding: "10px 16px", fontSize: 12,
                    borderBottom: "1px solid rgba(255,255,255,0.03)",
                    background: row.stars === 0 ? "rgba(239,68,68,0.05)" : "transparent",
                  }}>
                    <span style={{ fontWeight: 600, color: row.stars === 0 ? "#FCA5A5" : "#E2E8F0" }}>{row.name}</span>
                    <span style={{ color: "#94A3B8" }}>{row.servers}</span>
                    <span>{Array(5).fill(0).map((_, j) => (
                      <span key={j} style={{ color: j < row.stars ? "#FBBF24" : "#1E293B", fontSize: 14 }}>●</span>
                    ))}</span>
                    <span style={{
                      color: row.stars === 0 ? "#F87171" : "#64748B", fontSize: 11,
                      fontWeight: row.stars === 0 ? 700 : 400,
                    }}>{row.note}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Key Insight */}
            <div style={{
              background: "linear-gradient(135deg, rgba(249,115,22,0.08) 0%, rgba(6,182,212,0.08) 100%)",
              border: "1px solid rgba(249,115,22,0.2)",
              borderRadius: 12, padding: 20,
            }}>
              <div style={{ fontSize: 13, fontWeight: 700, color: "#FB923C", marginBottom: 6 }}>💡 Strategic Opportunity</div>
              <div style={{ fontSize: 13, color: "#CBD5E1", lineHeight: 1.6 }}>
                Prisma Access (Strata Cloud Manager) has <strong style={{ color: "#FCA5A5" }}>zero MCP implementations</strong> despite being the primary SASE management plane for Palo Alto Networks.
                Combined with Meraki and Mist MCP servers, this gives you unified AI-native orchestration across the three most common SMB/MSP networking stacks — a capability no incumbent offers.
              </div>
            </div>
          </div>
        )}

        {/* === ARCHITECTURE TAB === */}
        {activeTab === "architecture" && (
          <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>
            {/* Data Flow */}
            <div style={{
              background: "rgba(255,255,255,0.02)", border: "1px solid rgba(255,255,255,0.06)",
              borderRadius: 12, padding: 24,
            }}>
              <div style={{ fontSize: 14, fontWeight: 700, marginBottom: 20 }}>
                Reference Architecture · FastMCP + Vendor SDK Pattern
              </div>
              <div style={{ display: "flex", flexDirection: "column", gap: 4, alignItems: "center" }}>
                {ARCH_LAYERS.map((layer, i) => (
                  <div key={i} style={{ width: "100%", maxWidth: 560 }}>
                    <div style={{
                      display: "flex", alignItems: "center", gap: 12, padding: "12px 20px",
                      background: `${layer.color}10`, border: `1px solid ${layer.color}30`,
                      borderRadius: 10,
                    }}>
                      <span style={{ fontSize: 20 }}>{layer.icon}</span>
                      <div style={{ flex: 1 }}>
                        <div style={{ fontSize: 14, fontWeight: 700, color: layer.color }}>{layer.label}</div>
                        <div style={{ fontSize: 11, color: "#94A3B8", fontFamily: "monospace" }}>{layer.sub}</div>
                      </div>
                      <div style={{
                        fontSize: 10, color: "#475569", fontWeight: 600, background: "rgba(255,255,255,0.05)",
                        padding: "2px 8px", borderRadius: 4,
                      }}>L{i + 1}</div>
                    </div>
                    {i < ARCH_LAYERS.length - 1 && (
                      <div style={{ textAlign: "center", color: "#334155", fontSize: 14, lineHeight: "20px" }}>↓</div>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Project Structure */}
            <div style={{
              background: "rgba(255,255,255,0.02)", border: "1px solid rgba(255,255,255,0.06)",
              borderRadius: 12, padding: 24,
            }}>
              <div style={{ fontSize: 14, fontWeight: 700, marginBottom: 16 }}>
                Monorepo Structure · Per-Vendor Module
              </div>
              <pre style={{
                fontFamily: "'JetBrains Mono', 'Fira Code', monospace", fontSize: 12,
                color: "#94A3B8", lineHeight: 1.8, margin: 0, overflow: "auto",
                background: "rgba(0,0,0,0.3)", padding: 20, borderRadius: 8,
              }}>{`{vendor}-mcp-server/
├── pyproject.toml              # fastmcp>=2.5.1, vendor-sdk
├── src/{vendor}_mcp/
│   ├── server.py               # FastMCP init, transport, CLI
│   ├── client.py               # SDK client + lifecycle mgmt
│   ├── auth.py                 # Token caching & refresh
│   └── tools/
│       ├── troubleshooting.py  # Read-only monitoring tools
│       ├── configuration.py    # Config mgmt (write-gated)
│       └── security.py         # Policy tools (write-gated)
├── Dockerfile                  # Multi-stage build
└── tests/
    ├── test_tools.py           # Unit tests
    └── test_behavioral.py      # Tool hit rate & success rate`}</pre>
            </div>

            {/* Safety Model */}
            <div style={{
              background: "rgba(255,255,255,0.02)", border: "1px solid rgba(255,255,255,0.06)",
              borderRadius: 12, padding: 24,
            }}>
              <div style={{ fontSize: 14, fontWeight: 700, marginBottom: 16 }}>
                Write Safety · Four-Layer Defense Model
              </div>
              <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                {SAFETY_LAYERS.map((layer, i) => (
                  <div key={i} style={{
                    display: "flex", alignItems: "center", gap: 14, padding: "12px 16px",
                    background: `${layer.color}08`, border: `1px solid ${layer.color}20`,
                    borderRadius: 8,
                  }}>
                    <div style={{
                      width: 32, height: 32, borderRadius: 8, display: "flex",
                      alignItems: "center", justifyContent: "center",
                      background: `${layer.color}20`, color: layer.color,
                      fontWeight: 800, fontSize: 14, flexShrink: 0,
                    }}>{layer.num}</div>
                    <div>
                      <div style={{ fontSize: 13, fontWeight: 700, color: layer.color }}>{layer.label}</div>
                      <div style={{ fontSize: 11, color: "#94A3B8", fontFamily: "monospace" }}>{layer.desc}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Transport */}
            <div style={{
              background: "rgba(255,255,255,0.02)", border: "1px solid rgba(255,255,255,0.06)",
              borderRadius: 12, padding: 24,
            }}>
              <div style={{ fontSize: 14, fontWeight: 700, marginBottom: 16 }}>
                Dual Transport Strategy
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
                {[
                  { mode: "stdio", use: "Local · Claude Desktop / Code", env: "Individual engineers", cmd: "vendor-mcp --transport stdio", icon: "💻" },
                  { mode: "streamable-http", use: "Remote · Centralized hosted", env: "MSP SaaS platform", cmd: "vendor-mcp --transport streamable-http --port 8000", icon: "☁️" },
                ].map((t, i) => (
                  <div key={i} style={{
                    padding: 16, borderRadius: 8, background: "rgba(0,0,0,0.2)",
                    border: "1px solid rgba(255,255,255,0.05)",
                  }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
                      <span style={{ fontSize: 18 }}>{t.icon}</span>
                      <span style={{ fontSize: 13, fontWeight: 700, color: "#E2E8F0" }}>{t.mode}</span>
                    </div>
                    <div style={{ fontSize: 12, color: "#94A3B8", marginBottom: 4 }}>{t.use}</div>
                    <div style={{ fontSize: 11, color: "#64748B", marginBottom: 8 }}>{t.env}</div>
                    <code style={{
                      fontSize: 10, color: "#22C55E", fontFamily: "monospace",
                      background: "rgba(34,197,94,0.08)", padding: "4px 8px",
                      borderRadius: 4, display: "block", wordBreak: "break-all",
                    }}>{t.cmd}</code>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* === VENDOR DEEP DIVE TAB === */}
        {activeTab === "vendors" && (
          <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
            {/* Vendor Selector */}
            <div style={{ display: "flex", gap: 8 }}>
              {Object.entries(VENDORS).map(([key, v]) => (
                <button key={key} onClick={() => setActiveVendor(key)} style={{
                  padding: "10px 20px", borderRadius: 8, border: "none", cursor: "pointer",
                  fontSize: 13, fontWeight: 700, transition: "all 0.2s",
                  background: activeVendor === key ? `${v.color}20` : "rgba(255,255,255,0.03)",
                  color: activeVendor === key ? v.accent : "#64748B",
                  borderBottom: activeVendor === key ? `2px solid ${v.color}` : "2px solid transparent",
                }}>
                  {v.icon} {v.name}
                </button>
              ))}
            </div>

            {/* Vendor Header */}
            <div style={{
              background: `linear-gradient(135deg, ${vendor.bg} 0%, #0B0F1A 100%)`,
              border: `1px solid ${vendor.color}33`,
              borderRadius: 12, padding: 24, position: "relative", overflow: "hidden",
            }}>
              <div style={{ position: "absolute", top: -30, right: -10, fontSize: 120, opacity: 0.04 }}>{vendor.icon}</div>
              <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 16 }}>
                <span style={{ fontSize: 32 }}>{vendor.icon}</span>
                <div>
                  <h2 style={{ margin: 0, fontSize: 22, fontWeight: 800, color: vendor.accent }}>{vendor.name}</h2>
                  <div style={{ color: "#94A3B8", fontSize: 13 }}>{vendor.subtitle}</div>
                </div>
                <div style={{ marginLeft: "auto" }}><GapBadge level={vendor.gapLevel} /></div>
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 16 }}>
                {[
                  { label: "Auth Model", value: vendor.auth, detail: vendor.authDetail },
                  { label: "Rate Limiting", value: vendor.rateLimit },
                  { label: "Commit Model", value: vendor.commitModel, detail: vendor.uniqueChallenge },
                ].map((item, i) => (
                  <div key={i} style={{ padding: 12, background: "rgba(0,0,0,0.2)", borderRadius: 8 }}>
                    <div style={{ fontSize: 10, color: "#64748B", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 4 }}>{item.label}</div>
                    <div style={{ fontSize: 13, fontWeight: 600, color: "#E2E8F0" }}>{item.value}</div>
                    {item.detail && <div style={{ fontSize: 10, color: "#94A3B8", marginTop: 4 }}>{item.detail}</div>}
                  </div>
                ))}
              </div>
              <div style={{ marginTop: 12, display: "flex", gap: 16, fontSize: 12, color: "#94A3B8" }}>
                <span>SDK: <code style={{ color: vendor.accent }}>{vendor.sdk}</code></span>
                <span>Lang: <strong>{vendor.sdkLang}</strong></span>
                <span>API: <code style={{ color: "#64748B" }}>{vendor.apiBase}</code></span>
              </div>
            </div>

            {/* Tool Tiers */}
            {[
              { key: "tier1", label: "Tier 1 — AI-Assisted Troubleshooting", sub: "Read-only · Highest MSP value", color: "#22C55E" },
              { key: "tier2", label: "Tier 2 — Monitoring & Diagnostics", sub: "Read-only · Active probing", color: "#EAB308" },
              { key: "tier3", label: "Tier 3 — Configuration & Policy", sub: "Write-gated · Requires explicit enablement", color: "#EF4444" },
            ].map(tier => (
              <div key={tier.key} style={{
                background: "rgba(255,255,255,0.02)", border: "1px solid rgba(255,255,255,0.06)",
                borderRadius: 12, padding: 20,
              }}>
                <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 12 }}>
                  <div style={{ width: 4, height: 20, borderRadius: 2, background: tier.color }} />
                  <div>
                    <div style={{ fontSize: 13, fontWeight: 700, color: "#E2E8F0" }}>{tier.label}</div>
                    <div style={{ fontSize: 11, color: "#64748B" }}>{tier.sub}</div>
                  </div>
                </div>
                <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
                  {vendor.tools[tier.key].map((tool, i) => <ToolPill key={i} tool={tool} />)}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* === ROADMAP TAB === */}
        {activeTab === "roadmap" && (
          <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
            {/* Timeline */}
            <div style={{
              background: "rgba(255,255,255,0.02)", border: "1px solid rgba(255,255,255,0.06)",
              borderRadius: 12, padding: 24,
            }}>
              <div style={{ fontSize: 14, fontWeight: 700, marginBottom: 20 }}>Development Phases</div>
              <div style={{ position: "relative", paddingLeft: 32 }}>
                {/* Vertical line */}
                <div style={{
                  position: "absolute", left: 11, top: 8, bottom: 8, width: 2,
                  background: "linear-gradient(to bottom, #F97316, #06B6D4, #A855F7, #22C55E)",
                }} />
                {[
                  { ...VENDORS.prisma, tasks: ["OAuth2 token manager with 13-min proactive refresh", "Read-only security policy tools (list rules, objects, profiles)", "Commit-gated write operations with candidate → push model", "Folder-scoped queries (Mobile Users, Remote Networks, Shared)"] },
                  { ...VENDORS.meraki, tasks: ["Multi-org routing layer for MSP multi-tenancy", "Curated tools + Code Mode hybrid for 1,225 endpoints", "Action batch integration for bulk configuration", "Aggressive caching for 10 req/s rate limit"] },
                  { ...VENDORS.mist, tasks: ["Multi-region endpoint support (5 regional APIs)", "SLE metrics integration (Mist's AI-driven differentiator)", "Org-token-per-customer model for MSP operations", "Marvis anomaly alert integration"] },
                  { name: "Unified Deploy", icon: "🚀", color: "#22C55E", accent: "#4ADE80", phase: 4, weeks: "8", tasks: ["Docker packaging with identical structure", "Streamable HTTP + OAuth 2.1 for SaaS integration", "Vault / AWS Secrets Manager for credential management", "Optional unified netops-mcp meta-server with --services flag"] },
                ].map((phase, i) => (
                  <div key={i} style={{ display: "flex", gap: 16, marginBottom: i < 3 ? 24 : 0 }}>
                    <div style={{
                      width: 24, height: 24, borderRadius: "50%", flexShrink: 0,
                      background: phase.color, display: "flex", alignItems: "center",
                      justifyContent: "center", fontSize: 12, zIndex: 1,
                      boxShadow: `0 0 12px ${phase.color}40`,
                    }}>{phase.phase}</div>
                    <div style={{ flex: 1, paddingBottom: 4 }}>
                      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 6 }}>
                        <span style={{ fontSize: 16 }}>{phase.icon}</span>
                        <span style={{ fontSize: 15, fontWeight: 700, color: phase.accent }}>{phase.name}</span>
                        <span style={{
                          fontSize: 11, color: "#64748B", background: "rgba(255,255,255,0.05)",
                          padding: "2px 8px", borderRadius: 4,
                        }}>Weeks {phase.weeks}</span>
                      </div>
                      <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
                        {phase.tasks.map((task, j) => (
                          <div key={j} style={{
                            display: "flex", alignItems: "center", gap: 8,
                            fontSize: 12, color: "#94A3B8", padding: "4px 0",
                          }}>
                            <span style={{ color: phase.color, fontSize: 8 }}>◆</span>
                            {task}
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Auth Comparison */}
            <div style={{
              background: "rgba(255,255,255,0.02)", border: "1px solid rgba(255,255,255,0.06)",
              borderRadius: 12, overflow: "hidden",
            }}>
              <div style={{ padding: "14px 20px", borderBottom: "1px solid rgba(255,255,255,0.06)", fontSize: 14, fontWeight: 700 }}>
                Cross-Platform Comparison
              </div>
              <div style={{ overflowX: "auto" }}>
                <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 12 }}>
                  <thead>
                    <tr style={{ borderBottom: "1px solid rgba(255,255,255,0.06)" }}>
                      {["", "Prisma Access", "Cisco Meraki", "Juniper Mist"].map((h, i) => (
                        <th key={i} style={{
                          padding: "10px 16px", textAlign: "left", fontWeight: 700,
                          color: i === 0 ? "#64748B" : [VENDORS.prisma, VENDORS.meraki, VENDORS.mist][i - 1]?.accent,
                        }}>{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {[
                      ["Auth", "OAuth2 (15-min TTL)", "API Key / OAuth2", "Static Token"],
                      ["Rate Limit", "Token-based", "10 req/s per org", "5,000 req/hr"],
                      ["Commit Model", "Candidate → Push", "Immediate", "Immediate"],
                      ["SDK", "pan-scm-sdk", "meraki (official)", "mistapi"],
                      ["Endpoints", "~200 (config-scoped)", "1,225 operations", "~300 (hierarchical)"],
                      ["MCP Servers", "0 (gap!)", "4+ community", "2 early-stage"],
                      ["MSP Pattern", "TSG-scoped auth", "Multi-org API keys", "Org-level tokens"],
                    ].map((row, i) => (
                      <tr key={i} style={{ borderBottom: "1px solid rgba(255,255,255,0.03)" }}>
                        {row.map((cell, j) => (
                          <td key={j} style={{
                            padding: "8px 16px",
                            color: j === 0 ? "#64748B" : (cell.includes("gap") ? "#FCA5A5" : "#CBD5E1"),
                            fontWeight: j === 0 || cell.includes("gap") ? 600 : 400,
                            fontFamily: j > 0 ? "monospace" : "inherit",
                            fontSize: j > 0 ? 11 : 12,
                          }}>{cell}</td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Key Patterns */}
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
              {[
                { title: "Zscaler Reference Patterns", icon: "🏗️", items: [
                  "SDK-first: never raw REST calls",
                  "~10 tools per service module",
                  "{prefix}_{verb}_{resource} naming",
                  "Read-only default + explicit write flags",
                  "Environment-variable-driven transport",
                ]},
                { title: "MSP Platform Differentiators", icon: "🎯", items: [
                  "Multi-tenant credential routing",
                  "Rate-limit-aware tool design",
                  "Streamable HTTP for centralized deploy",
                  "Code Mode for large API surfaces",
                  "Behavioral testing (hit rate + success)",
                ]},
              ].map((card, i) => (
                <div key={i} style={{
                  background: "rgba(255,255,255,0.02)", border: "1px solid rgba(255,255,255,0.06)",
                  borderRadius: 12, padding: 20,
                }}>
                  <div style={{ fontSize: 14, fontWeight: 700, marginBottom: 12 }}>{card.icon} {card.title}</div>
                  <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                    {card.items.map((item, j) => (
                      <div key={j} style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12, color: "#94A3B8" }}>
                        <span style={{ color: "#22C55E", fontSize: 8 }}>●</span>
                        {item}
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.4; }
        }
        * { box-sizing: border-box; }
        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 3px; }
      `}</style>
    </div>
  );
}
