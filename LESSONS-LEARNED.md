# 关键教训（实测踩坑，勿重蹈）

## Gemini 自动化（CDP / browser relay）

- **tab 必须 bringToFront**：后台 tab 的合成鼠标点击会被页面忽略
- **只保留一个工作 tab**：草稿跨 tab 不同步，双 tab 必丢内容
- **`tab.run` 不能传 args、不能捕获闭包**：prompt 走 `/tmp` 文件中转（`Bun.write` → 页面内 `Bun.file` 读回）
- **`正在创建您的图片` 文本会残留**：完成判定以 blob 图数量/尺寸为准，文本只做参考
- **导出防重**：md5 对比上一张，连续 duplicate 说明新图未到，等待后重试
- 发送按钮在生成期间会变成「停止」，找不到「发送」时回退找任何可见的提交箭头

## TTS（Qwen3-TTS / mlx_audio）

- 单段超过 40 秒易失控（音调漂移、复读）——8~40s 是安全区，超限删段重跑
- 换参考文本必须显式传 `TTS_REF_TEXT` 环境变量：脚本内置默认值优先级高于 voices 目录里的 ref_10s.txt
- 音色参考用真人原声最稳；合成音色做旁白失控率高
- 每段合成后立即 ffprobe 时长，<8s 或 >40s 直接重跑

## Remotion / 装配

- 板图统一 `scale=1672:941:force_original_aspect_ratio=increase,crop=1672:941` 归一化，槽位坐标系才不会漂
- 槽位几何一旦验证（红框对位）就锁死，不要每讲微调
- 成片验收三件套：ffprobe 时长、silencedetect 无断轨、抽帧看 stages 渐显
- Remotion series tsx 由 `build_from_pack.py` 生成，不要手编

## 剧本

- 每讲固定 8 场：开场钩子 / 承接提问 / 概念×3（末场带 7s 停顿）/ 陷阱 / 动手例子 / 预告收尾
- 旁白总长 500–650 字 ≈ 2.5 分钟成片
- 网络搜证 1–2 次即可：一个钩子事实 + 一条硬核出处，写进 pack.json 的 research_notes
- 「主体」隐喻和台词必须互相呼应（图里钥匙=台词换钥匙）
