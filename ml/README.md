# Machine learning modules

```text
ml/
├── captioning/   # timeline → grounded text
├── configs/      # experiment and taxonomy configs
├── datasets/     # DataSEC/DataSED loaders
├── evaluation/   # classification, SED, caption, retrieval metrics
├── features/     # waveform/log-mel/encoder preprocessing
├── models/       # classifier, SED, hierarchy heads
├── retrieval/    # document builders and rankers
├── runs/         # ignored run artifacts
├── tracking/     # run manifests and reproducibility helpers
└── training/     # losses, loops, calibration
```

Public functions cần type hints. Model output phải kèm class order/taxonomy hash.

