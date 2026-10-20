# -*- coding: utf-8 -*-
"""MCP Server for Frequent Flyer Mileage Award Seat Value & Sniper Skill."""
import sys
import json
import logging
from typing import Dict, Any

from .core import FrequentFlyerAwardSeatSniper

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

TOOLS_SCHEMA = [
    {
        "name": "evaluate_award_redemption_value",
        "description": "Calculate Cents-Per-Point (CPP) value of airline award flight redemption against cash ticket baseline and taxes/fees.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "airline_program": {
                    "type": "string"
                },
                "cash_ticket_price_usd": {
                    "type": "number"
                },
                "required_points": {
                    "type": "integer"
                },
                "taxes_and_surcharges_usd": {
                    "type": "number"
                },
                "cabin_class": {
                    "type": "string",
                    "enum": [
                        "economy",
                        "premium_economy",
                        "business",
                        "first"
                    ]
                }
            },
            "required": [
                "airline_program",
                "cash_ticket_price_usd",
                "required_points",
                "taxes_and_surcharges_usd"
            ]
        }
    },
    {
        "name": "find_optimal_credit_card_transfer_partner",
        "description": "Identify best credit card rewards ecosystem (Amex, Chase, Citi, Capital One, Bilt) to transfer points with active bonus multipliers.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "target_airline": {
                    "type": "string"
                },
                "needed_airline_miles": {
                    "type": "integer"
                },
                "available_bank_points": {
                    "type": "object",
                    "properties": {
                        "chase_ur": {
                            "type": "integer"
                        },
                        "amex_mr": {
                            "type": "integer"
                        },
                        "citi_ty": {
                            "type": "integer"
                        },
                        "capone_miles": {
                            "type": "integer"
                        }
                    }
                }
            },
            "required": [
                "target_airline",
                "needed_airline_miles"
            ]
        }
    }
]

def handle_rpc(line: str) -> str:
    try:
        req = json.loads(line)
        method = req.get("method")
        msg_id = req.get("id")

        if method == "initialize":
            res = {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "genpark-personal-agent-frequent-flyer-mileage-award-seat-sniper-skill", "version": "1.0.0"}
            }
            return json.dumps({"jsonrpc": "2.0", "id": msg_id, "result": res})

        elif method == "tools/list":
            return json.dumps({"jsonrpc": "2.0", "id": msg_id, "result": {"tools": TOOLS_SCHEMA}})

        elif method == "tools/call":
            params = req.get("params", {})
            tool_name = params.get("name")
            args = params.get("arguments", {})

            target_func = getattr(FrequentFlyerAwardSeatSniper, tool_name, None)
            if not target_func:
                return json.dumps({"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32601, "message": f"Method not found: {tool_name}"}})

            result = target_func(**args)
            return json.dumps({
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "content": [{"type": "text", "text": json.dumps(result, indent=2)}]
                }
            })

        else:
            return json.dumps({"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32601, "message": f"Method not found: {method}"}})

    except Exception as e:
        return json.dumps({"jsonrpc": "2.0", "id": req.get("id") if "req" in locals() else None, "error": {"code": -32000, "message": str(e)}})

def run_test():
    print("[TEST] Running internal RPC self-test for genpark-personal-agent-frequent-flyer-mileage-award-seat-sniper-skill...")
    init_req = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
    init_res = json.loads(handle_rpc(init_req))
    assert init_res.get("result", {}).get("serverInfo", {}).get("name") == "genpark-personal-agent-frequent-flyer-mileage-award-seat-sniper-skill"

    list_req = json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
    list_res = json.loads(handle_rpc(list_req))
    assert len(list_res.get("result", {}).get("tools", [])) == 2
    print(f"[TEST] SUCCESS: {len(list_res['result']['tools'])} tools verified.")
    return True

if __name__ == "__main__":
    if "--test" in sys.argv:
        if run_test():
            sys.exit(0)
        sys.exit(1)

    for line in sys.stdin:
        if not line.strip():
            continue
        out = handle_rpc(line)
        sys.stdout.write(out + "\n")
        sys.stdout.flush()
