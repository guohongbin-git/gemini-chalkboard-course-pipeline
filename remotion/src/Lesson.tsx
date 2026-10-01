import React from "react";
import { AbsoluteFill, Audio, Sequence, staticFile, useVideoConfig } from "remotion";
import { Board, Caption, SlotView } from "./SlotView";
import { Timeline } from "./types";

export type LessonProps = {
  timeline: Timeline;
  /** 仅在探针片里替换成占位图；正式渲染留空。 */
  placeholderBoard?: boolean;
};

/**
 * 页长权威口径：PAGE_DURATIONS_SEC 累加（音频秒 + pageGap 留白）。
 *
 * 不要改用 audioSeconds 直接累加——那是「纯音频」，两者每页差 pageGap 秒。
 * METHODOLOGY §7 记录的 E9 教训：照 _meta.json 的 bounds 抽帧会渲到前一页尾巴。
 */
export const pageDurationsSec = (timeline: Timeline): number[] =>
  timeline.pages.map((p) => {
    const audio = p.audioSeconds ?? p.pageSeconds ?? 0;
    return audio + timeline.pageGap;
  });

export const totalFrames = (timeline: Timeline, fps: number): number =>
  Math.round(pageDurationsSec(timeline).reduce((a, b) => a + b, 0) * fps);

const Page: React.FC<{ timeline: Timeline; index: number; placeholderBoard?: boolean }> = ({
  timeline,
  index,
  placeholderBoard,
}) => {
  const page = timeline.pages[index];

  return (
    <AbsoluteFill style={{ backgroundColor: "#FFFFFF" }}>
      {placeholderBoard ? (
        // 探针片：纯白底。白底让「该有字却没字」一眼可见（METHODOLOGY §8.2）。
        <AbsoluteFill style={{ backgroundColor: "#FFFFFF" }} />
      ) : (
        <Board
          src={staticFile(page.board)}
          width={timeline.width}
          height={timeline.height}
        />
      )}
      {page.slots.map((slot) => (
        <SlotView key={slot.id} slot={slot} />
      ))}
      <Caption text={page.caption} />
      <Audio src={staticFile(page.audio)} />
    </AbsoluteFill>
  );
};

export const Lesson: React.FC<LessonProps> = ({ timeline, placeholderBoard }) => {
  const { fps } = useVideoConfig();
  let from = 0;

  return (
    <AbsoluteFill style={{ backgroundColor: "#FFFFFF" }}>
      {timeline.pages.map((page, i) => {
        const dur = Math.round(pageDurationsSec(timeline)[i] * fps);
        const start = from;
        from += dur;
        return (
          <Sequence key={page.id} from={start} durationInFrames={dur} name={page.id}>
            <Page timeline={timeline} index={i} placeholderBoard={placeholderBoard} />
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};
