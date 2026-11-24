# Grounded / faithful caption generation from a sound-event timeline: literature and methods (2022–2026)

Compiled 24/11/2026. Scope: captions produced from a detected event list (class, onset, offset, confidence) by templates and by a local LLM (Qwen ~9B, llama.cpp, grammar-constrained), scored by machine-checkable metrics (hallucination, omission, temporal order, forbidden inference, over-specific naming of merged classes). Constraint for recommendations: 4 days, no training, dev split only.

Verification legend: **[read]** = page/full text fetched in this session or marked V3 in the project's `docs/RELATED_WORK.md`; **[snippet]** = seen only in search result summaries; anything not seen at all is listed under Gaps.

---

## 1. Grounded / factual audio captioning literature and its metrics: how does ours compare?

### Takeaway
Audio-captioning hallucination work (ECHO, TAC, BRACE, AudioCapBench) measures hallucination either against clip-level labels (ECHO), with an audio-text model as judge (TAC's FLAM, BRACE's CLAP/LALM), or with a GPT judge against reference captions (AudioCapBench). None of the sources found checks a caption against a timestamped event list for hallucination, omission, order, forbidden inference and merged-class naming together. Our metric suite is a narrower but stricter and fully deterministic version of the same idea. The honest framing is "applies and extends ECHO/TAC-style grounding checks to a structured timeline", not "first".

### Cited Findings
- **ECHO** (Kuan, Huang, Lee 2024): ECHO-I = share of mentioned objects that are hallucinated, ECHO-S = share of captions with at least one hallucinated object. Nouns are extracted with spaCy and compared with ground-truth labels, imitating CHAIR from image captioning. There is no time or order component. [read] — [arXiv:2406.08402](https://arxiv.org/abs/2406.08402); project notes `docs/RELATED_WORK.md` §2.4 (29)
- **TAC: Timestamped Audio Captioning** (Kumar et al., arXiv Feb 2026, NeurIPS 2026 poster): produces captions with start/end times for each source in overlapping scenes. The authors argue LALMs produce "temporally inconsistent captions and frequent hallucinations". A TAC→LLM cascade reaches SOTA on MMAU-Pro, MMSU and MMAR. [read abstract] — [arXiv:2602.15766](https://arxiv.org/abs/2602.15766), [NeurIPS listing](https://neurips.cc/virtual/2026/poster/148688)
- TAC metrics: event F1, segment F1, and Hal% = share of predicted events whose FLAM audio-text score is below τ = 0.25. τ was fixed before evaluation and rankings are stable for τ ≥ 0.20 (Appendix B). The authors state the limit of reference-based scoring: a real but unannotated sound is counted as an FP. [read, V3 in project] — [arXiv:2602.15766v2](https://arxiv.org/abs/2602.15766); `docs/RELATED_WORK.md` §2.4 (27)
- Follow-ups seen only as titles: TAC2 ("timestamped audio captioning as composable functions", arXiv 2610.36568) and LongCap (hour-scale timestamped captioning, arXiv 2611.11125). [snippet] — [TAC2](https://arxiv.org/pdf/2610.36568), [LongCap](https://arxiv.org/pdf/2611.11125)
- **BRACE** (Guo et al., arXiv Dec 2025; listed in the NeurIPS 2025 Datasets & Benchmarks track):
  - BRACE-Hallucination: GPT-4o replaces one noun in a caption with a plausible but meaning-changing one. 2,027 clips, 10,315 caption pairs.
  - Best CLAP-based judge: F1 88.26 (M2D-CLAP, sliding window). Best LALM judge: 96.37 (GPT-4o-Audio-Preview).
  - BRACE-Main (2,496 pairs): best CLAP 70.01, best LALM 63.19.
  - [read] — [arXiv:2512.10403](https://arxiv.org/html/2512.10403v1), [NeurIPS page](https://papers.nips.cc/paper_files/paper/2025/hash/3a3ec21884760f891752e0661ecc0b0b-Abstract-Datasets_and_Benchmarks_Track.html)
- **AudioCapBench** (Salesforce, arXiv Feb 2026):
  - A GPT-4.1 judge scores Accuracy, Completeness (recall) and Hallucination from 0 to 10 against reference captions, where 10 means no hallucination.
  - gpt-4o-mini-audio-preview has the best hallucination score (7.90) but the lowest accuracy (1.63) and completeness (1.41), because its descriptions are brief and generic.
  - The authors note that a single judge may add systematic bias.
  - [read] — [arXiv:2602.23649](https://arxiv.org/html/2602.23649v1)
- **CLAIR-A** (Wu, Gonzalez, Darrell, Chan; ASRU 2025):
  - An LLM (GPT-4o) gives a semantic-distance score from a candidate caption to the reference captions.
  - Guided generation keeps the JSON output valid. With a fixed LLM, CFG-constrained decoding and temperature 0, the score is deterministic.
  - It is 5.8% relatively more accurate than FENSE on Clotho-Eval, and its explanations are rated up to 30% better.
  - Code: github.com/DavidMChan/clair-a.
  - [snippet + abstract] — [arXiv:2409.12962](https://arxiv.org/abs/2409.12962)
- **FENSE** (Zhou et al., ICASSP 2022): Sentence-BERT similarity plus a fluency error detector (repeated n-grams, incomplete sentences, missing verbs or conjunctions). The score is cut when an error is detected; papers describe the penalty differently, so check the version. FENSE beats earlier metrics by 14–25% accuracy on the new human-judgment benchmarks. The detector has P 96.8 / R 76.4 / F1 85.4 on 723 captions. [snippet] — [arXiv:2110.04684](https://arxiv.org/abs/2110.04684v2)
- **ACES** (Wijngaard, Formisano, Giordano, Dumontier, arXiv 2024):
  - A fine-tuned tagger marks caption words as WHO/WHAT/HOW/WHERE/WHEN (13 labels).
  - Phrases are compared with SBERT within the same category, with BERTScore-style matching and an F-score that weights recall 9× (as METEOR does).
  - Accuracy vs FENSE: AudioCaps-Eval 83.0 vs 85.3, Clotho-Eval 74.0 vs 75.7.
  - [read] — [arXiv:2403.18572](https://arxiv.org/html/2403.18572v1)
- **MACE** adds the audio itself to the evaluation and reports +3.28% / +4.36% relative accuracy over FENSE on AudioCaps-Eval / Clotho-Eval. [snippet] — [arXiv:2411.00321](https://arxiv.org/abs/2411.00321)
- **SED-conditioned captioning** (Xie, Xu, Wu, Yu; SJTU):
  - SED outputs, after double thresholding at 0.25/0.75, become a 4-level temporal tag (single / simultaneous / sequential / complex). Two events count as sequential if their overlap is under half the shorter event.
  - ACC_temp/F1_temp = binary "does the caption contain a sequential word (then, after, followed)".
  - On AudioCaps, F1_temp rose from 23.4 to 75.2, while CIDEr fell from 72.6 to 68.2.
  - On Clotho, CIDEr fell from 40.8 to 33.8, which the authors blame on SED domain mismatch.
  - [read] — [arXiv:2306.01533](https://arxiv.org/html/2306.01533v2)
- Event lists or tags given to an LLM to write captions or QA data are common in data generation. Make-An-Audio 2 turns tags into structured captions with timing, then has an LLM paraphrase them. A Qualcomm 2024 QA paper puts event labels and timestamps into GPT-4 prompts. [snippet] — [Make-An-Audio 2](https://arxiv.org/pdf/2305.18474), [Temporal AQA](https://arxiv.org/html/2409.06223v1)
- AHA (arXiv 2512.24052) is a hallucination-alignment framework with a four-dimension diagnostic benchmark. HalluAudio (arXiv 2604.19300) is a 2026 LALM hallucination benchmark. Neither is caption-from-timeline. [snippet] — [AHA](https://arxiv.org/pdf/2512.24052v2.pdf), [HalluAudio](https://arxiv.org/pdf/2604.19300)
- Weck & Serra 2023 is about **data leakage in text-audio retrieval** (SoundDesc duplicates), not captioning hallucination. Do not cite it for C2. [read] — [arXiv:2302.12258](https://arxiv.org/abs/2302.12258)
- Wijngaard et al. 2025 is a **survey of 69 audio-language datasets with a CLAP-based overlap analysis**, not a hallucination metric. The hallucination-adjacent Wijngaard paper is ACES (2024). [read] — [arXiv:2407.06947](https://arxiv.org/abs/2407.06947), [ACES](https://arxiv.org/html/2403.18572v1)

### Inferences
- Mapping of our metrics to the literature:

  | Our metric | Closest literature metric |
  |---|---|
  | hallucination | ECHO-I/ECHO-S (CHAIR-style); TAC Hal% (judge model); AudioCapBench "Hallucination" (LLM judge) |
  | omission | AudioCapBench "Completeness"; GEM "No-Omissions" (§2) |
  | temporal order | Xie et al.'s ACC/F1_temp (coarser: binary sequential-word check) |
  | forbidden context inference (cause/intent/danger) | no direct counterpart found; closest are ACES's WHO/HOW slots |
  | over-specific naming of merged classes | no counterpart found |

- Our metrics are deterministic lexicon matches, unlike LLM-judge metrics, which drift with the judge. This is a strength to state. The known weakness, shared with ECHO, is lexicon recall: the project's own audit measured lexicon-vs-human precision 0.896 and recall 0.936 (`CLAUDE.md` W5 entry).
- AudioCapBench's finding (short generic captions get the best hallucination score) is the exact critique of "0 hallucinations by construction". Our report should always pair hallucination with omission/coverage, as AudioCapBench pairs it with completeness.
- Cheap related-work addition (no experiment needed): a comparison table of ECHO, TAC, BRACE, AudioCapBench, CLAIR-A, FENSE, ACES and Xie against ours. Columns: reference type, judge type, deterministic?, time-aware?, measures omission?

### Gaps
- ECHO's exact venue (Interspeech?) is not confirmed. TAC's Hal% numbers per model were not extracted here; see project §2.4 (27).
- No source found that measures "forbidden inference" (cause/intent/danger) in audio captions. This looks like a genuine gap, but the search was limited to about 15 queries.
- CLAIR-A, FENSE and MACE numbers come from search snippets and abstracts, not tables.

---

## 2. Data-to-text faithfulness techniques (constrained decoding, plan-then-generate, verify-and-repair, faithfulness metrics)

### Takeaway
For a team that cannot train, the techniques that fit are all inference-time:
1. Deterministic post-hoc verification plus regeneration or repair, reusing our own lexicon checker as the verifier.
2. Separating content planning (done in code) from surface realisation (done by the LLM).
3. Constrained decoding that does not force the model to "reason inside the grammar".

NLI-based checks (Dušek & Kasner; AlignScore) are an independent second metric for omission/hallucination that costs no training.

### Cited Findings
- **Verify-and-correct loop:** "You Can Generate It Again" (Ren & Liu, arXiv 2023, v2 Aug 2025). The model generates, its output is checked on several aspects, and the findings become an error-indication prompt that asks for regeneration. Shown on small models (T5). [snippet] — [arXiv:2306.15933](https://arxiv.org/abs/2306.15933v1)
- **TWEAK** (Apple, 2023): reranks candidate generations with an NLI hypothesis-verification model, choosing outputs for faithfulness instead of regenerating. [snippet] — [arXiv:2311.09467](https://arxiv.org/pdf/2311.09467.pdf)
- **Symbolic references / verifiable generation:** outputs cite structured data so each claim can be checked. [snippet] — [arXiv:2311.09188](https://arxiv.org/pdf/2311.09188)
- **GEM 2024 data-to-text shared task** (RDF triples; factual, counterfactual and fictional data):
  - Human criteria include **No-Omissions** and **No-Additions**, together called "semantic accuracy".
  - LLM judges rank systems like humans do but give higher scores.
  - A hybrid pipeline (DCU-ADAPT) minimised unsupported additions but "frequently under-generates by omitting relevant content". This is the same hallucination/omission trade-off we observe.
  - SaarLST ranked first by retrieving in-context examples, and argued that in-context examples matter more for faithfulness than the base LLM.
  - [snippet] — [GEM 2024 proceedings](https://aclanthology.org/2024.inlg-genchal.pdf), [2024.inlg-genchal.2](https://aclanthology.org/2024.inlg-genchal.2.pdf), [2025.inlg-genchal.4](https://aclanthology.org/2025.inlg-genchal.4)
- **NLI semantic-accuracy metric** (Dušek & Kasner, INLG 2020): facts are turned into text with trivial templates, and entailment is checked both ways. Text ⊨ fact fails → omission; facts ⊨ text fails → hallucination. Accuracy is over 90% on E2E without references or in-domain training. Code: ufal/nlgi_eval. [snippet + abstract] — [arXiv:2011.10819](https://arxiv.org/abs/2011.10819), [ACL Anthology](https://aclanthology.org/2020.inlg-1.19)
- **AlignScore** (Zha et al., ACL 2023): a RoBERTa alignment model (125M/355M) trained on 4.7M examples from seven tasks, evaluated on 22 datasets. It scores context chunks against claim sentences (max per claim, then mean). The 355M version matches or beats ChatGPT/GPT-4-based metrics. Public HF model. [snippet + abstract] — [arXiv:2305.16739](https://arxiv.org/abs/2305.16739), [ACL](https://aclanthology.org/2023.acl-long.634)
- **Constrained decoding vs quality:**
  - "Let Me Speak Freely?" (Tam et al. 2024): format restrictions hurt reasoning, and stricter constraints hurt more.
  - "Constrained Decoding: Harmful or Beneficial?" (arXiv 2610.35328): when the prompt and output format match the grammar, constrained decoding consistently beats unconstrained.
  - 2026 work (arXiv 2601.07525) recommends reasoning freely first, then switching to the grammar (a trigger token or two passes).
  - [snippet] — [arXiv:2408.02442](https://arxiv.org/html/2408.02442v3), [arXiv:2610.35328](https://arxiv.org/pdf/2610.35328), [arXiv:2601.07525](https://arxiv.org/html/2601.07525v1)
- CLAIR-A itself uses CFG-constrained, temperature-0 decoding to make an LLM metric deterministic. This is an existing precedent for our llama.cpp grammar plus greedy setup. [snippet] — [arXiv:2409.12962](https://arxiv.org/abs/2409.12962)

### Inferences (ranked catalogue for 4 days, no training, dev only)

| # | Technique | What it is for us | Expected benefit | Cost | How to evaluate |
|---|---|---|---|---|---|
| 1 | **Verify → repair/regenerate loop with our own checker** | Run G1–G3 + lexicon on each LLM caption. On a violation (omitted class, banned term, wrong order), regenerate with an error-indication prompt (VCP-style) or fall back to the template sentence for the missing event. | Directly reduces omission/hallucination. The best-supported cheap method (VCP, TWEAK). | ~0.5–1 day code; extra LLM calls only on failing captions | Dev: omission/hallucination before vs after, number of regenerations, fallback rate |
| 2 | **Plan-in-code, realise-in-LLM** | Code builds an ordered, aggregated content plan (which events, merged/counted, in which order). The LLM only rephrases it. Our `constrained_cover` is already a version of this. | Fixes order and omission structurally. Describe as "content planning" in the report. | Low (mostly writing it up) | Order accuracy, omission vs number of events |
| 3 | **Two-pass "free then constrain"** | Let the model draft freely, then realise under the grammar, or put the grammar only on mentions. | May recover fluency lost to the grammar (Tam et al.; 2601.07525). Our grammar mostly enforces sequence, not reasoning, so the effect may be small. | 0.5 day | Dev: fluency proxy (FENSE detector or human check) + our metrics |
| 4 | **NLI-based second metric** (Dušek & Kasner bidirectional check; or AlignScore-large) | Template-verbalise each event ("A dog barks from 3 to 5 s") and check entailment against the caption. | An independent check of our lexicon metric. Answers "is the metric circular?". | ~0.5 day; NLI/AlignScore run on CPU/GPU, no training | Agreement (κ or % agreement) between lexicon and NLI decisions on dev |
| 5 | **Retrieved in-context examples** (SaarLST) | Few-shot examples of correct timeline→caption pairs chosen by similar class sets. | GEM 2024 evidence for faithfulness. | Low–medium | Dev metrics |
| 6 | **Rerank N candidates by checker score** (TWEAK-style) | Sample k captions and keep the one with the fewest violations. Costs determinism unless seeds are fixed. | Moderate | k× LLM time | Dev metrics + latency |

- Items 1, 2 and 4 are where the evidence is strongest relative to cost. Item 4 is the main defence against "0 hallucinations is by construction".

### Gaps
- NeuroLogic decoding, lexically constrained beam search, PARENT, QuestEval, Self-Refine and plan-then-generate papers (e.g. Puduppully et al.) were **not fetched** in this session, so no numbers are given for them. Cite only after verifying.
- The VCP and TWEAK figures were not extracted; only the method descriptions are known.
- Whether AlignScore or NLI models work on very short template-style sound-event sentences is untested (inference only).

---

## 3. Handling dense timelines (aggregation, salience, length budgets, omission vs verbosity)

### Takeaway
Little audio-specific literature exists. Evidence comes indirectly from data-to-text (GEM: hybrid pipelines trade additions for omissions) and from audio benchmarks where short captions score well on hallucination but badly on completeness. The practical answer is code-side aggregation (counts, "repeatedly", grouping by class), salience by duration/confidence, and metrics that define omission at the class level after aggregation.

### Cited Findings
- AudioCapBench: the most hallucination-free model was also the least complete (hallucination 7.90, completeness 1.41), showing the verbosity/omission trade-off. [read] — [arXiv:2602.23649](https://arxiv.org/html/2602.23649v1)
- GEM 2024 DCU-ADAPT: the pipeline that minimised unsupported additions under-generated, with worse No-Omissions. [snippet] — [2025.inlg-genchal / GEM proceedings](https://aclanthology.org/2024.inlg-genchal.pdf)
- Xie et al. collapse a whole SED output into a single 4-level temporal-relation tag. Overly complex tags on single-event Clotho clips hurt CIDEr (40.8 → 33.8), so over-describing temporal complexity is itself an error mode. [read] — [arXiv:2306.01533](https://arxiv.org/html/2306.01533v2)
- Make-An-Audio 2 turns tags into structured captions with timing and duration before the LLM paraphrases them, i.e. structure first, LLM second. [snippet] — [arXiv:2305.18474](https://arxiv.org/pdf/2305.18474)
- LongCap targets hour-scale audio by chunk-wise processing. [snippet, title only] — [arXiv:2611.11125](https://arxiv.org/pdf/2611.11125)

### Inferences
- The project already found that dense timelines cause omission: LBR V3's denser timeline raised constrained omission to 0.081 vs ~0.01 (CLAUDE.md, 11/11). The cheapest fix is aggregation in code before generation:
  - merge same-class events into "X (n times, between a and b s)";
  - cap the number of distinct mentions at K, ranked by total duration × confidence;
  - say "and other sounds" or list the rest in a structured tail.
- Omission must then be **redefined at the class level** (a class is covered if mentioned once), and the redefinition reported openly, ideally fixed before running dev.
- Report omission against a length budget: plot omission vs number of distinct classes per timeline, and caption length vs number of events. This turns the trade-off into a figure, not a hidden choice.

### Gaps
- No audio paper found that evaluates aggregation strategies for dense SED timelines. The data-to-text aggregation literature (e.g. sentence planning / aggregation in classic NLG) was not searched in this session.

---

## 4. Expressing uncertainty (hedging by detector confidence)

### Takeaway
Hedging words ("possibly", "likely") are a weak, distribution-dependent signal, even when LLMs choose them. For a timeline captioner, hedging should be **rule-based from calibrated detector confidence** (e.g. "possibly X" when the event score lies in a band), not left to the LLM. The claim should be validated by checking that hedged events are in fact less often correct on dev.

### Cited Findings
- Liu, Zong, Wang, Song ("Revisiting Epistemic Markers…", arXiv 2505.24778 v3, Apr 2026):
  - LLM marker confidence is fairly stable in-distribution but transfers poorly.
  - Consistency of marker ordering across domains (MRC) averages 21.34%. Cross-domain coefficient of variation averages 23.43%.
  - Marker-based ECE is 8.17% in-distribution vs 17.73% cross-domain (numeric confidence: 16.60%).
  - Human and LLM interpretations of markers diverge.
  - [read] — [arXiv:2505.24778](https://arxiv.org/html/2505.24778v3)
- "Anthropomimetic Uncertainty" (2025) reports verbalised-uncertainty calibration errors of up to 44% that vary by context and domain. [snippet] — [arXiv:2507.10587](https://arxiv.org/html/2507.10587v1)
- One study reports that adding "possibly" improved calibration more consistently than numeric statements. [snippet, primary study not identified] — via [search summary of arXiv:2507.10587 et al.](https://arxiv.org/pdf/2507.10587)

### Inferences
- A cheap dev experiment with no LLM changes:
  - Bucket dev events by LBR/rescorer score and compute precision per bucket (TP rate vs GT).
  - Choose one hedge band on dev (e.g. the bucket with precision < 0.5), pre-register it, and render those events with "possibly" (EN) / "có thể" (VI).
  - Report "hedged-event precision vs unhedged-event precision" on dev. This is a reliability diagram, measured on events rather than words.
  - It also softens hallucination counts in end-to-end mode: a hedged false positive is less harmful. Report it as a separate category, not as "no hallucination".
- The project already has temperature-scaling/ECE tooling (ADR-0017) and a calibration report (`report_calibration`, Phase F), so the extra code is small.

### Gaps
- No audio-captioning source found that uses detector confidence for verbal hedging. The "possibly" calibration study's primary source was not identified.

---

## 5. Bilingual (EN/VI) captioning, template vs LLM fluency, small-scale human evaluation

### Takeaway
No Vietnamese audio-captioning literature was found in this pass. For a thesis, the defensible protocol is a small human study documented with HEDS 3.0: two raters, blind to system, rating faithfulness, coverage and fluency on ~50–60 captions per system. Report agreement (Cohen's κ / Krippendorff's α) and keep LLM judges as secondary, since they are known to be lenient.

### Cited Findings
- HEDS (Shimorina & Belz 2021/HumEval 2022; HEDS 3.0 Belz & Thomson, GEM 2025) is a standard datasheet for recording human-evaluation design, raters and criteria for comparability and reproducibility. It has a LaTeX export. [snippet] — [HEDS 3.0 arXiv:2412.07940](https://arxiv.org/html/2412.07940v1), [ACL 2025.gem-1.6](https://aclanthology.org/2025.gem-1.6/), [HEDS 1.0](https://aclanthology.org/2022.humeval-1.6)
- GEM 2024: LLM judges rank systems like humans but give higher scores. [snippet] — [GEM 2024 proceedings](https://aclanthology.org/2024.inlg-genchal.pdf)
- FENSE's fluency-error detector (P 96.8 / R 76.4) is an off-the-shelf English fluency check usable on LLM captions. English only. [snippet] — [arXiv:2110.04684](https://arxiv.org/abs/2110.04684v2)
- BRACE finds CLAP/LALM judges detect single-noun hallucinations well (F1 up to 96.37) but judge overall caption quality poorly (≤ 70.01), so automatic judges are unreliable for "quality". [read] — [arXiv:2512.10403](https://arxiv.org/html/2512.10403v1)

### Inferences
- The project already ran a blind 60-caption read by the user (lexicon precision 0.896 / recall 0.936, ADR-0022 §6). Two cheap upgrades:
  1. A second rater on the same 60, giving κ.
  2. A filled HEDS-style table in the appendix.
- Template vs LLM: templates win on faithfulness by design, and LLMs are meant to win on fluency and naturalness. Without a fluency measurement the LLM branch has no stated advantage. FENSE's detector (EN) plus a small human fluency rating (EN+VI) fills this gap.
- VI-specific risk the project already handles: diacritic-insensitive matching creates false matches ("tội phạm"), so matching must keep diacritics (ADR-0025). Worth stating as a bilingual-evaluation finding.

### Gaps
- No sources on Vietnamese audio captioning or Vietnamese faithfulness metrics found (search not exhaustive). There are no VI equivalents of FENSE or AlignScore in this pass.

---

## 6. Critique of "zero hallucination by construction": making the evaluation non-trivial

### Takeaway
Template and grammar-constrained captions can only name classes from the timeline, so "0 hallucination against the timeline" is guaranteed and uninformative. The literature points to five ways to make the result meaningful:
1. Score end-to-end captions against **ground-truth annotations**, not the predicted timeline. TAC and ECHO both compare with reference labels, so detector errors propagate.
2. Always pair hallucination with completeness/omission (AudioCapBench).
3. Use an independent checker (NLI/AlignScore, or a CLAP/LALM judge as in BRACE/TAC).
4. Run adversarial inputs and prompts.
5. Measure informativeness and usefulness with humans.

### Cited Findings
- TAC Hal% uses an external audio-text model (FLAM), and the authors note that reference-based scoring counts real but unannotated sounds as false positives. Both judge types have known failure modes. [read] — [arXiv:2602.15766](https://arxiv.org/abs/2602.15766)
- AudioCapBench shows generic short captions get top hallucination scores with bottom completeness. Hallucination alone is gameable. [read] — [arXiv:2602.23649](https://arxiv.org/html/2602.23649v1)
- BRACE-Hallucination builds adversarial captions by swapping one plausible noun. The same recipe can stress-test our lexicon checker (does it catch "hammer" swapped in for "workshop" noise?). [read] — [arXiv:2512.10403](https://arxiv.org/html/2512.10403v1)
- GEM 2024 uses counterfactual and fictional inputs to test whether LLMs follow the data or their parametric knowledge. Analogue for us: timelines with implausible class combinations (e.g. cicadas + sirens + jet). [snippet] — [GEM 2024](https://aclanthology.org/2024.inlg-genchal.pdf), [arXiv:2609.09363](https://arxiv.org/pdf/2609.09363)
- Dušek & Kasner's bidirectional NLI gives an omission/hallucination signal independent of our lexicon. [snippet] — [arXiv:2011.10819](https://arxiv.org/abs/2011.10819)

### Inferences (concrete, dev-only, ranked)
1. **Report the three-level hierarchy explicitly**, most already measured:
   - (a) oracle timeline → caption: tests the generator;
   - (b) predicted timeline → caption scored against the predicted timeline: tests faithfulness to the input;
   - (c) predicted timeline → caption scored against **GT annotation**: the end-to-end factual error, inherited from SED.

   Only (b) is "0 by construction"; (c) is not, and is the honest headline. Cost: mostly writing.
2. **Counterfactual/adversarial timeline stress test** (GEM-style), 0.5 day:
   - feed timelines with implausible combinations, very short or low-confidence events, and many repeats;
   - measure whether the unconstrained LLM adds scene inferences ("a construction site", "an emergency"), forbidden G3 terms, or subclass names for merged classes.

   This gives the forbidden-inference and merged-class metrics non-trivial numbers for the LLM branches.
3. **Adversarial prompt test:** a system or user instruction that invites interpretation ("describe what is happening and why"). Measure the forbidden-inference rate for unconstrained vs constrained output. This shows the grammar's value.
4. **Checker validation:** inject BRACE-style one-word swaps into 50–100 dev captions and report the lexicon checker's detection rate. This turns "0 hallucinations" into "0 detected, by a checker with measured recall X".
5. **Informativeness:** report coverage (classes mentioned / classes in GT) and a small human usefulness rating next to hallucination.

### Gaps
- No source found that formally critiques "faithful by construction" template systems in audio captioning. The argument above combines AudioCapBench, TAC and GEM evidence and is our own inference.
- How strongly CLAP/FLAM judges agree with lexicon-based hallucination on SED-style captions is unknown (not tested in any source found).
