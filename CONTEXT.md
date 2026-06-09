# 一命千途领域上下文

## 核心领域词

- **命盘**：由出生信息生成的人生底色，包括八字、五行、十神、大运、流年、流月和命盘分析字段。
- **前传**：正式模拟开始前，根据命盘和开始年龄生成的早年经历、性格底色、初始人生状态和人生愿望。
- **人生模拟**：玩家进入正式人生后，以半年为一个回合推进状态、叙事和结局。
- **半年度选择**：人生模拟阶段的一次玩家决策。系统会把自由输入或行动按钮归一为 1 到 3 个行动重点，并用 D100、阶段事件、连续投入、愿望进度、长期系统和状态变化生成权威结果。
- **权威半年度记录**：半年度选择的确定性结果记录。它包含行动重点、D100 判定、状态变化、阶段事件、连续选择反馈、选择前后状态、流年/流月上下文等。AI 可以补充叙事，但不能改写其中的权威状态变化。
- **人生愿望**：玩家在前传阶段选择或默认获得的长期目标，用来评价行动同频度、目标进度和结局反馈。
- **结局图鉴**：同一访客多周目之间保留的结局收集状态。
- **状态发布**：把已经持久化或正在展示的权威 session 快照发送给当前玩家和观众的实时通知过程；它不是持久化本身。
- **AI enrichment Adapter**：围绕命盘分析、前传、半年度叙事和半年度总结的可选装饰层；它接收权威 artifact，返回可展示叙事或分析字段，不拥有 D100、状态变化或终局判定。
- **Life Session Model**：负责创建、补齐和归一化 session dict 的领域 Module；它维护 phase、history、ending codex、focus memory、行动选项和兼容默认值等 session invariants。
- **Ending Resolution Module**：把 session 与 finish reason 解析为权威 ending artifact，并同步生成结局图鉴 delta；它集中隐藏结局、终局标题、收束原因和结局档案摘要规则。
- **Action Guide Module**：把当前 session 解析为半年度选择的 decision-support artifact；它只提供行动预览、愿望同频、预计 D100 目标和连续投入预判，不推进权威半年度记录。
- **Life Context Projection Module**：把权威 session 状态投影为前端和 AI enrichment 可消费的当前人生上下文；它组合大运/流年/流月、人生愿望、长期系统、关系、连续选择和 Action Guide，但不推进 D100 或权威半年度记录。
- **Game Command Router Module**：把前端、测试和兼容旧字符串输入发来的玩家命令归一并分发到命盘、前传、人生愿望、半年度选择、回望人生和 reset 处理逻辑；同步与异步流程共享同一个命令 Interface。
- **State Projection Module**：把权威 session dict 投影为玩家端、直播端和未来导出端可消费的公开 state；它是前后端状态 shape 的运行时 seam，不让 internal_history 或调试字段泄漏到浏览器。
- **Storage Runtime Adapter**：为 durable persistence 提供显式数据根、session 索引和缓存运行时；测试使用临时 Adapter，而不是改写持久化 Module 的私有全局状态。
- **Secret Store Adapter**：负责把玩家自定义 AI API Key 从运行时明文转换为持久化密文，并在调用 OpenAI 兼容接口前临时 reveal；UI 只能得到 mask。
- **Life Stage Policy Module**：集中年龄阶段、阶段行动选项和未成年人安全行动降级规则。
- **Life Goal Progress Module**：集中人生愿望模板、默认愿望选择、愿望分数和达成度刷新规则。
- **Life Systems Module**：集中长期系统、关系网络和每次半年度记录后的系统趋势刷新。
- **phase-owned View Module**：前端每个 phase 的 label、可见面板、主要行动可用性和行为检查锚点；它让 `life_simulation` 明确独占模拟主内容，避免命盘/前传面板回流。
- **domain View Module**：前端按命盘、前传、人生模拟、结局图鉴、AI API 设置和人生档案导出划分的 View Module；`index.js` 只组合这些 Module，不拥有具体渲染 Implementation。
- **Frontend Runtime Module**：前端应用状态、DOM 索引、HTTP 请求、WebSocket/JSON Patch、modal focus trap 和布局控制的组合 Module；`index.js` 只做 wiring，不拥有这些运行时 Implementation。

## 架构约定

- 半年度选择的确定性推进应集中在半年度 resolution Module 中；WebSocket、持久化、AI 叙事和前端渲染不应重新实现 D100 或状态推进规则。
- AI enrichment 只能装饰命盘、前传、半年度记录或结局档案；权威状态变化来自后端确定性规则；prompt、JSON 提取和 OpenAI 调用集中在 AI enrichment Adapter。
- `state_manager.save_session()` 只负责 durable persistence；需要通知前端或直播观众时，通过状态发布 Module 显式 commit/publish。
- session 构造与兼容默认值集中在 Life Session Model；其它 Module 不应散落重建 phase 字段、结局图鉴 shape 或行动记忆 shape。
- 终局判定、隐藏结局和结局图鉴 delta 集中在 Ending Resolution Module；Life Session Model 只保留结局图鉴 catalog 和 session shape。
- 半年度选择建议集中在 Action Guide Module；半年度 resolution Module 只拥有权威 D100、状态推进、行动记忆提交和权威半年度记录补全。
- 当前人生上下文投影集中在 Life Context Projection Module；半年度 resolution Module 不应 import Action Guide Module 或生成展示用 action_guides。
- 玩家命令分发集中在 Game Command Router Module；`apply_player_action()` 与 `apply_player_action_async()` 只穿过同一个 command Interface。
- 玩家端与直播端 state shape 集中在 State Projection Module；发布和 `/game/init` 不直接返回权威 session dict。
- 持久化路径、session 索引、缓存状态、per-player lock、index lock 和 atomic replace 写入集中在 Storage Runtime Adapter；测试通过显式 runtime seam 替换存储根。
- 自定义 AI API Key 持久化必须通过 Secret Store Adapter；profile 文件不保存明文 `api_key`。
- 年龄阶段、人生愿望、长期系统等半年度选择内部政策分别集中在对应 Life Stage Policy / Life Goal Progress / Life Systems Module；半年度 resolution Module 保留权威半年度记录 Interface。
- 前端 phase visibility 集中在 phase-owned View Module；新增 UI 布局规则时优先补行为式 smoke，再补静态断言。
- 具体前端渲染集中在 domain View Module；`frontend/index.css` 作为 style Module manifest，实际样式按 domain 写入 `frontend/styles/`。
- 前端运行时集中在 Frontend Runtime Module；`frontend/index.js` 不拥有 fetch client、JSON Patch、WebSocket reconnect、modal focus trap 或状态/DOM 定义。
