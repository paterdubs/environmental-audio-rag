# Độ nhất quán chú giải — đo trên recording byte-identical

**Sinh tự động** `scripts.report_annotation_consistency` — 2026-09-23T04:56:46Z

## Phương pháp

DataSED chứa các cặp recording giống nhau **từng byte** nhưng mang hai `recording_id`, và mỗi bản được chú giải riêng. So hai chú giải đó cho ra một phép đo agreement mà không tốn công gán nhãn nào.

> ⚠️ **Cỡ mẫu 8 cặp.** Đây là tín hiệu cảnh báo, không phải một nghiên cứu agreement. Không dùng con số này làm ước lượng điểm cho bất kỳ đại lượng nào.

## Tổng hợp

| | |
|---|---:|
| Cặp byte-identical | 8 |
| Cặp **bất đồng về lớp hoặc số event** | **2** |
| Cặp so được biên | 6 |
| Biên nằm trong collar 0.2 s | 67 / 94 |

Lệch biên lớn nhất: **12.72 s** (`S-0289` vs `S-0500`).

## Chi tiết từng cặp

| Cặp | Event | Cùng lớp | Lệch biên lớn nhất | Biên trong collar |
|---|---|---|---:|---:|
| `S-0569` / `S-0572` | 12 / 12 | ✅ | 0.46 s | 20/24 |
| `S-0397` / `S-0585` | 6 / 6 | ❌ | — | — |
| `S-0621` / `S-0623` | 4 / 4 | ✅ | 0.19 s | 8/8 |
| `S-0108` / `S-0589` | 6 / 6 | ✅ | 5.46 s | 4/12 |
| `S-0062` / `S-0198` | 7 / 8 | ❌ | — | — |
| `S-0570` / `S-0571` | 19 / 19 | ✅ | 0.40 s | 26/38 |
| `S-0289` / `S-0500` | 1 / 1 | ✅ | 12.72 s | 0/2 |
| `S-0606` / `S-0622` | 5 / 5 | ✅ | 0.65 s | 9/10 |

## Bất đồng về lớp

### `S-0397` vs `S-0585`

- Chỉ có ở `S-0397`: `lawn_mower_brush_cutter_olive_shaker`
- Chỉ có ở `S-0585`: `propeller_aircrafts`

### `S-0062` vs `S-0198`

- Chỉ có ở `S-0062`: `birds`, `vacuum_cleaner_fan_hairdryer`
- Chỉ có ở `S-0198`: —

## Hệ quả

1. **Collar 0.2 s chặt hơn độ chính xác của nhãn.** Chỉ 67/94 biên của hai lần gán nhãn trên **cùng một audio** nằm trong khoảng đó. Sai số của model ở mức này không phân biệt được với nhiễu nhãn.
2. **Bất đồng về lớp là bằng chứng trực tiếp cho cặp dễ nhầm**, lấy từ chính ground truth chứ không từ ma trận nhầm của model. Nó nên đi vào [taxonomy.md §8](../taxonomy.md) như một nguồn độc lập.
3. Khi báo event-based F1 và PSDS, phải nêu con số này trong phần Hạn chế. Một cải thiện nhỏ hơn mức bất đồng của chính nhãn thì không tuyên bố được.

