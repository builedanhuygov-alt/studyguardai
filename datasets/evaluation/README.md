# Evaluation sets

Drop curated labeled clips here as `<name>/labels.json` plus a `manifest.json`
describing capture conditions (lighting, angle, device). Keep clips out of git;
commit only labels + manifests.

Run metrics with `studyguard.evaluation.metrics` and gate with
`studyguard.eval_gates` (posture ≥ 70%, focus ≥ 65%).
