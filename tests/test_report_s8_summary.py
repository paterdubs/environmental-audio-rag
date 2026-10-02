from scripts.report_s8_summary import caption_extract, render, retrieval_extract


def test_caption_extract_keeps_e2e_and_required_ci() -> None:
    metric = {"estimate": 0.1, "lower": 0.05, "upper": 0.15}
    payload = {
        "summary": {
            "template/e2e": {
                "n": 139,
                "hallucination_rate": 0.0,
                "omission_rate": 0.0,
                "forbidden_term_rate": 0.0,
            },
            "template/oracle": {
                "n": 139,
                "hallucination_rate": 0.0,
                "omission_rate": 0.0,
                "forbidden_term_rate": 0.0,
            },
        },
        "ci": {
            "template/e2e": {
                "hallucination_rate": metric,
                "omission_rate": metric,
                "forbidden_term_rate": metric,
            }
        },
    }
    result = caption_extract(payload)
    assert list(result) == ["template/e2e"]
    assert result["template/e2e"]["n"] == 139
    assert result["template/e2e"]["omission_rate"]["lower"] == 0.05


def test_retrieval_extract_and_render() -> None:
    row = {
        "n": 97,
        "ndcg@10": 0.5,
        "recall@1": 0.1,
        "recall@5": 0.3,
        "recall@10": 0.4,
        "filter_exactness": 1.0,
        "ci_ndcg@10": {"estimate": 0.5, "lower": 0.4, "upper": 0.6},
    }
    extracted = retrieval_extract({"summary": {"hybrid/en": row}})
    assert extracted["hybrid/en"]["filter_exactness"] == 1.0

    caption_metric = {"estimate": 0.0, "lower": 0.0, "upper": 0.0}
    caption = {
        "template/e2e": {
            "n": 139,
            "hallucination_rate": caption_metric,
            "omission_rate": caption_metric,
            "forbidden_term_rate": caption_metric,
        }
    }
    result = {
        "sources": {"caption_old": "old.json"},
        "rq2": {"baseline_v1_all": caption, "f2_all": caption, "f2_annotated": caption},
        "rq3": {
            "baseline_run_b_gold": extracted,
            "f2_gold": extracted,
            "f2_parsed": extracted,
            "answers_f2_gold": None,
            "answers_f2_parsed": None,
        },
    }
    text = render(result)
    assert "RQ2 — caption e2e" in text
    assert "hybrid/en" in text
