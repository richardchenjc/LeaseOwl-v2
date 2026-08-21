from leaseowl.segmenter import segment

SIMPLE = """TENANCY AGREEMENT
This Agreement is made between the parties.
1. The Tenant agrees to pay a deposit of one month.
2. Rent is payable on the first of each month.
3. The Tenant shall keep the premises clean.
"""

SECTIONED = """AGREEMENT
1. Definitions apply throughout.
2. Interpretation follows Singapore law.
1. The Landlord shall insure the premises.
2. The Landlord shall maintain the structure.
3. The Landlord provides quiet enjoyment.
"""

GAPPED = """AGREEMENT
1. First clause.
2. Second clause.
4. Fourth clause follows a gap.
"""

SUBNUMBERED = """AGREEMENT
1. Main obligations.
1.1 Sub-obligation stays inside clause one.
1.2 Another sub-obligation.
2. Second main clause.
"""

ADDRESS_TRAP = """AGREEMENT
18 Cross Street #15-02
Singapore 048423
1. Rent is payable monthly.
2. Deposit equals one month.
"""


def test_simple_sequence():
    rep = segment(SIMPLE)
    assert [c.clause_id for c in rep.clauses] == ["1", "2", "3"]
    assert rep.trustworthy and rep.preamble.startswith("TENANCY")


def test_restart_opens_new_section():
    rep = segment(SECTIONED)
    assert rep.n_sections == 2
    assert [c.clause_id for c in rep.clauses] == ["1", "2", "S2.1", "S2.2", "S2.3"]
    assert not rep.sequence_flags


def test_gap_is_flagged_never_silent():
    rep = segment(GAPPED)
    assert any("2 to 4" in f for f in rep.sequence_flags)
    assert not rep.trustworthy


def test_subclauses_fold_into_parent():
    rep = segment(SUBNUMBERED)
    assert [c.clause_id for c in rep.clauses] == ["1", "2"]
    assert "1.1" in rep.clauses[0].text and "1.2" in rep.clauses[0].text


def test_address_line_is_not_a_clause():
    rep = segment(ADDRESS_TRAP)
    assert [c.clause_id for c in rep.clauses] == ["1", "2"]
    assert "Cross Street" in rep.preamble


def test_no_numbering_requests_fallback():
    rep = segment("A free-form agreement with no numbered clauses at all.")
    assert rep.clauses == [] and not rep.trustworthy
    assert any("fallback" in f for f in rep.sequence_flags)
