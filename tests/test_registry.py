import pytest

from project_money.registry import ParamSpec, ToolSpec, ToolRegistry


def make_spec(name="fetch_prices", read_only=True):
    return ToolSpec(
        name=name,
        description="Read-only cached OHLCV panel lookup for one symbol.",
        params=(
            ParamSpec("symbol", "str", "ticker symbol", "SPY"),
            ParamSpec("start", "str", "ISO start date", "2020-01-01"),
        ),
        returns="DataFrame[date, open, high, low, close, volume]",
        provenance="local cache only; no live adapter",
        read_only=read_only,
    )


class TestToolSpecValidation:
    def test_valid_spec_passes(self):
        assert make_spec().validate() == []

    def test_write_capable_spec_rejected(self):
        problems = make_spec(read_only=False).validate()
        assert any("read_only" in p for p in problems)

    def test_action_word_in_name_rejected(self):
        # the registry structurally refuses execution-shaped identifiers —
        # including the review-flagged entry/exit/recommendation tokens
        for bad in (
            "place_order_tool",
            "buy_signal",
            "trade_executor",
            "fill_report",
            "entry_scanner",
            "exit_finder",
            "recommendation_engine",
        ):
            problems = make_spec(name=bad).validate()
            assert any("forbidden action token" in p for p in problems), bad

    def test_token_matching_avoids_substring_false_positives(self):
        # 'reorder' contains 'order' but is not the token 'order'
        assert make_spec(name="reorder_columns").validate() == []

    def test_action_word_in_param_name_rejected(self):
        spec = ToolSpec(
            name="fetch_prices",
            description="ok",
            params=(
                ParamSpec("order_size", "int", "n items", 1),
                ParamSpec("buy_threshold", "float", "level", 0.5),
            ),
            returns="x",
        )
        problems = spec.validate()
        assert sum("forbidden action token" in p for p in problems) == 2

    def test_multiline_description_rejected(self):
        spec = ToolSpec(
            name="fetch_prices",
            description="line one\nline two",
            params=(),
            returns="x",
        )
        assert any("one line" in p for p in spec.validate())

    def test_param_without_example_rejected(self):
        spec = ToolSpec(
            name="fetch_prices",
            description="ok",
            params=(ParamSpec("symbol", "str", "ticker", None),),
            returns="x",
        )
        assert any("worked example" in p for p in spec.validate())


class TestToolRegistry:
    def test_register_and_two_tier_docs(self):
        reg = ToolRegistry()
        reg.register(make_spec(), admission_report={"passed": True})
        assert reg.index() == ["fetch_prices — Read-only cached OHLCV panel lookup for one symbol."]
        docs = reg.get_docs("fetch_prices")
        assert "`symbol` (str)" in docs and "'SPY'" in docs
        assert "validated: yes" in docs

    def test_provisional_marker_without_admission(self):
        reg = ToolRegistry()
        reg.register(make_spec())
        assert "[provisional" in reg.index()[0]
        assert "do not rely" in reg.get_docs("fetch_prices")

    def test_invalid_spec_refused(self):
        reg = ToolRegistry()
        with pytest.raises(ValueError):
            reg.register(make_spec(read_only=False))

    def test_no_silent_overwrite(self):
        reg = ToolRegistry()
        reg.register(make_spec())
        with pytest.raises(ValueError):
            reg.register(make_spec())
        reg.register(make_spec(), replace=True)  # explicit replace allowed

    def test_find_router(self):
        reg = ToolRegistry()
        reg.register(make_spec())
        assert reg.find("ohlcv") == ["fetch_prices"]
        assert reg.find("nonexistent") == []

    def test_search_is_ranked_and_previewed(self):
        reg = ToolRegistry()
        reg.register(make_spec(name="fetch_prices"))
        reg.register(
            ToolSpec(
                name="fetch",
                description="Generic fetch helper for cached artifacts.",
                params=(),
                returns="bytes",
            )
        )
        results = reg.search("fetch")
        # exact-name match ranks above prefix match; preview attached
        assert results[0].startswith("fetch — Generic fetch helper")
        assert results[1].startswith("fetch_prices — ")
        assert reg.find("fetch") == ["fetch", "fetch_prices"]

    def test_replace_clears_stale_readiness(self):
        reg = ToolRegistry()
        reg.register(make_spec())
        reg.readiness_check("fetch_prices", lambda: (True, "cache ok for v1"))
        reg.register(make_spec(), replace=True)
        assert reg.readiness("fetch_prices") is None

    def test_unknown_lookup_raises(self):
        reg = ToolRegistry()
        with pytest.raises(KeyError):
            reg.get_docs("nope")

    def test_readiness_check_recorded(self):
        reg = ToolRegistry()
        reg.register(make_spec())
        result = reg.readiness_check("fetch_prices", lambda: (False, "cache dir missing"))
        assert result == {"ok": False, "detail": "cache dir missing"}
        assert reg.readiness("fetch_prices") == result
