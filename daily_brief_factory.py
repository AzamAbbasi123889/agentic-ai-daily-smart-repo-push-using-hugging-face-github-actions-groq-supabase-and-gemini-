#!/usr/bin/env python3
"""One daily, AI-generated build brief; the human implements the project."""
import argparse, html, json, os, random, re, sys
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo
import requests

ROOT=Path(__file__).resolve().parent
try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
except ImportError:
    pass
OUT=ROOT/"daily_briefs"
HISTORY=ROOT/"data"/"brief_history.json"
CATALOG=ROOT/"data"/"projects.json"
OWNER=os.getenv("GITHUB_OWNER","AzamAbbasi123889")
GROQ_MODEL=os.getenv("GROQ_MODEL","openai/gpt-oss-120b")
GEMINI_MODEL=os.getenv("GEMINI_MODEL","gemini-3.8-flash")
HF_OPTIMIZER_MODEL=os.getenv("HF_OPTIMIZER_MODEL", os.getenv("HF_MODEL", "openai/gpt-oss-120b:fastest"))
TODAY=datetime.now(ZoneInfo("Asia/Kolkata")).date().isoformat()
CATEGORIES=["Agentic AI and Multi-Agent Systems","Advanced RAG and GraphRAG",
"LLM Evaluation and Observability","Transformers and NLP","Computer Vision and Multimodal AI",
"MLOps and Model Monitoring","Deep Learning and Efficient Training","AI Automation and Tool Use",
"AI Safety, Privacy and Security","Applied ML and Forecasting","LangChain, LangGraph and CrewAI",
"AI Developer Tools and Code Intelligence"]
SYSTEM="""You are a senior AI research engineer and product architect. Return one valid JSON object only.
Design an original portfolio-grade project that a B.Tech AI/ML student will build independently.
Do not write source code. Avoid generic chatbots, PDF-only RAG, resume scanners, basic sentiment
analysis, churn/fraud predictors, simple image classifiers, and any item on the exclusion list.
Give a real differentiator, a realistic 3-10 day MVP, acceptance criteria, architecture, data model,
API contracts, test plan, measurable evaluation targets, security/privacy, and deployment options.
Prefer Python; select tools only when justified: FastAPI/Flask, PyTorch, scikit-learn, Transformers,
LangChain, LangGraph, CrewAI, LangSmith, Supabase/Postgres/pgvector, Neo4j, Redis, MLflow, DVC,
Docker, GitHub Actions, OpenTelemetry, React. Use reproducible data and free/local MVP options.
Never invent benchmark results or citations. Recent papers are inspiration, not proof of novelty.
Return these fields:
{"title":"string","slug":"kebab-case","category":"provided category","difficulty":"Beginner/Intermediate/Advanced/Expert",
"estimated_days":5,"summary":"2-3 sentences","problem_statement":"string","target_users":["..."],
"unique_angle":"string","tech_stack":["technology and why"],"prerequisites":["..."],
"learning_outcomes":["..."],"mvp_features":[{"name":"...","description":"...","acceptance_criteria":["..."]}],
"architecture":{"overview":"...","components":[{"name":"...","responsibility":"..."}],"data_flow":["..."]},
"data_model":[{"entity":"...","fields":["..."]}],
"api_endpoints":[{"method":"GET","path":"/...","purpose":"..."}],
"milestones":[{"week":1,"name":"...","tasks":["..."],"deliverable":"..."}],
"evaluation_plan":[{"metric":"...","how_to_measure":"...","target":"target, not result"}],
"test_plan":["..."],"deployment_plan":["..."],"safety_and_privacy":["..."],
"stretch_goals":["..."],"resume_bullet":"fill real metrics after implementation",
"interview_questions":["..."]}"""

def readj(path,default):
    try: return json.loads(path.read_text(encoding="utf-8"))
    except (OSError,json.JSONDecodeError): return default
def slug(s): return re.sub(r"-+","-",re.sub(r"[^a-z0-9]+","-",str(s).lower())).strip("-")[:70]
def parsej(s):
    s=re.sub(r"^```(?:json)?\s*|\s*```$","",(s or "").strip(),flags=re.I)
    a,b=s.find("{"),s.rfind("}")
    if a<0 or b<=a: raise ValueError("Model did not return JSON")
    return json.loads(s[a:b+1])
def github_repos():
    token=os.getenv("GH_TOKEN","").strip()
    url="https://api.github.com/user/repos" if token else f"https://api.github.com/users/{OWNER}/repos"
    h={"Accept":"application/vnd.github+json"}
    if token: h["Authorization"]=f"Bearer {token}"
    out=[]
    for p in range(1,6):
        q={"per_page":100,"page":p,"sort":"updated","direction":"desc"}
        if token: q["affiliation"]="owner"
        else: q["type"]="owner"
        try:
            r=requests.get(url,headers=h,params=q,timeout=20); r.raise_for_status(); rows=r.json()
            out += [{"name":x.get("name",""),"description":x.get("description") or ""} for x in rows]
            if len(rows)<100: break
        except Exception as e: print(f"[warning] Repo scan: {e}",file=sys.stderr); break
    return out
def papers():
    try:
        r=requests.get("https://export.arxiv.org/api/query",params={"search_query":"(cat:cs.AI OR cat:cs.CL OR cat:cs.CV OR cat:cs.LG)","start":0,"max_results":8,"sortBy":"submittedDate","sortOrder":"descending"},timeout=25)
        r.raise_for_status()
        import xml.etree.ElementTree as ET
        root=ET.fromstring(r.text); ns={"a":"http://www.w3.org/2005/Atom"}; out=[]
        for e in root.findall("a:entry",ns):
            title=" ".join(e.findtext("a:title","",ns).split()); url=e.findtext("a:id","",ns)
            if title and url: out.append({"title":html.unescape(title),"url":url,"date":e.findtext("a:updated","",ns)[:10],"summary":html.unescape(" ".join(e.findtext("a:summary","",ns).split())[:300])})
        return out
    except Exception as e: print(f"[warning] Research feed: {e}",file=sys.stderr); return []
def db_client(required):
    url=os.getenv("SUPABASE_URL","").strip()
    key=os.getenv("SUPABASE_SECRET_KEY","").strip() or os.getenv("SUPABASE_SERVICE_ROLE_KEY","").strip()
    if not url or not key:
        if required: raise RuntimeError("Add SUPABASE_URL and SUPABASE_SECRET_KEY (or SUPABASE_SERVICE_ROLE_KEY) to GitHub Actions secrets.")
        return None
    from supabase import create_client
    return create_client(url,key)
def memory(db):
    out=[]
    local=readj(HISTORY,[])
    if isinstance(local,list): out += [x for x in local if isinstance(x,dict)]
    cat=readj(CATALOG,{"projects":[]})
    if isinstance(cat,dict): out += cat.get("projects",[])
    if db:
        try: out += db.table("project_memory").select("slug,title,category,summary,tech_stack,status,created_at").order("created_at",desc=True).limit(200).execute().data or []
        except Exception as e: raise RuntimeError("Supabase project_memory unavailable; run supabase/schema.sql first.") from e
    return out
def choose_category(rows):
    counts={c:0 for c in CATEGORIES}
    for x in rows:
        c=x.get("category",""); d=str(x.get("created_at") or x.get("date") or "")[:10]
        try: age=(datetime.fromisoformat(TODAY)-datetime.fromisoformat(d)).days
        except ValueError: age=999
        if c in counts and 0<=age<30: counts[c]+=1
    low=min(counts.values())
    return random.Random(TODAY).choice([c for c,n in counts.items() if n==low])
def words(s):
    stop={"the","and","for","from","with","using","system","platform","engine","project","tool","app","based"}
    return {w for w in re.findall(r"[a-z0-9]+",str(s).lower()) if len(w)>2 and w not in stop}
def similarity(a,b):
    x,y=words(a),words(b); return len(x&y)/len(x|y) if x and y else 0
def prompt_for(category,rows,repos,refs):
    old=[]
    for x in rows[-100:]:
        t=x.get("title") or x.get("name") or x.get("repository") or x.get("slug")
        if t: old.append(f"- {t}: {str(x.get('summary') or x.get('description') or '')[:120]}")
    repo=[f"- {x['name']}: {x['description'][:90]}" for x in repos[:140] if x.get("name")]
    ref=[f"- {x['title']} ({x['date']}): {x['summary']} | {x['url']}" for x in refs]
    return f"""Date: {TODAY}. Rotate toward category: {category}.
Do not repeat existing repositories or past project problems. Existing repositories:
{chr(10).join(repo) or '- Repository list unavailable.'}
Past memory:
{chr(10).join(old) or '- No previous briefs found.'}
Recent arXiv research (use only exact links below if relevant):
{chr(10).join(ref) or '- Research feed unavailable.'}
Return every JSON field from the system schema. Give concrete endpoints, milestones, acceptance criteria,
testing, evaluation metrics, privacy, deployment and a portfolio-quality differentiator. Do not write code."""
def groq(prompt):
    from groq import Groq
    c=Groq(api_key=os.environ["GROQ_API_KEY"])
    r=c.chat.completions.create(model=GROQ_MODEL,messages=[{"role":"system","content":SYSTEM},{"role":"user","content":prompt}],response_format={"type":"json_object"},max_completion_tokens=6500)
    return parsej(r.choices[0].message.content),f"Groq / {GROQ_MODEL}"
def gemini(prompt):
    from google import genai
    c=genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    r=c.models.generate_content(model=GEMINI_MODEL,contents=SYSTEM+"\n"+prompt,config={"response_mime_type":"application/json"})
    return parsej(r.text),f"Gemini fallback / {GEMINI_MODEL}"
def huggingface_json(system_prompt, user_prompt, max_tokens=6500):
    """Call Hugging Face Inference Providers' OpenAI-compatible chat-completion API."""
    from huggingface_hub import InferenceClient
    token=os.getenv("HF_TOKEN", "").strip()
    if not token:
        raise RuntimeError("HF_TOKEN is not configured")
    client=InferenceClient(token=token)
    result=client.chat_completion(
        model=HF_OPTIMIZER_MODEL,
        messages=[
            {"role":"system", "content":system_prompt},
            {"role":"user", "content":user_prompt},
        ],
        response_format={"type":"json_object"},
        max_tokens=max_tokens,
    )
    content=result.choices[0].message.content
    if not content:
        raise ValueError("Hugging Face returned an empty completion")
    return parsej(content)
def generate(p):
    """Generate the initial project spec with Groq; use Gemini only as generation fallback.

    Hugging Face is deliberately NOT a project-generation fallback. It is reserved for the
    separate optimization pass below.
    """
    errs=[]
    if os.getenv("GROQ_API_KEY","").strip():
        try: return groq(p)
        except Exception as e: errs.append(f"Groq: {e}"); print(f"[warning] {errs[-1]}",file=sys.stderr)
    if os.getenv("GEMINI_API_KEY","").strip():
        try: return gemini(p)
        except Exception as e: errs.append(f"Gemini: {e}"); print(f"[warning] {errs[-1]}",file=sys.stderr)
    raise RuntimeError("Generation failed. Configure GROQ_API_KEY and/or GEMINI_API_KEY. "+" | ".join(errs))
def optimize_with_huggingface(spec):
    """Use Hugging Face Inference Providers as a dedicated project-spec optimizer.

    The optimizer improves technical clarity, MVP scope, architecture, acceptance criteria,
    data/API design and evaluation. It must not change the project's central idea, title or slug.
    If the optimizer fails, the unoptimized but valid Groq/Gemini result is retained.
    """
    if not os.getenv("HF_TOKEN", "").strip():
        return spec, {"enabled": False, "status": "skipped", "model": HF_OPTIMIZER_MODEL,
                      "reason": "HF_TOKEN not configured"}
    prompt = """Act as a strict senior AI systems engineer optimizing a project specification for a student
who will implement it manually. Return the COMPLETE optimized project as a JSON object matching the
same schema. Preserve the central project idea, exact title, exact slug, and category. Do not write
source code. Improve coherence, implementability, architecture boundaries, data model, API contracts,
acceptance criteria, realistic milestones, evaluation metrics, failure handling, tests, privacy, and
free/local-first setup. Remove unnecessary technologies; every retained technology must have a job.
Never invent test results or claim the project is proven novel. Keep effort within the requested 3-10 day
scope unless the original estimates otherwise. Only output the complete JSON object.


PROJECT TO OPTIMIZE:
""" + json.dumps(spec, ensure_ascii=False)
    try:
        optimized = huggingface_json(
            "You are an expert AI project specification optimizer. Respond with only valid JSON.",
            prompt,
            max_tokens=6500,
        )
        optimized = clean(optimized)
        if optimized["title"] != spec["title"] or optimized["slug"] != spec["slug"] or optimized["category"] != spec["category"]:
            raise ValueError("Optimizer changed the protected title, slug, or category")
        return optimized, {"enabled": True, "status": "optimized", "model": HF_OPTIMIZER_MODEL}
    except Exception as e:
        print(f"[warning] Hugging Face optimization failed; retaining original spec: {e}", file=sys.stderr)
        return spec, {"enabled": True, "status": "failed_keep_original", "model": HF_OPTIMIZER_MODEL,
                      "reason": str(e)[:500]}
def critique(s):
    review_prompt='Review novelty and feasibility. JSON only: {"novelty_score":1,"feasibility_score":1,"overlap_risks":["..."],"improvements":["..."]}. Scores 1-10. Brief: '+json.dumps(s,ensure_ascii=False)[:12000]
    if os.getenv("GEMINI_API_KEY","").strip():
        try:
            from google import genai
            c=genai.Client(api_key=os.environ["GEMINI_API_KEY"])
            r=c.models.generate_content(model=GEMINI_MODEL,contents=review_prompt,config={"response_mime_type":"application/json"})
            return parsej(r.text)
        except Exception as e: print(f"[warning] Gemini review: {e}",file=sys.stderr)
    return None
def clean(s):
    req=["title","summary","problem_statement","unique_angle","tech_stack","mvp_features","architecture","data_model","api_endpoints","milestones","evaluation_plan","test_plan","deployment_plan","learning_outcomes","resume_bullet","interview_questions"]
    bad=[k for k in req if not s.get(k)]
    if bad: raise ValueError("Missing fields: "+", ".join(bad))
    s["title"]=str(s["title"]).strip(); s["slug"]=slug(s.get("slug") or s["title"])
    if len(s["title"])<8 or not isinstance(s["tech_stack"],list) or len(s["tech_stack"])<3: raise ValueError("Title or tech stack is too weak")
    s.setdefault("category","AI Engineering"); s.setdefault("difficulty","Intermediate"); s.setdefault("estimated_days",5)
    for k in ("target_users","prerequisites","safety_and_privacy","stretch_goals"): s.setdefault(k,[])
    return s
def arr(x): return [str(v) for v in x if isinstance(v,(str,int,float)) and str(v).strip()] if isinstance(x,list) else []
def render(s,refs,provider,review,optimization):
    L=[f"# {s['title']}","",f"> {s['summary']}","",f"**Date:** {TODAY} | **Category:** {s['category']} | **Difficulty:** {s['difficulty']} | **Effort:** {s['estimated_days']} days","","**Build-it-yourself brief:** this factory produces the specification, not source code.","","## 1. Problem statement","",s["problem_statement"],"","### Target users",""]
    L += ["- "+x for x in arr(s.get("target_users"))]
    L += ["","## 2. Unique angle","",s["unique_angle"],"","## 3. MVP features and acceptance criteria",""]
    for f in s["mvp_features"]:
        if isinstance(f,dict):
            L += ["### "+str(f.get("name","Feature")),"",str(f.get("description","")),""]+["- [ ] "+x for x in arr(f.get("acceptance_criteria"))]+[""]
    L += ["## 4. Technology stack",""]+["- "+x for x in arr(s["tech_stack"])]
    a=s["architecture"]; L += ["","## 5. Architecture","",str(a.get("overview","")),""]
    for c in a.get("components",[]):
        if isinstance(c,dict): L.append(f"- **{c.get('name','Component')}** — {c.get('responsibility','')}")
    L += ["","### Data flow",""]+[f"{i}. {x}" for i,x in enumerate(arr(a.get("data_flow")),1)]
    L += ["","## 6. Data model",""]
    for d in s["data_model"]:
        if isinstance(d,dict): L.append(f"- **{d.get('entity','Entity')}:** {', '.join(arr(d.get('fields')))}")
    L += ["","## 7. API contracts","","| Method | Path | Purpose |","|---|---|---|"]
    for e in s["api_endpoints"]:
        if isinstance(e,dict): L.append(f"| {e.get('method','GET')} | {e.get('path','/')} | {str(e.get('purpose','')).replace('|','/')} |")
    L += ["","## 8. Build milestones",""]
    for m in s["milestones"]:
        if isinstance(m,dict): L += [f"### {m.get('week','')} — {m.get('name','Milestone')}",""]+["- [ ] "+x for x in arr(m.get("tasks"))]+["",f"**Deliverable:** {m.get('deliverable','Working increment')}",""]
    L += ["","## 9. Evaluation plan","","Targets to test, not claimed results.",""]
    for m in s["evaluation_plan"]:
        if isinstance(m,dict): L.append(f"- **{m.get('metric','Metric')}:** {m.get('how_to_measure','')} Target: {m.get('target','Set a baseline')}")
    for title,k in [("Testing checklist","test_plan"),("Deployment and setup","deployment_plan"),("Prerequisites","prerequisites"),("Safety and privacy","safety_and_privacy"),("Learning outcomes","learning_outcomes"),("Stretch goals","stretch_goals")]:
        L += ["",f"## {title}",""]+[("- [ ] " if k in ("test_plan","deployment_plan") else "- ")+x for x in arr(s.get(k))]
    L += ["","## Resume bullet — add real results after implementation","",s["resume_bullet"],"","## Interview questions",""]+["- "+x for x in arr(s["interview_questions"])]
    L += ["","## Recent research to explore","","Fetched from arXiv on this run; leads for further reading, not proof of originality.",""]
    for p in refs: L += [f"- [{p['title']}]({p['url']}) — updated {p['date']}.",f"  - {p['summary']}",""]
    if not refs: L.append("Live research feed unavailable.")
    L += ["", "## Hugging Face optimization", "", f"- Status: {optimization.get('status', 'not run')}", f"- Model: {optimization.get('model', HF_OPTIMIZER_MODEL)}"]
    if optimization.get("reason"):
        L.append(f"- Note: {optimization['reason']}")
    if review:
        L += ["", "## Gemini design review", "", f"- Novelty score: {review.get('novelty_score','unscored')}/10", f"- Feasibility score: {review.get('feasibility_score','unscored')}/10", ""]
        for k,label in [("overlap_risks","Overlap risks"),("improvements","Suggested improvements")]:
            L += [f"### {label}",""]+["- "+x for x in arr(review.get(k))]
    return "\n".join(L+["","---",f"Generated with {provider}. Verify assumptions and report only measured results.",""])
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--dry-run",action="store_true"); ap.add_argument("--require-supabase",action="store_true"); args=ap.parse_args()
    OUT.mkdir(parents=True,exist_ok=True)
    if not args.dry_run and any(OUT.glob(f"{TODAY}-*.md")): print(f"[info] Brief already exists for {TODAY}; one per day rule kept."); return 0
    db=db_client(args.require_supabase); rows=memory(db); repos=github_repos(); refs=papers(); cat=choose_category(rows); prompt=prompt_for(cat,rows,repos,refs)
    titles=[str(x.get("title") or x.get("name") or x.get("repository") or x.get("slug") or "") for x in rows]
    slugs={slug(x.get("name","")) for x in repos if x.get("name")}
    slugs.update(slug(x.get("repository") or x.get("name") or x.get("slug") or "") for x in rows)
    spec=provider=None; error="unknown error"
    for attempt in range(3):
        try:
            p=prompt if not attempt else prompt+"\nCreate a different candidate. Exclude: "+json.dumps(titles[-100:]+list(slugs)[-100:])
            candidate,provider=generate(p); candidate=clean(candidate)
            if candidate["slug"] in slugs or any(similarity(candidate["title"],t)>=0.72 for t in titles if t):
                error="duplicate candidate: "+candidate["title"]; titles.append(candidate["title"]); slugs.add(candidate["slug"]); continue
            spec=candidate; break
        except Exception as e: error=str(e); print(f"[warning] Candidate {attempt+1}: {e}",file=sys.stderr)
    if spec is None: raise RuntimeError("No unique brief generated after three attempts: "+error)
    spec, optimization = optimize_with_huggingface(spec)
    review=critique(spec) if os.getenv("GEMINI_API_KEY","").strip() else None
    md=render(spec,refs,provider,review,optimization); dest=OUT/f"{TODAY}-{spec['slug']}.md"
    if args.dry_run: print(md); print(f"\n[DRY RUN] Would save {dest.relative_to(ROOT)}"); return 0
    if db:
        db.table("project_memory").insert({"slug":spec["slug"],"title":spec["title"],"category":spec["category"],"difficulty":spec["difficulty"],"estimated_days":int(spec.get("estimated_days",5)),"summary":spec["summary"],"tech_stack":[str(x) for x in spec["tech_stack"]],"spec_json":spec,"brief_markdown":md,"research_sources":refs,"review_json":{"gemini":review or {},"huggingface_optimization":optimization},"ai_provider":provider,"status":"planned","build_notes":"","github_owner":OWNER}).execute()
    dest.write_text(md,encoding="utf-8")
    h=readj(HISTORY,[]); h=h if isinstance(h,list) else []
    h.append({"slug":spec["slug"],"title":spec["title"],"category":spec["category"],"summary":spec["summary"],"tech_stack":spec["tech_stack"],"created_at":datetime.now(timezone.utc).isoformat(),"status":"planned","brief_path":str(dest.relative_to(ROOT)),"ai_provider":provider,"optimizer":optimization})
    HISTORY.parent.mkdir(parents=True,exist_ok=True); HISTORY.write_text(json.dumps(h,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(f"[success] {dest.relative_to(ROOT)} | {spec['title']} | {provider}"); print("[success] Supabase memory saved." if db else "[info] Local history saved; Supabase not configured."); return 0
if __name__=="__main__":
    try: raise SystemExit(main())
    except Exception as e: print(f"[error] {e}",file=sys.stderr); raise SystemExit(1)
