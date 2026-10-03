from __future__ import annotations

import html
import json
import math
import random
from typing import Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components
from plotly.subplots import make_subplots

from optimizer import (
    CATEGORIES,
    MENU_CATALOG,
    PRIORITIES,
    create_ingredient,
    delete_ingredient,
    evaluate,
    initialize_db,
    list_ingredients,
    list_runs,
    replace_with_random_data,
    reset_sample_data,
    run_greedy,
    run_knapsack,
    save_run,
    sort_items,
    update_ingredient,
    utility,
)


st.set_page_config(
    page_title="Food Ingredient Purchase Optimizer",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="collapsed",
)


CSS = r"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');
:root {
  --ink:#18352c; --muted:#71827a; --green:#17845e; --green-dark:#116b4c;
  --mint:#e4f5ec; --lime:#d9f27d; --orange:#f4a443; --line:#e4ece6;
  --card:rgba(255,255,255,.86); --cursor-x:50vw; --cursor-y:20vh;
}
html { scroll-behavior:smooth; scroll-padding-top:96px; }
body, [data-testid="stAppViewContainer"] { background:#f5f8f4; color:var(--ink); }
[data-testid="stAppViewContainer"] { background-image:radial-gradient(ellipse at 10% 5%,rgba(210,243,224,.52),transparent 28%),radial-gradient(ellipse at 94% 16%,rgba(249,235,204,.35),transparent 24%),linear-gradient(180deg,#f8faf7 0%,#f3f7f2 100%); }
[data-testid="stAppViewContainer"]:before { content:""; position:fixed; inset:0; pointer-events:none; z-index:0; opacity:.28; background-image:linear-gradient(rgba(37,99,75,.025) 1px,transparent 1px),linear-gradient(90deg,rgba(37,99,75,.025) 1px,transparent 1px); background-size:36px 36px; }
[data-testid="stAppViewContainer"]:after { content:""; position:fixed; inset:0; pointer-events:none; z-index:0; background:radial-gradient(430px circle at var(--cursor-x) var(--cursor-y),rgba(94,193,142,.095),transparent 72%); }
[data-testid="stHeader"] { background:transparent; }
[data-testid="stMainBlockContainer"] { max-width:1580px; padding:1rem clamp(16px,3vw,48px) 4rem !important; position:relative; z-index:1; }
#MainMenu, footer { visibility:hidden; }
* { font-family:'DM Sans',Inter,system-ui,sans-serif; }
h1,h2,h3,h4 { font-family:Manrope,'DM Sans',sans-serif !important; color:var(--ink); letter-spacing:-.045em; }
.nav-wrap { position:sticky; top:0; z-index:999; display:flex; justify-content:space-between; align-items:center; gap:20px; margin:0 0 1.1rem; padding:11px 16px; border:1px solid rgba(218,231,220,.92); border-radius:16px; background:rgba(250,252,249,.96); backdrop-filter:blur(18px); box-shadow:0 8px 26px rgba(31,75,53,.07); }
.nav-brand { color:var(--ink) !important; font-weight:800; font-size:15px; letter-spacing:-.03em; text-decoration:none !important; display:flex; align-items:center; gap:9px; white-space:nowrap; }
.brand-mark { width:31px;height:31px;display:grid;place-items:center;border-radius:10px;background:linear-gradient(135deg,#d8f3df,#ebf8c0);font-size:16px; }
.nav-links { display:flex; align-items:center; gap:23px; }
.nav-links a { color:#718078 !important; text-decoration:none !important; font-size:12px; font-weight:600; transition:color .2s ease; }
.nav-links a:hover { color:var(--green); }
.nav-cta { background:#167b58; color:white !important; padding:10px 14px; border-radius:11px; box-shadow:0 5px 13px rgba(23,132,94,.15); }
.hero-shell { position:relative; display:grid; grid-template-columns:minmax(0,1.04fr) minmax(310px,.96fr); align-items:center; gap:14px; overflow:hidden; scroll-margin-top:96px; border:1px solid #dfeae1; border-radius:30px; padding:clamp(27px,4.1vw,58px); min-height:500px; background:radial-gradient(ellipse at 78% 46%,rgba(222,244,203,.75),transparent 35%),linear-gradient(117deg,#fff 0%,#fbfdf7 52%,#eff8e9 100%); box-shadow:0 25px 80px rgba(41,79,56,.105); }
.hero-shell:before { content:""; position:absolute; width:490px;height:490px; right:4%;top:-170px;border-radius:50%; background:radial-gradient(circle,rgba(217,242,125,.22),rgba(93,182,121,.06) 53%,transparent 72%); filter:blur(2px); pointer-events:none; }
.hero-copy { position:relative; z-index:4; max-width:660px; }
.eyebrow { display:inline-flex; align-items:center; gap:8px; padding:7px 11px; border:1px solid #d9e9d9; border-radius:100px; color:#337559; background:rgba(255,255,255,.67); font-size:10px; font-weight:800; letter-spacing:.12em; text-transform:uppercase; }
.eyebrow-dot { width:7px;height:7px;border-radius:50%;background:#53bd82;box-shadow:0 0 0 4px rgba(83,189,130,.13); }
.hero-title { margin:18px 0 13px; font:800 clamp(40px,5.5vw,70px)/.99 Manrope,sans-serif; letter-spacing:-.068em; color:#18372c; max-width:700px; }
.hero-title span { color:#16845b; }
.hero-sub { max-width:560px; color:#6d7d74; font-size:15px; line-height:1.75; }
.hero-actions { display:flex; gap:11px; flex-wrap:wrap; margin-top:24px; }
.hero-btn { display:inline-flex; align-items:center; justify-content:center; gap:8px; padding:12px 17px; border-radius:12px; text-decoration:none !important; font-size:12px; font-weight:700; transition:transform .25s cubic-bezier(.22,1,.36,1),box-shadow .25s,background .2s; }
.hero-btn:hover { transform:translateY(-3px); }
.hero-btn.primary { color:#fff !important;background:linear-gradient(135deg,#1c9367,#127653);box-shadow:0 9px 19px rgba(22,132,91,.2); }
.hero-btn.secondary { color:#23664d !important;border:1px solid #dce9df;background:rgba(255,255,255,.75); }
.hero-proof { display:flex; gap:16px; align-items:center; margin-top:26px; color:#7a8981; font-size:11px; }
.hero-proof strong { color:#375c48; }
.hero-art { position:relative; z-index:2; width:100%; height:410px; perspective:1100px; transform-style:preserve-3d; }
.scene3d-stage { position:absolute; inset:0; transform-style:preserve-3d; transform:rotateX(var(--scene-pitch,0deg)) rotateY(var(--scene-yaw,0deg)); transition:transform .24s cubic-bezier(.22,1,.36,1); }
.scene-glow { position:absolute; width:310px;height:310px;left:50%;top:47%;transform:translate(-50%,-50%) translateZ(-85px);border-radius:50%;background:radial-gradient(circle,rgba(172,224,156,.42),rgba(230,246,214,.34) 45%,transparent 72%);filter:blur(8px); }
.scene-orbit { position:absolute;left:50%;top:47%;width:330px;height:178px;border:1px solid rgba(69,144,95,.25);border-radius:50%;transform-style:preserve-3d; }
.scene-orbit.orbit-a { transform:translate(-50%,-50%) rotateX(73deg) rotateZ(-18deg) translateZ(-18px); }
.scene-orbit.orbit-b { width:276px;height:148px;border-color:rgba(226,165,79,.32);transform:translate(-50%,-50%) rotateX(73deg) rotateZ(52deg) translateZ(20px); }
.scene-orbit.orbit-c { width:235px;height:126px;border-style:dashed;border-color:rgba(74,157,110,.25);transform:translate(-50%,-50%) rotateX(72deg) rotateZ(102deg) translateZ(54px); }
.scene-platform { position:absolute;left:50%;top:52%;width:258px;height:182px;border-radius:50%;transform-style:preserve-3d; }
.scene-platform.shadow { transform:translate(-50%,-50%) rotateX(71deg) translateZ(-35px);background:rgba(41,96,58,.15);filter:blur(12px); }
.scene-platform.base { transform:translate(-50%,-50%) rotateX(71deg) translateZ(-5px);background:linear-gradient(145deg,#b8dca6,#81b987 50%,#589b76);border:1px solid rgba(255,255,255,.8);box-shadow:0 28px 34px rgba(41,95,62,.21),inset 0 5px 10px rgba(255,255,255,.68),inset 0 -10px 15px rgba(38,96,66,.16); }
.scene-platform.rim { width:224px;height:148px;transform:translate(-50%,-50%) rotateX(71deg) translateZ(3px);background:linear-gradient(135deg,#fbfff2,#d9ecc8 60%,#b3d5a8);border:1px solid rgba(255,255,255,.98);box-shadow:0 4px 0 rgba(84,143,93,.16),inset 0 0 0 5px rgba(255,255,255,.55); }
.scene-center { position:absolute;left:50%;top:42%;width:116px;height:116px;display:grid;place-items:center;transform:translate(-50%,-50%) translateZ(75px) rotateX(-7deg);border:1px solid rgba(255,255,255,.88);border-radius:40px;background:linear-gradient(145deg,#fff,#edf7e5);box-shadow:0 24px 38px rgba(48,103,65,.2),inset 0 2px 5px white;font-size:55px;animation:bob3d 5.5s ease-in-out infinite; }
.ingredient-orb { position:absolute;display:grid;place-items:center;width:63px;height:63px;border:1px solid rgba(255,255,255,.92);border-radius:23px;background:linear-gradient(145deg,#fff,#f0f6e9);box-shadow:0 16px 23px rgba(51,96,62,.17),inset 0 2px 4px white;font-size:30px;transform-style:preserve-3d;animation:bob3d 5.1s ease-in-out infinite; }
.ingredient-orb.tomato { top:112px;left:11%;transform:rotateY(-17deg) rotateX(9deg) translateZ(106px);animation-delay:-1.4s; }
.ingredient-orb.avocado { top:121px;right:12%;transform:rotateY(18deg) rotateX(-8deg) translateZ(65px);animation-delay:-2.6s; }
.ingredient-orb.pepper { bottom:69px;left:13%;transform:rotateY(16deg) rotateX(7deg) translateZ(82px);animation-delay:-3.4s; }
.ingredient-orb.leaf { top:155px;right:10%;transform:rotateY(-18deg) rotateX(-6deg) translateZ(112px);animation-delay:-.7s; }
.scene-card { position:absolute;z-index:5;min-width:122px;padding:11px 13px;border:1px solid rgba(255,255,255,.93);border-radius:15px;background:rgba(255,255,255,.94);box-shadow:0 17px 32px rgba(44,83,55,.15),inset 0 1px white;backdrop-filter:blur(14px);transform-style:preserve-3d; }
.scene-card small { display:block;color:#829087;font-size:8px;font-weight:800;letter-spacing:.12em;text-transform:uppercase; }
.scene-card strong { display:block;color:#204733;font:800 13px Manrope,sans-serif;margin-top:5px; }
.scene-card span { display:block;color:#34845f;font-size:9px;font-weight:700;margin-top:3px; }
.scene-card.card-input { left:0;top:27px;transform:translateZ(90px) rotateY(7deg) rotateX(4deg); }
.scene-card.card-budget { right:0;top:41px;transform:translateZ(50px) rotateY(-9deg) rotateX(3deg); }
.scene-card.card-result { right:2%;bottom:23px;transform:translateZ(115px) rotateY(-6deg) rotateX(-4deg); }
.scene-label { position:absolute;left:2%;bottom:2px;transform:translateZ(30px);padding:7px 10px;border:1px solid rgba(116,169,119,.2);border-radius:999px;background:rgba(255,255,255,.9);color:#668774;font-size:8px;font-weight:800;letter-spacing:.13em;white-space:nowrap; }
.section-head { display:flex; justify-content:space-between; align-items:end; gap:18px; margin:43px 0 17px; }
.section-kicker { display:block; color:#3b9870; font-size:10px; letter-spacing:.15em; font-weight:800; text-transform:uppercase; margin-bottom:7px; }
.section-title { margin:0; color:#1b3a2f; font:800 clamp(24px,3vw,34px)/1.15 Manrope,sans-serif; letter-spacing:-.055em; }
.section-sub { margin:7px 0 0;color:#7b8981;font-size:12px;line-height:1.6;max-width:760px; }
.metric-card { position:relative; overflow:hidden; min-height:119px; padding:17px 17px 15px; border:1px solid rgba(224,234,225,.95); border-radius:17px; background:rgba(255,255,255,.94); box-shadow:0 9px 27px rgba(42,77,52,.06); transition:transform .25s cubic-bezier(.22,1,.36,1),box-shadow .25s,border-color .2s; transform:perspective(900px) rotateX(var(--rx,0deg)) rotateY(var(--ry,0deg)); }
.metric-card:hover { border-color:#cae3d1; box-shadow:0 17px 32px rgba(42,93,59,.10); }
.metric-card:after { content:"";position:absolute;inset:0;background:radial-gradient(200px circle at var(--spot-x,50%) var(--spot-y,50%),rgba(120,202,146,.13),transparent 70%);pointer-events:none; }
.metric-label { color:#819087; font-size:10px; font-weight:700; letter-spacing:.08em; text-transform:uppercase; }
.metric-value { margin-top:10px;color:#1b3c30;font:800 26px/1 Manrope,sans-serif;letter-spacing:-.05em; }
.metric-note { margin-top:8px;color:#91a097;font-size:10px; }
.metric-icon { position:absolute;right:15px;top:15px;width:29px;height:29px;border-radius:10px;background:#eff8ee;display:grid;place-items:center;font-size:14px; }
.panel { border:1px solid #e2ebe3; border-radius:20px; background:rgba(255,255,255,.95); box-shadow:0 10px 28px rgba(41,75,51,.055); padding:20px; }
.panel-soft { background:linear-gradient(135deg,rgba(255,255,255,.92),rgba(245,251,243,.94)); }
.panel-label { color:#3d9871; font-size:9px; font-weight:800; letter-spacing:.13em; text-transform:uppercase; }
.item-chip { display:flex;align-items:center;justify-content:space-between;gap:10px;padding:10px 11px;border:1px solid #e2ebe3;background:#fff;border-radius:12px;margin:6px 0;transition:transform .22s ease,box-shadow .22s,border-color .22s;transform:perspective(700px) rotateX(var(--rx,0deg)) rotateY(var(--ry,0deg)); }
.item-chip:hover { border-color:#bfdfc8; transform:translateY(-2px); box-shadow:0 7px 17px rgba(32,92,55,.07); }
.item-chip-name { color:#294538;font-size:12px;font-weight:700; }
.item-chip-meta { color:#87958d;font-size:10px;margin-top:2px; }
.pill { display:inline-flex; align-items:center; gap:5px; border-radius:100px; padding:5px 9px; color:#398361; background:#edf8ef; font-size:10px; font-weight:700; }
.pill.orange { color:#a76a20;background:#fff5e5; }
.pill.gray { color:#6f8075;background:#f0f4f0; }
.decision-good { color:#16805a;font-weight:800; }
.decision-bad { color:#ad6b33;font-weight:800; }
.alg-card { height:100%; border:1px solid #e4ece4;border-radius:17px;padding:17px;background:linear-gradient(145deg,#fff,#f7faf5);transform:perspective(750px) rotateX(var(--rx,0deg)) rotateY(var(--ry,0deg));transition:transform .24s ease,box-shadow .24s; }
.alg-card h4 { margin:8px 0 5px;font-size:15px; }
.alg-card p { margin:0;color:#78877e;font-size:11px;line-height:1.6; }
.formula { border-left:3px solid #45a777;background:#f1f8f1;color:#34624b;padding:12px 14px;border-radius:0 12px 12px 0;font-family:ui-monospace,monospace;font-size:11px;line-height:1.6;overflow:auto; }
.timeline-step { padding:10px 12px;border:1px solid #e5eee6;border-radius:12px;background:#fff;color:#53675b;font-size:11px;transform:perspective(650px) rotateX(var(--rx,0deg)) rotateY(var(--ry,0deg));transition:transform .2s ease,box-shadow .2s; }
.timeline-step strong { color:#16845c; }
.status-good { color:#1c8b63;background:#eaf7ed;border:1px solid #d7edda;border-radius:999px;padding:5px 9px;font-size:10px;font-weight:700; }
.footer-note { color:#91a097;font-size:10px;text-align:center;padding:29px 0 6px; }
.reveal { opacity:0; transform:translateY(13px) scale(.985); transition:opacity .65s cubic-bezier(.22,1,.36,1),transform .65s cubic-bezier(.22,1,.36,1); }
.reveal.revealed { opacity:1;transform:translateY(0) scale(1); }
div[data-testid="stButton"] button, div[data-testid="stFormSubmitButton"] button { border-radius:11px; font-weight:700; transition:transform .2s cubic-bezier(.22,1,.36,1),box-shadow .2s,background .2s; }
div[data-testid="stButton"] button:hover, div[data-testid="stFormSubmitButton"] button:hover { transform:translateY(-2px);box-shadow:0 8px 17px rgba(27,119,80,.14); }
div[data-testid="stButton"] button:active, div[data-testid="stFormSubmitButton"] button:active { transform:scale(.98); }
div[data-testid="stTabs"] button[aria-selected="true"] { color:#167b58; }
div[data-testid="stDataFrame"] { border:1px solid #e5ece5;border-radius:14px;overflow:hidden; }
div[data-testid="stPlotlyChart"] { border:1px solid #e5ece5;border-radius:15px;background:rgba(255,255,255,.75);padding:5px;box-shadow:0 5px 16px rgba(42,77,52,.035); }
div[data-testid="stSelectbox"] div[data-baseweb="select"] > div, div[data-testid="stNumberInput"] input, div[data-testid="stTextInput"] input { border-radius:10px; }
[data-testid="stMetric"] { background:transparent; }
.stAlert { border-radius:13px; }
/* Keep Streamlit's native controls in the same light, garden-green visual system. */
[data-testid="stWidgetLabel"], [data-testid="stWidgetLabel"] p { color:#496456 !important; }
[data-testid="stSelectbox"] [data-baseweb="select"] > div,
[data-testid="stMultiSelect"] [data-baseweb="select"] > div,
[data-testid="stNumberInput"] input, [data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea { background:#fff !important; border-color:#dce9df !important; color:#18352c !important; }
[data-testid="stSelectbox"] [data-baseweb="select"] *,
[data-testid="stMultiSelect"] [data-baseweb="select"] * { color:#18352c !important; }
[data-testid="stSelectbox"] .react-aria-ComboBox [role="group"],
[data-testid="stMultiSelect"] .react-aria-ComboBox [role="group"] { background:#fff !important; border:1px solid #dce9df !important; border-radius:10px !important; box-shadow:0 2px 5px rgba(39,83,55,.035) !important; }
[data-testid="stSelectbox"] input[role="combobox"],
[data-testid="stMultiSelect"] input[role="combobox"] { background:transparent !important; color:#18352c !important; }
[data-testid="stSelectbox"] button[aria-haspopup="listbox"],
[data-testid="stMultiSelect"] button[aria-haspopup="listbox"] { background:transparent !important; color:#557163 !important; }
[data-testid="stRadioOption"] { color:#345444 !important; }
[data-testid="stRadioOption"] > div { padding:5px 7px; border-radius:9px; }
[data-testid="stRadioOption"] > div > div:first-child { background:#fff !important; border:1px solid #cbdacf !important; }
[data-testid="stRadioOption"]:has(input:checked) > div > div:first-child { background:#edf7ef !important; border-color:#16845c !important; }
[data-testid="stRadioOption"]:has(input:checked) > div > div:first-child > div { background:#16845c !important; }
[data-testid="stSlider"] [data-rac][data-orientation="horizontal"] { accent-color:#16845c !important; }
[data-testid="stSlider"] [data-rac][style*="position: absolute"] { background:#16845c !important; }
[data-testid="stSlider"] [data-testid="stSliderThumbValue"] { background:#fff !important; border:1px solid #dce9df !important; border-radius:999px !important; color:#16845c !important; padding:1px 6px !important; }
[data-testid="stSlider"] [data-testid="stSliderThumbValue"] p { color:#16845c !important; }
[data-testid="stSlider"] [data-testid="stSliderTickBar"] { color:#84958a !important; }
[data-testid="stSlider"] [role="group"][data-orientation="horizontal"] > div[data-rac][data-orientation="horizontal"] > div:first-child { filter:hue-rotate(105deg) saturate(.7); }
[data-testid="stExpander"] details > summary { background:rgba(255,255,255,.92) !important; border:1px solid #e2ebe3 !important; border-radius:12px !important; color:#294538 !important; }
[data-testid="stExpander"] details[open] > summary { background:#f2f8f1 !important; border-color:#dce9df !important; color:#294538 !important; }
[data-testid="stExpander"] details[open] > summary * { color:#496456 !important; }
[data-testid="stExpander"] details[open] > div { background:rgba(255,255,255,.88) !important; border-color:#e2ebe3 !important; }
div[data-testid="stButton"] button[kind="primary"],
div[data-testid="stFormSubmitButton"] button[kind="primary"] { color:#fff !important; background:linear-gradient(135deg,#1c9367,#127653) !important; border:1px solid #127653 !important; }
div[data-testid="stButton"] button[kind="secondary"],
div[data-testid="stFormSubmitButton"] button[kind="secondary"] { color:#23664d !important; background:#fff !important; border:1px solid #dce9df !important; }
div[data-testid="stVerticalBlockBorderWrapper"] { border-color:#dfeae1 !important; border-radius:20px !important; background:rgba(255,255,255,.68); }
[data-testid="stToolbar"] .stDeployButton { display:none !important; }
[data-testid="stProgressBarTrack"] { background:#e8f1e9 !important; border-radius:999px !important; }
[data-testid="stProgressBarTrack"] > div { background:linear-gradient(90deg,#16845c,#75bd83) !important; border-radius:999px !important; }
@keyframes bob3d { 0%,100%{ translate:0 0; } 50%{ translate:0 -9px; } }
@media(max-width:900px) { .hero-shell{grid-template-columns:minmax(0,1.02fr) minmax(290px,.98fr);min-height:470px;padding:32px 28px}.hero-art{height:360px;opacity:1}.hero-copy{max-width:100%}.hero-title{font-size:clamp(39px,5vw,52px)}.scene-card{min-width:108px;padding:9px 10px}.scene-orbit.orbit-a{width:290px}.scene-platform{width:232px;height:164px}.scene-platform.base{width:232px;height:164px}.scene-platform.rim{width:202px;height:134px}.nav-links{gap:11px}.nav-links a{font-size:10px} }
@media(max-width:700px) { .hero-shell{grid-template-columns:1fr;gap:0;padding:27px 23px 9px;min-height:0}.hero-copy{max-width:100%}.hero-title{font-size:clamp(38px,10vw,54px)}.hero-art{height:330px;margin-top:0}.hero-proof{gap:9px;flex-wrap:wrap}.scene-card.card-input{left:0}.scene-card.card-budget{right:0}.scene-card.card-result{right:0}.nav-wrap{padding:9px 11px}.nav-links a:not(.nav-cta){display:none}.hero-sub{font-size:13px}.section-head{margin-top:32px}.panel{padding:15px} }
@media(max-width:420px) { .hero-shell{padding-left:18px;padding-right:18px}.hero-art{height:285px;transform:scale(.9);transform-origin:center top;margin-bottom:-22px}.scene-card{min-width:100px}.scene-card.card-input{top:18px}.scene-card.card-budget{top:27px}.scene-card.card-result{bottom:20px}.scene-orbit.orbit-a{width:250px}.scene-platform.base{width:205px;height:144px}.scene-platform.rim{width:178px;height:119px}.ingredient-orb{width:52px;height:52px;font-size:26px;border-radius:19px} }
@media(prefers-reduced-motion:reduce) { *,*:before,*:after { scroll-behavior:auto !important;animation-duration:.01ms !important;animation-iteration-count:1 !important;transition-duration:.01ms !important; } .reveal{opacity:1;transform:none;} }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# Pointer glow, restrained card tilt, and viewport reveal are attached to the Streamlit document.
components.html(r"""
<script>
(() => {
  try {
    const doc = window.parent.document;
    if (doc.__foodOptimizerInteractions) return;
    doc.__foodOptimizerInteractions = true;
    let raf = 0;
    doc.addEventListener('pointermove', event => {
      if (raf) return;
      raf = requestAnimationFrame(() => {
        doc.documentElement.style.setProperty('--cursor-x', event.clientX + 'px');
        doc.documentElement.style.setProperty('--cursor-y', event.clientY + 'px');
        const scene = event.target.closest && event.target.closest('.hero-art');
        if (scene) {
          const box = scene.getBoundingClientRect();
          const x = (event.clientX - box.left) / box.width;
          const y = (event.clientY - box.top) / box.height;
          scene.style.setProperty('--scene-yaw', ((x - .5) * 17) + 'deg');
          scene.style.setProperty('--scene-pitch', ((.5 - y) * 12) + 'deg');
        }
        const card = event.target.closest && event.target.closest('.metric-card,.item-chip,.alg-card,.timeline-step');
        if (card) {
          const box = card.getBoundingClientRect();
          const x = (event.clientX - box.left) / box.width;
          const y = (event.clientY - box.top) / box.height;
          card.style.setProperty('--spot-x', (x * 100) + '%');
          card.style.setProperty('--spot-y', (y * 100) + '%');
          card.style.setProperty('--ry', ((x - .5) * 6) + 'deg');
          card.style.setProperty('--rx', ((.5 - y) * 4) + 'deg');
        }
        const magnet = event.target.closest && event.target.closest('.hero-btn,.nav-cta,[data-testid="stButton"] button,[data-testid="stFormSubmitButton"] button');
        if (magnet) {
          const box = magnet.getBoundingClientRect();
          const dx = ((event.clientX - box.left) / box.width - .5) * 5;
          const dy = ((event.clientY - box.top) / box.height - .5) * 4;
          magnet.style.transform = `translate(${dx.toFixed(1)}px,${dy.toFixed(1)}px)`;
        }
        raf = 0;
      });
    }, {passive:true});
    doc.addEventListener('pointerout', event => {
      const scene = event.target.closest && event.target.closest('.hero-art');
      if (scene && (!event.relatedTarget || !scene.contains(event.relatedTarget))) {
        scene.style.setProperty('--scene-yaw', '0deg'); scene.style.setProperty('--scene-pitch', '0deg');
      }
      const card = event.target.closest && event.target.closest('.metric-card,.item-chip,.alg-card,.timeline-step');
      if (card && (!event.relatedTarget || !card.contains(event.relatedTarget))) {
        card.style.setProperty('--rx', '0deg'); card.style.setProperty('--ry', '0deg');
      }
      const magnet = event.target.closest && event.target.closest('.hero-btn,.nav-cta,[data-testid="stButton"] button,[data-testid="stFormSubmitButton"] button');
      if (magnet && (!event.relatedTarget || !magnet.contains(event.relatedTarget))) magnet.style.transform = '';
    }, {passive:true});
    const reveal = node => {
      if (node.nodeType !== 1) return;
      if (node.matches('.section-head,.metric-card,.panel,.alg-card')) node.classList.add('reveal');
      node.querySelectorAll && node.querySelectorAll('.section-head,.metric-card,.panel,.alg-card').forEach(el => el.classList.add('reveal'));
    };
    const countUp = element => {
      if (element.dataset.counted) return;
      element.dataset.counted = 'true';
      const original = element.dataset.value || element.textContent;
      const match = original.match(/^(₹?)([\d,]+(?:\.\d+)?)(.*)$/);
      if (!match || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
      const start = 0, end = Number(match[2].replaceAll(',', ''));
      const decimals = (match[2].split('.')[1] || '').length;
      const began = performance.now(), duration = 760;
      const tick = now => {
        const p = Math.min(1, (now - began) / duration), eased = 1 - Math.pow(1 - p, 4);
        const num = (start + (end - start) * eased).toLocaleString('en-IN', {minimumFractionDigits:decimals, maximumFractionDigits:decimals});
        element.textContent = match[1] + num + match[3];
        if (p < 1) requestAnimationFrame(tick);
      };
      requestAnimationFrame(tick);
    };
    const io = new IntersectionObserver(entries => entries.forEach(entry => {
      if (entry.isIntersecting) {
        if (entry.target.matches('.metric-value')) countUp(entry.target);
        else entry.target.classList.add('revealed');
        io.unobserve(entry.target);
      }
    }), {threshold:.08});
    const observe = root => {
      root.querySelectorAll && root.querySelectorAll('.reveal:not(.revealed)').forEach(el => io.observe(el));
      root.querySelectorAll && root.querySelectorAll('.metric-value[data-value]:not([data-counted])').forEach(el => io.observe(el));
    };
    reveal(doc.body); observe(doc);
    new MutationObserver(records => records.forEach(record => record.addedNodes.forEach(node => { reveal(node); observe(node); })))
      .observe(doc.body, {childList:true,subtree:true});
  } catch (error) { /* visual enhancement only; the optimizer works without it */ }
})();
</script>
""", height=0, width=0)


def section_head(kicker: str, title: str, subtitle: str = "") -> None:
    subtitle_html = f'<p class="section-sub">{html.escape(subtitle)}</p>' if subtitle else ""
    st.markdown(
        f'<div class="section-head"><div><span class="section-kicker">{html.escape(kicker)}</span>'
        f'<h2 class="section-title">{html.escape(title)}</h2>'
        f'{subtitle_html}</div></div>',
        unsafe_allow_html=True,
    )


def metric_card(icon: str, label: str, value: str, note: str = "") -> None:
    st.markdown(
        f'<div class="metric-card"><span class="metric-icon">{icon}</span>'
        f'<div class="metric-label">{html.escape(label)}</div><div class="metric-value" data-value="{html.escape(value, quote=True)}">{html.escape(value)}</div>'
        f'<div class="metric-note">{html.escape(note)}</div></div>', unsafe_allow_html=True,
    )


def money(value: float | int) -> str:
    return f"₹{int(round(value)):,}"


def sync_budget_from_slider() -> None:
    st.session_state.budget = st.session_state.budget_slider


def sync_budget_from_number() -> None:
    st.session_state.budget_slider = st.session_state.budget


def safe_result(algorithm_result: dict[str, Any], items: list[dict[str, Any]], budget: int, objective: str, strategy: str = "") -> dict[str, Any]:
    result = dict(algorithm_result)
    result["budget"] = int(budget)
    result["priority"] = objective
    result["strategy"] = strategy or result.get("strategy", "")
    result["metrics"] = evaluate(items, result["selected_ids"], budget)
    result["items"] = items
    return result


def run_and_save(items: list[dict[str, Any]], budget: int, objective: str, algorithm: str, strategy: str = "Balanced Score") -> dict[str, Any]:
    if algorithm == "Greedy":
        raw = run_greedy(items, budget, strategy, objective)
    else:
        raw = run_knapsack(items, budget, objective)
    result = safe_result(raw, items, budget, objective, strategy)
    result["summary"] = {"elapsed_ms": result["elapsed_ms"], "selected_count": result["metrics"]["items_selected"]}
    save_run(result)
    return result


def html_item_chip(item: dict[str, Any], selected: bool, why: str = "") -> str:
    safe_name = html.escape(str(item["name"]))
    color = "#16805a" if selected else "#a76b35"
    mark = "✓" if selected else "×"
    sub = f'{money(item["cost"])} · {int(item["coverage"])} menus · {float(item["waste_pct"]):.1f}% waste'
    reason = f'<div class="item-chip-meta" style="margin-top:6px;line-height:1.5">{html.escape(why)}</div>' if why else ""
    return (f'<div class="item-chip"><div><div class="item-chip-name">{safe_name}</div>'
            f'<div class="item-chip-meta">{sub}</div>{reason}</div>'
            f'<span style="font-size:17px;font-weight:800;color:{color}">{mark}</span></div>')


def explain_decisions(result: dict[str, Any], items: list[dict[str, Any]]) -> tuple[list[tuple[dict[str, Any], str]], list[tuple[dict[str, Any], str]]]:
    chosen_ids = set(result["selected_ids"])
    chosen = [x for x in items if x["id"] in chosen_ids]
    rejected = [x for x in items if x["id"] not in chosen_ids]
    chosen_reasons: dict[int, str] = {}
    rejected_reasons: dict[int, str] = {}
    if result["algorithm"] == "Greedy":
        for step in result.get("decisions", []):
            (chosen_reasons if step["id"] in chosen_ids else rejected_reasons)[step["id"]] = step["why"]
    else:
        remaining = int(result["budget"]) - sum(int(x["cost"]) for x in chosen)
        for item in chosen:
            chosen_reasons[item["id"]] = (
                f"Included in the highest-value feasible combination for {result['priority'].lower()}; "
                f"its objective value is {utility(item, result['priority']) / 10:.0f} points."
            )
        for item in rejected:
            if int(item["cost"]) > remaining:
                reason = f"Adding it would exceed the ₹{remaining:,} left in the optimal plan."
            elif utility(item, result["priority"]) == 0:
                reason = "It fits by itself, but its weighted score is zero after the waste penalty, so it does not improve the DP objective."
            else:
                reason = (f"The selected combination achieves a higher total {result['priority'].lower()} "
                          f"objective for this capacity once all competing items are considered.")
            rejected_reasons[item["id"]] = reason
    return ([(x, chosen_reasons.get(x["id"], "Selected by the algorithm's objective and budget rule.")) for x in chosen],
            [(x, rejected_reasons.get(x["id"], "Not included in the selected plan.")) for x in rejected])


def plotly_style(fig, height: int = 310):
    fig.update_layout(
        height=height, margin=dict(l=8, r=10, t=26, b=9),
        paper_bgcolor="rgba(255,255,255,0)", plot_bgcolor="rgba(255,255,255,0)",
        font=dict(family="DM Sans, sans-serif", color="#607168", size=11),
        legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0),
        hoverlabel=dict(bgcolor="#fff", bordercolor="#dfe9e1", font_color="#244a37"),
    )
    fig.update_xaxes(showgrid=False, zeroline=False, linecolor="#e7eee8")
    fig.update_yaxes(gridcolor="#eef3ee", zeroline=False, linecolor="#e7eee8")
    return fig


def render_metric_row(metrics: dict[str, Any], budget: int) -> None:
    cols = st.columns(5)
    values = [
        ("₹", "Budget used", f'{money(metrics["total_cost"])}', f'{money(metrics["remaining"])} remaining'),
        ("⌂", "Menu coverage", f'{metrics["coverage_pct"]:.0f}%', f'{metrics["coverage_count"]} of {len(MENU_CATALOG)} menus'),
        ("♻", "Expected waste", f'{metrics["waste_pct"]:.1f}%', f'{metrics["waste_exposure"]:.0f} rupees at risk'),
        ("◈", "Items selected", str(metrics["items_selected"]), "Whole purchase units"),
        ("✦", "Plan score", f'{metrics["score"]:.1f}', "Coverage · waste · spend"),
    ]
    for col, (icon, label, value, note) in zip(cols, values):
        with col:
            metric_card(icon, label, value, note)


def build_dp_view(result: dict[str, Any], items: list[dict[str, Any]], budget: int) -> pd.DataFrame:
    rows = result.get("dp_rows", [])
    if not rows:
        return pd.DataFrame()
    capacities = result.get("dp_capacities", sorted(set([0, budget, *[round(budget * fraction) for fraction in (.2, .4, .6, .8)]])))
    data = []
    for index, (item, values) in enumerate(zip(items, rows), 1):
        row = {"Item considered": f"{index:02d} · {item['name']}"}
        for cap, value in zip(capacities, values):
            row[f"₹{cap:,}"] = round(value / 10, 1)
        data.append(row)
    return pd.DataFrame(data)


try:
    initialize_db()
except Exception as exc:
    st.error(f"The local ingredient database could not be opened: {exc}")
    st.stop()

items = list_ingredients()
if "budget" not in st.session_state:
    st.session_state.budget = 5000
if "budget_slider" not in st.session_state:
    st.session_state.budget_slider = int(st.session_state.budget)
if "objective" not in st.session_state:
    st.session_state.objective = "Balanced Optimization"
if "algorithm_choice" not in st.session_state:
    st.session_state.algorithm_choice = "Compare Both"
if st.session_state.get("latest_result") is None:
    initial = safe_result(run_knapsack(items, st.session_state.budget, st.session_state.objective), items, st.session_state.budget, st.session_state.objective)
    st.session_state.latest_result = initial
if "comparison" not in st.session_state:
    st.session_state.comparison = None


# Sticky product navigation and hero.
st.markdown("""
<div id="top"></div>
<div class="nav-wrap">
  <a class="nav-brand" href="#top"><span class="brand-mark">🥗</span> Ingredient Optimizer</a>
  <div class="nav-links"><a href="#overview">Overview</a><a href="#ingredients">Ingredients</a><a href="#algorithms">Algorithms</a><a href="#optimization">Optimization</a><a href="#results">Results</a><a class="nav-cta" href="#optimization">Start optimizing ↗</a></div>
</div>
<div class="hero-shell">
 <div class="hero-copy">
  <span class="eyebrow"><span class="eyebrow-dot"></span> Food intelligence · DAA laboratory</span>
  <h1 class="hero-title">Optimize Every Ingredient.<br><span>Waste Nothing.</span></h1>
  <p class="hero-sub">An intelligent, algorithm-driven system that builds the strongest menu coverage under a fixed budget while keeping expected food waste in view.</p>
  <div class="hero-actions"><a class="hero-btn primary" href="#optimization">⚡ Start optimization</a><a class="hero-btn secondary" href="#algorithms">↗ Explore algorithms</a></div>
  <div class="hero-proof"><span>● <strong>Exact 0/1 DP</strong></span><span>● <strong>Live greedy trace</strong></span><span>● <strong>SQLite persistence</strong></span></div>
 </div>
 <div class="hero-art" aria-label="Interactive 3D ingredient optimization scene">
  <div class="scene3d-stage">
   <div class="scene-glow"></div>
   <div class="scene-orbit orbit-a"></div><div class="scene-orbit orbit-b"></div><div class="scene-orbit orbit-c"></div>
   <div class="scene-platform shadow"></div><div class="scene-platform base"></div><div class="scene-platform rim"></div>
   <div class="scene-center">🥗</div>
   <div class="ingredient-orb tomato">🍅</div><div class="ingredient-orb avocado">🥑</div>
   <div class="ingredient-orb pepper">🫑</div><div class="ingredient-orb leaf">🥬</div>
   <div class="scene-card card-input"><small>01 · Ingredient</small><strong>Cost + coverage</strong><span>structured input</span></div>
   <div class="scene-card card-budget"><small>02 · Capacity</small><strong>₹ Budget</strong><span>hard constraint</span></div>
   <div class="scene-card card-result"><small>03 · Purchase plan</small><strong>Buy or skip</strong><span>DP-backed decision</span></div>
   <div class="scene-label">KNAPSACK · GREEDY · SORT</div>
  </div>
 </div>
</div>
""", unsafe_allow_html=True)


# Overview metrics use the actual current selection.
latest = st.session_state.latest_result
latest_metrics = evaluate(items, latest.get("selected_ids", []), int(latest.get("budget", st.session_state.budget)))
st.markdown('<div id="overview"></div>', unsafe_allow_html=True)
section_head("Live dashboard", "The plan at a glance", "Every number below is calculated from the saved ingredient dataset and the current purchase plan.")
render_metric_row(latest_metrics, int(latest.get("budget", st.session_state.budget)))


# Optimization control panel.
st.markdown('<div id="optimization"></div>', unsafe_allow_html=True)
section_head("Control room", "Set the buying strategy", "Tune the budget and objective, then run one algorithm or compare both against the same ingredient set.")
with st.container(border=True):
    st.markdown('<div class="panel-label">Optimization control panel</div>', unsafe_allow_html=True)
    control_cols = st.columns([1.15, 1.45, 1.55, 1.2])
    with control_cols[0]:
        st.slider("Budget slider", min_value=0, max_value=50000, step=100, key="budget_slider", on_change=sync_budget_from_slider)
        st.number_input("Budget (₹)", min_value=0, max_value=50000, step=100, key="budget", on_change=sync_budget_from_number, help="Exact integer-rupee capacity used by 0/1 Knapsack.")
    with control_cols[1]:
        st.selectbox("Optimization priority", ["Maximum Menu Coverage", "Minimum Waste", "Maximum Value", "Balanced Optimization"], key="objective")
    with control_cols[2]:
        st.radio("Algorithm", ["Greedy", "Knapsack", "Compare Both"], key="algorithm_choice", horizontal=True)
    with control_cols[3]:
        st.markdown("<div style='height:26px'></div>", unsafe_allow_html=True)
        run_clicked = st.button("⚡ Optimize purchases", type="primary", use_container_width=True, key="main_optimize")
    with st.expander("How the selected objective becomes algorithm value"):
        st.markdown("The dynamic program maximizes this additive score per ingredient; coverage, benefit, priority, and waste use the current row values. These weights make trade-offs explicit.")
        formulas = {
            "Maximum Menu Coverage": "10 × (100·coverage + 4·benefit + 12·priority − 1.3·waste%)",
            "Minimum Waste": "10 × (15·benefit + 15·coverage + 5·priority − 45·waste%)",
            "Maximum Value": "10 × (100·benefit + 12·coverage + 10·priority − 2·waste%)",
            "Balanced Optimization": "10 × (52·benefit + 48·coverage + 16·priority − 4·waste%)",
        }
        st.code(formulas[st.session_state.objective] + "  · priority points: High 3 / Medium 2 / Low 1", language="text")
        st.caption("The optimizer floors negative item scores at zero, so a very wasteful item can be left out even when some budget remains.")
    if run_clicked:
        if not items:
            st.warning("Add at least one ingredient before optimizing.")
        elif st.session_state.budget <= 0:
            st.warning("Set a budget above ₹0 to run an optimization.")
        else:
            with st.spinner("Calculating feasible purchase plans…"):
                main_greedy_strategy = st.session_state.get("greedy_strategy", "Balanced Score")
                if st.session_state.algorithm_choice == "Greedy":
                    chosen = run_and_save(items, st.session_state.budget, st.session_state.objective, "Greedy", main_greedy_strategy)
                    st.session_state.comparison = None
                    st.session_state.greedy_trace = chosen
                    st.session_state.knapsack_trace = None
                elif st.session_state.algorithm_choice == "Knapsack":
                    chosen = run_and_save(items, st.session_state.budget, st.session_state.objective, "0/1 Knapsack")
                    st.session_state.comparison = None
                    st.session_state.knapsack_trace = chosen
                    st.session_state.greedy_trace = None
                else:
                    greedy_result = run_and_save(items, st.session_state.budget, st.session_state.objective, "Greedy", main_greedy_strategy)
                    knapsack_result = run_and_save(items, st.session_state.budget, st.session_state.objective, "0/1 Knapsack")
                    st.session_state.comparison = {"Greedy": greedy_result, "0/1 Knapsack": knapsack_result}
                    st.session_state.greedy_trace = greedy_result
                    st.session_state.knapsack_trace = knapsack_result
                    chosen = knapsack_result
                st.session_state.latest_result = chosen
            st.toast("Purchase plan updated from the current ingredient data.", icon="✅")
            st.rerun()


# Ingredient manager.
st.markdown('<div id="ingredients"></div>', unsafe_allow_html=True)
section_head("Your dataset", "Ingredient library", "Add, search, filter, sort, edit, and remove the items your algorithms are allowed to purchase.")

with st.expander("＋ Add an ingredient", expanded=False):
    with st.form("add_ingredient_form", clear_on_submit=True):
        add_cols = st.columns([1.25, 1, 1, 1, 1])
        with add_cols[0]:
            new_name = st.text_input("Ingredient name", placeholder="e.g. Chickpeas")
        with add_cols[1]:
            new_category = st.selectbox("Category", CATEGORIES, key="add_category")
        with add_cols[2]:
            new_cost = st.number_input("Cost (₹)", min_value=1, max_value=1000000, value=350, step=50)
        with add_cols[3]:
            new_quantity = st.number_input("Quantity / packs", min_value=1, max_value=10000, value=1, step=1)
        with add_cols[4]:
            new_benefit = st.number_input("Benefit value", min_value=0.0, max_value=100000.0, value=50.0, step=1.0)
        add_cols2 = st.columns([2, 1, 1, 1, 1])
        with add_cols2[0]:
            new_menus = st.multiselect("Menus supported", MENU_CATALOG, help="Coverage is counted as the distinct menus selected here.")
        with add_cols2[1]:
            new_priority = st.selectbox("Priority", PRIORITIES, key="add_priority")
        with add_cols2[2]:
            new_waste = st.number_input("Expected waste (%)", min_value=0.0, max_value=100.0, value=5.0, step=0.5)
        with add_cols2[3]:
            new_shelf = st.number_input("Shelf life (days)", min_value=1, max_value=3650, value=14, step=1)
        with add_cols2[4]:
            st.markdown(f"<div style='padding-top:27px;color:#648171;font-size:12px;font-weight:700'>Coverage · {len(new_menus)} menus</div>", unsafe_allow_html=True)
        add_submitted = st.form_submit_button("Add to ingredient library", type="primary")
    if add_submitted:
        if not new_name.strip():
            st.error("Enter an ingredient name.")
        else:
            try:
                create_ingredient({"name": new_name, "category": new_category, "cost": new_cost, "quantity": new_quantity,
                                   "benefit": new_benefit, "menus": new_menus, "priority": new_priority,
                                   "waste_pct": new_waste, "shelf_life": new_shelf})
                st.session_state.latest_result = None
                st.session_state.comparison = None
                st.session_state.greedy_trace = None
                st.session_state.knapsack_trace = None
                st.toast(f"{new_name.strip()} added.", icon="🥕")
                st.rerun()
            except Exception as exc:
                if "UNIQUE constraint failed" in str(exc):
                    st.error("An ingredient with that name already exists. Edit the existing row or choose another name.")
                else:
                    st.error(f"Could not save the ingredient: {exc}")

all_items = list_ingredients()
filter_cols = st.columns([1.5, 1, 1, 1])
with filter_cols[0]:
    search = st.text_input("Search ingredients", placeholder="Search name or category…", key="ingredient_search")
with filter_cols[1]:
    category_filter = st.selectbox("Category filter", ["All categories", *CATEGORIES], key="category_filter")
with filter_cols[2]:
    table_sort = st.selectbox("Sort table by", ["Name", "Cost", "Coverage", "Waste", "Priority"], key="table_sort")
with filter_cols[3]:
    table_order = st.selectbox("Order", ["Best first", "Lowest first", "Highest first"], key="table_order")
filtered_items = [x for x in all_items if (not search or search.casefold() in x["name"].casefold() or search.casefold() in x["category"].casefold())
                  and (category_filter == "All categories" or x["category"] == category_filter)]
if table_sort == "Name":
    filtered_items.sort(key=lambda x: x["name"].casefold(), reverse=table_order == "Highest first")
else:
    table_criterion = {"Cost": "Cost", "Coverage": "Coverage", "Waste": "Waste", "Priority": "Priority"}[table_sort]
    table_sorted = sort_items(filtered_items, table_criterion, table_order)
    filtered_items = table_sorted["items"]

if filtered_items:
    table_rows = [{"Ingredient": x["name"], "Category": x["category"], "Cost": money(x["cost"]), "Qty": x["quantity"],
                   "Menus": x["coverage"], "Priority": x["priority"], "Waste": f'{x["waste_pct"]:.1f}%',
                   "Shelf life": f'{x["shelf_life"]} days', "Value": round(x["benefit"], 1)} for x in filtered_items]
    st.dataframe(pd.DataFrame(table_rows), use_container_width=True, hide_index=True, height=min(430, 37 + len(table_rows) * 36))
    st.caption(f"Showing {len(filtered_items)} of {len(all_items)} ingredients · coverage is the count of distinct supported menus.")
else:
    st.info("No ingredients match these filters. Clear the search or add an ingredient to continue.")

if all_items:
    with st.expander("✎ Edit or delete an ingredient", expanded=False):
        edit_target_id = st.selectbox("Choose an ingredient", [x["id"] for x in all_items],
                                      format_func=lambda ingredient_id: next(f'{x["name"]} · {money(x["cost"])}' for x in all_items if x["id"] == ingredient_id),
                                      key="edit_target")
        edit_target = next((x for x in all_items if x["id"] == edit_target_id), None)
        if edit_target:
            with st.form(f"edit_form_{edit_target['id']}"):
                ecols = st.columns([1.3, 1, 1, 1, 1])
                with ecols[0]:
                    edit_name = st.text_input("Name", value=edit_target["name"])
                with ecols[1]:
                    edit_category = st.selectbox("Category", CATEGORIES, index=CATEGORIES.index(edit_target["category"]) if edit_target["category"] in CATEGORIES else len(CATEGORIES)-1)
                with ecols[2]:
                    edit_cost = st.number_input("Cost (₹)", min_value=1, max_value=1000000, value=int(edit_target["cost"]), step=50)
                with ecols[3]:
                    edit_quantity = st.number_input("Quantity", min_value=1, max_value=10000, value=int(edit_target["quantity"]), step=1)
                with ecols[4]:
                    edit_benefit = st.number_input("Benefit value", min_value=0.0, max_value=100000.0, value=float(edit_target["benefit"]), step=1.0)
                ecols2 = st.columns([2, 1, 1, 1, 1])
                with ecols2[0]:
                    edit_menus = st.multiselect("Menus supported", MENU_CATALOG, default=[m for m in edit_target["menus"] if m in MENU_CATALOG], key=f"edit_menus_{edit_target['id']}")
                with ecols2[1]:
                    edit_priority = st.selectbox("Priority", PRIORITIES, index=PRIORITIES.index(edit_target["priority"]) if edit_target["priority"] in PRIORITIES else 1)
                with ecols2[2]:
                    edit_waste = st.number_input("Waste (%)", min_value=0.0, max_value=100.0, value=float(edit_target["waste_pct"]), step=0.5)
                with ecols2[3]:
                    edit_shelf = st.number_input("Shelf life (days)", min_value=1, max_value=3650, value=int(edit_target["shelf_life"]), step=1)
                with ecols2[4]:
                    st.markdown(f"<div style='padding-top:27px;color:#648171;font-size:12px;font-weight:700'>Coverage · {len(edit_menus)} menus</div>", unsafe_allow_html=True)
                save_edit = st.form_submit_button("Save changes", type="primary")
            if save_edit:
                if not edit_name.strip():
                    st.error("Ingredient name cannot be empty.")
                else:
                    try:
                        update_ingredient(edit_target["id"], {"name": edit_name, "category": edit_category, "cost": edit_cost,
                                                               "quantity": edit_quantity, "benefit": edit_benefit, "menus": edit_menus,
                                                               "priority": edit_priority, "waste_pct": edit_waste, "shelf_life": edit_shelf})
                        st.session_state.latest_result = None
                        st.session_state.comparison = None
                        st.session_state.greedy_trace = None
                        st.session_state.knapsack_trace = None
                        st.toast(f"{edit_name.strip()} updated.", icon="✅")
                        st.rerun()
                    except Exception as exc:
                        if "UNIQUE constraint failed" in str(exc):
                            st.error("Another ingredient already uses that name.")
                        else:
                            st.error(f"Could not update the ingredient: {exc}")
            st.markdown("---")
            confirm_delete = st.checkbox(f"Confirm deletion of {edit_target['name']}", key=f"confirm_delete_{edit_target['id']}")
            if st.button("Delete selected ingredient", disabled=not confirm_delete, key=f"delete_{edit_target['id']}"):
                try:
                    delete_ingredient(edit_target["id"])
                    st.session_state.latest_result = None
                    st.session_state.comparison = None
                    st.session_state.greedy_trace = None
                    st.session_state.knapsack_trace = None
                    st.toast(f"{edit_target['name']} deleted.", icon="🗑️")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Could not delete the ingredient: {exc}")
else:
    st.info("The ingredient library is empty. Add an ingredient or generate a sample dataset to begin.")


# Sorting lab.
st.markdown('<div id="algorithms"></div>', unsafe_allow_html=True)
section_head("DAA · Sorting", "Sorting laboratory", "See how the optimizer orders real ingredient rows before greedy selection and inspect the work performed by insertion sort.")
sort_cols = st.columns([1, 1, 1, 1.2])
with sort_cols[0]:
    sort_criterion = st.selectbox("Sorting criterion", ["Cost", "Coverage", "Waste", "Value", "Value / Cost ratio", "Priority"], key="sort_criterion")
with sort_cols[1]:
    sort_direction = st.selectbox("Direction", ["Best first", "Lowest first", "Highest first"], key="sort_direction")
with sort_cols[2]:
    sort_scope = st.selectbox("Dataset", ["Filtered rows", "All ingredients"], key="sort_scope")
with sort_cols[3]:
    st.markdown("<div style='height:27px'></div>", unsafe_allow_html=True)
    sort_clicked = st.button("⇅ Sort ingredients", use_container_width=True, key="run_sort")
source_for_sort = filtered_items if sort_scope == "Filtered rows" else all_items
if "sort_lab_result" not in st.session_state:
    st.session_state.sort_lab_result = None
if sort_clicked:
    if len(source_for_sort) < 2:
        st.warning("Add at least two visible ingredients to run the sorting demonstration.")
    else:
        st.session_state.sort_lab_result = {
            "before": list(source_for_sort), "criterion": sort_criterion, "direction": sort_direction,
            **sort_items(source_for_sort, sort_criterion, sort_direction),
        }
sort_data = st.session_state.sort_lab_result
if sort_data:
    sort_a, sort_b, sort_c = st.columns([1, .58, 1])
    with sort_a:
        st.markdown('<div class="panel"><div class="panel-label">Before sorting</div><div style="height:7px"></div>', unsafe_allow_html=True)
        for item in sort_data["before"][:8]:
            st.markdown(html_item_chip(item, True), unsafe_allow_html=True)
        if len(sort_data["before"]) > 8:
            st.caption(f"+ {len(sort_data['before']) - 8} more rows")
        st.markdown("</div>", unsafe_allow_html=True)
    with sort_b:
        st.markdown('<div class="panel panel-soft" style="text-align:center"><div class="panel-label">Sorting process</div><div style="font-size:24px;margin:17px 0;color:#199065">↔</div>', unsafe_allow_html=True)
        st.markdown(f"**Insertion sort**  \n{html.escape(sort_data['criterion'])} · {html.escape(sort_data['direction'])}")
        st.markdown(f"<div class='item-chip-meta' style='margin-top:12px'>{sort_data['comparisons']} comparisons<br>{sort_data['swaps']} swaps</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with sort_c:
        st.markdown('<div class="panel"><div class="panel-label">After sorting</div><div style="height:7px"></div>', unsafe_allow_html=True)
        for item in sort_data["items"][:8]:
            st.markdown(html_item_chip(item, True), unsafe_allow_html=True)
        if len(sort_data["items"]) > 8:
            st.caption(f"+ {len(sort_data['items']) - 8} more rows")
        st.markdown("</div>", unsafe_allow_html=True)
    st.caption(f"Insertion sort · {sort_data['comparisons']} comparisons · {sort_data['swaps']} adjacent swaps · {sort_data['elapsed_ms']:.3f} ms on this run. Timing varies with the machine and dataset.")
else:
    st.markdown('<div class="panel panel-soft"><span class="panel-label">Ready to sort</span><div style="margin-top:7px;color:#7b8981;font-size:12px">Choose a criterion and run the lab to see the before and after ordering, comparison count, swaps, and local execution time.</div></div>', unsafe_allow_html=True)


# Algorithm visualization cards.
section_head("DAA · Selection", "Two ways to spend the same budget", "Greedy makes a quick local choice; 0/1 Knapsack evaluates combinations with dynamic programming.")
gcol, kcol = st.columns(2)
with gcol:
    with st.container(border=True):
        st.markdown('<div class="panel-label">01 · Local decision rule</div><h3 style="margin:.35rem 0 .3rem">Greedy strategy</h3><p style="color:#78877e;font-size:12px;line-height:1.65">Repeatedly select the highest-ranked feasible ingredient for the chosen ratio. It is fast, but a locally strong pick can block a better overall combination.</p>', unsafe_allow_html=True)
        greedy_strategy = st.selectbox("Greedy ranking", ["Highest Coverage / Cost", "Highest Value / Cost", "Lowest Waste / Cost", "Balanced Score"], key="greedy_strategy")
        run_greedy_clicked = st.button("▶ Run Greedy Algorithm", use_container_width=True, key="run_greedy")
        if run_greedy_clicked:
            if not all_items:
                st.warning("Add an ingredient before running Greedy.")
            elif st.session_state.budget <= 0:
                st.warning("Set a budget above ₹0 before running Greedy.")
            else:
                raw_greedy = run_greedy(all_items, st.session_state.budget, greedy_strategy, st.session_state.objective)
                greedy_result = safe_result(raw_greedy, all_items, st.session_state.budget, st.session_state.objective, greedy_strategy)
                greedy_result["summary"] = {"elapsed_ms": raw_greedy["elapsed_ms"], "selected_count": greedy_result["metrics"]["items_selected"]}
                save_run(greedy_result)
                st.session_state.latest_result = greedy_result
                st.session_state.greedy_trace = greedy_result
                st.toast("Greedy trace ready.", icon="🧭")
                st.rerun()
        trace = st.session_state.get("greedy_trace")
        if trace:
            st.markdown(f"<span class='pill'>Strategy · {html.escape(trace['strategy'])}</span> <span class='pill gray'>Ratio = rank score / cost</span>", unsafe_allow_html=True)
            trace_rows = [{"Step": row["step"], "Ingredient": row["name"], "Cost": money(row["cost"]), "Benefit": row["benefit"],
                           "Ratio": f'{row["ratio"]:.4f}', "Decision": row["decision"], "Remaining": money(row["remaining"])} for row in trace["decisions"]]
            st.dataframe(pd.DataFrame(trace_rows), use_container_width=True, hide_index=True, height=min(350, 37 + len(trace_rows) * 34))
            with st.expander("Why each Greedy decision?", expanded=True):
                for row in trace["decisions"]:
                    label = "✓ SELECTED" if row["id"] in set(trace["selected_ids"]) else "× REJECTED"
                    st.markdown(f"**Step {row['step']} · {html.escape(row['name'])}**  \n{label} · {html.escape(row['why'])}")
            st.caption(f"The local pass uses insertion sort to order candidates, then scans each once · {trace['comparisons']} sort comparisons · {trace['elapsed_ms']:.3f} ms.")
        else:
            st.caption("Run it to reveal each ingredient's ratio, remaining capacity, and selection or rejection reason.")
with kcol:
    with st.container(border=True):
        st.markdown('<div class="panel-label">02 · Global combination search</div><h3 style="margin:.35rem 0 .3rem">0/1 Knapsack</h3><p style="color:#78877e;font-size:12px;line-height:1.65">Cost is weight, the selected objective score is value, and the budget is capacity. Each item is either bought once or skipped.</p>', unsafe_allow_html=True)
        explanation_mode = st.toggle("Technical explanation", value=False, key="technical_explanation")
        st.markdown('<div class="formula">DP[i][w] = max(DP[i−1][w], value[i] + DP[i−1][w−cost[i]])</div>', unsafe_allow_html=True)
        if explanation_mode:
            st.caption("For each ingredient i and integer budget w, keep the best objective score using the first i ingredients. The descending capacity loop preserves 0/1 use: an item cannot be reused in the same iteration.")
            st.caption(f"Time: O(n × B) · memory: O(B) for the score row plus the trace rows · capacity is integer rupees (B = {int(st.session_state.budget):,}).")
        else:
            st.caption("Simple view · Should we buy this ingredient or skip it? The DP table compares both choices at each budget checkpoint.")
        run_knap_clicked = st.button("▶ Run Knapsack Algorithm", use_container_width=True, key="run_knapsack")
        if run_knap_clicked:
            if not all_items:
                st.warning("Add an ingredient before running Knapsack.")
            elif st.session_state.budget <= 0:
                st.warning("Set a budget above ₹0 before running Knapsack.")
            else:
                with st.spinner("Filling the dynamic-programming table…"):
                    knap_result = run_and_save(all_items, st.session_state.budget, st.session_state.objective, "0/1 Knapsack")
                st.session_state.latest_result = knap_result
                st.session_state.knapsack_trace = knap_result
                st.toast("Optimal feasible combination calculated.", icon="🧮")
                st.rerun()
        dp_trace = st.session_state.get("knapsack_trace")
        if dp_trace and dp_trace.get("dp_rows"):
            dp_df = build_dp_view(dp_trace, dp_trace["items"], int(dp_trace["budget"]))
            st.dataframe(dp_df, use_container_width=True, hide_index=True, height=min(320, 42 + len(dp_df) * 33))
            st.caption(f"{dp_trace['cells_calculated']:,} feasible DP cells calculated · final objective value {dp_trace['optimal_value'] / 10:,.0f} · {dp_trace['elapsed_ms']:.3f} ms.")
            with st.expander("Purchase / skip decisions"):
                selected_ids = set(dp_trace["selected_ids"])
                dp_chosen, dp_rejected = explain_decisions(dp_trace, dp_trace["items"])
                for item, why in dp_chosen:
                    st.markdown(f"**✓ Buy · {html.escape(item['name'])}** — {html.escape(why)}")
                for item, why in dp_rejected:
                    st.markdown(f"**× Skip · {html.escape(item['name'])}** — {html.escape(why)}")
        else:
            st.caption("Run it to animate a compact set of DP budget checkpoints and inspect the buy / skip decision for every row.")


# Algorithm comparison, based on actual runs.
section_head("Evidence, not claims", "Greedy vs. Knapsack", "Run Compare Both in the control panel to calculate these metrics from identical inputs. Waste is spend-weighted; lower is better.")
comparison = st.session_state.get("comparison")
if comparison:
    greedy_cmp = comparison["Greedy"]
    knap_cmp = comparison["0/1 Knapsack"]
    comp_metrics = [("Total cost", "total_cost", "currency"), ("Menu coverage", "coverage_pct", "pct"),
                    ("Expected waste", "waste_pct", "pct"), ("Items selected", "items_selected", "count"),
                    ("Execution time (ms)", "elapsed_ms", "time")]
    fig = make_subplots(rows=1, cols=5, subplot_titles=[m[0] for m in comp_metrics], horizontal_spacing=.055)
    for col, (label, key, kind) in enumerate(comp_metrics, 1):
        vals = []
        for name, result in (("Greedy", greedy_cmp), ("0/1 Knapsack", knap_cmp)):
            raw = result["metrics"].get(key, result.get(key, 0))
            vals.append((name, raw))
        fig.add_trace(go.Bar(x=[x[0] for x in vals], y=[x[1] for x in vals], marker_color=["#a8cdb0", "#18835d"],
                             text=[f"₹{v:,.0f}" if kind == "currency" else (f"{v:.1f}%" if kind == "pct" else f"{v:.2f}" if kind == "time" else f"{v:.0f}") for _, v in vals],
                             textposition="outside", showlegend=False), row=1, col=col)
        fig.update_yaxes(showgrid=False, visible=False, rangemode="tozero", row=1, col=col)
    plotly_style(fig, height=285)
    fig.update_layout(bargap=.48)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False}, key="comparison_chart")
    cmp_cols = st.columns(2)
    for col, (label, result) in zip(cmp_cols, (("Greedy", greedy_cmp), ("0/1 Knapsack", knap_cmp))):
        m = result["metrics"]
        with col:
            st.markdown(f'<div class="panel"><span class="panel-label">{label}</span><div style="margin-top:8px;color:#294b39;font-size:13px;line-height:1.9">Cost <b>{money(m["total_cost"])}</b> · Coverage <b>{m["coverage_pct"]:.0f}%</b><br>Expected waste <b>{m["waste_pct"]:.1f}%</b> · Items <b>{m["items_selected"]}</b><br>Elapsed <b>{result.get("elapsed_ms",0):.3f} ms</b></div></div>', unsafe_allow_html=True)
    st.markdown("**What the comparison means:** Greedy is a fast local heuristic and can miss the best combination. Knapsack is exact for this integer-cost, additive-value 0/1 formulation; its result is optimal for the selected objective, not automatically best on every displayed metric.")
else:
    st.markdown('<div class="panel panel-soft"><span class="panel-label">Waiting for a comparison run</span><div style="margin-top:7px;color:#7b8981;font-size:12px">Choose “Compare Both” and optimize to calculate cost, menu coverage, expected waste, selected items, and measured runtime for both algorithms.</div></div>', unsafe_allow_html=True)


# Results and explanations.
st.markdown('<div id="results"></div>', unsafe_allow_html=True)
section_head("Purchase plan", "Your optimized purchase plan", "A transparent plan with a reason attached to every selected and rejected ingredient.")
latest = st.session_state.get("latest_result")
if latest is None:
    items = list_ingredients()
    if items:
        latest = safe_result(run_knapsack(items, st.session_state.budget, st.session_state.objective), items, st.session_state.budget, st.session_state.objective)
        st.session_state.latest_result = latest
latest_items = list_ingredients()
if latest and latest_items:
    # Ignore any deleted or stale IDs; all data shown is recalculated from the current SQLite rows.
    current_ids = {x["id"] for x in latest_items}
    latest["selected_ids"] = [x for x in latest.get("selected_ids", []) if x in current_ids]
    result_metrics = evaluate(latest_items, latest["selected_ids"], int(latest.get("budget", st.session_state.budget)))
    latest["metrics"] = result_metrics
    st.markdown(f'<div class="panel panel-soft"><span class="status-good">✓ {html.escape(latest["algorithm"])} plan · {html.escape(latest["priority"])}</span><span style="float:right;color:#829087;font-size:10px">Budget capacity {money(latest["budget"])}</span></div>', unsafe_allow_html=True)
    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    render_metric_row(result_metrics, int(latest["budget"]))
    chosen_reasons, rejected_reasons = explain_decisions(latest, latest_items)
    left_res, right_res = st.columns([1.1, .9])
    with left_res:
        st.markdown('<div class="panel"><div class="panel-label">✓ Selected ingredients</div><div style="height:7px"></div>', unsafe_allow_html=True)
        if chosen_reasons:
            for item, reason in sorted(chosen_reasons, key=lambda pair: (-pair[0]["benefit"], pair[0]["name"])):
                st.markdown(html_item_chip(item, True, reason), unsafe_allow_html=True)
        else:
            st.markdown("<div style='margin-top:12px;color:#7f8d84;font-size:12px'>No item fits under this budget. Increase the budget to build a feasible set.</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with right_res:
        with st.expander(f"Ingredients not selected · {len(rejected_reasons)}", expanded=True):
            if rejected_reasons:
                for item, reason in sorted(rejected_reasons, key=lambda pair: (pair[0]["cost"], pair[0]["name"])):
                    st.markdown(html_item_chip(item, False, reason), unsafe_allow_html=True)
            else:
                st.markdown("All ingredients were selected; their combined cost fits the budget.")
    st.caption("Coverage percentage is the share of the 12 named menus supported by at least one selected ingredient. Expected waste is weighted by ingredient spend; these are planning estimates, not measured spoilage.")
else:
    st.info("Add ingredients to generate a purchase plan.")


# Charts: cost/coverage, waste, budget allocation, covered menus.
section_head("Impact view", "Waste, coverage & budget", "Hover charts for ingredient details. Budget allocation updates when you run a new plan.")
if latest_items and latest:
    waste_col, alloc_col = st.columns([1.05, .95])
    with waste_col:
        st.markdown('<div class="panel"><div class="panel-label">♻ Waste reduction analysis</div><div style="height:7px"></div>', unsafe_allow_html=True)
        base = result_metrics["baseline_waste_pct"]
        after = result_metrics["waste_pct"]
        reduction = ((base - after) / base * 100) if base > 0 else 0
        waste_fig = go.Figure(go.Bar(x=["Before plan", "After plan"], y=[base, after], marker_color=["#e8b665", "#47a777"],
                                     text=[f"{base:.1f}%", f"{after:.1f}%"], textposition="outside", hovertemplate="%{x}<br>Weighted waste: %{y:.1f}%<extra></extra>"))
        waste_fig.update_yaxes(title="Expected waste · % of spend", rangemode="tozero")
        plotly_style(waste_fig, 260)
        st.plotly_chart(waste_fig, use_container_width=True, config={"displayModeBar": False}, key="waste_chart")
        direction = "reduction" if reduction >= 0 else "increase"
        st.markdown(f'<span class="pill">{abs(reduction):.1f}% {direction} vs. buying every item</span> <span class="pill orange">{money(result_metrics["baseline_exposure"] - result_metrics["waste_exposure"])} less expected waste cost</span>', unsafe_allow_html=True)
        waste_items = sorted(latest_items, key=lambda x: x["cost"] * x["waste_pct"], reverse=True)[:5]
        if waste_items:
            st.caption("Highest waste exposure in the ingredient library")
            for item in waste_items:
                contribution = int(item["cost"]) * float(item["waste_pct"]) / 100
                st.markdown(f"**{html.escape(item['name'])}** · {money(contribution)} expected exposure · {item['waste_pct']:.1f}%")
        st.markdown("</div>", unsafe_allow_html=True)
    with alloc_col:
        st.markdown('<div class="panel"><div class="panel-label">◔ Budget allocation</div><div style="height:7px"></div>', unsafe_allow_html=True)
        category_costs: dict[str, int] = {}
        for item in result_metrics["selected"]:
            category_costs[item["category"]] = category_costs.get(item["category"], 0) + int(item["cost"])
        if category_costs:
            alloc_fig = px.pie(names=list(category_costs.keys()), values=list(category_costs.values()), hole=.69,
                               color_discrete_sequence=["#16845c", "#89c79a", "#d8e9a1", "#e9b35e", "#7ca9a0", "#bdceca"])
            alloc_fig.update_traces(textinfo="percent", hovertemplate="%{label}<br>Spend: ₹%{value:,}<br>%{percent}<extra></extra>", marker=dict(line=dict(color="white", width=3)))
            alloc_fig.add_annotation(text=f"{money(result_metrics['total_cost'])}<br><span style='font-size:10px'>used</span>", showarrow=False, font=dict(size=17, color="#244a37"))
            plotly_style(alloc_fig, 285)
            st.plotly_chart(alloc_fig, use_container_width=True, config={"displayModeBar": False}, key="allocation_chart")
        else:
            st.info("No purchases fit this budget yet.")
        st.progress(min(1.0, result_metrics["total_cost"] / max(1, result_metrics["total_budget"])), text=f"Used {money(result_metrics['total_cost'])} · remaining {money(result_metrics['remaining'])} of {money(result_metrics['total_budget'])}")
        st.markdown("**Spend by category**")
        for category, amount in sorted(category_costs.items(), key=lambda x: x[1], reverse=True):
            st.markdown(f"{category} · **{money(amount)}**")
        st.markdown("</div>", unsafe_allow_html=True)

    chart_a, chart_b = st.columns([1.12, .88])
    with chart_a:
        st.markdown('<div class="panel"><div class="panel-label">Ingredient cost · menu coverage · waste · 3D map</div><div style="height:7px"></div>', unsafe_allow_html=True)
        scatter_data = pd.DataFrame([{"Ingredient": x["name"], "Cost": x["cost"], "Menus": x["coverage"], "Waste": x["waste_pct"], "Category": x["category"], "Priority": x["priority"]} for x in latest_items])
        scatter = px.scatter_3d(scatter_data, x="Cost", y="Menus", z="Waste", color="Category", size="Waste", size_max=18,
                                hover_name="Ingredient", hover_data={"Priority": True, "Waste": ":.1f", "Cost": ":,", "Menus": True},
                                color_discrete_sequence=["#16845c", "#94c98c", "#dfa64e", "#719f93", "#bdce7f", "#b6cbc0"])
        scatter.update_traces(marker=dict(opacity=.9, line=dict(width=1, color="white")))
        plotly_style(scatter, 340)
        axis_style = dict(backgroundcolor="rgba(255,255,255,0)", gridcolor="#eaf1eb", zerolinecolor="#dce8de", color="#71827a")
        scatter.update_layout(scene=dict(
            xaxis={**axis_style, "title": "Cost · ₹"},
            yaxis={**axis_style, "title": "Menus supported"},
            zaxis={**axis_style, "title": "Expected waste · %"},
            aspectmode="manual", aspectratio=dict(x=1.05, y=.8, z=.78), dragmode="orbit",
            camera=dict(eye=dict(x=1.55, y=1.45, z=1.05)),
        ))
        st.caption("Drag to rotate the ingredient field; each axis shows a planning trade-off.")
        st.plotly_chart(scatter, use_container_width=True, config={"displayModeBar": False}, key="cost_coverage_chart")
        st.markdown("</div>", unsafe_allow_html=True)
    with chart_b:
        st.markdown('<div class="panel"><div class="panel-label">Menu coverage map</div><div style="height:7px"></div>', unsafe_allow_html=True)
        covered_set = set(result_metrics["covered_menus"])
        for index, menu in enumerate(MENU_CATALOG):
            covered = menu in covered_set
            st.markdown(f'<div class="item-chip"><div class="item-chip-name">{("🍽" if covered else "◌")} {html.escape(menu)}</div><span class="{"decision-good" if covered else "decision-bad"}">{"COVERED ✓" if covered else "NOT COVERED"}</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div style="margin-top:13px;font:800 26px Manrope;color:#1b3c30">{result_metrics["coverage_pct"]:.0f}% <span style="font:500 11px DM Sans;color:#839188">· {result_metrics["coverage_count"]}/{len(MENU_CATALOG)} menus</span></div>', unsafe_allow_html=True)
        st.progress(min(1.0, result_metrics["coverage_pct"] / 100))
        st.markdown("</div>", unsafe_allow_html=True)

    data_col, split_col = st.columns([1.2, .8])
    with data_col:
        st.markdown('<div class="panel"><div class="panel-label">Waste by ingredient · cost exposure</div><div style="height:7px"></div>', unsafe_allow_html=True)
        waste_rows = pd.DataFrame([{"Ingredient": x["name"], "Expected waste cost": int(x["cost"]) * float(x["waste_pct"]) / 100,
                                    "Plan": "Selected" if x["id"] in set(latest["selected_ids"]) else "Not selected", "Waste rate": x["waste_pct"]} for x in latest_items])
        waste_by_item = px.bar(waste_rows.sort_values("Expected waste cost", ascending=True), x="Expected waste cost", y="Ingredient", color="Plan", orientation="h",
                               hover_data={"Waste rate": ":.1f", "Expected waste cost": ":.2f"}, color_discrete_map={"Selected": "#16845c", "Not selected": "#d6dfd7"})
        waste_by_item.update_layout(showlegend=True, legend=dict(orientation="h", y=1.08, x=0))
        waste_by_item.update_xaxes(title="Expected waste exposure · ₹")
        plotly_style(waste_by_item, max(260, 22 * len(latest_items)))
        st.plotly_chart(waste_by_item, use_container_width=True, config={"displayModeBar": False}, key="ingredient_waste_chart")
        st.markdown("</div>", unsafe_allow_html=True)
    with split_col:
        st.markdown('<div class="panel"><div class="panel-label">Selected vs. not selected</div><div style="height:7px"></div>', unsafe_allow_html=True)
        selected_count = result_metrics["items_selected"]
        rejected_count = len(latest_items) - selected_count
        split_fig = go.Figure(go.Pie(labels=["Selected", "Not selected"], values=[selected_count, rejected_count], hole=.68,
                                     marker_colors=["#16845c", "#dce7dd"], textinfo="label+value", sort=False,
                                     hovertemplate="%{label}: %{value} ingredients (%{percent})<extra></extra>"))
        split_fig.add_annotation(text=f"{selected_count}<br><span style='font-size:10px'>selected</span>", showarrow=False, font=dict(size=17, color="#244a37"))
        plotly_style(split_fig, 300)
        st.plotly_chart(split_fig, use_container_width=True, config={"displayModeBar": False}, key="selected_rejected_chart")
        st.markdown("</div>", unsafe_allow_html=True)


# Algorithm workflow and complexity.
section_head("Under the hood", "How the optimizer works", "The pipeline is deterministic for a fixed dataset, budget, objective, and algorithm.")
process_cols = st.columns(7)
process_steps = [("01", "Input data"), ("02", "Sort candidates"), ("03", "Score value"), ("04", "Run Greedy"), ("05", "Run Knapsack"), ("06", "Compare"), ("07", "Purchase plan")]
for col, (number, label) in zip(process_cols, process_steps):
    with col:
        st.markdown(f'<div class="timeline-step"><strong>{number}</strong><br>{label}</div>', unsafe_allow_html=True)
st.markdown("<div style='height:13px'></div>", unsafe_allow_html=True)
complex_cols = st.columns(3)
complexity = [
    ("Greedy + insertion sort", "O(n²) in this visible insertion-sort implementation", "The selection scan is O(n); the displayed ordering pass uses insertion sort so its measured worst case is quadratic."),
    ("0/1 Knapsack", "O(n × B) time", "B is the integer-rupee budget capacity; the algorithm keeps one score row and records decisions for explanation."),
    ("Sorting laboratory", "Insertion sort · O(n²)", "The lab reports actual comparisons, adjacent swaps, and elapsed time for the current rows."),
]
for col, (name, order, description) in zip(complex_cols, complexity):
    with col:
        st.markdown(f'<div class="alg-card"><span class="panel-label">COMPLEXITY NOTE</span><h4>{html.escape(name)}</h4><div style="color:#16845c;font:700 12px ui-monospace,monospace;margin:8px 0">{html.escape(order)}</div><p>{html.escape(description)}</p></div>', unsafe_allow_html=True)


# Playground actions & persisted run history.
section_head("Hands-on", "Algorithm playground", "Generate a fresh realistic dataset, reset to the curated sample, or replay the current configuration.")
play_cols = st.columns([1.2, 1.2, 1.2, 2.3])
with play_cols[0]:
    random_clicked = st.button("🎲 Generate random dataset", use_container_width=True, key="random_dataset")
with play_cols[1]:
    reset_clicked = st.button("↺ Reset sample data", use_container_width=True, key="reset_dataset")
with play_cols[2]:
    replay_clicked = st.button("▶ Run again", use_container_width=True, key="run_again")
with play_cols[3]:
    st.caption("Generate and reset replace ingredient rows. Saved run history remains available in SQLite.")
if random_clicked:
    try:
        replace_with_random_data(seed=random.SystemRandom().randint(0, 10**9), count=16)
        st.session_state.latest_result = None
        st.session_state.comparison = None
        st.session_state.sort_lab_result = None
        st.session_state.greedy_trace = None
        st.session_state.knapsack_trace = None
        st.toast("A new 16-item dataset is ready.", icon="🎲")
        st.rerun()
    except Exception as exc:
        st.error(f"Could not generate the dataset: {exc}")
if reset_clicked:
    try:
        reset_sample_data()
        st.session_state.latest_result = None
        st.session_state.comparison = None
        st.session_state.sort_lab_result = None
        st.session_state.greedy_trace = None
        st.session_state.knapsack_trace = None
        st.toast("Curated sample ingredients restored.", icon="↺")
        st.rerun()
    except Exception as exc:
        st.error(f"Could not reset the dataset: {exc}")
if replay_clicked:
    choice = st.session_state.algorithm_choice
    replay_strategy = st.session_state.get("greedy_strategy", "Balanced Score")
    if choice == "Compare Both":
        g = run_and_save(list_ingredients(), st.session_state.budget, st.session_state.objective, "Greedy", replay_strategy)
        k = run_and_save(list_ingredients(), st.session_state.budget, st.session_state.objective, "0/1 Knapsack")
        st.session_state.comparison = {"Greedy": g, "0/1 Knapsack": k}
        st.session_state.greedy_trace = g
        st.session_state.knapsack_trace = k
        st.session_state.latest_result = k
    else:
        replayed = run_and_save(list_ingredients(), st.session_state.budget, st.session_state.objective, choice, replay_strategy)
        st.session_state.latest_result = replayed
        st.session_state.comparison = None
        if choice == "Greedy":
            st.session_state.greedy_trace = replayed
            st.session_state.knapsack_trace = None
        else:
            st.session_state.knapsack_trace = replayed
            st.session_state.greedy_trace = None
    st.toast("Algorithm replayed with the current controls.", icon="▶")
    st.rerun()

history = list_runs(12)
if history:
    with st.expander("Recent saved optimization runs", expanded=False):
        history_rows = [{"Run": f"#{r['id']}", "Recorded at": r["created_at"], "Algorithm": r["algorithm"],
                         "Budget": money(r["budget"]), "Spend": money(r["total_cost"]), "Coverage": f"{r['coverage_pct']:.0f}%",
                         "Waste": f"{r['waste_pct']:.1f}%", "Score": f"{r['score']:.1f}"} for r in history]
        st.dataframe(pd.DataFrame(history_rows), use_container_width=True, hide_index=True)

st.markdown('<div class="footer-note">Food Ingredient Purchase Optimizer · SQLite persistence · 0/1 dynamic programming · greedy heuristics · insertion sort</div>', unsafe_allow_html=True)
