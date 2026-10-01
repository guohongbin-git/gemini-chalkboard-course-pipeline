/**
 * 槽位与时间轴的数据契约。
 *
 * 板面图里零汉字：图只画「景」和「框」，字全部由这里的 slot 填。
 * 坐标一律 1920×1080 基准，与 board 1672×941 等比缩放后由 <Board> 统一映射。
 */

export type Role =
  | "title"
  | "subtitle"
  | "tag"
  | "layertitle"
  | "layertext"
  | "celltitle"
  | "celltext"
  | "databar"
  | "plaque_text"
  | "plaque_note"
  | "inner_note"
  | "outer_note"
  | "year"
  | "body";

export type Slot = {
  id: string;
  x: number;
  y: number;
  w: number;
  h: number;
  role: Role;
  usage: string;
  /** 逐字文本（渲染进槽位的内容）。有 anchor 时按帧铺开进场。 */
  text?: string;
  /** 进场锚点：页内帧号。缺省表示与页同帧出现。 */
  anchor?: number;
  /** 竖排（印章式）。E8 大钟桥 / E9 P8 用过。 */
  vertical?: boolean;
  /** tag 型槽位无底板，不计入槽位完整性统计。 */
  noBacking?: boolean;
  /** 由 Remotion 画留白卡底（米白圆角矩形），板面图只管场景。cs106a 系列起用。 */
  backing?: boolean;
  /** 覆盖默认字号。 */
  fontSize?: number;
  color?: string;
  align?: "left" | "center" | "right";
};

export type Page = {
  id: string;
  /** 板面图相对 public/ 的路径，例如 "boards/page_01.png" */
  board: string;
  /** 旁白音频相对 public/ 的路径，例如 "audio/dazhongsi/p01.wav" */
  audio: string;
  /** 字幕（口播全文） */
  caption?: string;
  /** 本页槽位 */
  slots: Slot[];
  /** 纯音频秒数（由 gen_audio_timing.py 从实测时长写入） */
  audioSeconds?: number;
  /** 含留白的整页秒数 = audioSeconds + gap */
  pageSeconds?: number;
};

export type Timeline = {
  fps: number;
  width: number;
  height: number;
  /** 每页尾部留白秒数 */
  pageGap: number;
  pages: Page[];
};
