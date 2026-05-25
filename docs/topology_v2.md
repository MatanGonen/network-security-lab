# Topology v2 — Dual Path BGP

R_ISP elevated from static transit to AS65003 BGP speaker.
Creates two paths between AS65001 and AS65002:
- Path A: R1 ↔ R2 (direct, AS-PATH = 65002)
- Path B: R1 → R_ISP → R2 (transit, AS-PATH = 65003 65002)

Best path selection demonstrated via AS-PATH Prepending:
- Without prepending: direct wins (shorter AS-PATH)
- With prepending: transit wins (direct AS-PATH becomes 4 hops)