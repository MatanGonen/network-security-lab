# BGP↔OSPF Redistribution Notes

## Administrative Distance Values
- Connected: 0
- Static: 1
- eBGP: 20
- OSPF: 110
- iBGP: 200

## Loop Risk Scenario
Without route-map filtering:
- R1 redistributes ALL ospf routes into BGP
- R1 sends to R2 via eBGP
- R2 might (in larger topologies) redistribute BGP back into OSPF
- Loop possible

## Prevention Methods
1. **Route-map filtering** (used here) — explicit prefix-list of what to redistribute
2. **Route tagging** — `set tag 100` on redistribution + `deny tag 100` on the other direction
3. **Administrative Distance** — Cisco uses AD to break ties, but doesn't prevent loops

## Real-World Application
Direct Connect / ExpressRoute:
- Customer router runs OSPF internally + eBGP to AWS
- Same exact pattern as this lab
- redistribute ospf into bgp + careful filtering

## Summary
Redistribution without route-map is the textbook loop risk. In my lab I used 
prefix-list with route-map to explicitly select 10.10.10.0/30 only. The route 
appeared in R2 with origin code '?' confirming redistribution origin.