# BGP Established / No Routes

## Symptoms
- VPN connectivity broken between HQ and Branch
- Linux_LAN cannot ping Linux_BRANCH (timeout)
- BGP session shows Established but no routes received from neighbor

## Investigation Steps
1. show ip bgp summary → Established, PfxRcd=0 (suspicious — expected 1)
2. show ip bgp 10.0.0.4 → "% Network not in table"
3. show ip bgp neighbors 172.16.100.2 routes → empty
4. (on R2) show ip bgp neighbors 172.16.100.1 advertised-routes → route missing

## Packet Analysis
Wireshark filter: bgp.update
- BGP UPDATE packet present
- WITHDRAWN ROUTES section contains 10.0.0.4/30
- prefix-list filter dropping the route before advertisement

## Root Cause
Outbound prefix-list on R2 explicitly deny 10.0.0.4/30. 
R2 doesn't advertise the route to either neighbor (R1 direct or R_ISP).
BGP session stays up because TCP-179 is healthy — only the prefix is filtered.

## Fix
Remove prefix-list from both outbound neighbor relationships:
no neighbor 172.16.100.1 prefix-list BLOCK_BRANCH_OUT out
no neighbor 172.16.2.1 prefix-list BLOCK_BRANCH_OUT out
clear ip bgp * soft out

## Lesson Learned
- BGP Established ≠ routes flowing
- "% Network not in table" + neighbor Established = filter issue
- Check both directions: in/out prefix-lists, route-maps
- AD doesn't matter here — routes don't even arrive
