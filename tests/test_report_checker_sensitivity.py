import random
from pathlib import Path

from ml.captioning.lexicon import CaptionLexicon
from ml.taxonomy import load_taxonomy
from scripts.report_checker_sensitivity import name, perturb, score, synonyms, unsupported

ROOT = Path(__file__).resolve().parents[1]
TAXONOMY = load_taxonomy(ROOT / "ml/configs/taxonomy.yaml")
LEXICON = CaptionLexicon.from_taxonomy(TAXONOMY)
CLASSES = tuple(TAXONOMY.polyphonic_class_ids)
TEXT = "A birds is audible from 0.0 to 5.0 seconds."


def test_swapping_the_mention_to_an_absent_class_is_caught():
    new = perturb(TEXT, "swap_canonical", ["train"], LEXICON, {}, random.Random(0), "x")
    assert name("train") in new
    assert unsupported(new, {"birds"}, LEXICON) > unsupported(TEXT, {"birds"}, LEXICON)


def test_kinds_that_need_an_absent_class_or_synonym_return_none():
    rng = random.Random(0)
    assert perturb(TEXT, "insert_class", [], LEXICON, {}, rng, "x") is None
    assert perturb(TEXT, "swap_synonym", ["train"], LEXICON, {}, rng, "x") is None


def test_synonyms_exclude_the_template_name():
    syn = synonyms(LEXICON, CLASSES)
    assert all(name(c).lower() not in phrases for c, phrases in syn.items())


def test_out_of_vocabulary_source_is_invisible_to_the_checker():
    result = score([(TEXT, {"birds"})], LEXICON, CLASSES)
    assert result["by_kind"]["insert_oov"]["n"] == 1
    assert result["by_oov_source"]["a baby crying"]["rate"] == 1.0
    hammer = TEXT + " A hammer striking can also be heard."
    assert unsupported(hammer, {"birds"}, LEXICON) == 0
