#!/usr/bin/env python3
"""Build an offline local review page for private repair-episode candidates."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any


HTML = r"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>Private repair-episode review</title><style>
:root{--ink:#172026;--muted:#617080;--line:#cbd5df;--accent:#0f766e;--warn:#b45309}*{box-sizing:border-box}body{margin:0;font:16px/1.45 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;color:var(--ink)}main{max-width:1120px;margin:0 auto;padding:24px}h1,h2{margin:0 0 10px}h1{font-size:1.5rem}h2{font-size:1.03rem;margin-top:16px}.muted{color:var(--muted)}.notice{border-left:4px solid var(--warn);background:#fff7ed;padding:11px 13px;margin:14px 0}.grid{display:grid;grid-template-columns:minmax(0,1fr) 360px;gap:18px}.box{border:1px solid var(--line);border-radius:8px;padding:14px;margin-bottom:14px}.text{white-space:pre-wrap;overflow-wrap:anywhere;border:1px solid #dbe2ea;border-radius:6px;padding:10px;max-height:260px;overflow:auto;font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;background:#fbfdff}label{display:grid;gap:6px;margin:13px 0;font-weight:650}select,textarea,button{font:inherit}select,textarea{width:100%;padding:9px 10px;border:1px solid var(--line);border-radius:6px}textarea{min-height:90px;resize:vertical}.actions{display:flex;gap:9px;flex-wrap:wrap;margin-top:14px}button{padding:9px 13px;border:1px solid var(--line);border-radius:7px;background:#fff;cursor:pointer}.primary{background:var(--accent);border-color:var(--accent);color:white}.flag{display:inline-block;background:#fff7ed;color:#7c2d12;border:1px solid #fed7aa;border-radius:999px;padding:3px 7px;margin:2px;font-size:.84rem}@media(max-width:860px){main{padding:16px}.grid{display:block}}</style></head><body><main id="app"></main><script>
const ITEMS=__ITEMS__;let i=0,ratings={};const app=document.getElementById('app');const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));const options={decision:['unreviewed','retain','reject','needs_followup'],interpretation_assessment:['clear_model_misinterpretation','clarification_required','reasonable_competing_interpretations','relevant_context_lost','user_changed_request','non_pragmatic_capability_or_factual_error','insufficient_evidence'],failure_surface:['conversational_misunderstanding','action_scope_failure','mixed','non_pragmatic','unclear'],privacy_disposition:['not_reviewed','synthetic_or_public_safe','sanitize_possible','do_not_derive','needs_manual_review']};
function key(){return 'ap_private_discovery_review'}function get(item){return {episode_id:item.episode_id,decision:'unreviewed',interpretation_assessment:'',failure_surface:'',privacy_disposition:'not_reviewed',notes:'',...(ratings[item.episode_id]||{})}}function save(){localStorage.setItem(key(),JSON.stringify({i,ratings}))}function restore(){try{const x=JSON.parse(localStorage.getItem(key()));if(x){i=x.i||0;ratings=x.ratings||{}}}catch(_){}}function select(name,value){return `<label>${esc(name.replaceAll('_',' '))}<select data-name="${esc(name)}">${options[name].map(x=>`<option ${value===x?'selected':''}>${esc(x)}</option>`).join('')}</select></label>`}function render(){const item=ITEMS[i],r=get(item);app.innerHTML=`<h1>Private repair-episode review</h1><p class="muted">Candidate ${i+1} of ${ITEMS.length}; ${esc(item.episode_id)}</p><div class="notice">These are local discovery candidates, not labels or benchmark items. A repair turn records intended interpretation after the fact; it does not prove the original request had only one reasonable reading. Do not copy this material outside the private boundary.</div><div class="grid"><section><div class="box"><b>Retrieval signals</b><p>${item.retrieval_signals.map(x=>`<span class="flag">${esc(x)}</span>`).join(' ')||'none'}</p><b>Privacy / third-party flags</b><p>${item.privacy_flags.map(x=>`<span class="flag">${esc(x)}</span>`).join(' ')||'none detected'}</p><h2>Preceding context</h2><div class="text">${item.preceding_context.map(x=>`${esc(x.role)}: ${esc(x.content)}`).join('\n\n')||'(none retained)'}</div><h2>Target prompt</h2><div class="text">${esc(item.target_prompt)}</div><h2>Model interpretation or action</h2><div class="text">${esc(item.model_interpretation_or_action)}</div><h2>Repair turn</h2><div class="text">${esc(item.repair_turn)}</div></div></section><aside><div class="box">${select('decision',r.decision)}${select('interpretation_assessment',r.interpretation_assessment)}${select('failure_surface',r.failure_surface)}${select('privacy_disposition',r.privacy_disposition)}<label>Notes<textarea data-name="notes">${esc(r.notes)}</textarea></label><div class="actions"><button id="back">Back</button><button class="primary" id="next">${i+1===ITEMS.length?'Finish':'Next'}</button><button id="download">Download decisions</button></div></div></aside></div>`;document.querySelectorAll('[data-name]').forEach(n=>n.onchange=n.oninput=()=>{ratings[item.episode_id]={...get(item),[n.dataset.name]:n.value,updated_at:new Date().toISOString()};save()});document.getElementById('back').onclick=()=>{i=Math.max(0,i-1);save();render()};document.getElementById('next').onclick=()=>{i+=1;save();i>=ITEMS.length?finish():render()};document.getElementById('download').onclick=download}function finish(){app.innerHTML=`<h1>Review complete</h1><p>${Object.keys(ratings).length} candidate decisions saved locally.</p><div class="actions"><button id="return">Return</button><button class="primary" id="download">Download decisions</button></div>`;document.getElementById('return').onclick=()=>{i=Math.max(0,ITEMS.length-1);render()};document.getElementById('download').onclick=download}function download(){const payload={schema_version:1,kind:'private_repair_episode_review',saved_at:new Date().toISOString(),decisions:ITEMS.map(get)};const blob=new Blob([JSON.stringify(payload,null,2)],{type:'application/json'});const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='repair-episode-decisions.json';document.body.appendChild(a);a.click();a.remove()}restore();render();
</script></main></body></html>"""


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidates", required=True, type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    candidates = read_jsonl(args.candidates.resolve())
    out_dir = args.out_dir.resolve()
    if out_dir.exists() and any(out_dir.iterdir()):
        if not args.overwrite:
            raise SystemExit(f"review output exists: {out_dir}; pass --overwrite")
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    html = HTML.replace("__ITEMS__", json.dumps(candidates, ensure_ascii=False))
    (out_dir / "index.html").write_text(html, encoding="utf-8")
    (out_dir / "README.md").write_text(
        "# Private Repair-Episode Review\n\n"
        "Open `index.html` directly in a browser. Decisions remain in browser storage until "
        "downloaded. Keep downloaded JSON in the private run directory and use the companion "
        "ingester if you want a retained/rejected queue.\n",
        encoding="utf-8",
    )
    print(f"Built offline review page for {len(candidates)} private candidates: {out_dir / 'index.html'}")


if __name__ == "__main__":
    main()
