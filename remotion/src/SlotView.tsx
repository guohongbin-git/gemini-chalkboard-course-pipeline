import React from "react";
import { Img, interpolate, useCurrentFrame } from "remotion";
import { Role, Slot } from "./types";

/**
 * 槽位底板颜色：与 METHODOLOGY §8.1 的验收判据一致（米色 #E8E0CB 区间）。
 * 板面图留的空白框应当与此色接近，渲染时不必再画底，直接写字。
 */
const ROLE_STYLE: Record<Role, React.CSSProperties> = {
  title: { fontSize: 72, fontWeight: 800, color: "#1A1A1A", fontFamily: '"Hiragino Sans GB", "PingFang SC", sans-serif' },
  subtitle: { fontSize: 40, fontWeight: 500, color: "#3A3A3A" },
  tag: { fontSize: 28, fontWeight: 700, color: "#5A3A1E" },
  layertitle: { fontSize: 44, fontWeight: 800, color: "#1A1A1A" },
  layertext: { fontSize: 34, fontWeight: 500, color: "#2E2E2E" },
  celltitle: { fontSize: 40, fontWeight: 800, color: "#1A1A1A" },
  celltext: { fontSize: 30, fontWeight: 500, color: "#2E2E2E", whiteSpace: "pre-line" },
  databar: { fontSize: 34, fontWeight: 600, color: "#2A2A2A" },
  plaque_text: { fontSize: 56, fontWeight: 800, color: "#7A1F1A" },
  plaque_note: { fontSize: 24, fontWeight: 500, color: "#6A4038" },
  inner_note: { fontSize: 26, fontWeight: 600, color: "#3A3A3A" },
  outer_note: { fontSize: 22, fontWeight: 500, color: "#5A5A5A" },
  year: { fontSize: 44, fontWeight: 800, color: "#1A1A1A" },
  body: { fontSize: 30, fontWeight: 500, color: "#2E2E2E", whiteSpace: "pre-line" },
};

const IN_FRAMES = 12;

export const SlotView: React.FC<{ slot: Slot }> = ({ slot }) => {
  const frame = useCurrentFrame();
  const start = slot.anchor ?? 0;
  const local = frame - start;

  // 槽位在 anchor 之前完全不渲染 —— 与 E9「末项按 anchor 铺满」的口径一致。
  if (local < 0) return null;

  const base = ROLE_STYLE[slot.role];
  const progress = interpolate(Math.min(local, IN_FRAMES), [0, IN_FRAMES], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const style: React.CSSProperties = {
    position: "absolute",
    left: slot.x,
    top: slot.y,
    width: slot.w,
    height: slot.h,
    display: "flex",
    flexDirection: slot.vertical ? "row" : "column",
    alignItems: slot.align === "center" ? "center" : slot.align === "right" ? "flex-end" : "flex-start",
    justifyContent: "center",
    opacity: progress,
    transform: `translateY(${(1 - progress) * 10}px)`,
    overflow: "hidden",
    ...base,
    fontSize: slot.fontSize ?? base.fontSize,
    color: slot.color ?? base.color,
    textAlign: slot.align ?? (slot.vertical ? "center" : "left"),
    lineHeight: 1.35,
    // 留白卡：程序画的底。颜色刻意落在 qa_slots.py card_mask 的米色区间内，
    // 这样「槽位有底板」的验收判据对 CSS 卡同样成立。
    ...(slot.backing
      ? {
          background: "#EFE9D8",
          borderRadius: 16,
          padding: "10px 26px",
          boxShadow: "0 2px 10px rgba(43,76,126,0.10)",
          border: "1px solid #D8CFB8",
        }
      : {}),
  };

  // 竖排：逐字成列，从右往左（印章式）。
  if (slot.vertical) {
    return (
      <div style={style}>
        {(slot.text ?? "").split("").map((ch, i) => (
          <span key={i} style={{ writingMode: "vertical-rl", lineHeight: 1.05 }}>
            {ch}
          </span>
        ))}
      </div>
    );
  }

  return <div style={style}>{slot.text ?? ""}</div>;
};

/** 字幕条：固定 bottom:8，横跨全宽，占 y≈988–1072（slotcheck 第三层据此检测冲突）。 */
export const Caption: React.FC<{ text?: string }> = ({ text }) => {
  if (!text) return null;
  const frame = useCurrentFrame();
  return (
    <div
      style={{
        position: "absolute",
        left: 0,
        right: 0,
        bottom: 8,
        padding: "14px 40px",
        textAlign: "center",
        fontFamily: '"Hiragino Sans GB", "PingFang SC", sans-serif',
        fontSize: 40,
        lineHeight: 1.4,
        color: "#F2EDE0",
        textShadow: "0 2px 6px rgba(0,0,0,0.9)",
        opacity: interpolate(frame, [0, 10], [0, 1], { extrapolateRight: "clamp" }),
      }}
    >
      {text}
    </div>
  );
};

/**
 * 板面图铺底并等比映射到 1920×1080。
 * 板面 1672×941 与 1920×1080 比例不同，故用 contain 居中，槽位坐标需与之一致。
 */
export const Board: React.FC<{ src: string; width: number; height: number }> = ({
  src,
  width,
  height,
}) => (
  <Img
    src={src}
    style={{
      position: "absolute",
      inset: 0,
      width,
      height,
      objectFit: "fill",
    }}
  />
);
