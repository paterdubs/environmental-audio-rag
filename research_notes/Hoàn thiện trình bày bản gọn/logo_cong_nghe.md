# Hình "tổng quan công nghệ" có logo cho khóa luận: nguồn logo, pháp lý, cách vẽ offline, cách đặt vào Word

Ghi chú của researcher, ngày 28/11/2026. Mọi số phiên bản, slug, mã màu trong ghi chú này đọc trực tiếp từ
tệp. Không có số nào chép tay từ trí nhớ. Đã đọc gói npm `simple-icons@16.38.1` (tải tarball về scratchpad,
chỉ đọc `data/simple-icons.json`, `DISCLAIMER.md`, `LICENSE.md` và các tệp SVG) và metadata của các wheel Python
(tải bằng `pip download --only-binary=:all: --no-deps`, không cài, không chạy). Không sửa tệp nào trong repo.

Danh sách công nghệ thật của hệ thống, đối chiếu từ tệp (không theo danh sách gợi ý của đề bài):

| Tầng | Công nghệ | Bằng chứng trong repo |
|---|---|---|
| Hạ tầng | Docker Compose (3 dịch vụ db, inference, api); ảnh `pgvector/pgvector:pg16`, `python:3.12-slim`, `node:24-slim` | `docker-compose.yml`; `services/api/Dockerfile` dòng 5, 12; `services/inference/Dockerfile` dòng 13 |
| Ngôn ngữ | Python 3.12 (venv 3.12.10, CI `python-version: "3.12"`); Node.js 24 chỉ để build giao diện | `.github/workflows/ci.yml`; Dockerfile |
| Học máy | PyTorch ≥2.8; librosa; soundfile; NumPy; SciPy; pandas; scikit-learn (GBM của LBR); iterative-stratification; PyYAML; tqdm; jsonschema | `requirements.txt`, `requirements-inference.txt`, `requirements-torch.txt` |
| Mô hình SED (mã nghiên cứu, không phải sản phẩm có thương hiệu) | PANNs CNN14 (RQ1); BEATs và Frame-MobileNet qua PretrainedSED; EfficientSED (phần sequence, MIT) | `ml/models/external/{beats,frame_mn,efficientsed_tf}/NOTICE.md` |
| Đánh giá | sed_eval, psds_eval, pycocoevalcap; pytest, ruff | `requirements-eval.txt`, `requirements.txt` |
| Mô hình ngôn ngữ | llama.cpp build b11158 + `Qwen_Qwen3.5-9B-Q4_K_M.gguf` | `report/final_tables/f15_tech_stack.md` |
| Truy hồi | sentence-transformers (BGE-M3), mô hình nạp offline từ `artifacts/hf` (`HF_HUB_OFFLINE=1`). **Không** dùng FlagEmbedding | `requirements-retrieval.txt`; `docker-compose.yml` |
| Lưu trữ | PostgreSQL 16 + pgvector; psycopg 3; gói Python `pgvector`; alembic | `requirements-api.txt`, `requirements-db.txt` |
| Dịch vụ | FastAPI, Uvicorn, python-multipart, httpx; Pydantic (import trực tiếp ở `services/api/app/schemas.py`, `services/inference/app/main.py`, `ml/retrieval/*.py`) | `requirements-services.txt`; grep import |
| Giao diện | React ^19.3, TypeScript ^7.0, Vite ^8.3, TanStack Query ^5.103, Vitest ^5.0, Playwright ^1.63, phông IBM Plex (`@fontsource`) | `services/frontend/package.json` |
| CI và mã nguồn | Git, GitHub, GitHub Actions (`actions/checkout@v4`, `setup-python@v5`, `setup-node@v4`) | `.github/workflows/ci.yml` |
| Dựng báo cáo | Pandoc (`find_pandoc()` trong `scripts/build_midterm_report.py`), matplotlib 3.11.2, lxml 6.1.3, Microsoft Word qua COM (`Word.Application`, `ExportAsFixedFormat` trong `scripts/update_docx_fields.ps1`) | các tệp vừa nêu; `pip list` của `.venv` |

Lưu ý cho người viết: bảng `f15_tech_stack.md` hiện không có NumPy, SciPy, pandas, Pydantic, Git/GitHub, Pandoc,
matplotlib, Word. Nếu hình logo có các mục này mà bảng không có, hình và bảng sẽ lệch nhau.

## Câu hỏi 1. Công nghệ nào có trong Simple Icons (slug, mã màu, phiên bản gói), cái nào đã bị gỡ

### Takeaway
Simple Icons bản mới nhất là **16.38.1** (npm, cập nhật 24/11/2026, 3 472 biểu tượng). Bản này có đủ phần lõi
Python/PyTorch/NumPy/scikit-learn/FastAPI/Pydantic/PostgreSQL/Docker/React/TypeScript/Vite/Hugging Face/Git/GitHub/
Pandoc/Qwen. Bản này **không có** Uvicorn, librosa, matplotlib, pgvector, psycopg, sentence-transformers, BGE/BAAI,
llama.cpp, Playwright và Microsoft Word. Word nằm trong nhóm biểu tượng Microsoft bị gỡ ở bản 13.0.0. Bảy mã màu
thương hiệu có độ tương phản với nền trắng dưới 3:1 (React, Hugging Face, scikit-learn, SciPy, Vitest, TanStack,
Ruff), nên các logo này phải đặt trên nền tối hoặc dùng bản màu đầy đủ chính thức.

### Cited Findings
- Phiên bản npm hiện hành là `simple-icons` **16.38.1**, `time.modified = 2026-11-24T17:13:49Z` (kết quả `npm view`). Tarball có 3 472 tệp SVG trong `icons/` và tệp dữ liệu `data/simple-icons.json` với 3 472 mục. Mỗi SVG có `viewBox="0 0 24 24"` và một `<path>` đơn sắc — [simple-icons-16.38.1.tgz](https://registry.npmjs.org/simple-icons/-/simple-icons-16.38.1.tgz)
- Gói Python `simplepycons` **1!16.38.1** (giấy phép MIT, Python ≥3.10, wheel thuần Python 5,2 MB) bọc đúng bản Simple Icons này. Mỗi biểu tượng có `name`, `title`, `primary_color` (dạng `"#EE4C2C"`, có dấu #), `raw_svg`, `source`, `guidelines_url`, `license`; truy cập bằng `all_icons["python"]` — [PyPI simplepycons](https://pypi.org/project/simplepycons/); [GitHub carstencodes/simplepycons](https://github.com/carstencodes/simplepycons)
- Tên `simple-icons` và `pysimpleicons` **không** có trên PyPI (`pip index versions` trả "No matching distribution") — [PyPI](https://pypi.org/)
- Mục có trong 16.38.1, đọc từ `data/simple-icons.json` (slug | title | hex | nguồn | hướng dẫn thương hiệu | giấy phép) — [simple-icons-16.38.1.tgz](https://registry.npmjs.org/simple-icons/-/simple-icons-16.38.1.tgz):
  - `python` | Python | `#3776AB` | python.org/community/logos | python.org/community/logos | —
  - `pytorch` | PyTorch | `#EE4C2C` | pytorch.github.io logo.svg | PyTorch-Brand-Guidelines.pdf | —
  - `numpy` | NumPy | `#013243` | numpy.org/press-kit | numpy/branding/logo/logoguidelines.md | —
  - `scipy` | SciPy | `#8CAAE6` | — | — | —
  - `pandas` | pandas | `#150458` | pandas.pydata.org/about/citing.html | cùng trang | —
  - `scikitlearn` | scikit-learn | `#F7931E` | scikit-learn doc/logos | — | —
  - `fastapi` | FastAPI | `#009688` | — | — | —
  - `pydantic` | Pydantic | `#E92063` | — | — | —
  - `postgresql` | PostgreSQL | `#4169E1` | wiki.postgresql.org/wiki/Logo | postgresql.org/about/policies/trademarks | —
  - `docker` | Docker | `#2496ED` | docker.com/company/newsroom/media-resources | — | —
  - `react` | React | `#61DAFB` | create-react-app logo.svg | — | —
  - `typescript` | TypeScript | `#3178C6` | typescriptlang.org/branding | cùng trang | —
  - `vite` | Vite | `#9135FF` | voidzero community-design-resources | — | —
  - `vitest` | Vitest | `#00FF74` | voidzero community-design-resources | — | —
  - `reactquery` | React Query | `#FF4154`; `tanstack` | TanStack | `#ECE8D1` | — | — | —
  - `huggingface` | Hugging Face | `#FFD21E` | huggingface.co/brand | huggingface.co/brand | —
  - `git` | Git | `#F03C2E` | git-scm.com/community/logos | — | **CC-BY-3.0**
  - `github` | GitHub | `#181717` | github.com/logos | github.com/logos | —
  - `githubactions` | GitHub Actions | `#2088FF` | — | — | —
  - `pandoc` | Pandoc | `#4093DA` | tarleb/pandoc-logo | — | **CC-BY-SA-4.0**
  - `qwen` | QWen | `#6950EF` | qwen.ai | — | —
  - `nodedotjs` | Node.js | `#5FA04E` | nodejs.org/en/about/branding | cùng trang | —
  - `pytest` | Pytest | `#0A9EDC`; `ruff` | Ruff | `#D7FF64`; `yaml` | YAML | `#CB171E`; `nvidia` | NVIDIA | `#76B900`; `meta` | Meta | `#0467DF` (có guidelines Meta); `alibabacloud` | `#FF6A00`; `ollama` | `#000000`; `npm` | `#CB3837`
- Slug **không có** trong 16.38.1 (kiểm bằng tên tệp và tìm trong tiêu đề): `uvicorn`, `playwright`, `microsoftword`, `microsoftoffice`, `matplotlib`, `librosa`, `pgvector`, `psycopg`, `httpx`, `sentencetransformers`, `dockercompose`, `llama`/llama.cpp, `cuda`, `alembic`, `windows`, `powershell`, `visualstudiocode`, `openai`. Tìm "llama", "playwright", "word", "matplotlib", "vector", "sentence", "uvicorn", "psycopg", "librosa", "bge", "baai" không ra mục nào liên quan — [simple-icons-16.38.1.tgz](https://registry.npmjs.org/simple-icons/-/simple-icons-16.38.1.tgz)
- Bản **13.0.0** gỡ 39 biểu tượng. PR #10019 gỡ 28 biểu tượng Microsoft, gồm Microsoft, Microsoft Word, Excel, PowerPoint, Teams, Visio, Azure và C#. PR #11314 gỡ IBM, IBM Cloud, IBM Watson; các PR khác gỡ Google Domains/Hangouts/Podcasts, Daimler, DocuSign. Trang release không nêu lý do — [newreleases.io: simple-icons 13.0.0](https://newreleases.io/project/github/simple-icons/simple-icons/release/13.0.0)
- Simple Icons gỡ biểu tượng khi thương hiệu yêu cầu, qua email `removals at simpleicons dot org` hoặc issue. Việc gỡ thường gom vào hai bản major mỗi năm, nhưng có thể gỡ ngay — `DISCLAIMER.md` trong [simple-icons-16.38.1.tgz](https://registry.npmjs.org/simple-icons/-/simple-icons-16.38.1.tgz)
- Thư mục `media/` của llama.cpp hiện chỉ thấy `matmul.png` và `matmul.svg`, không có tệp logo hay ghi chú giấy phép logo — [github.com/ggml-org/llama.cpp/tree/master/media](https://github.com/ggml-org/llama.cpp/tree/master/media)
- Tỉ số tương phản mã màu với nền trắng (công thức WCAG, tự tính từ hex ở trên): React 1,62; Hugging Face 1,45; scikit-learn 2,30; SciPy 2,33; Vitest 1,35; TanStack 1,23; Ruff 1,14 (đều dưới 3). Các mã còn lại từ 3,03 (pytest) đến 17,89 (GitHub) — tính trên dữ liệu [simple-icons-16.38.1.tgz](https://registry.npmjs.org/simple-icons/-/simple-icons-16.38.1.tgz)

### Inferences
- Phân loại đề xuất cho từng công nghệ của hệ thống:
  - **Dùng biểu tượng Simple Icons được** (sau khi xem pháp lý ở câu 2): PyTorch, NumPy, pandas, SciPy, scikit-learn, FastAPI, Pydantic, Docker (đại diện cả Docker Compose), React, TypeScript, Vite, Vitest, TanStack Query (`reactquery` cho đúng tên "Query"), Hugging Face (vai trò kho mô hình), Git, GitHub, GitHub Actions, Pandoc, Qwen, Node.js, pytest, Ruff.
  - **Nên dùng bản màu chính thức thay cho bản đơn sắc**: Python (logo hai màu, xem câu 2), PostgreSQL (`elephant.png`, hoặc chỉ ghi chữ), Hugging Face (bản đơn sắc vàng gần như không thấy trên nền trắng).
  - **Không có logo, dùng nhãn chữ**: llama.cpp, Uvicorn, librosa, soundfile, matplotlib, sed_eval, psds_eval, pycocoevalcap, sentence-transformers, BGE-M3, pgvector, psycopg, httpx, alembic, PANNs CNN14, BEATs, Frame-MobileNet/PretrainedSED, EfficientSED, Playwright, Microsoft Word.
- Đừng dùng logo Ollama hay logo Meta/Llama cho llama.cpp. Hệ thống không chạy Ollama, và llama.cpp không phải sản phẩm của Meta, nên hai logo này đều gây hiểu sai. Cũng đừng dùng logo Alibaba Cloud cho Qwen: mô hình chạy cục bộ, không qua dịch vụ đám mây.
- Nhãn chữ là lựa chọn tốt cho mô hình nghiên cứu (CNN14, BEATs, Frame-MobileNet, BGE-M3), vì đây là tên mô hình trong bài báo, không phải sản phẩm. Nhãn có thể ghi kèm năm hoặc tác giả, ví dụ "PANNs CNN14 (Kong 2020)".
- Phông IBM Plex dùng trong giao diện thuộc IBM, và IBM đã bị gỡ khỏi Simple Icons. Không cần đưa phông vào hình công nghệ.

### Gaps
- Chưa tìm được lý do Simple Icons gỡ nhóm Microsoft (#10019). Trang release không ghi; phần lớn có thể do Microsoft yêu cầu, nhưng chưa xác minh.
- Chưa xác minh Playwright và matplotlib **từng** có trong Simple Icons hay chưa từng có. Chỉ biết chắc bản 16.38.1 không có.
- Chưa kiểm logo chính thức của Uvicorn, librosa, matplotlib, psycopg, sentence-transformers và BAAI: có tồn tại không, giấy phép gì. Các dự án này có thể có logo trong repo hoặc trang tài liệu, nhưng chưa tra.

## Câu hỏi 2. Giấy phép và nhãn hiệu: được dùng logo nào trong khóa luận phi thương mại, với điều kiện gì

### Takeaway
CC0 của Simple Icons chỉ áp cho **dữ liệu SVG**, không trao quyền nhãn hiệu. Chính `DISCLAIMER.md` nói không phải
mọi biểu tượng đều là CC0 và đề nghị người dùng tự xin phép. Hầu hết chính sách thương hiệu cho phép dùng **tên**
để nói đúng sự thật ("hệ thống chạy trên PostgreSQL"). Riêng **logo** thì chặt hơn:
- Microsoft cấm dùng logo khi không có giấy phép.
- PostgreSQL cấm sửa logo và cấm đặt Slonik cạnh logo khác.
- PSF cần xin phép nếu chỉ đổi màu logo Python.
- Linux Foundation (PyTorch) cấm biến thể màu.
- Docker yêu cầu đúng màu đã duyệt.

Cách an toàn: dùng logo chính thức không sửa, hoặc biểu tượng Simple Icons đúng màu thương hiệu khi bản đơn sắc
trùng với dấu hiệu chính thức. Bỏ logo Microsoft và Slonik khỏi hình nhiều logo. Thêm chú thích nhãn hiệu.

### Cited Findings
- **Simple Icons**: "Simple Icons is released under CC0 - though that doesn't mean to imply that all icons within the project are also CC0. Please see individual licenses where available."; "Simple Icons cannot be held responsible for any legal activity raised by a brand, or users of the package. We ask that our users seek the correct permissions to use the icons relevant to their project."; người dùng được đề nghị đọc trang `guidelines` hoặc `source` của từng thương hiệu — `DISCLAIMER.md` trong [simple-icons-16.38.1.tgz](https://registry.npmjs.org/simple-icons/-/simple-icons-16.38.1.tgz) (cùng nội dung trên [GitHub simple-icons](https://github.com/simple-icons/simple-icons/blob/develop/DISCLAIMER.md))
- **Simple Icons, giấy phép riêng từng biểu tượng** ghi trong JSON: Git `CC-BY-3.0`, Pandoc `CC-BY-SA-4.0`. Các mục còn lại trong danh sách ở câu 1 có `license: null`, và disclaimer nói "the absence of license data ... does not imply that the icon is not released under a license" — [simple-icons-16.38.1.tgz](https://registry.npmjs.org/simple-icons/-/simple-icons-16.38.1.tgz)
- **Python (PSF)**:
  - Được dùng "Python" hoặc "the unaltered logos" để nói phần mềm viết bằng hoặc tương thích với Python mà không cần xin phép trước.
  - Bài báo học thuật được miễn ký hiệu ®.
  - Logo chỉ đổi màu hoặc phông cần PSF Trademarks Committee cho phép.
  - Không được xóa ký hiệu ™.
  - Câu ghi chú gợi ý: "'Python' and the Python logos are trademarks or registered trademarks of the Python Software Foundation, used by ___ with permission from the Foundation".
  - Liên hệ: psf-trademarks@python.org.

  Nguồn: [PSF Trademark Usage Policy](https://www.python.org/psf/trademarks/)
- **PostgreSQL**:
  - Được dùng tên Postgres/PostgreSQL trong bài viết và tài liệu khi đúng sự thật, miễn không hàm ý liên kết hay được bảo trợ.
  - Nguyên văn: "The marks should not be modified in any way without prior approval. They should not be presented with other trademarks or logos."
  - Slonik "must appear in one of the forms below": `elephant.png` (màu) hoặc `elephant-bw.png`.
  - "For pretty much any use not discussed above, you must contact us for permission".
  - Câu ghi chú: "Postgres, PostgreSQL and the Slonik Logo are trademarks or registered trademarks of the PostgreSQL Community Association of Canada, and used with their permission."
  - Liên hệ: board@lists.postgres.ca.

  Nguồn: [PostgreSQL Trademark Policy](https://www.postgresql.org/about/policies/trademarks/)
- **Docker**: trang media chỉ có quy tắc trình bày: "Do not stretch or distort", "Do not outline", "Do not apply shadows or effects", "Do not rotate", "Always use these color treatments exactly as provided", "Do not use unapproved colors", cao tối thiểu 24 px, khoảng trống 0,5x cho biểu tượng. Quyền dùng của bên thứ ba nằm ở trang Trademark Guidelines riêng — [Docker media resources](https://www.docker.com/company/newsroom/media-resources/); [Docker Trademark Guidelines](https://www.docker.com/legal/trademark-guidelines/)
- **PyTorch / Linux Foundation**:
  - Dùng tài liệu thương hiệu PyTorch Foundation đồng nghĩa với đồng ý LF Terms of Use, LF Trademark Usage Guidelines và hướng dẫn thương hiệu PyTorch.
  - Repo artwork ưu tiên SVG và bản biểu tượng (icon).
  - Kết quả tìm kiếm nhắc tới một bản PDF cũ năm 2021 ghi Facebook, Inc. trong ghi chú nhãn hiệu; bản này đã lỗi thời.

  Nguồn: [PyTorch Brand Guidelines](https://pytorch.org/brand-guidelines/); [pytorch-fdn/artwork](https://github.com/pytorch-fdn/artwork)
- **Linux Foundation**:
  - "You may make fair use of word marks to make true factual statements"; fair use "does not permit you to state or imply that the owner of a mark produces, endorses" sản phẩm.
  - "A trademark should not be altered or amended in any way"; "A logo should not be displayed with color variations, or with other elements superimposed on top of the logo".
  - Dùng ghi chú nhãn hiệu ở lần xuất hiện đầu hoặc nổi bật nhất.
  - "Individual projects under The Linux Foundation may have additional guidelines".

  Nguồn: [LF Trademark Usage](https://www.linuxfoundation.org/legal/trademark-usage)
- **Microsoft** (Word, và Playwright, BEATs vì đều là dự án Microsoft):
  - "Many uses, including our logos, app and product icons, and other designs, will require a license first"; "Don't use Microsoft's logos, icons, or designs, in any manner".
  - Tên sản phẩm được dùng trong văn bản "without alteration ... to refer to Microsoft and its products", dùng như tính từ ("Word documents"), không hàm ý được bảo trợ.
  - Câu ghi chú: "Microsoft, (list additional trademarks in alphabetical order) are trademarks of the Microsoft group of companies."

  Nguồn: [Microsoft Trademark and Brand Guidelines](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks)
- **Hugging Face**: trang brand có tệp tải về (.svg, .png, .ai: logo chuẩn, logo kèm chữ, bản đơn sắc, bản "pirate") với câu "Download the official Hugging Face brand assets to use in your projects". Màu: `#FFD21E`, `#FF9D00`, `#6B7280`. Trang **không** nêu hạn chế hay giấy phép — [huggingface.co/brand](https://huggingface.co/brand)
- **React (Meta)**: ngày 07/08/2018, collaborator Dan Abramov (gaearon) trả lời trong issue rằng logo React theo **CC BY 4.0** "just like the documentation itself", và trỏ tới hướng dẫn thương hiệu của Facebook. Năm 2020 có người hỏi lại chỗ ghi giấy phép này nhưng không ai trả lời — [facebook/react#12570](https://github.com/facebook/react/issues/12570)
- **Qwen (Alibaba)**:
  - Không tìm thấy hướng dẫn logo chính thức.
  - Giấy phép mô hình Qwen1.5 ghi rằng không trao quyền dùng tên thương mại hay nhãn hiệu, trừ phần cần cho thông báo bắt buộc.
  - Alibaba gom thương hiệu AI về "Qwen" (tiếng Trung "千问大模型") từ 03/2026.

  Nguồn: [Qwen1.5 LICENSE trên Hugging Face](https://huggingface.co/Qwen/Qwen1.5-1.8B-Chat-GGUF/blob/07800fcba6d5d1df3dfa36e3763374a2c0d9f91b/LICENSE); [TechNode 02/03/2026](https://technode.com/2026/03/02/alibaba-unifies-ai-branding-under-qwen/)
- **Luật Việt Nam**:
  - Một bài phân tích thứ cấp nêu: theo khoản 2 Điều 125 Luật SHTT, chủ sở hữu không được cấm người khác "sử dụng trung thực" tên người và dấu hiệu mô tả.
  - Bài cũng cho rằng hành vi vì mục đích cá nhân, phi thương mại hoặc nghiên cứu không bị coi là xâm phạm.
  - Văn bản luật gốc (bản hợp nhất sau sửa đổi 2022) chưa được đọc để đối chiếu.

  Nguồn: [Luật Minh Khuê](https://luatminhkhue.vn/cac-truong-hop-chu-so-huu-khong-duoc-ngan-cam-nguoi-khac-su-dung-doi-tuong-so-huu-cong-nghiep.aspx); văn bản hợp nhất để đối chiếu: [160/VBHN-VPQH](https://datafiles.chinhphu.vn/cpp/files/vbpq/2026/10/160-vbhn-vpqh.signed.pdf)

### Inferences
- Ba lớp quyền tách nhau:
  1. Quyền tác giả với tệp SVG. Simple Icons trao CC0 cho phần dữ liệu của họ; riêng Git là CC BY 3.0, Pandoc là CC BY-SA 4.0, React là CC BY 4.0 theo lời maintainer.
  2. Quyền nhãn hiệu với dấu hiệu, do chủ thương hiệu giữ.
  3. Hướng dẫn trình bày (màu, khoảng trống, không biến dạng).

  CC0 chỉ giải quyết lớp 1. Khóa luận phi thương mại, dùng logo để **nhận diện** công nghệ thật sự dùng, là kiểu dùng mang tính chỉ dẫn (nominative) mà PSF và LF mô tả là chấp nhận được cho tên. Với logo thì mỗi chủ có điều kiện riêng.
- Đề xuất xử lý theo từng thương hiệu:
  - **Python**: dùng logo hai màu chính thức từ python.org/community/logos, không dùng bản đơn sắc `#3776AB` của Simple Icons. PSF nói logo chỉ đổi màu cần xin phép.
  - **PostgreSQL**: chính sách nói Slonik "should not be presented with other trademarks or logos", và chỉ cho hai dạng tệp chính thức. Hình nhiều logo vì vậy vi phạm câu chữ chính sách, dù rủi ro thực tế với khóa luận rất thấp. Đề xuất: ghi chữ "PostgreSQL 16 + pgvector" trong ô màu `#4169E1`, không vẽ Slonik. Muốn có Slonik thì gửi email xin phép board@lists.postgres.ca.
  - **PyTorch, Docker**: bản Simple Icons trùng với biểu tượng chính thức (ngọn lửa cam, cá voi xanh) và đúng màu thương hiệu. Giữ nguyên tỉ lệ, không viền, không bóng, không xoay, không đặt chữ đè lên.
  - **Microsoft Word, Playwright, BEATs**: chỉ ghi tên bằng chữ, không vẽ logo.
  - **React**: dùng được, kèm ghi công CC BY 4.0. Màu `#61DAFB` cần nền tối mới đủ tương phản.
  - **Hugging Face**: dùng logo màu chính thức từ trang brand (có viền và chi tiết tối), không dùng bản đơn sắc vàng.
  - **Qwen**: dùng biểu tượng `qwen` của Simple Icons ở mức chỉ dẫn, kèm câu ghi chú. Không có hướng dẫn chính thức nên không có ràng buộc trình bày nào để tuân theo.
  - **Git, Pandoc**: ghi công đúng giấy phép. Pandoc là CC BY-SA, nên hình chứa logo Pandoc phải cho phép người khác dùng lại theo cùng giấy phép. Đơn giản hơn là bỏ logo Pandoc, vì đây là công cụ dựng báo cáo, không thuộc hệ thống.
- Hình công nghệ của *hệ thống* không cần Pandoc, Word, matplotlib, Git/GitHub. Đây là công cụ làm báo cáo và quản lý mã. Bỏ chúng đi thì giảm số thương hiệu phải xử lý và giữ hình đúng chủ đề. Nếu muốn, các công cụ này có thể vào Phụ lục B (tái lập) dưới dạng bảng chữ.

### Gaps
- Chưa đọc trực tiếp trang Docker Trademark Guidelines, GitHub Logos (github.com/logos), NumPy `logoguidelines.md`, TypeScript branding, Node.js branding và Meta brand resources. Chưa biết các trang này có giới hạn riêng cho bên thứ ba hay không.
- Chưa đọc văn bản gốc Điều 125, Điều 129 Luật SHTT (bản hợp nhất 2022). Ngoại lệ "phi thương mại, nghiên cứu" trong bài thứ cấp có thể thuộc nhóm sáng chế/kiểu dáng chứ không áp cho nhãn hiệu, nên cần đối chiếu trước khi trích trong báo cáo.
- Chưa tra được tác giả logo Git để ghi công theo CC BY 3.0 (trí nhớ là Jason Long, chưa xác minh từ git-scm.com).
- Chưa có quy định của Khoa/IUH về logo bên thứ ba trong khóa luận.

## Câu hỏi 3. Đường vẽ offline đáng tin nhất bằng Python 3.12 trên Windows 11, không quyền admin, không Cairo

### Takeaway
Đường đề xuất có hai bước:
1. Lấy SVG của Simple Icons theo một phiên bản cố định. Hoặc vendor khoảng 20 tệp SVG cần dùng cùng một manifest
   nguồn gốc, hoặc dùng `simplepycons` 1!16.38.1 (MIT).
2. Vẽ đường `d` trực tiếp thành `PathPatch` của matplotlib bằng `svgpath2mpl` 1.0.0 (BSD, 7 KB, chỉ cần NumPy và
   matplotlib, đã có trong venv).

Cách này không cần thư viện native, kết quả là vector trong cùng hình matplotlib, xuất PNG 600 dpi hoặc SVG.

Muốn ra PNG riêng từng logo, kể cả logo màu chính thức dạng SVG nhiều phần tử, dùng `resvg-py` 0.5.0 (MIT,
wheel `cp310-abi3-win_amd64` đóng sẵn bản Rust, không Cairo).

Tránh `cairosvg` (LGPL, cần DLL cairo qua `cairocffi`). Tránh `svglib` + `reportlab` (LGPL; reportlab 5.1.2 đòi
Pillow ≥13 trong khi venv có Pillow 12.3.0; xuất bitmap cần `rlPyCairo`).

### Cited Findings
- `svgpath2mpl` **1.0.0**, giấy phép BSD, wheel `py2.py3-none-any` 7 KB, phụ thuộc `numpy`, `matplotlib`. Docstring: "Parse SVG path definition strings into matplotlib Path objects", hỗ trợ đủ lệnh `MmZzLlHhVvCcSsQqTtAa`, gồm cung tròn (`A`) đổi sang tham số tâm; hàm công khai `parse_path` — [PyPI svgpath2mpl](https://pypi.org/project/svgpath2mpl/); [GitHub nvictus/svgpath2mpl](https://github.com/nvictus/svgpath2mpl)
- `resvg_py` **0.5.0**:
  - Giấy phép MIT (tệp `LICENSE` trong wheel, © 2024 baseplate-admin), Python ≥3.10, có wheel `resvg_py-0.5.0-cp310-abi3-win_amd64.whl` 1,2 MB chứa `resvg_py.pyd` biên dịch sẵn.
  - Hàm `svg_to_bytes(svg_string=None, svg_path=None, background=None, width=None, height=None, zoom=None, dpi=0.0, ...) -> bytes`, trả PNG.
  - README: "A safe and high level binding for the resvg project".

  Nguồn: [PyPI resvg-py](https://pypi.org/project/resvg-py/); [GitHub baseplate-admin/resvg-py](https://github.com/baseplate-admin/resvg-py)
- `CairoSVG` **2.9.1**: LGPL-3.0-or-later, phụ thuộc `cairocffi`, `cssselect2`, `defusedxml`, `pillow`, `tinycss2` — [PyPI CairoSVG](https://pypi.org/project/CairoSVG/). `cairocffi` nạp thư viện cairo native lúc chạy. Windows không có sẵn thư viện này, đây là lý do cần "system Cairo" (suy từ danh sách phụ thuộc; chưa thử trên máy)
- `svglib` **2.5.0**: LGPL-3.0-or-later, "A pure-Python library for reading and converting SVG", đòi `reportlab>=4.4.3`, `lxml>=6.0.0`; extra `bitmaps` cần `rlpycairo>=0.4.0` — [PyPI svglib](https://pypi.org/project/svglib/)
- `reportlab` **5.1.2**: giấy phép BSD, đòi `pillow>=13.0.0`; extra `pycairo` cần `rlPyCairo`, `freetype-py` — [PyPI reportlab](https://pypi.org/project/reportlab/). Venv của dự án có `pillow 12.3.0` (`pip list`), nên cài svglib sẽ kéo theo nâng cấp Pillow.
- `simplepycons` 1!16.38.1: `raw_svg` giữ SVG gốc 24×24 nhưng **ngắt dòng bên trong thuộc tính `d`**. Trường `guidelines_url` của PyTorch bị cắt mất tên tệp PDF vì ngắt dòng (`.../assets/brand-guidelines/`). `customize_svg(fill=...)` đặt màu, mặc định lấy `primary_color` — đọc `simplepycons/_pytorch.py`, `base_icon.py` trong wheel ([PyPI simplepycons](https://pypi.org/project/simplepycons/))
- Venv dự án đã có `matplotlib 3.11.2`, `numpy 2.5.3`, `pillow 12.3.0`, `lxml 6.1.3`, chưa có `python-docx`. Bản hiện hành của `python-docx` là 1.2.0, MIT, phụ thuộc `lxml>=3.1.0` — `pip list` của `.venv`; [PyPI python-docx](https://pypi.org/project/python-docx/)
- `mingrammer/diagrams` (MIT) vẽ sơ đồ kiến trúc "as code" với bộ biểu tượng nhà cung cấp, kể cả nhóm On-Premises, Programming, Generic, C4. README ghi: "It uses Graphviz to render the diagram, so you need to install Graphviz" — [GitHub mingrammer/diagrams](https://github.com/mingrammer/diagrams)

### Inferences
- **Nguồn SVG nên dùng: vendor tệp, không phụ thuộc gói lúc dựng.** Tải tarball `simple-icons@16.38.1` một lần, chép vào repo (ví dụ `report/logos/`) đúng các SVG cần dùng, cùng một `manifest.yaml` ghi:
  - slug, title, hex, `source`, `guidelines`, `license` (từ `data/simple-icons.json`);
  - phiên bản 16.38.1 và SHA-256 của tarball;
  - tệp `DISCLAIMER.md`.

  Logo màu chính thức (Python, Hugging Face, PostgreSQL nếu được phép) tải từ trang brand, ghi URL và ngày tải. Cách này hợp quy ước "mọi số và hình truy được về artifact" của repo. Nó cũng không vướng lỗi ngắt dòng của simplepycons, và không cần mạng khi dựng.
- **Mẫu mã (chưa chạy thử; chỉ phác cách làm)**. Vẽ biểu tượng đơn sắc vào hình matplotlib:

  ```python
  # report-time only: SVG đã vendor, không mạng
  import re
  from pathlib import Path
  from matplotlib.patches import PathPatch
  from matplotlib.transforms import Affine2D
  from svgpath2mpl import parse_path          # BSD, 1.0.0

  def load_icon_path(svg_file: Path):
      svg = svg_file.read_text(encoding="utf-8")
      d = re.search(r'\sd="([^"]+)"', svg, re.S).group(1)
      return parse_path(" ".join(d.split()))  # gom khoảng trắng/xuống dòng

  def draw_icon(ax, svg_file: Path, x: float, y: float, size: float, color: str):
      """Vẽ biểu tượng 24x24 vào ô vuông (x, y, size) theo toạ độ dữ liệu của ax."""
      path = load_icon_path(svg_file)
      # SVG: gốc trên-trái, trục y đi xuống -> lật y rồi tịnh tiến
      tf = Affine2D().scale(size / 24, -size / 24).translate(x, y + size)
      ax.add_patch(PathPatch(tf.transform_path(path), facecolor=color,
                             edgecolor="none", lw=0))

  # fig.savefig("f_tech_overview.png", dpi=600); fig.savefig("f_tech_overview.svg")
  ```

  Phải kiểm bằng mắt từng logo xem lỗ bên trong (vòng của PyTorch, mắt của Docker) có bị tô kín không. Quy tắc tô (nonzero hay even-odd) của matplotlib với đường phức hợp chưa được xác minh trong ghi chú này.
- **Mẫu mã render PNG từng logo, kể cả SVG màu chính thức** (chưa chạy thử):

  ```python
  import resvg_py                               # MIT, 0.5.0, wheel abi3 win_amd64
  svg = Path("report/logos/python-official.svg").read_text(encoding="utf-8")
  png = resvg_py.svg_to_bytes(svg_string=svg, width=600)   # bytes PNG, nền trong suốt
  Path("report/logos/png/python.png").write_bytes(bytes(png))
  # sau đó: matplotlib OffsetImage/AnnotationBbox, hoặc nhúng thẳng vào DOCX
  ```

- Xếp hạng độ tin cậy trên Windows không quyền admin:
  1. `svgpath2mpl` + matplotlib, thuần Python, đã có matplotlib.
  2. `resvg-py`, wheel biên dịch sẵn, không native ngoài.
  3. `svglib`, vướng xung đột Pillow.
  4. `cairosvg`, cần DLL cairo.

  `mingrammer/diagrams` cần Graphviz, là chương trình cài ngoài, và bộ biểu tượng của nó có bản quyền riêng. Không nên dùng.
- Cài thêm (nếu người dùng duyệt) chỉ cần `svgpath2mpl` cho đường 1. Gói này nhỏ và không kéo phụ thuộc mới. Nên ghi vào một tệp yêu cầu riêng cho báo cáo (ví dụ `requirements-report.txt`), không vào `requirements.txt` của hệ thống.

### Gaps
- Chưa chạy thử mẫu mã nào; ràng buộc là không cài gói vào venv dự án và không chạy mã đã tải. Cần một lượt thử trong venv phụ trước khi dùng.
- Chưa xác minh `resvg_py.svg_to_bytes` trả `bytes` hay `list[int]` ở bản 0.5.0. Stub ghi `bytes`, nên mẫu mã bọc thêm `bytes(...)` cho chắc.
- Chưa kiểm gói `resvg` 0.2.0 (tên khác trên PyPI) là gì. Đừng nhầm với `resvg-py`.

## Câu hỏi 4. Đặt logo vào Word: nhúng SVG kèm PNG dự phòng hay chỉ PNG 300–600 dpi

### Takeaway
Word cho Microsoft 365 trên Windows chèn và sửa được SVG, và có lệnh "Convert to Shape". Trong DOCX, ảnh SVG lưu
thành hai phần: `a:blip` trỏ tới **PNG dự phòng**, phần mở rộng `svgBlip` trỏ tới SVG gốc. LibreOffice từng bỏ qua
SVG và chỉ hiện PNG. Với hình logo khổ nhỏ trong báo cáo xuất PDF qua Word COM, chỉ dùng PNG 600 dpi là đường đơn
giản và chắc nhất; repo đã có sẵn đường chèn PNG. SVG chỉ đáng làm nếu cần vector trong PDF.

### Cited Findings
- Microsoft: Word cho Microsoft 365 chèn và sửa SVG trên Windows, Mac, Android; "You can't insert an SVG image in iOS"; có thể chuột phải → Convert to Shape để tách SVG thành hình sửa được. Trang có nhãn Applies To gồm Word 2024/2021/2019 nhưng không nói rõ các bản đó chèn được SVG. Trang không nói gì về PDF hay bản Word cũ — [Microsoft Support: Edit SVG images in Microsoft 365](https://support.microsoft.com/en-us/office/edit-svg-images-in-microsoft-365-69f29d39-194a-4072-8c35-dbe5e7ea528c)
- Cấu trúc DOCX: `a:blip` chính trỏ tới PNG, phần mở rộng `svgBlip` trỏ tới SVG. Theo Aspose, Word luôn ghi kèm PNG dự phòng cho SVG. Đặc tả Microsoft mô tả `svgBlip` ở mục 2.26.1.1 — [Aspose forum: SVG translated as PNG](https://forum.aspose.com/t/svg-translated-as-png/278893); [Microsoft Learn (MS-ODRAWXML, Pictures)](https://msdn.microsoft.com/en-us/library/7e1f1524-1569-4aa2-a6c9-aab2d855bd48)
- LibreOffice (báo lỗi 2019) bỏ qua `svgBlip` và hiện PNG dự phòng — [LibreOffice bugs list, 06/2019](https://lists.freedesktop.org/archives/libreoffice-bugs/2019-June/199646.html)
- Repo: `scripts/report_docx/package.py` đã gom ảnh có `r:embed`, đổi `rId`, thêm quan hệ `.../relationships/image` và `Default Extension="png"`. Tức là đường **PNG** đã có sẵn. `scripts/report_docx/diagram.py` (184 dòng) hiện chỉ sinh `wps:wsp` (hộp, đường nối) trong canvas `wpc:wpc`, chưa có ảnh. Bản PDF chính thức xuất bằng Word COM (`ExportAsFixedFormat` trong `scripts/update_docx_fields.ps1`) — đọc trực tiếp các tệp trong repo

### Inferences
- Logo rộng khoảng 1 cm ở 600 dpi chỉ cần khoảng 236 px. PNG 600 dpi cho logo đơn sắc nhỏ là dư độ nét khi in, tệp vẫn nhẹ. Ngưỡng 300 dpi đủ cho hình matplotlib hiện có. Nên dùng 600 dpi cho hình nhiều chữ nhỏ và logo.
- Ba cách đặt vào báo cáo, xếp theo độ hợp với repo:
  - **(a)** Cả hình là một PNG matplotlib 600 dpi, chèn như các hình `build_final_figures.py`. Đơn giản nhất; không sửa được trong Word.
  - **(b)** Giữ sơ đồ DrawingML sửa được (`diagram.py`) và thêm logo dưới dạng hình chữ nhật tô ảnh: `<a:blipFill><a:blip r:embed="rIdN"/><a:stretch><a:fillRect/></a:stretch></a:blipFill>` trong `wps:spPr`. Cần thêm quan hệ ảnh vào package, việc mà `package.py` đã làm cho ảnh Pandoc. Sơ đồ vẫn kéo thả được trong Word, đúng tinh thần "sơ đồ sửa được" của bản gọn.
  - **(c)** Bảng Word có cột logo, ảnh PNG nhỏ nằm trong ô. Bảng vẫn là chữ thật, tìm kiếm được.
- Không nên nhúng SVG bằng `svgBlip` tự viết, trừ khi đã thử: GUID phần mở rộng và namespace `asvg` phải đúng đặc tả, nếu không Word có thể báo tệp hỏng. Repo đã gặp một lần Word không mở được DOCX vì XML sai (nhật ký 25/11).

### Gaps
- Chưa xác minh Word COM `ExportAsFixedFormat` giữ SVG ở dạng vector trong PDF hay rasterize.
- Chưa đọc trực tiếp mục 2.26.1.1 MS-ODRAWXML: chưa có GUID chính xác của `svgBlip` và câu nói PNG dự phòng là bắt buộc hay tùy chọn. Một nguồn thứ ba nói "tùy chọn trong Word hiện đại" nhưng chưa xác minh.
- Chưa kiểm Pandoc docx writer xử lý ảnh SVG thế nào (có sinh PNG dự phòng không, cần `rsvg-convert` không).

## Câu hỏi 5. Hai đến ba mẫu bố cục cho hình tổng quan công nghệ

### Takeaway
Ba mẫu, mỗi mẫu trả lời một câu hỏi khác:
1. **Kiến trúc phân tầng có logo theo tầng**: hệ thống gồm những gì.
2. **Luồng yêu cầu dạng làn, logo trên mỗi tác nhân**: các phần nói chuyện với nhau ra sao.
3. **Hình bảng vai trò (logo | tên | phiên bản | vai trò)**: mỗi công nghệ làm gì.

Cả ba nên sinh từ cùng một nguồn dữ liệu với bảng `f15_tech_stack.md`, để hình và bảng không lệch nhau.

### Cited Findings
- Bảng `f15_tech_stack.md` đã có sẵn cột Tầng (Hạ tầng, Học máy, Đánh giá, Mô hình ngôn ngữ, Truy hồi, Lưu trữ, Dịch vụ, Giao diện), Phiên bản đọc từ tệp cấu hình, Vai trò và ADR. Bảng được sinh tự động bởi `scripts.report_system_tables` tại git `0e8680f` — `report/final_tables/f15_tech_stack.md` trong repo
- Chương 5 bản gọn đã mô tả kiến trúc: giao diện gọi API qua HTTP; API là điểm điều phối duy nhất, gọi dịch vụ suy luận, gọi llama.cpp để phân tích câu hỏi, đọc ghi kho sự kiện. Quy trình nghiên cứu không chạy lúc phục vụ, chỉ cung cấp checkpoint và tham số đã khóa. Luồng hỏi đáp gồm: llama.cpp + lược đồ JSON → thẻ bộ lọc → BGE-M3 nhúng câu hỏi → một câu SQL vừa lọc vừa xếp hạng cosine — `report/gon_src/05_trien_khai.md` dòng 48, 70 trong repo
- Ví dụ công cụ vẽ sơ đồ kiến trúc bằng biểu tượng nhà cung cấp (on-prem, programming, generic, C4): `mingrammer/diagrams` — [GitHub mingrammer/diagrams](https://github.com/mingrammer/diagrams)
- Shields.io dùng Simple Icons cho huy hiệu dạng "logo + chữ". Đây là kiểu nhãn chữ có màu thương hiệu dễ nhận ra, và thay đổi hay gỡ biểu tượng do dự án Simple Icons quyết định — [shields.io blog: simple icons 13](https://shields.io/blog/simple-icons-13)

### Inferences
- **Mẫu 1, kiến trúc phân tầng** (đề xuất làm hình chính ở mục "Công nghệ sử dụng"):
  - Bố cục: các dải ngang từ dưới lên: Hạ tầng (Docker) → Dữ liệu và huấn luyện, nghiên cứu (PyTorch, librosa, NumPy, scikit-learn, sed_eval/psds_eval) → Phục vụ mô hình (dịch vụ suy luận: PyTorch + Frame-MobileNet B0 + LBR; BGE-M3 qua sentence-transformers; llama.cpp + Qwen3.5-9B) → Dịch vụ API (FastAPI, Uvicorn, Pydantic, httpx) → Lưu trữ (PostgreSQL 16 + pgvector, psycopg) → Giao diện (React, TypeScript, Vite, TanStack Query).
  - Tầng nghiên cứu nối vào tầng phục vụ bằng mũi tên **đứt nét** ghi "checkpoint + tham số đã khóa", khớp câu ở Chương 5.
  - Mỗi chip: logo 0,8–1 cm, tên, phiên bản lấy từ cùng dữ liệu với f15.
  - Công nghệ không có logo dùng chip chữ cùng kích thước, viền xám, để hình không lộ ra hai cấp đối xử.
- **Mẫu 2, luồng yêu cầu dạng làn**:
  - Năm làn: Trình duyệt (React) | API (FastAPI) | Suy luận (PyTorch, BGE-M3) | llama.cpp (Qwen) | PostgreSQL + pgvector. Logo ở đầu mỗi làn.
  - Mũi tên đánh số cho hai luồng: tải lên (tệp → kiểm tra → SED → mô tả → nhúng → ghi kho) và hỏi đáp (câu hỏi → llama.cpp → thẻ → nhúng → SQL lọc + cosine → trích dẫn).
  - Có thể làm hai hình nhỏ, hoặc một hình với hai màu mũi tên.
  - Mẫu này trùng vai với các hình `fig:uploadflow` và `fig:queryflow` đã có. Nếu làm thì nên **thêm logo lên đầu làn của hình đã có** (cách (b) ở câu 4), không vẽ hình mới.
- **Mẫu 3, hình bảng vai trò**: lưới 3–4 cột thẻ, mỗi thẻ gồm logo, tên + phiên bản, một dòng vai trò ("Kho sự kiện: lọc, điều kiện thời gian, xếp hạng vector trong một câu SQL"). Cách khác rẻ hơn là thêm cột logo vào bảng f15 (cách (c) ở câu 4). Bảng là chữ thật, hội đồng đọc được, và không thêm hình thứ hai trùng nội dung với bảng.
- Quy tắc chung cho cả ba mẫu:
  - Logo không thay chữ: luôn ghi tên dưới logo, vì bản in đen trắng làm mất màu thương hiệu.
  - Logo màu nhạt (React, Hugging Face, Vitest, TanStack, Ruff, scikit-learn, SciPy) đặt trên ô nền tối, hoặc dùng bản màu chính thức có viền.
  - Khoảng trống quanh logo ít nhất 0,5 lần chiều cao, theo yêu cầu của Docker.
  - Không xoay, không bóng, không viền logo.
  - Một mục chú thích nguồn dưới hình, theo mẫu `@@NOTE:` của repo.

### Gaps
- Không tìm được ví dụ cụ thể từ khóa luận hoặc bài báo đã công bố dùng hình "tech stack có logo". Phần lớn ví dụ kiểu này nằm trong blog kỹ thuật và README; chưa có nguồn học thuật để trích làm tiền lệ.
- Chưa tra quy định của Khoa về hình có logo thương mại trong khóa luận.

## Câu hỏi 6. Ghi chú nhãn hiệu và ghi công logo trong khóa luận

### Takeaway
Dùng **một** chú thích chung (chú thích dưới hình hoặc một dòng ở trang viết tắt hay lời nói đầu). Chú thích nêu
ba ý: logo là nhãn hiệu của chủ sở hữu, việc dùng chỉ nhằm nhận diện, không hàm ý liên kết. Kèm ghi công giấy phép
cho các logo có giấy phép riêng (Git CC BY 3.0, Pandoc CC BY-SA 4.0, React CC BY 4.0), và câu riêng mà PostgreSQL
và Microsoft yêu cầu, nếu dùng các thương hiệu đó.

### Cited Findings
- Microsoft gợi ý: "Microsoft, (list additional trademarks in alphabetical order) are trademarks of the Microsoft group of companies." — [Microsoft Trademark and Brand Guidelines](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks)
- PostgreSQL yêu cầu "wherever possible": "Postgres, PostgreSQL and the Slonik Logo are trademarks or registered trademarks of the PostgreSQL Community Association of Canada, and used with their permission." — [PostgreSQL Trademark Policy](https://www.postgresql.org/about/policies/trademarks/)
- PSF gợi ý (tùy chọn với bài viết): "'Python' and the Python logos are trademarks or registered trademarks of the Python Software Foundation, used by ___ with permission from the Foundation"; bài báo học thuật không cần ® — [PSF Trademark Usage Policy](https://www.python.org/psf/trademarks/)
- Linux Foundation: ghi chú nhãn hiệu ở lần xuất hiện đầu hoặc nổi bật nhất; ® sau lần dùng đầu với nhãn đã đăng ký — [LF Trademark Usage](https://www.linuxfoundation.org/legal/trademark-usage)
- Giấy phép riêng cần ghi công: Git `CC-BY-3.0`, Pandoc `CC-BY-SA-4.0` (dữ liệu Simple Icons 16.38.1); React CC BY 4.0 (maintainer, 2018) — [simple-icons-16.38.1.tgz](https://registry.npmjs.org/simple-icons/-/simple-icons-16.38.1.tgz); [facebook/react#12570](https://github.com/facebook/react/issues/12570)

### Inferences
- Câu đề xuất, đặt dưới hình hoặc ở trang "Danh mục viết tắt":
  > *Các tên và logo sản phẩm trong hình là nhãn hiệu hoặc nhãn hiệu đã đăng ký của chủ sở hữu tương ứng; nhóm dùng chúng chỉ để nhận diện công nghệ mà hệ thống sử dụng, không hàm ý liên kết hay được các chủ sở hữu xác nhận. Biểu tượng đơn sắc lấy từ Simple Icons 16.38.1 (CC0 1.0); logo React theo CC BY 4.0; logo Git theo CC BY 3.0. Python và logo Python là nhãn hiệu của Python Software Foundation. Microsoft Word là nhãn hiệu của tập đoàn Microsoft.*
- Ghi chú PostgreSQL có cụm "used with their permission". Nếu không xin phép mà vẫn vẽ Slonik, câu này sẽ sai sự thật. Đây thêm một lý do để chỉ ghi chữ "PostgreSQL" mà không vẽ Slonik. Khi đó chỉ cần ghi "PostgreSQL là nhãn hiệu của PostgreSQL Community Association of Canada".
- Câu gợi ý của PSF cũng có "with permission". Với khóa luận không xin phép, bỏ phần đó, giữ phần nêu chủ sở hữu.
- Nên ghi phiên bản Simple Icons và ngày tải vào manifest logo (câu 3). Thương hiệu có thể đổi hoặc bị gỡ giữa các bản, giống nhóm Microsoft ở 13.0.0.

### Gaps
- Chưa có quy định mẫu của IUH hay Khoa về câu ghi chú nhãn hiệu trong khóa luận.
- Chưa xác minh tên tác giả cần ghi cho logo Git theo CC BY 3.0.
