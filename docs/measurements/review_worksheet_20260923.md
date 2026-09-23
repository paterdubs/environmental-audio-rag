# Phiếu duyệt tay — cặp trùng lặp xuyên dataset

**Sinh tự động** `scripts.build_review_worksheet` — 2026-09-23T03:45:16Z

**35 cặp** cần quyết định. Đây là phần **duy nhất** của cổng D3 không tự động hoá được, và là phần quyết định tính hợp lệ của RQ1.

## Câu hỏi phải trả lời cho mỗi cặp

> Hai file này có phải **cùng một bản ghi gốc** không?

Không phải hỏi *có giống nhau không* — hai tiếng còi xe khác nhau nghe rất giống. Hỏi là *có phải cùng một lần thu* không: cùng nền, cùng vọng âm, cùng nhiễu nền, cùng nhịp biến thiên.

| Dấu hiệu **cùng nguồn** | Dấu hiệu **khác nguồn** |
|---|---|
| Nhiễu nền trùng khớp từng đoạn | Nền khác hẳn (một bên có gió, một bên không) |
| Âm phụ ngẫu nhiên có ở cả hai (chim, tiếng người) | Chỉ tiếng nguồn chính giống nhau |
| Vọng âm và độ xa giống nhau | Khoảng cách tới nguồn khác nhau rõ |
| Biến thiên cao độ trùng nhau theo thời gian | Cùng loại nguồn nhưng nhịp khác |

## Cách điền

Mở `data/manifests/review_worksheet.csv`, điền ba cột:

| Cột | Giá trị |
|---|---|
| `decision` | một trong `duplicate`, `distinct`, `unsure` |
| `decided_by` | tên bạn, ví dụ `human:patph` |
| `note` | lý do ngắn — dòng này đi vào phụ lục khóa luận |

`unsure` là câu trả lời hợp lệ. Nó được xử lý **thận trọng**: coi như `duplicate` và loại clip pretraining, vì loại nhầm một clip rẻ hơn nhiều so với giữ lại một rò rỉ.

Điền xong chạy:

```bash
.venv/Scripts/python.exe -m scripts.apply_review_decisions
.venv/Scripts/python.exe -m scripts.check_leakage datased
```

## Danh sách

Xếp theo similarity giảm dần — cặp đầu đáng ngờ nhất.

### rev-001 · similarity 0.9474 · chồng lấp 8.5 s

- pretraining: `datasec:DATASEC/Train/Train-0031.wav`
- benchmark: `datased:DataSED - DataSED - Dataset for Sound Event Detection of environmental noise/SED_wav/S-0241.wav`

```bash
ffplay -autoexit -nodisp "D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\data\raw\datasec\extracted\DATASEC\Train\Train-0031.wav"
ffplay -autoexit -nodisp "D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\data\raw\datased\extracted\DataSED - DataSED - Dataset for Sound Event Detection of environmental noise\SED_wav\S-0241.wav"
```

### rev-002 · similarity 0.9379 · chồng lấp 14.0 s

- pretraining: `datasec:DATASEC/Train/Train-0015.wav`
- benchmark: `datased:DataSED - DataSED - Dataset for Sound Event Detection of environmental noise/SED_wav/S-0215.wav`

```bash
ffplay -autoexit -nodisp "D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\data\raw\datasec\extracted\DATASEC\Train\Train-0015.wav"
ffplay -autoexit -nodisp "D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\data\raw\datased\extracted\DataSED - DataSED - Dataset for Sound Event Detection of environmental noise\SED_wav\S-0215.wav"
```

### rev-003 · similarity 0.9152 · chồng lấp 40.5 s

- pretraining: `datasec:DATASEC/Sirens and alarms/Sirens/Sirens-0044.wav`
- benchmark: `datased:DataSED - DataSED - Dataset for Sound Event Detection of environmental noise/SED_wav/S-0315.wav`

```bash
ffplay -autoexit -nodisp "D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\data\raw\datasec\extracted\DATASEC\Sirens and alarms\Sirens\Sirens-0044.wav"
ffplay -autoexit -nodisp "D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\data\raw\datased\extracted\DataSED - DataSED - Dataset for Sound Event Detection of environmental noise\SED_wav\S-0315.wav"
```

### rev-004 · similarity 0.9133 · chồng lấp 10.0 s

- pretraining: `datasec:DATASEC/Sirens and alarms/Alarms/Alarms-0003.wav`
- benchmark: `datased:DataSED - DataSED - Dataset for Sound Event Detection of environmental noise/SED_wav/S-0632.wav`

```bash
ffplay -autoexit -nodisp "D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\data\raw\datasec\extracted\DATASEC\Sirens and alarms\Alarms\Alarms-0003.wav"
ffplay -autoexit -nodisp "D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\data\raw\datased\extracted\DataSED - DataSED - Dataset for Sound Event Detection of environmental noise\SED_wav\S-0632.wav"
```

### rev-005 · similarity 0.9090 · chồng lấp 5.0 s

- pretraining: `datasec:DATASEC/Sirens and alarms/Sirens/Sirens-0030.wav`
- benchmark: `datased:DataSED - DataSED - Dataset for Sound Event Detection of environmental noise/SED_wav/S-0319.wav`

```bash
ffplay -autoexit -nodisp "D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\data\raw\datasec\extracted\DATASEC\Sirens and alarms\Sirens\Sirens-0030.wav"
ffplay -autoexit -nodisp "D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\data\raw\datased\extracted\DataSED - DataSED - Dataset for Sound Event Detection of environmental noise\SED_wav\S-0319.wav"
```

### rev-006 · similarity 0.9007 · chồng lấp 3.5 s

- pretraining: `datasec:DATASEC/Sirens and alarms/Sirens/Sirens-0047.wav`
- benchmark: `datased:DataSED - DataSED - Dataset for Sound Event Detection of environmental noise/SED_wav/S-0309.wav`

```bash
ffplay -autoexit -nodisp "D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\data\raw\datasec\extracted\DATASEC\Sirens and alarms\Sirens\Sirens-0047.wav"
ffplay -autoexit -nodisp "D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\data\raw\datased\extracted\DataSED - DataSED - Dataset for Sound Event Detection of environmental noise\SED_wav\S-0309.wav"
```

### rev-007 · similarity 0.8899 · chồng lấp 3.0 s

- pretraining: `datasec:DATASEC/Music/Music-0087.wav`
- benchmark: `datased:DataSED - DataSED - Dataset for Sound Event Detection of environmental noise/SED_wav/S-0606.wav`

```bash
ffplay -autoexit -nodisp "D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\data\raw\datasec\extracted\DATASEC\Music\Music-0087.wav"
ffplay -autoexit -nodisp "D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\data\raw\datased\extracted\DataSED - DataSED - Dataset for Sound Event Detection of environmental noise\SED_wav\S-0606.wav"
```

### rev-008 · similarity 0.8899 · chồng lấp 3.0 s

- pretraining: `datasec:DATASEC/Music/Music-0087.wav`
- benchmark: `datased:DataSED - DataSED - Dataset for Sound Event Detection of environmental noise/SED_wav/S-0622.wav`

```bash
ffplay -autoexit -nodisp "D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\data\raw\datasec\extracted\DATASEC\Music\Music-0087.wav"
ffplay -autoexit -nodisp "D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\data\raw\datased\extracted\DataSED - DataSED - Dataset for Sound Event Detection of environmental noise\SED_wav\S-0622.wav"
```

### rev-009 · similarity 0.8895 · chồng lấp 4.0 s

- pretraining: `datasec:DATASEC/Music/Music-0198.wav`
- benchmark: `datased:DataSED - DataSED - Dataset for Sound Event Detection of environmental noise/SED_wav/S-0606.wav`

```bash
ffplay -autoexit -nodisp "D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\data\raw\datasec\extracted\DATASEC\Music\Music-0198.wav"
ffplay -autoexit -nodisp "D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\data\raw\datased\extracted\DataSED - DataSED - Dataset for Sound Event Detection of environmental noise\SED_wav\S-0606.wav"
```

### rev-010 · similarity 0.8895 · chồng lấp 4.0 s

- pretraining: `datasec:DATASEC/Music/Music-0198.wav`
- benchmark: `datased:DataSED - DataSED - Dataset for Sound Event Detection of environmental noise/SED_wav/S-0622.wav`

```bash
ffplay -autoexit -nodisp "D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\data\raw\datasec\extracted\DATASEC\Music\Music-0198.wav"
ffplay -autoexit -nodisp "D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\data\raw\datased\extracted\DataSED - DataSED - Dataset for Sound Event Detection of environmental noise\SED_wav\S-0622.wav"
```

### rev-011 · similarity 0.8783 · chồng lấp 10.5 s

- pretraining: `datasec:DATASEC/Propeller aircrafts/Helicopters/Helicopters-0050.wav`
- benchmark: `datased:DataSED - DataSED - Dataset for Sound Event Detection of environmental noise/SED_wav/S-0594.wav`

```bash
ffplay -autoexit -nodisp "D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\data\raw\datasec\extracted\DATASEC\Propeller aircrafts\Helicopters\Helicopters-0050.wav"
ffplay -autoexit -nodisp "D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\data\raw\datased\extracted\DataSED - DataSED - Dataset for Sound Event Detection of environmental noise\SED_wav\S-0594.wav"
```

### rev-012 · similarity 0.8746 · chồng lấp 4.0 s

- pretraining: `datasec:DATASEC/Music/Music-0120.wav`
- benchmark: `datased:DataSED - DataSED - Dataset for Sound Event Detection of environmental noise/SED_wav/S-0606.wav`

```bash
ffplay -autoexit -nodisp "D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\data\raw\datasec\extracted\DATASEC\Music\Music-0120.wav"
ffplay -autoexit -nodisp "D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\data\raw\datased\extracted\DataSED - DataSED - Dataset for Sound Event Detection of environmental noise\SED_wav\S-0606.wav"
```

### rev-013 · similarity 0.8746 · chồng lấp 4.0 s

- pretraining: `datasec:DATASEC/Music/Music-0120.wav`
- benchmark: `datased:DataSED - DataSED - Dataset for Sound Event Detection of environmental noise/SED_wav/S-0622.wav`

```bash
ffplay -autoexit -nodisp "D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\data\raw\datasec\extracted\DATASEC\Music\Music-0120.wav"
ffplay -autoexit -nodisp "D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\data\raw\datased\extracted\DataSED - DataSED - Dataset for Sound Event Detection of environmental noise\SED_wav\S-0622.wav"
```

### rev-014 · similarity 0.8744 · chồng lấp 3.0 s

- pretraining: `datasec:DATASEC/Music/Music-0168.wav`
- benchmark: `datased:DataSED - DataSED - Dataset for Sound Event Detection of environmental noise/SED_wav/S-0606.wav`

```bash
ffplay -autoexit -nodisp "D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\data\raw\datasec\extracted\DATASEC\Music\Music-0168.wav"
ffplay -autoexit -nodisp "D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\data\raw\datased\extracted\DataSED - DataSED - Dataset for Sound Event Detection of environmental noise\SED_wav\S-0606.wav"
```

### rev-015 · similarity 0.8744 · chồng lấp 3.0 s

- pretraining: `datasec:DATASEC/Music/Music-0168.wav`
- benchmark: `datased:DataSED - DataSED - Dataset for Sound Event Detection of environmental noise/SED_wav/S-0622.wav`

```bash
ffplay -autoexit -nodisp "D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\data\raw\datasec\extracted\DATASEC\Music\Music-0168.wav"
ffplay -autoexit -nodisp "D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\data\raw\datased\extracted\DataSED - DataSED - Dataset for Sound Event Detection of environmental noise\SED_wav\S-0622.wav"
```

### rev-016 · similarity 0.8739 · chồng lấp 3.0 s

- pretraining: `datasec:DATASEC/Music/Music-0835.wav`
- benchmark: `datased:DataSED - DataSED - Dataset for Sound Event Detection of environmental noise/SED_wav/S-0606.wav`

```bash
ffplay -autoexit -nodisp "D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\data\raw\datasec\extracted\DATASEC\Music\Music-0835.wav"
ffplay -autoexit -nodisp "D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\data\raw\datased\extracted\DataSED - DataSED - Dataset for Sound Event Detection of environmental noise\SED_wav\S-0606.wav"
```

### rev-017 · similarity 0.8739 · chồng lấp 3.0 s

- pretraining: `datasec:DATASEC/Music/Music-0835.wav`
- benchmark: `datased:DataSED - DataSED - Dataset for Sound Event Detection of environmental noise/SED_wav/S-0622.wav`

```bash
ffplay -autoexit -nodisp "D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\data\raw\datasec\extracted\DATASEC\Music\Music-0835.wav"
ffplay -autoexit -nodisp "D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\data\raw\datased\extracted\DataSED - DataSED - Dataset for Sound Event Detection of environmental noise\SED_wav\S-0622.wav"
```

### rev-018 · similarity 0.8721 · chồng lấp 5.0 s

- pretraining: `datasec:DATASEC/Music/Music-0125.wav`
- benchmark: `datased:DataSED - DataSED - Dataset for Sound Event Detection of environmental noise/SED_wav/S-0606.wav`

```bash
ffplay -autoexit -nodisp "D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\data\raw\datasec\extracted\DATASEC\Music\Music-0125.wav"
ffplay -autoexit -nodisp "D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\data\raw\datased\extracted\DataSED - DataSED - Dataset for Sound Event Detection of environmental noise\SED_wav\S-0606.wav"
```

### rev-019 · similarity 0.8721 · chồng lấp 5.0 s

- pretraining: `datasec:DATASEC/Music/Music-0125.wav`
- benchmark: `datased:DataSED - DataSED - Dataset for Sound Event Detection of environmental noise/SED_wav/S-0622.wav`

```bash
ffplay -autoexit -nodisp "D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\data\raw\datasec\extracted\DATASEC\Music\Music-0125.wav"
ffplay -autoexit -nodisp "D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\data\raw\datased\extracted\DataSED - DataSED - Dataset for Sound Event Detection of environmental noise\SED_wav\S-0622.wav"
```

### rev-020 · similarity 0.8694 · chồng lấp 5.0 s

- pretraining: `datasec:DATASEC/Vacuum cleaner fan and hairdryer/fan/fan-0013.wav`
- benchmark: `datased:DataSED - DataSED - Dataset for Sound Event Detection of environmental noise/SED_wav/S-0323.wav`

```bash
ffplay -autoexit -nodisp "D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\data\raw\datasec\extracted\DATASEC\Vacuum cleaner fan and hairdryer\fan\fan-0013.wav"
ffplay -autoexit -nodisp "D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\data\raw\datased\extracted\DataSED - DataSED - Dataset for Sound Event Detection of environmental noise\SED_wav\S-0323.wav"
```

### rev-021 · similarity 0.8690 · chồng lấp 25.5 s

- pretraining: `datasec:DATASEC/Wind turbine/Wind turbine-0007.wav`
- benchmark: `datased:DataSED - DataSED - Dataset for Sound Event Detection of environmental noise/SED_wav/S-0717.wav`

```bash
ffplay -autoexit -nodisp "D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\data\raw\datasec\extracted\DATASEC\Wind turbine\Wind turbine-0007.wav"
ffplay -autoexit -nodisp "D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\data\raw\datased\extracted\DataSED - DataSED - Dataset for Sound Event Detection of environmental noise\SED_wav\S-0717.wav"
```

### rev-022 · similarity 0.8662 · chồng lấp 30.0 s

- pretraining: `datasec:DATASEC/Sirens and alarms/Sirens/Sirens-0046.wav`
- benchmark: `datased:DataSED - DataSED - Dataset for Sound Event Detection of environmental noise/SED_wav/S-0237.wav`

```bash
ffplay -autoexit -nodisp "D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\data\raw\datasec\extracted\DATASEC\Sirens and alarms\Sirens\Sirens-0046.wav"
ffplay -autoexit -nodisp "D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\data\raw\datased\extracted\DataSED - DataSED - Dataset for Sound Event Detection of environmental noise\SED_wav\S-0237.wav"
```

### rev-023 · similarity 0.8607 · chồng lấp 3.0 s

- pretraining: `datasec:DATASEC/Thunder fireworks and gunshot/Fireworks/Fireworks-0056.wav`
- benchmark: `datased:DataSED - DataSED - Dataset for Sound Event Detection of environmental noise/SED_wav/S-0606.wav`

```bash
ffplay -autoexit -nodisp "D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\data\raw\datasec\extracted\DATASEC\Thunder fireworks and gunshot\Fireworks\Fireworks-0056.wav"
ffplay -autoexit -nodisp "D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\data\raw\datased\extracted\DataSED - DataSED - Dataset for Sound Event Detection of environmental noise\SED_wav\S-0606.wav"
```

### rev-024 · similarity 0.8607 · chồng lấp 3.0 s

- pretraining: `datasec:DATASEC/Thunder fireworks and gunshot/Fireworks/Fireworks-0056.wav`
- benchmark: `datased:DataSED - DataSED - Dataset for Sound Event Detection of environmental noise/SED_wav/S-0622.wav`

```bash
ffplay -autoexit -nodisp "D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\data\raw\datasec\extracted\DATASEC\Thunder fireworks and gunshot\Fireworks\Fireworks-0056.wav"
ffplay -autoexit -nodisp "D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\data\raw\datased\extracted\DataSED - DataSED - Dataset for Sound Event Detection of environmental noise\SED_wav\S-0622.wav"
```

### rev-025 · similarity 0.8602 · chồng lấp 3.0 s

- pretraining: `datasec:DATASEC/Music/Music-0891.wav`
- benchmark: `datased:DataSED - DataSED - Dataset for Sound Event Detection of environmental noise/SED_wav/S-0606.wav`

```bash
ffplay -autoexit -nodisp "D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\data\raw\datasec\extracted\DATASEC\Music\Music-0891.wav"
ffplay -autoexit -nodisp "D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\data\raw\datased\extracted\DataSED - DataSED - Dataset for Sound Event Detection of environmental noise\SED_wav\S-0606.wav"
```

### rev-026 · similarity 0.8602 · chồng lấp 3.0 s

- pretraining: `datasec:DATASEC/Music/Music-0891.wav`
- benchmark: `datased:DataSED - DataSED - Dataset for Sound Event Detection of environmental noise/SED_wav/S-0622.wav`

```bash
ffplay -autoexit -nodisp "D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\data\raw\datasec\extracted\DATASEC\Music\Music-0891.wav"
ffplay -autoexit -nodisp "D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\data\raw\datased\extracted\DataSED - DataSED - Dataset for Sound Event Detection of environmental noise\SED_wav\S-0622.wav"
```

### rev-027 · similarity 0.8601 · chồng lấp 11.0 s

- pretraining: `datasec:DATASEC/Music/Music-0125.wav`
- benchmark: `datased:DataSED - DataSED - Dataset for Sound Event Detection of environmental noise/SED_wav/S-0661.wav`

```bash
ffplay -autoexit -nodisp "D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\data\raw\datasec\extracted\DATASEC\Music\Music-0125.wav"
ffplay -autoexit -nodisp "D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\data\raw\datased\extracted\DataSED - DataSED - Dataset for Sound Event Detection of environmental noise\SED_wav\S-0661.wav"
```

### rev-028 · similarity 0.8596 · chồng lấp 3.0 s

- pretraining: `datasec:DATASEC/Thunder fireworks and gunshot/Fireworks/Fireworks-0037.wav`
- benchmark: `datased:DataSED - DataSED - Dataset for Sound Event Detection of environmental noise/SED_wav/S-0089.wav`

```bash
ffplay -autoexit -nodisp "D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\data\raw\datasec\extracted\DATASEC\Thunder fireworks and gunshot\Fireworks\Fireworks-0037.wav"
ffplay -autoexit -nodisp "D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\data\raw\datased\extracted\DataSED - DataSED - Dataset for Sound Event Detection of environmental noise\SED_wav\S-0089.wav"
```

### rev-029 · similarity 0.8590 · chồng lấp 15.0 s

- pretraining: `datasec:DATASEC/Propeller aircrafts/Helicopters/Helicopters-0058.wav`
- benchmark: `datased:DataSED - DataSED - Dataset for Sound Event Detection of environmental noise/SED_wav/S-0594.wav`

```bash
ffplay -autoexit -nodisp "D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\data\raw\datasec\extracted\DATASEC\Propeller aircrafts\Helicopters\Helicopters-0058.wav"
ffplay -autoexit -nodisp "D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\data\raw\datased\extracted\DataSED - DataSED - Dataset for Sound Event Detection of environmental noise\SED_wav\S-0594.wav"
```

### rev-030 · similarity 0.8577 · chồng lấp 3.0 s

- pretraining: `datasec:DATASEC/Workshop/drill/drill-0004.wav`
- benchmark: `datased:DataSED - DataSED - Dataset for Sound Event Detection of environmental noise/SED_wav/S-0323.wav`

```bash
ffplay -autoexit -nodisp "D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\data\raw\datasec\extracted\DATASEC\Workshop\drill\drill-0004.wav"
ffplay -autoexit -nodisp "D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\data\raw\datased\extracted\DataSED - DataSED - Dataset for Sound Event Detection of environmental noise\SED_wav\S-0323.wav"
```

### rev-031 · similarity 0.8547 · chồng lấp 4.0 s

- pretraining: `datasec:DATASEC/Music/Music-0178.wav`
- benchmark: `datased:DataSED - DataSED - Dataset for Sound Event Detection of environmental noise/SED_wav/S-0606.wav`

```bash
ffplay -autoexit -nodisp "D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\data\raw\datasec\extracted\DATASEC\Music\Music-0178.wav"
ffplay -autoexit -nodisp "D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\data\raw\datased\extracted\DataSED - DataSED - Dataset for Sound Event Detection of environmental noise\SED_wav\S-0606.wav"
```

### rev-032 · similarity 0.8547 · chồng lấp 4.0 s

- pretraining: `datasec:DATASEC/Music/Music-0178.wav`
- benchmark: `datased:DataSED - DataSED - Dataset for Sound Event Detection of environmental noise/SED_wav/S-0622.wav`

```bash
ffplay -autoexit -nodisp "D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\data\raw\datasec\extracted\DATASEC\Music\Music-0178.wav"
ffplay -autoexit -nodisp "D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\data\raw\datased\extracted\DataSED - DataSED - Dataset for Sound Event Detection of environmental noise\SED_wav\S-0622.wav"
```

### rev-033 · similarity 0.8524 · chồng lấp 3.0 s

- pretraining: `datasec:DATASEC/Music/Music-0234.wav`
- benchmark: `datased:DataSED - DataSED - Dataset for Sound Event Detection of environmental noise/SED_wav/S-0606.wav`

```bash
ffplay -autoexit -nodisp "D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\data\raw\datasec\extracted\DATASEC\Music\Music-0234.wav"
ffplay -autoexit -nodisp "D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\data\raw\datased\extracted\DataSED - DataSED - Dataset for Sound Event Detection of environmental noise\SED_wav\S-0606.wav"
```

### rev-034 · similarity 0.8524 · chồng lấp 3.0 s

- pretraining: `datasec:DATASEC/Music/Music-0234.wav`
- benchmark: `datased:DataSED - DataSED - Dataset for Sound Event Detection of environmental noise/SED_wav/S-0622.wav`

```bash
ffplay -autoexit -nodisp "D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\data\raw\datasec\extracted\DATASEC\Music\Music-0234.wav"
ffplay -autoexit -nodisp "D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\data\raw\datased\extracted\DataSED - DataSED - Dataset for Sound Event Detection of environmental noise\SED_wav\S-0622.wav"
```

### rev-035 · similarity 0.8503 · chồng lấp 3.5 s

- pretraining: `datasec:DATASEC/Train/Train-0056.wav`
- benchmark: `datased:DataSED - DataSED - Dataset for Sound Event Detection of environmental noise/SED_wav/S-0210.wav`

```bash
ffplay -autoexit -nodisp "D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\data\raw\datasec\extracted\DATASEC\Train\Train-0056.wav"
ffplay -autoexit -nodisp "D:\IUH_K18\HK1N5\KLTN2\environmental-audio-rag\data\raw\datased\extracted\DataSED - DataSED - Dataset for Sound Event Detection of environmental noise\SED_wav\S-0210.wav"
```

## Ghi chú kỹ thuật

- Fingerprint: frame 1.0 s, hop 0.5 s, 40 chiều, `fmax` 7000 Hz.
- Similarity là cosine trung bình trên đoạn chồng lấp dài nhất, sau khi chuẩn hoá z-score theo thống kê corpus.
- Mọi cặp ở đây nằm dưới 0.95, tức **không** đạt ngưỡng tự động. Ba cặp vượt 0.95 đã được xử lý bằng luật và không có trong phiếu này.

