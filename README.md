# Grounded Environmental Audio Monitoring and RAG-based Event Retrieval

Khóa luận Khoa học dữ liệu về phát hiện sự kiện âm thanh môi trường, sinh mô tả có căn cứ và truy xuất sự kiện bằng RAG.

> Trạng thái: khung kiến trúc ban đầu. Chưa tải dữ liệu, chưa huấn luyện model, chưa có kết quả thực nghiệm. Xem [STATUS](docs/STATUS.md).

## 1. Bài toán

Hệ thống nhận recording môi trường dài, phát hiện class cùng onset/offset, tạo caption chỉ từ event timeline, lưu event có cấu trúc và trả lời truy vấn dựa trên bằng chứng đã lưu.

```text
audio → SED → event timeline → grounded caption → event store → hybrid retrieval
```

Phạm vi dữ liệu:

- **DataSEC:** clip sự kiện tách rời; dùng cho pretraining, classification và subclass refinement.
- **DataSED:** recording thực tế liên tục; dùng cho temporal/polyphonic SED và benchmark chính.

Hệ thống không tuyên bố phát hiện tội phạm, ý định, tình trạng khẩn cấp hay sự cố trường học. Output mô tả nguồn âm quan sát được.

## 2. Câu hỏi nghiên cứu

1. Pretraining trên DataSEC cải thiện SED trên DataSED đến mức nào?
2. Caption bị ràng buộc bởi event timeline giảm hallucination đến mức nào so với caption không ràng buộc?
3. Kết hợp metadata filtering và semantic retrieval cải thiện Recall@k/MRR cho truy vấn sự kiện ra sao?
4. Classifier phân cấp có tách được subclass DataSEC trong các coarse class gộp hay không?

## 3. Đóng góp dự kiến

- Pipeline tái lập từ archive công bố đến classification và polyphonic SED.
- Mô hình chuyển giao DataSEC → DataSED, có kiểm tra duplicate xuyên dataset.
- Caption có căn cứ, đo event hallucination và temporal-order agreement.
- RAG truy xuất recording theo class, thời gian, duration và quan hệ trước–sau.
- Ứng dụng web minh họa upload, timeline, caption và truy vấn.

## 4. Kiến trúc

```mermaid
flowchart LR
    A[DataSEC isolated clips] --> B[Encoder pretraining]
    C[DataSED continuous recordings] --> D[Polyphonic SED]
    B --> D
    D --> E[Event timeline]
    E --> F[Grounded caption]
    E --> G[Structured event store]
    F --> G
    G --> H[Filter + vector retrieval]
    H --> I[Evidence-bound answer]
```

Chi tiết: [SYSTEM](docs/SYSTEM.md), [DATA_PLAN](docs/DATA_PLAN.md), [taxonomy](docs/taxonomy.md), [evaluation protocol](docs/evaluation_protocol.md).

## 5. Cấu trúc repository

```text
environmental-audio-rag/
├── contracts/          # schema giao tiếp giữa data, model và service
├── data/               # raw/interim/features/annotations/manifests/splits
├── docs/               # đặc tả, kế hoạch, protocol, ADR, measurements
├── ml/                 # datasets, features, models, training, evaluation
├── notebooks/          # chỉ dùng khám phá; logic chính phải vào ml/ hoặc scripts/
├── scripts/            # entry point tái lập pipeline
├── services/           # api, inference, frontend, stream
└── tests/              # contract, unit và integration tests
```

## 6. Nguồn chân lý

| Nội dung | File |
|---|---|
| Phạm vi và kiến trúc | `docs/SYSTEM.md` |
| Trạng thái thực tế | `docs/STATUS.md` |
| Roadmap | `docs/PLAN.md` |
| Dữ liệu và split | `docs/DATA_PLAN.md` |
| Class và mapping | `docs/taxonomy.md` |
| Đánh giá | `docs/evaluation_protocol.md` |
| Quyết định kiến trúc | `docs/decisions/` |

## 7. Nguyên tắc

- Không commit raw audio, feature tensor, checkpoint hoặc vector index.
- Không sửa nhãn nguồn để làm đẹp kết quả; mọi exclusion cần reason code.
- Không dùng DataSED test để chọn threshold, duration prior hoặc checkpoint.
- Caption không được thêm event ngoài timeline đầu vào.
- Mọi số liệu trong báo cáo phải truy ngược được tới manifest, config và model artifact.

