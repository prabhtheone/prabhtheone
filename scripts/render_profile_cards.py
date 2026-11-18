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
BG, PANEL, EDGE, FG, MUTED, GREEN, BLUE = "#070b10", "#0d141c", "#1b2a36", "#e8f0f5", "#91a4b3", "#39ff88", "#76b7ff"
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
def main():
    OUT.mkdir(exist_ok=True)
    data=json.loads(DATA.read_text()) if DATA.exists() else {"days":[]}
    days=data.get("days",[])
    chars="".join([ "Prabhjot Singh Building useful software and learning systems engineering C C++ GitHub LinkedIn Portfolio Featured repositories contributions month active days busiest day streak "]+[r[0]+r[2]+r[3] for r in REPOS]+[d["date"] for d in days])
    fonts=font_data(chars)
    write("hero.svg", rect(35,40,8,178,GREEN,4,GREEN)+txt(75,105,"PRABHJOT SINGH",48,FG,750)+txt(77,151,"B.Tech CSE student · India",22,GREEN,600)+txt(77,190,"Building useful software, learning systems engineering, and contributing to open source.",19,MUTED)+txt(77,232,"C  /  C++  /  PYTHON  /  OPEN SOURCE",14,BLUE,600,"mono"),260,0,fonts)
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
    # GitHub calendar, seven rows; day cells remain native SVG shapes for img rendering.
    body=txt(45,55,"CONTRIBUTION GRAPH",15,GREEN,700,"mono")
    by={dt.date.fromisoformat(d["date"]):int(d.get("count",0)) for d in days if d.get("date")}
    dates=sorted(by)
    if dates:
      start=dates[0]-dt.timedelta(days=dates[0].weekday())
      for d in dates:
        col=(d-start).days//7; row=d.weekday(); val=by[d]
        opacity=.12 if val==0 else min(.95,.35+.15*val)
        body+=f'<rect x="{45+col*13}" y="{85+row*17}" width="10" height="13" rx="3" fill="{GREEN}" opacity="{opacity:.2f}"><title>{d.isoformat()}: {val} contributions</title></rect>'
    body+=txt(45,235,"Less",11,MUTED)+''.join(f'<rect x="{90+i*17}" y="224" width="12" height="12" rx="3" fill="{GREEN}" opacity="{v}"/>' for i,v in enumerate([.12,.35,.55,.75,.95]))+txt(190,235,"More",11,MUTED)
    write("contribution-graph.svg",body,260,1.4,fonts)
    print("Rendered",len(list(OUT.glob("*.svg"))),"SVG cards ("+("static" if STATIC else "animated")+")")
if __name__=="__main__": main()
