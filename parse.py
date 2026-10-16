import re, json, sys
src = open(sys.argv[1], encoding="utf-8").read()
out, cat = [], None
for line in src.splitlines():
    m = re.match(r"^### (.+)", line)
    if m: cat = m.group(1).strip(); continue
    if not line.startswith("| [") or cat is None: continue
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    if len(cells) < 5: continue
    lm = re.match(r"\[(.+?)\]\((.+?)\)", cells[0])
    if not lm: continue
    auth = cells[2].strip("`")
    out.append({"name": lm.group(1), "url": lm.group(2), "description": cells[1],
                "auth": "" if auth.lower()=="no" else auth, "https": cells[3].lower()=="yes",
                "cors": cells[4].lower(), "category": cat})
json.dump(out, open(sys.argv[2],"w",encoding="utf-8"), ensure_ascii=False, indent=1)
from collections import Counter
print(len(out), "APIs,", len({a['category'] for a in out}), "catégories,", sum(1 for a in out if not a['auth']), "sans auth")
