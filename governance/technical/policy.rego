package eaip.authz

import future.keywords.if
import future.keywords.in

default allow = false

# C-R-02: RCE nesting depth SHALL NOT exceed 4 levels
allow if {
    input.rce.depth <= 4
    all_children_valid(input.rce)
}

all_children_valid(rce) if {
    count(rce.children) == 0
}

all_children_valid(rce) if {
    count(rce.children) > 0
    every child in rce.children {
        child.depth <= 4
        all_children_valid(child)
    }
}

# C-R-03: Child RCE TokenBudget SHALL NOT exceed its parent's remaining budget
allow if {
    valid_token_budgets(input.rce)
}

valid_token_budgets(rce) if {
    count(rce.children) == 0
}

valid_token_budgets(rce) if {
    count(rce.children) > 0
    every child in rce.children {
        child.state.token_budget <= (rce.state.token_budget - rce.state.tokens_consumed)
        valid_token_budgets(child)
    }
}

# C-R-04: RCE payloads exceeding 64 KiB MUST apply compression
# (Simplified check for the spec demonstration)
allow if {
    input.rce_size_kb < 64
}

allow if {
    input.rce_size_kb >= 64
    input.rce.compression_algo == "zstd"
    input.rce.compression_level >= 3
}
