#!/usr/bin/env python3
"""Render animated, GitHub-safe SVG cards for the profile README.

Set STATIC=1 to emit screenshot-ready final frames without CSS or SMIL animation.
"""
from __future__ import annotations
import base64, collections, datetime as dt, html, json, os, pathlib, shutil, subprocess, tempfile, urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "cards"
DATA = ROOT / "data" / "contributions.json"
STATIC = os.getenv("STATIC", "0") == "1"
BG, PANEL, EDGE, FG, MUTED, GREEN, BLUE = "#0B080A", "#190D10", "#42131D", "#FFF1F2", "#D6A3AA", "#FF3B4E", "#FF7A86"
REPOS = [
 ("CCExtractor", "ccextractor", "C · Open source", "Subtitle extraction and media tooling; my primary open-source focus."),
 ("Banking System", "banking-system", "C · Systems fundamentals", "Terminal banking simulation focused on validation, persistence and tests."),
 ("FirstPR AI", "FirstPR-AI", "Python · Local AI", "A contribution mentor for exploring issues, codebases and test plans."),
 ("Ledger FinTech Demo", "ledger-fintech-demo", "React · FinTech", "Browser-based wallet, payments and financial-workflow demonstration."),
]
def esc(s): return html.escape(str(s), quote=True)
def font_data(chars):
    """Subset Inter and IBM Plex Mono with pyftsubset; embed as base64 WOFF."""
    pyft = shutil.which("pyftsubset")
    if not pyft: raise RuntimeError("Install fonttools[woff] and brotli (requirements.txt).")
    urls = [
      ("Inter", "https://raw.githubusercontent.com/google/fonts/main/ofl/inter/Inter%5Bopsz%2Cwght%5D.ttf"),
      ("Plex", "https://raw.githubusercontent.com/google/fonts/main/ofl/ibmplexmono/IBMPlexMono-Regular.ttf"),
    ]
    css=[]
    with tempfile.TemporaryDirectory() as td:
      for name,url in urls:
        src=pathlib.Path(td)/(name+".ttf"); dst=pathlib.Path(td)/(name+".woff")
        req=urllib.request.Request(url, headers={"User-Agent":"profile-card-renderer"})
        with urllib.request.urlopen(req, timeout=30) as response: src.write_bytes(response.read())
        subprocess.run([pyft, str(src), "--output-file="+str(dst), "--flavor=woff",
                        "--unicodes=U+"+",U+".join(f"{ord(c):04X}" for c in sorted(set(chars)) if ord(c)<0x10000),
                        "--layout-features=*", "--name-IDs=0,1,2,4,6"], check=True, stdout=subprocess.DEVNULL)
        data=base64.b64encode(dst.read_bytes()).decode()
        css.append(f"@font-face{{font-family:'{name}';src:url(data:font/woff;base64,{data}) format('woff');font-display:swap}}")
    return "".join(css)
def svg(name, body, w=1000, h=260, delay=0, fonts=""):
    motion="" if STATIC else f"""
    <style>
    @keyframes enter{{from{{opacity:0;transform:translateY(18px)}}to{{opacity:1;transform:translateY(0)}}}}
    .card-enter{{opacity:0;animation:enter .75s cubic-bezier(.2,.7,.2,1) {delay}s forwards}}
    @media(prefers-reduced-motion:reduce){{*,*::before,*::after{{animation:none!important;transition:none!important;opacity:1!important;transform:none!important}} .smil{{display:none!important}}}}
    </style>"""
    if STATIC: motion='<style>.card-enter{opacity:1}</style>'
    smil = '' if STATIC else f'<animate class="smil" attributeName="opacity" from="0" to="1" dur="0.75s" begin="{delay}s" fill="freeze"/>'
    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img">
    <title>{esc(name)}</title><defs><linearGradient id="shine"><stop stop-color="{GREEN}" stop-opacity=".2"/><stop offset="1" stop-color="{BLUE}" stop-opacity="0"/></linearGradient></defs>
    <style>{fonts}text{{font-family:Inter,Arial,sans-serif}}.mono{{font-family:Plex,'Courier New',monospace}}</style>{motion}
    <rect x="1" y="1" width="{w-2}" height="{h-2}" rx="22" fill="{BG}" stroke="{EDGE}"/>
    <rect x="1" y="1" width="{w-2}" height="5" rx="3" fill="{GREEN}" opacity=".85"/>
    <g class="card-enter">{body}{smil}</g></svg>'''
def txt(x,y,s,size=22,fill=FG,weight=400,cls=""):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" font-weight="{weight}" class="{cls}">{esc(s)}</text>'
def rect(x,y,w,h,fill=PANEL,rx=12,stroke=EDGE):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}"/>'
def write(name, body, h=260, delay=0, fonts=""):
    (OUT/name).write_text(svg(name,body,h=h,delay=delay,fonts=fonts),encoding="utf-8")
def streak(days):
    today=dt.date.today(); by={dt.date.fromisoformat(x["date"]):int(x.get("count",0)) for x in days}
    n=0; d=today
    if by.get(d,0)==0: d-=dt.timedelta(days=1)
    while by.get(d,0)>0: n+=1; d-=dt.timedelta(days=1)
    return n

def code_line(y, parts, size=16):
    spans = "".join(f'<tspan fill="{color}">{esc(value)}</tspan>' for color, value in parts)
    return f'<text x="72" y="{y}" font-size="{size}" class="mono">{spans}</text>'

def render_whoami(fonts):
    body = txt(45, 48, "WHOAMI // DEVELOPER PROFILE", 14, GREEN, 700, "mono")
    body += rect(35, 68, 930, 270, PANEL, 16, EDGE)
    body += '<circle cx="62" cy="91" r="4" fill="#FF3B4E"/>'
    body += '<circle cx="77" cy="91" r="4" fill="#FF7A86"/>'
    body += '<circle cx="92" cy="91" r="4" fill="#6B3039"/>'
    body += txt(118, 96, "~/prabhjot/profile.cpp", 11, MUTED, 500, "mono")
    lines = [
        (126, [(GREEN, "struct "), (FG, "Developer"), (GREEN, " {")], 18),
        (160, [(BLUE, "    string "), (FG, "name"), (FG, " = "), (GREEN, '"Prabhjot Singh"'), (FG, ";")], 16),
        (190, [(BLUE, "    string "), (FG, "role"), (FG, " = "), (GREEN, '"B.Tech CSE Student"'), (FG, ";")], 16),
        (220, [(BLUE, "    vector<string> "), (FG, "focus"), (FG, " = {"), (GREEN, '"C", "C++", "DSA", "Open Source"'), (FG, "};")], 15),
        (250, [(BLUE, "    vector<string> "), (FG, "building"), (FG, " = {"), (GREEN, '"Banking System", "FirstPR AI", "Ledger"'), (FG, "};")], 14),
        (280, [(BLUE, "    string "), (FG, "mindset"), (FG, " = "), (GREEN, '"Ideas never die."'), (FG, ";")], 16),
        (310, [(GREEN, "};")], 18),
    ]
    for y, parts, size in lines:
        body += code_line(y, parts, size)
    if not STATIC:
        body += '<circle cx="908" cy="92" r="5" fill="#FF3B4E"><animate attributeName="opacity" values=".35;1;.35" dur="2.4s" repeatCount="indefinite"/></circle>'
    write("whoami.svg", body, 365, 0.35, fonts)

def render_journey(fonts):
    body = txt(45, 48, "THE JOURNEY SO FAR", 15, GREEN, 700, "mono")
    body += txt(955, 48, "01 → 06  /  STILL IN PROGRESS", 11, MUTED, 500, "mono")
    body += '<defs><path id="journey-route" d="M175 91 H825 V281 H175"/></defs>'
    body += '<path d="M175 91 H825 V281 H175" fill="none" stroke="#6B3039" stroke-width="3" stroke-linecap="round" stroke-dasharray="5 9"/>'
    if not STATIC:
        body += '<path d="M175 91 H825 V281 H175" fill="none" stroke="#FF3B4E" stroke-width="3" stroke-linecap="round" stroke-dasharray="22 210" opacity=".95"><animate attributeName="stroke-dashoffset" values="0;-696" dur="8s" repeatCount="indefinite"/></path>'
        body += '<circle r="6" fill="#FFF1F2" stroke="#FF3B4E" stroke-width="3"><animateMotion dur="9s" repeatCount="indefinite" rotate="auto"><mpath xlink:href="#journey-route"/></animateMotion></circle>'

    milestones = [
        ("01", "FOUNDATIONS", ["C, C++, DSA and problem solving", "built through regular practice,", "debugging and learning by doing."]),
        ("02", "FIRST SYSTEM", ["Banking System in C with", "authentication, input validation,", "file persistence and transactions."]),
        ("03", "DEVELOPER TOOLING", ["FirstPR AI: a mentor concept for", "understanding issues, codebases", "and planning useful tests."]),
        ("04", "FINTECH EXPLORATION", ["Ledger demo exploring wallets,", "payments, budgeting, fraud flows", "and merchant operations."]),
        ("05", "OPEN-SOURCE COMMUNITY", ["Hacktoberfest and KCET PRs/events;", "learning collaborative workflows,", "focused fixes and reviewable PRs."]),
        ("06", "RECOGNITION & NEXT", ["Top-5 at an NIT Jalandhar event;", "Campus Ambassador — Tata", "Imagination Challenge."]),
    ]
    placements = [
        (25, 112, 175, 91, milestones[0]),
        (350, 112, 500, 91, milestones[1]),
        (675, 112, 825, 91, milestones[2]),
        (675, 302, 825, 281, milestones[3]),
        (350, 302, 500, 281, milestones[4]),
        (25, 302, 175, 281, milestones[5]),
    ]
    for i, (x, y, cx, cy, item) in enumerate(placements):
        number, title, desc = item
        body += rect(x, y, 300, 145, PANEL, 13, EDGE)
        body += f'<rect x="{x+1}" y="{y+1}" width="298" height="4" rx="2" fill="{GREEN}"/>'
        body += txt(x+18, y+34, number, 13, GREEN, 700, "mono")
        body += txt(x+62, y+34, title, 14, FG, 700)
        for j, line in enumerate(desc):
            body += txt(x+18, y+70+j*22, line, 12, MUTED, 400)
        body += f'<circle cx="{cx}" cy="{cy}" r="13" fill="{PANEL}" stroke="{GREEN}" stroke-width="2"/>'
        body += txt(cx-9, cy+4, number, 9, FG, 700, "mono")
        if not STATIC:
            body += f'<circle cx="{cx}" cy="{cy}" r="16" fill="none" stroke="{GREEN}" stroke-width="1.5" opacity="0"><animate attributeName="r" values="13;22;13" dur="3.6s" begin="{i*0.42:.2f}s" repeatCount="indefinite"/><animate attributeName="opacity" values=".7;0;.7" dur="3.6s" begin="{i*0.42:.2f}s" repeatCount="indefinite"/></circle>'
    write("journey.svg", body, 475, 0.55, fonts)

def main():
    OUT.mkdir(exist_ok=True)
    data=json.loads(DATA.read_text()) if DATA.exists() else {"days":[]}
    days=data.get("days",[])
    chars="".join([ "Prabhjot Singh Building useful software and learning systems engineering C C++ GitHub LinkedIn Portfolio Featured repositories contributions month active days busiest day streak Ideas never die ~/ideas $ "]+[r[0]+r[2]+r[3] for r in REPOS]+[d["date"] for d in days]) + "Who am I C++ Developer Profile struct Developer string name Prabhjot Singh role B.Tech CSE Student vector focus C C++ DSA Open Source building Banking System FirstPR AI Ledger mindset Ideas never die THE JOURNEY SO FAR FOUNDATIONS Problem solving DSA debugging stronger fundamentals FIRST SYSTEM authentication validation file persistence transaction flows DEVELOPER TOOLING mentor concept exploring issues codebases test plans FINTECH EXPLORATION wallets payments budgeting fraud workflows merchant operations OPEN SOURCE COMMUNITY Hacktoberfest KCET PRs events collaborative maintainer-friendly workflows RECOGNITION Top-5 NIT Jalandhar event Campus Ambassador Tata Imagination Challenge"
    fonts=font_data(chars)
    render_whoami(fonts)
    render_journey(fonts)
    # A compact terminal panel under the name. The clip-path reveal makes the
    # motto appear as if it is being typed, one character at a time.
    terminal = (
      rect(76,158,520,58,PANEL,12,EDGE)
      + '<circle cx="96" cy="174" r="3.5" fill="#FF3B4E"/>'
      + '<circle cx="109" cy="174" r="3.5" fill="#FF7A86"/>'
      + '<circle cx="122" cy="174" r="3.5" fill="#6B3039"/>'
      + txt(142,179,"~/ideas",11,MUTED,500,"mono")
      + '<text x="96" y="201" font-size="16" fill="#FF7A86" font-weight="600" class="mono">$</text>'
      + '<defs><clipPath id="typed-line"><rect x="116" y="183" width="0" height="23"><animate attributeName="width" values="0;170;170;0" keyTimes="0;0.72;0.9;1" dur="4.8s" repeatCount="indefinite"/></rect></clipPath></defs>'
      + '<text x="116" y="201" font-size="16" fill="#FFF1F2" font-weight="600" class="mono" clip-path="url(#typed-line)">Ideas never die.</text>'
      + '<rect x="116" y="185" width="2" height="19" rx="1" fill="#FF3B4E"><animate attributeName="x" values="116;270;270;116" keyTimes="0;0.72;0.9;1" dur="4.8s" repeatCount="indefinite"/><animate attributeName="opacity" values="1;1;0;0;1" keyTimes="0;0.45;0.5;0.95;1" dur="4.8s" repeatCount="indefinite"/></rect>'
    )
    hero = (
      rect(35,39,7,240,GREEN,4,GREEN)
      + txt(75,100,"PRABHJOT SINGH",46,FG,750)
      + txt(77,137,"B.Tech CSE student · India",19,GREEN,650)
      + terminal
      + txt(77,248,"Building useful software, learning systems engineering, and contributing to open source.",16,MUTED)
      + txt(77,276,"C  /  C++  /  PYTHON  /  OPEN SOURCE",13,BLUE,650,"mono")
    )
    write("hero.svg",hero,310,0,fonts)
    for filename,label,sub,url in [
      ("github.svg","GITHUB","Open-source work","https://github.com/prabhtheone"),
      ("linkedin.svg","LINKEDIN","Let's connect","https://www.linkedin.com/in/prabhjot-singh-6aa788432"),
      ("portfolio.svg","PORTFOLIO","Projects & experiments","https://prabhtheone.vercel.app")]:
      body=rect(20,20,960,180)+txt(55,85,label,27,GREEN,700)+txt(55,130,sub,18,MUTED)+txt(920,130,"↗",28,BLUE,700)
      write(filename,body,220,0.25,fonts)
    monthly=collections.defaultdict(int)
    for d in days:
      if "date" in d: monthly[d["date"][:7]]+=int(d.get("count",0))
    months=sorted(monthly)[-12:]; maxv=max([monthly[m] for m in months] or [1]) or 1
    active=sum(1 for d in days if int(d.get("count",0))>0)
    total=sum(monthly.values()); best=max(days,key=lambda d:int(d.get("count",0)),default={})
    body=txt(45,55,"CONTRIBUTION ACTIVITY",15,GREEN,700,"mono")+txt(45,105,f"{total:,}",38,FG,700)+txt(45,137,"contributions · last 12 months",15,MUTED)+txt(355,105,str(streak(days)),38,FG,700)+txt(355,137,"day streak",15,MUTED)+txt(570,105,str(active),38,FG,700)+txt(570,137,"active days",15,MUTED)+txt(790,105,best.get("date","—"),22,FG,700)+txt(790,137,"busiest day",15,MUTED)
    for i,m in enumerate(months):
      x=55+i*76; val=monthly[m]; bar=max(4,70*val/maxv)
      body+=f'<rect x="{x}" y="{224-bar}" width="38" height="{bar}" rx="5" fill="{GREEN}" opacity=".85"/>'
      body+=txt(x-4,248,m[5:],11,MUTED,400,"mono")
    if not total: body+=txt(45,195,"Contribution counts currently unavailable or zero in source data.",14,MUTED)
    write("contributions.svg",body,275,0.5,fonts)
    for i,(title,slug,tech,desc) in enumerate(REPOS):
      body=txt(45,58,"FEATURED REPOSITORY",14,GREEN,700,"mono")+txt(45,112,title,34,FG,700)+txt(45,151,tech,17,BLUE,600)+txt(45,197,desc,17,MUTED)+txt(925,218,"↗",25,GREEN,700)
      write("repo-"+slug+".svg",body,245,0.7+i*.2,fonts)
    # GitHub calendar with a staggered crimson pulse that travels diagonally across the cells.
    body=txt(45,55,"CONTRIBUTION MAP  //  MOVING WAVE",15,GREEN,700,"mono")
    by={dt.date.fromisoformat(d["date"]):int(d.get("count",0)) for d in days if d.get("date")}
    dates=sorted(by)
    if dates:
      start=dates[0]-dt.timedelta(days=dates[0].weekday())
      for d in dates:
        col=(d-start).days//7; row=d.weekday(); val=by[d]
        opacity=.12 if val==0 else min(.95,.35+.15*val)
        peak=min(.98,max(.58,opacity+.48))
        pulse="" if STATIC else f'<animate class="smil" attributeName="opacity" values="{opacity:.2f};{peak:.2f};{opacity:.2f}" keyTimes="0;.16;1" dur="5.2s" begin="{col*.075+row*.10:.2f}s" repeatCount="indefinite"/>'
        body+=f'<rect x="{45+col*13}" y="{85+row*17}" width="10" height="13" rx="3" fill="{GREEN}" opacity="{opacity:.2f}"><title>{d.isoformat()}: {val} contributions</title>{pulse}</rect>'
    body+=txt(45,235,"LESS",11,MUTED)+''.join(f'<rect x="{90+i*17}" y="224" width="12" height="12" rx="3" fill="{GREEN}" opacity="{v}"/>' for i,v in enumerate([.12,.35,.55,.75,.95]))+txt(190,235,"MORE",11,MUTED)
    write("contribution-graph.svg",body,260,1.4,fonts)
    print("Rendered",len(list(OUT.glob("*.svg"))),"SVG cards ("+("static" if STATIC else "animated")+")")
if __name__=="__main__": main()
