from typing import List, Dict, Any, Optional
import json, re
import xml.etree.ElementTree as ET

try:
    import yaml
except ImportError:
    yaml = None  # si pyyaml n'est pas installé


# ---------- Diff / Patch ------------------------------------------------------
def parse_diff_tool(diff_text: str) -> Dict[str, Any]:
    """
    Parse un texte .diff/.patch en hunks structurés.
    Args:
        diff_text: contenu du diff (string)
    Returns:
        {"hunks":[{"file":str,"header":str,"added":[str],"removed":[str],"snippet":str}, ...]}
    """
    if not diff_text:
        return {"hunks": []}

    hunks: List[Dict[str, Any]] = []
    lines = diff_text.splitlines()
    cur_file: Optional[str] = None
    header = ""
    added: List[str] = []
    removed: List[str] = []
    snippet: List[str] = []

    def commit():
        nonlocal hunks, cur_file, header, added, removed, snippet
        if cur_file and (added or removed or snippet):
            hunks.append({
                "file": cur_file,
                "header": header,
                "added": added[:],
                "removed": removed[:],
                "snippet": "\n".join(snippet[-40:])
            })
        header, added, removed, snippet = "", [], [], []

    for ln in lines:
        if ln.startswith("diff --git "):
            commit()
            cur_file = None
        if ln.startswith("+++ ") or ln.startswith("--- "):
            if ln.startswith("+++ b/"):
                cur_file = ln[6:]
            elif ln.startswith("+++ "):
                cur_file = ln[4:]
        elif ln.startswith("@@ "):
            header = ln
        else:
            if ln.startswith("+"): added.append(ln[1:])
            elif ln.startswith("-"): removed.append(ln[1:])
            snippet.append(ln)

    commit()
    return {"hunks": hunks}


# ---------- JSON / YAML extraction -------------------------------------------
def extract_json_tool(text: str) -> Dict[str, Any]:
    """
    Extrait un objet JSON depuis du texte (essayes JSON direct, sinon 1er bloc {...}).
    Args: text
    Returns: {"ok": bool, "data": dict|null}
    """
    if not text:
        return {"ok": False, "data": None}
    try:
        return {"ok": True, "data": json.loads(text)}
    except Exception:
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            try:
                return {"ok": True, "data": json.loads(text[start:end+1])}
            except Exception:
                return {"ok": False, "data": None}
        return {"ok": False, "data": None}

def extract_yaml_tool(text: str) -> Dict[str, Any]:
    """
    Extrait un objet YAML depuis du texte (si pyyaml dispo).
    Args: text
    Returns: {"ok": bool, "data": dict|null}
    """
    if not text or yaml is None:
        return {"ok": False, "data": None}
    try:
        data = yaml.safe_load(text)
        return {"ok": True, "data": data}
    except Exception:
        return {"ok": False, "data": None}


# ---------- Coverage (coverage.xml / lcov.info) ------------------------------
def coverage_from_coverage_xml_tool(xml_text: str) -> Dict[str, Any]:
    """
    Calcule les % de couverture depuis un coverage.xml Cobertura/Jacoco-like.
    Args: xml_text
    Returns: {"line_pct": float, "branch_pct": float}
    """
    if not xml_text:
        return {"line_pct": 0.0, "branch_pct": 0.0}
    try:
        root = ET.fromstring(xml_text)
        line_rate = float(root.attrib.get("line-rate", 0.0)) * 100.0
        branch_rate = float(root.attrib.get("branch-rate", 0.0)) * 100.0
        return {"line_pct": round(line_rate, 2), "branch_pct": round(branch_rate, 2)}
    except Exception:
        return {"line_pct": 0.0, "branch_pct": 0.0}

def coverage_from_lcov_tool(lcov_text: str) -> Dict[str, Any]:
    """
    Calcule un % ligne depuis un lcov.info.
    Args: lcov_text
    Returns: {"line_pct": float, "lines_total": int, "lines_covered": int}
    """
    if not lcov_text:
        return {"line_pct": 0.0, "lines_total": 0, "lines_covered": 0}
    total, covered = 0, 0
    for line in lcov_text.splitlines():
        if line.startswith("DA:"):
            try:
                _, rest = line.split("DA:", 1)
                _, count = rest.split(",")
                total += 1
                if int(count) > 0:
                    covered += 1
            except Exception:
                continue
    pct = (covered / total * 100.0) if total else 0.0
    return {"line_pct": round(pct, 2), "lines_total": total, "lines_covered": covered}


# ---------- Security (Semgrep / Bandit) --------------------------------------
def normalize_bandit_tool(doc_text: str) -> Dict[str, Any]:
    """
    Normalise un rapport Bandit (JSON ou YAML) en findings génériques.
    Args: doc_text
    Returns: {"findings":[{"rule_id","title","severity","file","line","message"}]}
    """
    data = extract_json_tool(doc_text)["data"] or extract_yaml_tool(doc_text)["data"] or {}
    findings: List[Dict[str, Any]] = []
    for r in (data or {}).get("results", []):
        findings.append({
            "rule_id": r.get("test_id") or r.get("test_name"),
            "title": r.get("issue_text"),
            "severity": (r.get("issue_severity") or "LOW").upper(),
            "file": r.get("filename"),
            "line": r.get("line_number"),
            "message": r.get("more_info") or r.get("issue_confidence"),
        })
    return {"findings": findings}

def normalize_semgrep_tool(doc_text: str) -> Dict[str, Any]:
    """
    Normalise un rapport Semgrep (JSON ou YAML) en findings génériques.
    Args: doc_text
    Returns: {"findings":[{"rule_id","title","severity","file","line","message"}]}
    """
    data = extract_json_tool(doc_text)["data"] or extract_yaml_tool(doc_text)["data"] or {}
    findings: List[Dict[str, Any]] = []
    for r in (data or {}).get("results", []):
        loc = r.get("path") or (r.get("extra", {}).get("metavars", {}).get("path", {}).get("abstract_content"))
        sev = (r.get("extra", {}).get("severity") or "LOW").upper()
        findings.append({
            "rule_id": r.get("check_id") or r.get("rule_id"),
            "title": r.get("extra", {}).get("message") or "Semgrep finding",
            "severity": sev,
            "file": loc or r.get("path"),
            "line": (r.get("start") or {}).get("line"),
            "message": (r.get("extra", {}).get("metadata") or {}).get("shortlink", ""),
        })
    return {"findings": findings}


# ---------- Stack traces ------------------------------------------------------
_STACK_PATTERNS = [
    re.compile(r'File "([^"]+)", line (\d+), in ([^\n]+)'),        # Python
    re.compile(r'at ([\w./-]+):(\d+):\d+'),                        # JS/TS
    re.compile(r'at ([\w.$/\\-]+)\(([\w./-]+):(\d+)\)'),           # Java (Class.method(File.java:123))
]

def parse_stacktrace_tool(text: str) -> Dict[str, Any]:
    """
    Extrait fichiers/lignes depuis des stack traces (Python/JS/Java).
    Args: text
    Returns: {"items":[{"file","line","symbol"}]}
    """
    items: List[Dict[str, Any]] = []
    if not text:
        return {"items": items}
    for pat in _STACK_PATTERNS:
        for m in pat.finditer(text):
            g = m.groups()
            if len(g) == 3 and str(g[1]).isdigit():
                items.append({"file": g[0], "line": int(g[1]), "symbol": g[2]})
            elif len(g) == 2 and str(g[1]).isdigit():
                items.append({"file": g[0], "line": int(g[1]), "symbol": ""})
            elif len(g) == 3 and str(g[2]).isdigit():
                items.append({"file": g[1], "line": int(g[2]), "symbol": g[0]})
    return {"items": items}


# ---------- Score qualité -----------------------------------------------------
def quality_score_tool(coverage_line_pct: float = 0.0, violations: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """
    Calcule un score qualité 0–100.
    Args:
        coverage_line_pct: pourcentage lignes couvertes (0-100)
        violations: liste [{"severity":"LOW|MEDIUM|HIGH", ...}]
    Returns:
        {"score": int}
    """
    score = int(max(0.0, min(100.0, float(coverage_line_pct or 0.0))))
    for v in (violations or []):
        sev = (v.get("severity") or "LOW").upper()
        score -= 5 if sev == "HIGH" else 2 if sev == "MEDIUM" else 1
    return {"score": max(0, min(score, 100))}


# ------------------------------------------------------------------------------
# UTILITAIRES GÉNÉRIQUES (JSON / YAML / TABLE)
# ------------------------------------------------------------------------------

def _extract_json(text: str) -> Optional[dict]:
    if not text:
        return None
    try:
        return json.loads(text)
    except Exception:
        # tente bloc {...}
        s, e = text.find("{"), text.rfind("}")
        if s >= 0 and e > s:
            try:
                return json.loads(text[s:e+1])
            except Exception:
                return None
    return None

def _extract_yaml(text: str) -> Optional[dict]:
    if not text or yaml is None:
        return None
    try:
        return yaml.safe_load(text)
    except Exception:
        return None

def _to_number(val, default=0.0) -> float:
    try:
        return float(val)
    except Exception:
        return float(default)

def _count_by(items: List[Dict[str, Any]], key: str) -> Dict[str, int]:
    out: Dict[str, int] = {}
    for it in items or []:
        k = str(it.get(key, "") or "").upper()
        out[k] = out.get(k, 0) + 1
    return out


# ------------------------------------------------------------------------------
# 1) PROJECT MANAGEMENT MODULE
# SprintManagerAgent / BacklogGroomerBot / TeamCoordinatorAgent
# ------------------------------------------------------------------------------

def pm_parse_issues_tool(json_or_yaml_text: str) -> Dict[str, Any]:
    """
    Parse un backlog (Linear/Jira-like) pour extraire: id, title, status, points, assignee.
    Returns: {"items":[{id,title,status,points,assignee}], "totals":{"points":X}}
    """
    data = _extract_json(json_or_yaml_text) or _extract_yaml(json_or_yaml_text) or {}
    items: List[Dict[str, Any]] = []
    total_points = 0.0
    for it in data.get("issues", data.get("items", [])) or []:
        pts = _to_number(it.get("points") or it.get("story_points") or 0)
        total_points += pts
        items.append({
            "id": it.get("id") or it.get("key"),
            "title": it.get("title") or it.get("summary"),
            "status": it.get("status") or it.get("state"),
            "points": pts,
            "assignee": (it.get("assignee") or {}).get("name") if isinstance(it.get("assignee"), dict) else it.get("assignee"),
            "labels": it.get("labels") or []
        })
    return {"items": items, "totals": {"points": total_points}}

def pm_burndown_from_events_tool(text: str) -> Dict[str, Any]:
    """
    Calcule un burndown (date -> points_restants) à partir d'événements 'add/remove/close' avec 'points'.
    Input attendu: JSON {"events":[{"date":"YYYY-MM-DD","op":"add|remove|close","points":N}...]}
    """
    data = _extract_json(text) or {}
    series: Dict[str, float] = {}
    remaining = 0.0
    for ev in sorted(data.get("events", []), key=lambda x: x.get("date", "")):
        op = (ev.get("op") or "").lower()
        pts = _to_number(ev.get("points", 0))
        date = ev.get("date", "")
        if op in ("add", "open"): remaining += pts
        elif op in ("remove",): remaining -= pts
        elif op in ("close", "done"): remaining -= pts
        remaining = max(0.0, remaining)
        series[date] = round(remaining, 2)
    return {"burndown": series}

def pm_capacity_plan_tool(text: str) -> Dict[str, Any]:
    """
    Estime la capacité d'un sprint: velocity, dispo équipe, focus factor.
    Input JSON: {"velocity": N, "members":[{"name":"A","availability":1.0}, ...], "focus_factor": 0.7}
    Returns: {"capacity_points": X}
    """
    data = _extract_json(text) or {}
    velocity = _to_number(data.get("velocity", 0))
    focus = _to_number(data.get("focus_factor", 0.7))
    members = data.get("members", [])
    availability = sum(_to_number(m.get("availability", 1.0)) for m in members) or 1.0
    capacity = velocity * focus * availability
    return {"capacity_points": round(capacity, 2)}


# ------------------------------------------------------------------------------
# 2) DEVOPS MODULE
# DeploymentManagerBot / PipelineOrchestratorAgent / SystemMonitorBot
# ------------------------------------------------------------------------------

def devops_parse_ci_config_tool(yaml_or_json_text: str) -> Dict[str, Any]:
    """
    Extrait les jobs/steps d'une config CI (CircleCI/GitHub Actions-like).
    Returns: {"jobs":[{"name":..., "steps":[...]}]}
    """
    data = _extract_yaml(yaml_or_json_text) or _extract_json(yaml_or_json_text) or {}
    jobs = []
    for name, job in (data.get("jobs") or {}).items():
        steps = []
        for st in job.get("steps", []):
            if isinstance(st, dict):
                k = list(st.keys())[0]
                steps.append(k)
            else:
                steps.append(str(st))
        jobs.append({"name": name, "steps": steps})
    return {"jobs": jobs}

def devops_junit_summary_tool(xml_text: str) -> Dict[str, Any]:
    """
    Résume un rapport JUnit XML: tests, failures, errors, skipped.
    """
    if not xml_text:
        return {"tests": 0, "failures": 0, "errors": 0, "skipped": 0}
    try:
        root = ET.fromstring(xml_text)
        # <testsuite tests=".." failures=".." errors=".." skipped="..">
        if root.tag.endswith("testsuite"):
            return {
                "tests": int(root.attrib.get("tests", 0)),
                "failures": int(root.attrib.get("failures", 0)),
                "errors": int(root.attrib.get("errors", 0)),
                "skipped": int(root.attrib.get("skipped", 0))
            }
        # <testsuites>
        total = {"tests": 0, "failures": 0, "errors": 0, "skipped": 0}
        for ts in root.findall(".//testsuite"):
            total["tests"] += int(ts.attrib.get("tests", 0))
            total["failures"] += int(ts.attrib.get("failures", 0))
            total["errors"] += int(ts.attrib.get("errors", 0))
            total["skipped"] += int(ts.attrib.get("skipped", 0))
        return total
    except Exception:
        return {"tests": 0, "failures": 0, "errors": 0, "skipped": 0}

def devops_parse_k8s_manifest_tool(yaml_text: str) -> Dict[str, Any]:
    """
    Extrait les images, replicas et ports d'un manifest Kubernetes (Deployment/Service).
    Returns: {"deployments":[{name, image, replicas}], "services":[{name, ports}]} 
    """
    data = _extract_yaml(yaml_text) or {}
    deployments, services = [], []
    if isinstance(data, dict) and "kind" in data:
        docs = [data]
    elif isinstance(data, list):
        docs = data
    else:
        docs = []

    for d in docs:
        kind = d.get("kind", "")
        meta = d.get("metadata", {}) or {}
        name = meta.get("name")
        if kind == "Deployment":
            spec = d.get("spec", {}) or {}
            replicas = spec.get("replicas", 1)
            tpl = (spec.get("template") or {}).get("spec", {}) or {}
            containers = tpl.get("containers", []) or []
            for c in containers:
                deployments.append({"name": name, "image": c.get("image"), "replicas": replicas})
        elif kind == "Service":
            spec = d.get("spec", {}) or {}
            ports = [{"port": p.get("port"), "targetPort": p.get("targetPort")} for p in (spec.get("ports") or [])]
            services.append({"name": name, "ports": ports})
    return {"deployments": deployments, "services": services}

def devops_logs_errors_tool(log_text: str) -> Dict[str, Any]:
    """
    Agrège les erreurs par motif depuis des logs (stack, ERROR, exception).
    Returns: {"top_errors":[{"pattern","count"}]}
    """
    if not log_text:
        return {"top_errors": []}
    patterns = [
        r'ERROR[: ]+([^\n]+)', r'Exception[: ]+([^\n]+)', r'CRITICAL[: ]+([^\n]+)'
    ]
    counts: Dict[str, int] = {}
    for pat in patterns:
        for m in re.finditer(pat, log_text):
            msg = m.group(1).strip()
            counts[msg] = counts.get(msg, 0) + 1
    top = sorted([{"pattern": k, "count": v} for k, v in counts.items()], key=lambda x: -x["count"])[:20]
    return {"top_errors": top}

def devops_latency_parse_tool(text: str) -> Dict[str, Any]:
    """
    Extrait des latences p50/p95/p99 depuis des lignes 'latency=123ms' ou 'p95=250ms'.
    Returns: {"p50":..., "p95":..., "p99":...} si trouvé.
    """
    vals = {}
    for key in ["p50", "p95", "p99", "latency"]:
        m = re.search(rf'{key}\s*=\s*(\d+)\s*ms', text or "", re.IGNORECASE)
        if m:
            vals[key.upper()] = int(m.group(1))
    return {"p50": vals.get("P50"), "p95": vals.get("P95"), "p99": vals.get("P99"), "latency": vals.get("LATENCY")}


# ------------------------------------------------------------------------------
# 3) DOCUMENTATION MODULE
# DocGeneratorAgent / WikiMaintainerBot / KnowledgeOrganizerAgent
# ------------------------------------------------------------------------------

def doc_parse_openapi_tool(text: str) -> Dict[str, Any]:
    """
    Extrait des endpoints d'un OpenAPI (YAML/JSON) : méthode, chemin, résumé.
    Returns: {"endpoints":[{"method","path","summary"}]}
    """
    data = _extract_json(text) or _extract_yaml(text) or {}
    endpoints = []
    for path, methods in (data.get("paths") or {}).items():
        for method, spec in (methods or {}).items():
            if not isinstance(spec, dict):
                continue
            endpoints.append({
                "method": method.upper(),
                "path": path,
                "summary": spec.get("summary") or (spec.get("operationId") or "")
            })
    return {"endpoints": endpoints}

def doc_extract_codeblocks_tool(md_text: str) -> Dict[str, Any]:
    """
    Extrait les blocs de code (```lang ...```) d'un Markdown.
    Returns: {"blocks":[{"lang","code"}]}
    """
    blocks = []
    for m in re.finditer(r"```([\w+-]*)\n(.*?)```", md_text or "", re.DOTALL):
        lang = m.group(1) or ""
        code = m.group(2).strip()
        blocks.append({"lang": lang, "code": code})
    return {"blocks": blocks}

def wiki_front_matter_tool(md_text: str) -> Dict[str, Any]:
    """
    Parse le front matter YAML d'une page Markdown (--- ... ---).
    Returns: {"front_matter": dict or None}
    """
    if not md_text:
        return {"front_matter": None}
    m = re.match(r"^---\n(.*?)\n---\n", md_text, re.DOTALL)
    if not m:
        return {"front_matter": None}
    data = _extract_yaml(m.group(1))
    return {"front_matter": data}

def knowledge_tag_extract_tool(text: str) -> Dict[str, Any]:
    """
    Tente d'extraire des tags/keywords simples (mots fréquents >3 lettres, hors stop-words FR/EN minimaux).
    Returns: {"tags":[...]}
    """
    stop = set("the and of to a in for on with les des aux une un et ou de la le du".split())
    words = re.findall(r"[a-zA-Z]{4,}", text or "")
    freq: Dict[str, int] = {}
    for w in words:
        lw = w.lower()
        if lw in stop: continue
        freq[lw] = freq.get(lw, 0) + 1
    tags = [k for k, v in sorted(freq.items(), key=lambda x: -x[1])[:15]]
    return {"tags": tags}


# ------------------------------------------------------------------------------
# 4) TESTING MODULE
# TestCaseGeneratorBot / TestExecutorAgent / QualityAssuranceBot
# ------------------------------------------------------------------------------

def test_parse_requirements_tool(text: str) -> Dict[str, Any]:
    """
    Extrait des 'requirements' simples depuis un doc (lignes commençant par REQ-...:).
    Returns: {"requirements":[{"id","text"}]}
    """
    reqs = []
    for m in re.finditer(r"^(REQ[-_]\w+)\s*:\s*(.+)$", text or "", re.MULTILINE):
        reqs.append({"id": m.group(1), "text": m.group(2).strip()})
    return {"requirements": reqs}

def test_junit_summary_tool(xml_text: str) -> Dict[str, Any]:
    """
    Résumé JUnit (identique logique devops mais dédié testing).
    """
    if not xml_text:
        return {"tests": 0, "failures": 0, "errors": 0, "skipped": 0}
    try:
        root = ET.fromstring(xml_text)
        if root.tag.endswith("testsuite"):
            return {
                "tests": int(root.attrib.get("tests", 0)),
                "failures": int(root.attrib.get("failures", 0)),
                "errors": int(root.attrib.get("errors", 0)),
                "skipped": int(root.attrib.get("skipped", 0))
            }
        total = {"tests": 0, "failures": 0, "errors": 0, "skipped": 0}
        for ts in root.findall(".//testsuite"):
            total["tests"] += int(ts.attrib.get("tests", 0))
            total["failures"] += int(ts.attrib.get("failures", 0))
            total["errors"] += int(ts.attrib.get("errors", 0))
            total["skipped"] += int(ts.attrib.get("skipped", 0))
        return total
    except Exception:
        return {"tests": 0, "failures": 0, "errors": 0, "skipped": 0}

def test_visual_diff_summary_tool(json_text: str) -> Dict[str, Any]:
    """
    Parse un résultat de visual testing type Applitools-like (JSON simplifié).
    Input: {"results":[{"name":"page X","diff_pct":1.2,"status":"passed|failed"}]}
    Returns: {"passed":N,"failed":N,"avg_diff_pct":X}
    """
    data = _extract_json(json_text) or {}
    results = data.get("results", []) or []
    passed = sum(1 for r in results if str(r.get("status","")).lower() == "passed")
    failed = sum(1 for r in results if str(r.get("status","")).lower() == "failed")
    diffs = [_to_number(r.get("diff_pct", 0)) for r in results]
    avg = round(sum(diffs) / len(diffs), 2) if diffs else 0.0
    return {"passed": passed, "failed": failed, "avg_diff_pct": avg}


# ------------------------------------------------------------------------------
# 5) SECURITY MODULE
# VulnerabilityScannerAgent / ComplianceMonitorBot / SecurityAuditorAgent
# ------------------------------------------------------------------------------

def sec_comprehensive_scan_tool(scan_data: str) -> Dict[str, Any]:
    """
    Comprehensive security scan analysis tool that can handle multiple scan formats.
    Returns: {"findings":[{"type","severity","file","line","desc","tool"}], "by_severity":{...}}
    """
    try:
        data = _extract_json(scan_data) or {}
        findings = []
        
        # Handle various scan tool outputs
        if "vulnerabilities" in data:  # Generic format
            for v in data.get("vulnerabilities", []):
                findings.append({
                    "type": v.get("type", "vulnerability"),
                    "severity": (v.get("severity") or "LOW").upper(),
                    "file": v.get("file") or v.get("path") or "",
                    "line": v.get("line") or v.get("lineNumber"),
                    "desc": v.get("description") or v.get("title") or "",
                    "tool": v.get("tool") or "unknown"
                })
        elif "results" in data:  # Checkmarx-like format
            for r in data.get("results", []):
                findings.append({
                    "type": "security_issue",
                    "severity": (r.get("severity") or "LOW").upper(),
                    "file": r.get("fileName") or r.get("path") or "",
                    "line": r.get("line") or r.get("lineNumber"),
                    "desc": r.get("description") or r.get("resultDescription") or "",
                    "tool": "security_scanner"
                })
        
        return {"findings": findings, "by_severity": _count_by(findings, "severity")}
    except Exception as e:
        return {"findings": [], "by_severity": {}, "error": str(e)}

def sec_normalize_veracode_tool(xml_or_json_text: str) -> Dict[str, Any]:
    """
    Normalise un rapport Veracode (XML ou JSON) en findings génériques.
    Returns: {"findings":[{"cwe","severity","file","line","desc"}], "by_severity":{...}}
    """
    data = _extract_json(xml_or_json_text)
    findings = []
    if data:
        for f in data.get("findings", []):
            findings.append({
                "cwe": f.get("cwe"), "severity": (f.get("severity") or "LOW").upper(),
                "file": f.get("file"), "line": f.get("line"), "desc": f.get("desc")
            })
        return {"findings": findings, "by_severity": _count_by(findings, "severity")}
    # XML (Veracode XML summaries)
    try:
        root = ET.fromstring(xml_or_json_text)
        for flaw in root.findall(".//flaw"):
            findings.append({
                "cwe": flaw.attrib.get("cweid"),
                "severity": str(flaw.attrib.get("severity") or "0"),
                "file": flaw.attrib.get("sourcefilepath") or flaw.attrib.get("module") or "",
                "line": flaw.attrib.get("line"),
                "desc": flaw.attrib.get("description") or ""
            })
        # Convertir numeric severity (1-5) en HIGH/MEDIUM/LOW simple
        for f in findings:
            try:
                sev = int(f["severity"])
                f["severity"] = "HIGH" if sev >= 4 else "MEDIUM" if sev == 3 else "LOW"
            except Exception:
                f["severity"] = str(f["severity"]).upper()
    except Exception:
        pass
    return {"findings": findings, "by_severity": _count_by(findings, "severity")}

def sec_normalize_checkmarx_tool(json_text: str) -> Dict[str, Any]:
    """
    Normalise un rapport Checkmarx JSON.
    Returns: {"findings":[{"query","severity","file","line","desc"}], "by_severity":{...}}
    """
    data = _extract_json(json_text) or {}
    findings = []
    for r in data.get("results", []):
        findings.append({
            "query": r.get("queryName") or r.get("queryID"),
            "severity": (r.get("severity") or "LOW").upper(),
            "file": (r.get("fileName") or r.get("path")),
            "line": r.get("line"),
            "desc": r.get("description") or r.get("resultDescription") or ""
        })
    return {"findings": findings, "by_severity": _count_by(findings, "severity")}

def sec_policy_compliance_tool(policy_yaml_or_json_text: str, findings_text: str) -> Dict[str, Any]:
    """
    Évalue une policy (YAML/JSON) contre des findings normalisés (JSON).
    Returns: {"status":"PASS|FAIL", "violations":[...]}
    Policy ex.: {"min_coverage":80,"block_on":{"HIGH":1,"MEDIUM":5}}
    """
    policy = _extract_yaml(policy_yaml_or_json_text) or _extract_json(policy_yaml_or_json_text) or {}
    f = _extract_json(findings_text) or {}
    by_sev = f.get("by_severity") or _count_by(f.get("findings", []), "severity")
    violations = []
    block_on = policy.get("block_on", {})
    for sev, limit in (block_on or {}).items():
        n = int(by_sev.get(str(sev).upper(), 0))
        if n >= int(limit):
            violations.append({"severity": str(sev).upper(), "count": n, "limit": int(limit)})
    status = "FAIL" if violations else "PASS"
    return {"status": status, "violations": violations}
