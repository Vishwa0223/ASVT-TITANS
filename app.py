import plotly.graph_objects as go
import streamlit as st

from src.ai_analysis import analyze_market
from src.ui_helpers import (
    ASSET_TICKERS,
    STRATEGIES,
    add_price_trace,
    add_signal_traces,
    aligned_comparison,
    apply_strategy,
    apply_theme,
    chart_layout,
    load_asset_data,
    run_backtest,
    render_sidebar,
    signal_summary,
)

st.set_page_config(page_title="QuantX | Quantitative Intelligence", page_icon="Q", layout="wide")
apply_theme()
render_sidebar("Dashboard")

st.markdown(
    """
    <style>
    .block-container { max-width: 1540px; padding-top: 1.1rem; }
    [data-testid="stAppViewContainer"] { overflow-x: hidden; }
    [data-testid="stAppViewContainer"]::before {
        content: ""; position: fixed; inset: 0; pointer-events: none; opacity: .28;
        background-image: linear-gradient(rgba(76,201,240,.045) 1px, transparent 1px),
            linear-gradient(90deg, rgba(123,97,255,.045) 1px, transparent 1px);
        background-size: 72px 72px; mask-image: linear-gradient(to bottom, black, transparent 82%);
    }
    .site-nav { display:flex; align-items:center; justify-content:space-between; gap:1rem; padding:.8rem 1rem;
        border:1px solid rgba(148,163,184,.15); border-radius:1.1rem; background:rgba(7,14,29,.68);
        backdrop-filter:blur(18px); box-shadow:0 18px 45px rgba(0,0,0,.2); }
    .hero-wrap { padding: 4.5rem 0 3rem; position:relative; }
    .eyebrow { color:#8ea9d1; font-size:.68rem; letter-spacing:.2em; text-transform:uppercase; font-weight:800; }
    .hero-title { font-size:clamp(2.8rem,4.7vw,5.4rem); line-height:.98; letter-spacing:-.055em; font-weight:850;
        margin:.85rem 0 1.5rem; max-width:720px; color:#493129; overflow-wrap:normal; word-break:normal; hyphens:none; }
    .gradient-text { background:linear-gradient(100deg,#63d9ff 5%,#7b61ff 55%,#d9a4ff 95%);
        background-clip:text; -webkit-background-clip:text; color:transparent; }
    .hero-copy { max-width:610px; color:#b8c9e7; font-size:1.12rem; line-height:1.75; }
    .hero-note { color:#7e96bd; font-size:.75rem; margin-top:1rem; }
    .hero-buttons { display:flex; gap:.75rem; flex-wrap:wrap; margin-top:1.6rem; }
    .hero-buttons [data-testid="stPageLink"] a, .cta-link [data-testid="stPageLink"] a { border-radius:.75rem;
        padding:.72rem 1rem; border:1px solid rgba(148,163,184,.22); background:linear-gradient(135deg,#3a86ff,#6857d9);
        color:#493129; font-weight:750; box-shadow:0 10px 26px rgba(139,89,123,.14); }
    .hero-buttons .secondary [data-testid="stPageLink"] a { background:rgba(15,28,52,.72); }
    .research-panel { border:1px solid rgba(111,180,255,.28); border-radius:1.25rem; padding:1rem;
        background:linear-gradient(145deg,rgba(21,39,72,.9),rgba(9,17,34,.86)); box-shadow:0 24px 70px rgba(23,93,170,.22); }
    .panel-top { display:flex; align-items:center; justify-content:space-between; margin-bottom:.6rem; }
    .panel-label { color:#9fb9df; font-size:.68rem; letter-spacing:.14em; text-transform:uppercase; font-weight:800; }
    .live-dot { display:inline-block; width:.45rem; height:.45rem; border-radius:50%; background:#4ade80; box-shadow:0 0 12px #4ade80; margin-right:.35rem; }
    .panel-kpis { display:grid; grid-template-columns:repeat(3,1fr); gap:.65rem; margin-top:.7rem; }
    .panel-kpi { border:1px solid rgba(148,163,184,.14); border-radius:.85rem; padding:.7rem; background:rgba(5,13,29,.54); }
    .panel-kpi-label { color:#7690b7; font-size:.65rem; text-transform:uppercase; letter-spacing:.1em; }
    .panel-kpi-value { color:#493129; font-size:1.2rem; font-weight:800; margin-top:.3rem; }
    .section-intro { max-width:620px; margin-bottom:1.2rem; }
    .section-title { font-size:clamp(2rem,4vw,3.6rem); line-height:1.02; letter-spacing:-.055em; font-weight:800; margin:.2rem 0 .7rem; }
    .section-copy { color:#9eb4d7; line-height:1.65; }
    .market-strip { display:flex; align-items:center; gap:.7rem; color:#7992b9; font-size:.66rem; letter-spacing:.15em; text-transform:uppercase; margin:1rem 0 .7rem; }
    .market-strip::after { content:""; height:1px; flex:1; background:linear-gradient(90deg,rgba(76,201,240,.4),transparent); }
    .asset-card { min-height:170px; padding:1rem; border-radius:1rem; border:1px solid rgba(148,163,184,.14); background:rgba(12,24,46,.76); transition:transform .25s ease,border-color .25s ease,box-shadow .25s ease; }
    .asset-card:hover { transform:translateY(-4px); border-color:rgba(76,201,240,.42); box-shadow:0 16px 34px rgba(38,121,208,.18); }
    .asset-head { display:flex; align-items:center; justify-content:space-between; }
    .asset-symbol { color:#6fdfff; font-size:.65rem; letter-spacing:.15em; font-weight:800; }
    .asset-name { color:#493129; font-size:1.05rem; font-weight:800; margin-top:.3rem; }
    .asset-price { font-size:1.55rem; font-weight:850; margin-top:1rem; }
    .asset-meta { color:#8fa8ce; font-size:.72rem; margin-top:.35rem; }
    .asset-positive { color:#69e49b; font-weight:800; }
    .asset-negative { color:#ff7b9b; font-weight:800; }
    .layer-card { min-height:225px; padding:1.2rem; border:1px solid rgba(148,163,184,.14); border-radius:1.15rem; background:linear-gradient(145deg,rgba(18,34,62,.84),rgba(9,17,32,.86)); transition:transform .25s ease,border-color .25s ease; }
    .layer-card:hover { transform:translateY(-5px); border-color:rgba(123,97,255,.5); }
    .layer-number { color:#6687b7; font-size:.75rem; letter-spacing:.18em; font-weight:850; }
    .layer-icon { font-size:1.55rem; margin:.8rem 0; }
    .layer-title { color:#493129; font-weight:800; letter-spacing:.02em; }
    .layer-copy { color:#8fa8cd; font-size:.82rem; line-height:1.55; margin-top:.45rem; }
    .pipeline { display:grid; grid-template-columns:repeat(5,1fr); gap:.7rem; align-items:stretch; }
    .pipeline-step { position:relative; padding:1rem .8rem; border:1px solid rgba(76,201,240,.17); border-radius:.9rem; background:rgba(11,27,50,.7); text-align:center; }
    .pipeline-step:not(:last-child)::after { content:"→"; position:absolute; right:-.78rem; top:38%; color:#4cc9f0; font-size:1.3rem; z-index:2; text-shadow:0 0 14px rgba(76,201,240,.8); }
    .pipeline-num { color:#4cc9f0; font-size:.66rem; letter-spacing:.16em; font-weight:850; }
    .pipeline-title { color:#493129; font-weight:800; margin:.5rem 0; font-size:.86rem; }
    .pipeline-copy { color:#849dc2; font-size:.7rem; line-height:1.45; }
    .bento-card { min-height:245px; border:1px solid rgba(148,163,184,.14); border-radius:1.15rem; padding:1.1rem; background:linear-gradient(150deg,rgba(18,34,61,.88),rgba(8,16,30,.88)); overflow:hidden; }
    .bento-card.tall { min-height:330px; }
    .bento-label { color:#7e9ac2; font-size:.66rem; letter-spacing:.16em; text-transform:uppercase; font-weight:800; }
    .bento-title { color:#493129; font-size:1.25rem; font-weight:800; margin:.55rem 0 .35rem; }
    .bento-copy { color:#91a9cc; font-size:.78rem; line-height:1.55; }
    .preview-shell { padding:1.2rem; border:1px solid rgba(76,201,240,.22); border-radius:1.25rem; background:linear-gradient(145deg,rgba(14,34,61,.95),rgba(7,17,32,.94)); box-shadow:0 25px 65px rgba(16,93,158,.16); }
    .preview-title { font-size:1.65rem; font-weight:820; letter-spacing:-.035em; }
    .preview-asset { color:#6fdfff; font-size:.72rem; text-transform:uppercase; letter-spacing:.15em; margin-top:.25rem; }
    .stat-grid { display:grid; grid-template-columns:repeat(6,1fr); gap:.55rem; margin:1rem 0; }
    .stat-cell { padding:.65rem; border:1px solid rgba(148,163,184,.13); border-radius:.7rem; background:rgba(5,13,27,.55); }
    .stat-cell small { color:#7891b6; display:block; font-size:.6rem; text-transform:uppercase; letter-spacing:.08em; }
    .stat-cell strong { display:block; margin-top:.3rem; color:#493129; font-size:.9rem; }
    .strategy-mini { padding:1rem; min-height:145px; border:1px solid rgba(148,163,184,.14); border-radius:.95rem; background:rgba(13,27,49,.7); }
    .strategy-mini strong { display:block; margin:.6rem 0 .3rem; }
    .strategy-mini span { color:#8ca5c9; font-size:.75rem; line-height:1.45; }
    .ai-box { min-height:240px; padding:1.4rem; border:1px solid rgba(123,97,255,.36); border-radius:1.2rem; background:radial-gradient(circle at 90% 10%,rgba(123,97,255,.24),transparent 35%),linear-gradient(145deg,rgba(24,30,72,.94),rgba(9,16,34,.92)); }
    .ai-prompt { color:#493129; font-size:1.25rem; line-height:1.5; margin:1.2rem 0; max-width:580px; }
    .trust-value { color:#493129; font-size:2.2rem; font-weight:850; letter-spacing:-.05em; }
    .trust-label { color:#819bc1; font-size:.68rem; letter-spacing:.12em; text-transform:uppercase; line-height:1.4; }
    .footer { margin-top:3rem; padding:1.2rem 0 .5rem; border-top:1px solid rgba(148,163,184,.13); color:#8098bc; font-size:.75rem; }
    @media (max-width: 850px) { .pipeline { grid-template-columns:1fr; } .pipeline-step:not(:last-child)::after { content:"↓"; right:48%; top:auto; bottom:-1.2rem; } .stat-grid { grid-template-columns:repeat(2,1fr); } .site-nav { align-items:flex-start; } }
    .site-nav, .research-panel, .asset-card, .layer-card, .pipeline-step, .bento-card, .preview-shell, .strategy-mini, .ai-box {
        background:rgba(255,255,255,.92); border-color:#d9dee7; box-shadow:0 14px 34px rgba(31,41,55,.08);
    }
    .panel-kpi, .stat-cell { background:#f4f6f8; border-color:#e1e5eb; }
    .hero-title, .section-title, .preview-title, .asset-name, .layer-title, .pipeline-title, .bento-title, .panel-kpi-value, .stat-cell strong, .trust-value { color:#1f2937; }
    .brand-title { color:#1f2937; }
    .brand-sub { color:#667085; }
    .hero-copy, .section-copy, .bento-copy, .layer-copy, .pipeline-copy, .asset-meta, .hero-note, .panel-label, .panel-kpi-label, .stat-cell small, .strategy-mini span, .trust-label { color:#667085; }
    .eyebrow, .asset-symbol, .preview-asset, .pipeline-num { color:#2563eb; }
    .gradient-text { background:linear-gradient(100deg,#2563eb 10%,#0f766e 90%); background-clip:text; -webkit-background-clip:text; }
    .hero-buttons [data-testid="stPageLink"] a, .cta-link [data-testid="stPageLink"] a { background:#1f2937; box-shadow:0 10px 24px rgba(31,41,55,.16); }
    .hero-buttons .secondary [data-testid="stPageLink"] a { background:#fff; color:#1f2937; border-color:#cbd5e1; }
    [data-testid="stAppViewContainer"]::before { opacity:.45; background-image:linear-gradient(rgba(31,41,55,.035) 1px, transparent 1px), linear-gradient(90deg, rgba(31,41,55,.035) 1px, transparent 1px); }
    html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stAppViewContainer"] > .main { background:linear-gradient(145deg,#fff3e7 0%,#ffeedd 52%,#f7e4df 100%) !important; color:#493129; }
    [data-testid="stAppViewContainer"]::before { opacity:.24; background-image:radial-gradient(rgba(139,89,123,.12) 1px, transparent 1px); background-size:28px 28px; mask-image:linear-gradient(to bottom, black, transparent 70%); }
    .stApp * { color:#493129 !important; }
    .stApp svg { color:#493129 !important; fill:currentColor; }
    .site-nav, .research-panel, .asset-card, .layer-card, .pipeline-step, .bento-card, .preview-shell, .strategy-mini, .ai-box { background:rgba(255,248,240,.84) !important; border-color:#ead8cc !important; box-shadow:0 14px 34px rgba(73,49,41,.09) !important; }
    .hero-title, .section-title, .preview-title, .asset-name, .layer-title, .pipeline-title, .bento-title, .panel-kpi-value, .stat-cell strong, .trust-value, .brand-title { color:#493129 !important; font-family:'Playfair Display', Georgia, serif; }
    .hero-title { font-size:clamp(2.9rem,5vw,5.6rem); line-height:1.02; letter-spacing:-.035em; }
    .section-title { letter-spacing:-.025em; }
    .hero-copy, .section-copy, .bento-copy, .layer-copy, .pipeline-copy, .asset-meta, .hero-note, .panel-label, .panel-kpi-label, .stat-cell small, .strategy-mini span, .trust-label, .brand-sub { color:#765f59 !important; }
    .ai-prompt, .footer, .asset-price, .strategy-mini strong, .bento-label { color:#493129 !important; }
    .eyebrow, .asset-symbol, .preview-asset, .pipeline-num { color:#8b597b !important; }
    .gradient-text { background:linear-gradient(100deg,#8b597b 10%,#efa3a0 58%,#c47d83 95%); background-clip:text; -webkit-background-clip:text; color:transparent; }
    .hero-buttons [data-testid="stPageLink"] a, .cta-link [data-testid="stPageLink"] a { background:#efa3a0 !important; border-color:#d58f91 !important; color:#493129 !important; box-shadow:0 10px 24px rgba(139,89,123,.14); }
    .hero-buttons .secondary [data-testid="stPageLink"] a { background:#fff8f0 !important; color:#493129 !important; border-color:#ead8cc !important; }
    .panel-kpi, .stat-cell { background:#fff3e7 !important; border-color:#ead8cc !important; }
    .live-dot { background:#8b597b; box-shadow:0 0 12px rgba(139,89,123,.5); }
    .market-strip::after { background:linear-gradient(90deg,rgba(139,89,123,.45),transparent); }
    .asset-positive { color:#8b597b; }
    .asset-negative { color:#b65f68; }
    .layer-card:hover, .asset-card:hover { border-color:#efa3a0 !important; box-shadow:0 16px 34px rgba(139,89,123,.14); }
    .pipeline-step:not(:last-child)::after { color:#8b597b; text-shadow:0 0 14px rgba(139,89,123,.35); }
    .layer-icon, .site-nav svg, .site-nav [data-testid="stPageLink"] svg, .hero-buttons [data-testid="stPageLink"] svg { color:#493129 !important; fill:currentColor; }
    @media (max-width: 850px) { .hero-wrap { padding:2.8rem 0 2rem; } .hero-title { font-size:clamp(2.4rem,12vw,4rem); } .panel-kpis { grid-template-columns:1fr; } }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(ttl=900, show_spinner=False)
def home_snapshot():
    market_data = {asset: load_asset_data(asset) for asset in ASSET_TICKERS}
    strategy_data, result, metrics, backtester = run_backtest("Bitcoin", "SMA Crossover", 100000.0, 0.1, 1.0)
    return market_data, strategy_data, result, metrics, backtester


market_data, bitcoin_data, backtest_result, backtest_metrics, backtester = home_snapshot()

st.markdown(
    """
    <div class="site-nav">
      <div class="brand-wrap"><div class="brand-mark">Q</div><div><div class="brand-title">QuantX</div><div class="brand-sub">Quantitative multi-asset intelligence</div></div></div>
      <div class="eyebrow">See the market · understand the risk · test the strategy</div>
    </div>
    """,
    unsafe_allow_html=True,
)

hero_left, hero_right = st.columns([1.08, .92], gap="large")
with hero_left:
    st.markdown(
        """
        <div class="hero-wrap">
          <div class="eyebrow">Quantitative finance · AI · backtesting</div>
          <div class="hero-title">Turn Market Data<br>Into <span class="gradient-text">Quantitative&nbsp;Intelligence.</span></div>
          <div class="hero-copy">AI-powered quantitative intelligence for multi-asset market research, risk analysis, and strategy backtesting.</div>
          <div class="hero-note">Analyze Gold, Bitcoin and NVIDIA. Discover trends, measure risk, test strategies, and understand market behavior in one platform.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    with st.container(horizontal=True, gap="small"):
        st.page_link("pages/1_📈_Markets.py", label="🚀 Explore markets", icon=":material/arrow_forward:")
        st.page_link("pages/3_🔬_Backtesting.py", label="🔬 Start backtesting", icon=":material/science:")

with hero_right:
    st.markdown("<div class='hero-wrap'>", unsafe_allow_html=True)
    st.markdown(
        "<div class='research-panel'><div class='panel-top'><span class='panel-label'><span class='live-dot'></span>Research workspace · historical data</span><span class='panel-label'>BTC-USD</span></div>",
        unsafe_allow_html=True,
    )
    hero_fig = go.Figure()
    add_price_trace(hero_fig, bitcoin_data.tail(210))
    hero_fig.add_trace(go.Scatter(x=bitcoin_data.tail(210).index, y=bitcoin_data.tail(210)["SMA"], name="SMA", line={"color": "#8d72ff", "width": 1.4}))
    hero_fig.add_trace(go.Scatter(x=bitcoin_data.tail(210).index, y=bitcoin_data.tail(210)["EMA"], name="EMA", line={"color": "#55e2ff", "width": 1.4}))
    add_signal_traces(hero_fig, bitcoin_data.tail(210), "SMA Crossover")
    hero_fig.update_layout(showlegend=False, **chart_layout(280))
    st.plotly_chart(hero_fig, width="stretch", config={"displayModeBar": False})
    latest_btc = bitcoin_data.iloc[-1]
    bitcoin_signal = signal_summary(bitcoin_data)
    st.markdown(
        f"""<div class='panel-kpis'><div class='panel-kpi'><div class='panel-kpi-label'>Current signal</div><div class='panel-kpi-value'>{'🟢' if bitcoin_signal['latest'] == 'BUY' else '🔴' if bitcoin_signal['latest'] == 'SELL' else '⚪'} {bitcoin_signal['latest']}</div></div><div class='panel-kpi'><div class='panel-kpi-label'>Annualized volatility</div><div class='panel-kpi-value'>{latest_btc['Annualized_Volatility'] * 100:.2f}%</div></div><div class='panel-kpi'><div class='panel-kpi-label'>Sharpe ratio</div><div class='panel-kpi-value'>{backtest_metrics['Sharpe Ratio']:.2f}</div></div></div></div>""",
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div class='market-strip'>Historical market data</div>", unsafe_allow_html=True)
market_columns = st.columns(3)
for column, (asset, data) in zip(market_columns, market_data.items()):
    latest = data.iloc[-1]
    daily_return = latest["Daily_Return"] * 100
    ticker = ASSET_TICKERS[asset]
    with column:
        with st.container(border=True):
            st.markdown(f"<div class='asset-card'><div class='asset-head'><div><div class='asset-symbol'>{ticker}</div><div class='asset-name'>{asset}</div></div><span class='{'asset-positive' if daily_return >= 0 else 'asset-negative'}'>{'▲' if daily_return >= 0 else '▼'} {abs(daily_return):.2f}%</span></div><div class='asset-price'>${latest['Close']:,.2f}</div><div class='asset-meta'>Trend · <span class='{'asset-positive' if daily_return >= 0 else 'asset-negative'}'>{'positive session' if daily_return >= 0 else 'negative session'}</span></div></div>", unsafe_allow_html=True)
            st.page_link("pages/1_📈_Markets.py", label=f"Explore {asset}", icon=":material/arrow_forward:")

st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)
st.markdown("<div class='section-intro'><div class='eyebrow'>The QuantX architecture</div><div class='section-title'>One platform.<br>Five intelligence layers.</div><div class='section-copy'>A focused research loop that moves from observed market behavior to explainable quantitative decisions.</div></div>", unsafe_allow_html=True)

layers = [
    ("01", "◈", "Market intelligence", "Understand price behavior, trends and momentum.", "pages/1_📈_Markets.py", ":material/show_chart:"),
    ("02", "⌁", "Strategy engine", "Generate and analyze quantitative trading signals.", "pages/2_🧠_Strategies.py", ":material/psychology:"),
    ("03", "◌", "Risk lab", "Measure volatility, drawdown, Sharpe and correlation.", "pages/4_⚠️_Risk_Analysis.py", ":material/warning:"),
    ("04", "⟲", "Backtesting", "Simulate strategies against historical market data.", "pages/3_🔬_Backtesting.py", ":material/science:"),
    ("05", "✦", "AI insights", "Turn quantitative results into understandable insights.", "pages/5_🤖_AI_Insights.py", ":material/smart_toy:"),
]
layer_columns = st.columns(5)
for column, (number, icon, title, copy, path, material_icon) in zip(layer_columns, layers):
    with column:
        st.markdown(f"<div class='layer-card'><div class='layer-number'>{number}</div><div class='layer-icon'>{icon}</div><div class='layer-title'>{title}</div><div class='layer-copy'>{copy}</div></div>", unsafe_allow_html=True)
        st.page_link(path, label="Open layer", icon=material_icon)

st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)
st.markdown("<div class='section-intro'><div class='eyebrow'>From signal to decision</div><div class='section-title'>The research loop.</div></div>", unsafe_allow_html=True)
st.markdown(
    "<div class='pipeline'>" + "".join(
        f"<div class='pipeline-step'><div class='pipeline-num'>{number}</div><div class='pipeline-title'>{title}</div><div class='pipeline-copy'>{copy}</div></div>"
        for number, title, copy in [
            ("01 · DATA", "Market data", "Historical data from Gold, Bitcoin and NVIDIA"),
            ("02 · ANALYZE", "Quant analysis", "SMA, EMA, returns and volatility"),
            ("03 · STRATEGY", "Strategy", "SMA, EMA, Momentum and Mean Reversion"),
            ("04 · BACKTEST", "Backtest", "Portfolio simulation and benchmark comparison"),
            ("05 · INSIGHT", "Insight", "Risk metrics and AI-powered interpretation"),
        ]
    ) + "</div>",
    unsafe_allow_html=True,
)

st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)
st.markdown("<div class='section-intro'><div class='eyebrow'>Product surface</div><div class='section-title'>Everything you need to research a market.</div></div>", unsafe_allow_html=True)

bento_a, bento_b = st.columns([1.35, 1], gap="medium")
with bento_a:
    with st.container(border=True):
        st.markdown("<div class='bento-card tall'><div class='bento-label'>📈 Market analytics</div><div class='bento-title'>Read the shape of price.</div><div class='bento-copy'>Layer price action with moving averages and return behavior to see what the market is actually doing.</div></div>", unsafe_allow_html=True)
        mini = go.Figure()
        mini.add_trace(go.Scatter(x=bitcoin_data.tail(120).index, y=bitcoin_data.tail(120)["Close"], line={"color": "#55e2ff", "width": 2}, name="BTC"))
        mini.add_trace(go.Scatter(x=bitcoin_data.tail(120).index, y=bitcoin_data.tail(120)["EMA"], line={"color": "#8d72ff", "width": 1.5}, name="EMA"))
        mini.update_layout(showlegend=False, **chart_layout(190))
        st.plotly_chart(mini, width="stretch", config={"displayModeBar": False})
with bento_b:
    with st.container(border=True):
        st.markdown("<div class='bento-card tall'><div class='bento-label'>🧠 AI intelligence</div><div class='bento-title'>Make the numbers legible.</div><div class='bento-copy'>A research assistant that turns selected market evidence into concise observations about trend, risk and strategy.</div><div style='margin-top:1.3rem;padding:1rem;border:1px solid rgba(139,89,123,.25);border-radius:.85rem;color:#493129;background:rgba(239,163,160,.18);'>✦ “Historical momentum is positive, but risk remains measurable.”</div></div>", unsafe_allow_html=True)

bento_c, bento_d, bento_e = st.columns(3, gap="medium")
with bento_c:
    with st.container(border=True):
        st.markdown("<div class='bento-card'><div class='bento-label'>⚡ Strategy lab</div><div class='bento-title'>Signals with a reason.</div><div class='bento-copy'>Compare four strategy families and inspect their actual buy and sell markers.</div></div>", unsafe_allow_html=True)
with bento_d:
    with st.container(border=True):
        st.markdown("<div class='bento-card'><div class='bento-label'>🛡 Risk analytics</div><div class='bento-title'>Know the downside.</div><div class='bento-copy'>Volatility, drawdown, Sharpe and correlation put performance in context.</div></div>", unsafe_allow_html=True)
with bento_e:
    with st.container(border=True):
        st.markdown("<div class='bento-card'><div class='bento-label'>🔬 Backtesting</div><div class='bento-title'>Test before trusting.</div><div class='bento-copy'>Replay a strategy across history with capital, costs and benchmark comparison.</div></div>", unsafe_allow_html=True)

st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)
with st.container(border=True):
    st.markdown("<div class='preview-shell'><div class='eyebrow'>Market intelligence preview</div><div class='preview-title'>Understand the market before you trade it.</div><div class='preview-asset'>Selected asset · Bitcoin · BTC-USD</div>", unsafe_allow_html=True)
    st.markdown(
        f"<div class='stat-grid'><div class='stat-cell'><small>Price</small><strong>${latest_btc['Close']:,.2f}</strong></div><div class='stat-cell'><small>Daily return</small><strong>{latest_btc['Daily_Return'] * 100:.2f}%</strong></div><div class='stat-cell'><small>SMA</small><strong>${latest_btc['SMA']:,.2f}</strong></div><div class='stat-cell'><small>EMA</small><strong>${latest_btc['EMA']:,.2f}</strong></div><div class='stat-cell'><small>Volatility</small><strong>{latest_btc['Volatility'] * 100:.2f}%</strong></div><div class='stat-cell'><small>Signal</small><strong>{bitcoin_signal['latest']}</strong></div></div>",
        unsafe_allow_html=True,
    )
    preview_fig = go.Figure()
    preview_fig.add_trace(go.Scatter(x=bitcoin_data.tail(260).index, y=bitcoin_data.tail(260)["Close"], name="Price", line={"color": "#55e2ff", "width": 2.2}))
    preview_fig.add_trace(go.Scatter(x=bitcoin_data.tail(260).index, y=bitcoin_data.tail(260)["SMA"], name="SMA", line={"color": "#8d72ff", "width": 1.5}))
    preview_fig.add_trace(go.Scatter(x=bitcoin_data.tail(260).index, y=bitcoin_data.tail(260)["EMA"], name="EMA", line={"color": "#f5c76a", "width": 1.5}))
    add_signal_traces(preview_fig, bitcoin_data.tail(260), "SMA Crossover")
    preview_fig.update_layout(**chart_layout(290))
    st.plotly_chart(preview_fig, width="stretch", config={"displayModeBar": False})
    st.page_link("pages/1_📈_Markets.py", label="Explore full analysis →", icon=":material/arrow_forward:")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)
st.markdown("<div class='section-intro'><div class='eyebrow'>Strategy engine</div><div class='section-title'>From signal to strategy.</div></div>", unsafe_allow_html=True)
strategy_columns = st.columns(4)
strategy_copy = {
    "SMA Crossover": "Trend persistence through moving-average alignment.",
    "EMA Trend": "Responsive directional signals from exponential averages.",
    "Momentum": "Directional acceleration from price movement.",
    "Mean Reversion": "Price dislocations relative to a rolling mean.",
}
for column, strategy in zip(strategy_columns, STRATEGIES):
    with column:
        with st.container(border=True):
            st.markdown(f"<div class='strategy-mini'><div class='layer-number'>{'0' + str(STRATEGIES.index(strategy) + 1)}</div><strong>{strategy}</strong><span>{strategy_copy[strategy]}</span></div>", unsafe_allow_html=True)
st.page_link("pages/2_🧠_Strategies.py", label="Explore strategy lab →", icon=":material/arrow_forward:")

st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)
backtest_left, backtest_right = st.columns([1.4, .8], gap="large")
with backtest_left:
    st.markdown("<div class='eyebrow'>Backtesting preview</div><div class='section-title'>Would your strategy have worked?</div><div class='section-copy'>Replay the SMA crossover strategy on real Bitcoin history and compare it against buy and hold.</div>", unsafe_allow_html=True)
    comparison = aligned_comparison(backtest_result, bitcoin_data, 100000.0)
    comparison_fig = go.Figure()
    comparison_fig.add_trace(go.Scatter(x=comparison["Date"], y=comparison["Strategy"], name="Strategy", line={"color": "#55e2ff", "width": 2.2}))
    comparison_fig.add_trace(go.Scatter(x=comparison["Date"], y=comparison["Buy & Hold"], name="Buy & hold", line={"color": "#8d72ff", "width": 2.2}))
    comparison_fig.update_layout(**chart_layout(300))
    st.plotly_chart(comparison_fig, width="stretch", config={"displayModeBar": False})
with backtest_right:
    with st.container(border=True):
        st.markdown("<div class='bento-label'>SMA crossover · BTC-USD</div>", unsafe_allow_html=True)
        st.metric("Initial capital", "$100,000")
        st.metric("Total return", f"{backtest_metrics['Total Return (%)']:.2f}%")
        st.metric("Sharpe ratio", f"{backtest_metrics['Sharpe Ratio']:.2f}")
        st.metric("Maximum drawdown", f"{backtest_metrics['Max Drawdown (%)']:.2f}%")
        st.page_link("pages/3_🔬_Backtesting.py", label="Run a backtest →", icon=":material/arrow_forward:")

st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)
ai_left, ai_right = st.columns([1.1, .9], gap="large")
with ai_left:
    st.markdown("<div class='eyebrow'>QuantX intelligence</div><div class='section-title'>Ask QuantX about the market.</div><div class='section-copy'>Ask for a grounded read on trend, risk, momentum and strategy using the same evidence that powers the feature pages.</div>", unsafe_allow_html=True)
with ai_right:
    with st.container(border=True):
        st.markdown("<div class='ai-box'><div class='panel-label'>✦ QuantX intelligence</div><div class='ai-prompt'>“Analyze Bitcoin’s current trend and risk profile.”</div>", unsafe_allow_html=True)
        if st.button("Analyze →", key="home_ai_analyze"):
            prompt = f"Analyze Bitcoin using these historical observations: latest price {latest_btc['Close']:.4f}, daily return {latest_btc['Daily_Return'] * 100:.2f}%, annualized volatility {latest_btc['Annualized_Volatility'] * 100:.2f}%, SMA {latest_btc['SMA']:.4f}, EMA {latest_btc['EMA']:.4f}, backtest Sharpe {backtest_metrics['Sharpe Ratio']:.2f}, and maximum drawdown {backtest_metrics['Max Drawdown (%)']:.2f}%. Return concise sections: Trend, Risk, Momentum, Strategy. Historical evidence only."
            try:
                response = analyze_market(prompt)
                st.success("Analysis complete")
                st.markdown(response)
            except Exception:
                st.warning("AI analysis is unavailable right now. Configure FEATHERLESS_API_KEY to enable the research assistant. No API key is displayed.")
        st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)
with st.container(border=True):
    trust_columns = st.columns(4)
    trust_stats = [("3", "Supported assets"), ("4", "Quantitative strategies"), ("7+", "Risk & performance metrics"), ("AI", "Powered analysis")]
    for column, (value, label) in zip(trust_columns, trust_stats):
        with column:
            st.markdown(f"<div class='trust-value'>{value}</div><div class='trust-label'>{label}</div>", unsafe_allow_html=True)

st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)
with st.container(border=True):
    st.markdown("<div class='section-intro'><div class='eyebrow'>QuantX research workspace</div><div class='section-title'>Ready to explore the market differently?</div><div class='section-copy'>From raw historical data to quantitative insight — everything you need is in one platform.</div></div>", unsafe_allow_html=True)
    with st.container(horizontal=True, gap="small"):
        st.page_link("pages/1_📈_Markets.py", label="Explore markets", icon=":material/show_chart:")
        st.page_link("pages/3_🔬_Backtesting.py", label="Run your first backtest", icon=":material/science:")

st.markdown(
    """
    <div class="footer"><div class="brand-wrap"><div class="brand-mark">Q</div><div><div class="brand-title">QuantX</div><div class="brand-sub">Quantitative multi-asset financial intelligence</div></div></div><div style="margin-top:.8rem;">Markets · Strategies · Backtesting · Risk analysis · AI insights</div><div style="margin-top:.35rem;">Built for quantitative research and financial intelligence.</div></div>
    """,
    unsafe_allow_html=True,
)
