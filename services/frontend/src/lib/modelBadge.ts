import type { Language, ModelsStatus } from "../api/types";

export interface ModelBadge {
  text: string;
  /** true khi hệ đang phục vụ KHÔNG phải số chính thức đã khóa (cấu hình demo/ứng dụng). */
  demo: boolean;
}

const OPERATING_POINT = {
  recall_first: { vi: "điểm ưu tiên phát hiện", en: "detection-first point" },
  f1: { vi: "điểm F1", en: "F1 point" },
} as const;

function basename(path: string): string {
  return path.split("/").filter(Boolean).pop() ?? path;
}

/** Tên biến thể LBR đọc từ tên run (vd. sed_lbr_B0v3_… → V3); run không gắn nhãn là V2. */
function lbrVariant(lbrRun: string): string {
  const match = /v(\d+)_/i.exec(basename(lbrRun));
  return `V${match ? match[1] : "2"}`;
}

/** Tên hệ SED đọc từ tên run đang phục vụ, không ghi cứng. */
function systemName(servedRun: string): string {
  const name = basename(servedRun);
  if (/B0/.test(name)) return "B0";
  if (/ensemble_t2b/.test(name)) return "f2";
  return name;
}

/** Nhãn mô hình trên thanh trạng thái, tính từ `/models/status` thay vì chuỗi ghi cứng. */
export function describeModel(status: ModelsStatus, language: Language): ModelBadge {
  const vi = language === "vi";
  const lbrRun = typeof status.lbr_run === "string" ? status.lbr_run : null;
  if (lbrRun) {
    const point = OPERATING_POINT[status.operating_point as keyof typeof OPERATING_POINT];
    const pointText = point ? point[language] : String(status.operating_point ?? "");
    const label = `LBR ${lbrVariant(lbrRun)} · ${pointText}`;
    return {
      text: vi
        ? `${label} — cấu hình ứng dụng, không phải số chính`
        : `${label} — application configuration, not the headline result`,
      demo: true,
    };
  }
  const name = systemName(status.served_run);
  if (status.official) {
    return {
      text: vi ? `SED ${name} — hệ thống chính thức` : `SED ${name} — official system`,
      demo: false,
    };
  }
  return {
    text: vi ? `SED ${name} — cấu hình demo, chưa phải hệ thống chính thức`
             : `SED ${name} — demo configuration, not the official system`,
    demo: true,
  };
}
