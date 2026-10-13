# Queue OOF chồng lấn — chỉ dry-run

CLI thật chỉ in lệnh, không thực thi train/dump/build/selector, state không đổi. Không skip: 16 lệnh; --skip-raw-cv: 14 lệnh, vẫn build raw/overlap, chỉ CV overlap. θ dùng --modes global --workers 2; cSEBB dùng --workers 2. Runner giả kiểm resume và dừng khi lỗi.

## skip_raw_cv=False

```text
D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\.venv\Scripts\python.exe -m scripts.train_sed --encoder frame_mn --recipe t2b --train-fixes --seed 20260922 --cv-fold 0
D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\.venv\Scripts\python.exe -m scripts.train_sed --encoder frame_mn --recipe t2b --train-fixes --seed 20260922 --cv-fold 1
D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\.venv\Scripts\python.exe -m scripts.train_sed --encoder frame_mn --recipe t2b --train-fixes --seed 20260922 --cv-fold 2
D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\.venv\Scripts\python.exe -m scripts.train_sed --encoder frame_mn --recipe t2b --train-fixes --seed 20260922 --cv-fold 3
D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\.venv\Scripts\python.exe -m scripts.train_sed --encoder frame_mn --recipe t2b --train-fixes --seed 20260922 --cv-fold 4
D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\.venv\Scripts\python.exe -m scripts.dump_predictions <fold-0-run> --split dev --hop-seconds 5 --weighting triangular:0.3 --label B0_f0_h5
D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\.venv\Scripts\python.exe -m scripts.dump_predictions <fold-1-run> --split dev --hop-seconds 5 --weighting triangular:0.3 --label B0_f1_h5
D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\.venv\Scripts\python.exe -m scripts.dump_predictions <fold-2-run> --split dev --hop-seconds 5 --weighting triangular:0.3 --label B0_f2_h5
D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\.venv\Scripts\python.exe -m scripts.dump_predictions <fold-3-run> --split dev --hop-seconds 5 --weighting triangular:0.3 --label B0_f3_h5
D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\.venv\Scripts\python.exe -m scripts.dump_predictions <fold-4-run> --split dev --hop-seconds 5 --weighting triangular:0.3 --label B0_f4_h5
D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\.venv\Scripts\python.exe -m scripts.build_oof --label B0_h10 <fold-0-run> <fold-1-run> <fold-2-run> <fold-3-run> <fold-4-run>
D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\.venv\Scripts\python.exe -m scripts.build_oof --label B0_h5 <rewindow-fold-0-run> <rewindow-fold-1-run> <rewindow-fold-2-run> <rewindow-fold-3-run> <rewindow-fold-4-run>
D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\.venv\Scripts\python.exe -m scripts.select_postproc_cv <oof_h10-run> --modes global --workers 2 --eval-set annotated
D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\.venv\Scripts\python.exe -m scripts.select_sebb_cv <oof_h10-run> --workers 2 --eval-set annotated
D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\.venv\Scripts\python.exe -m scripts.select_postproc_cv <oof_h5-run> --modes global --workers 2 --eval-set annotated
D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\.venv\Scripts\python.exe -m scripts.select_sebb_cv <oof_h5-run> --workers 2 --eval-set annotated
```

## skip_raw_cv=True

```text
D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\.venv\Scripts\python.exe -m scripts.train_sed --encoder frame_mn --recipe t2b --train-fixes --seed 20260922 --cv-fold 0
D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\.venv\Scripts\python.exe -m scripts.train_sed --encoder frame_mn --recipe t2b --train-fixes --seed 20260922 --cv-fold 1
D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\.venv\Scripts\python.exe -m scripts.train_sed --encoder frame_mn --recipe t2b --train-fixes --seed 20260922 --cv-fold 2
D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\.venv\Scripts\python.exe -m scripts.train_sed --encoder frame_mn --recipe t2b --train-fixes --seed 20260922 --cv-fold 3
D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\.venv\Scripts\python.exe -m scripts.train_sed --encoder frame_mn --recipe t2b --train-fixes --seed 20260922 --cv-fold 4
D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\.venv\Scripts\python.exe -m scripts.dump_predictions <fold-0-run> --split dev --hop-seconds 5 --weighting triangular:0.3 --label B0_f0_h5
D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\.venv\Scripts\python.exe -m scripts.dump_predictions <fold-1-run> --split dev --hop-seconds 5 --weighting triangular:0.3 --label B0_f1_h5
D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\.venv\Scripts\python.exe -m scripts.dump_predictions <fold-2-run> --split dev --hop-seconds 5 --weighting triangular:0.3 --label B0_f2_h5
D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\.venv\Scripts\python.exe -m scripts.dump_predictions <fold-3-run> --split dev --hop-seconds 5 --weighting triangular:0.3 --label B0_f3_h5
D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\.venv\Scripts\python.exe -m scripts.dump_predictions <fold-4-run> --split dev --hop-seconds 5 --weighting triangular:0.3 --label B0_f4_h5
D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\.venv\Scripts\python.exe -m scripts.build_oof --label B0_h10 <fold-0-run> <fold-1-run> <fold-2-run> <fold-3-run> <fold-4-run>
D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\.venv\Scripts\python.exe -m scripts.build_oof --label B0_h5 <rewindow-fold-0-run> <rewindow-fold-1-run> <rewindow-fold-2-run> <rewindow-fold-3-run> <rewindow-fold-4-run>
D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\.venv\Scripts\python.exe -m scripts.select_postproc_cv <oof_h5-run> --modes global --workers 2 --eval-set annotated
D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\.venv\Scripts\python.exe -m scripts.select_sebb_cv <oof_h5-run> --workers 2 --eval-set annotated
```
