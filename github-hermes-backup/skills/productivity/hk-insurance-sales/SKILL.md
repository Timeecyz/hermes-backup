---
name: hk-insurance-sales
description: "Hong Kong insurance sales: plan parsing, scenario modeling, client pitch writing, CRS/FATCA tax objection handling for high-net-worth mainland Chinese clients."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [hk-insurance, sales-script, client-pitch, crs, fatca, estate-tax]
    homepage: internal
---

# HK Insurance Sales Workflow

Complete workflow for advising mainland Chinese HNW clients on Hong Kong savings/whole-life insurance products.

## Trigger Conditions

- User asks to analyze a HK insurance plan (any Excel/PDF from a HK insurer)
- User asks to write a sales pitch, client script, or objection-handling guide
- User mentions: CRS, FATCA, US tax居民, 遗产税, 赠与税, 资金出境, 香港保险
- User provides a client profile (name, age, nationality of children, investment profile, budget)

## Workflow Overview

```
1. Parse plan data (Excel or PDF)
2. Build withdrawal/scenario model
3. Write client-specific sales language
4. Cover tax objections (CRS 2.0 / FATCA / US estate tax)
5. Recommend product structure (beneficiary, trust, policy ownership)
6. Output: sales script + optional infographic/PPT
```

## Step 1: Parse HK Insurance Plan

### Excel files (.xlsx) — No openpyxl needed

HK insurer plan Excel files are ZIP archives. Parse with `zipfile + xml.etree.ElementTree`:

```python
import zipfile, xml.etree.ElementTree as ET

path = 'plan.xlsx'
with zipfile.ZipFile(path) as z:
    # Shared strings (all text values)
    ss_xml = z.read('xl/sharedStrings.xml').decode('utf-8')
    # Sheet data
    sheet_xml = z.read('xl/worksheets/sheet1.xml').decode('utf-8')
    # Workbook (sheet names)
    wb_xml = z.read('xl/workbook.xml').decode('utf-8')

# Parse shared strings
root = ET.fromstring(ss_xml)
ns = {'ns': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
strings = []
for si in root.findall('ns:si', ns):
    texts = si.findall('.//ns:t', ns)
    val = ''.join(t.text or '' for t in texts)
    strings.append(val)
```

Key shared string indices for most HK insurer plans:
- [0] = product name
- [1-5] = insured info (gender, age, policy duration, payment term, annual premium)
- [8] = short summary string (e.g. "IRR 6.57%")
- [10-18] = column headers (Year, Annual Premium, Cumulative Premium, Guaranteed Surrender, Reversion Bonus, Final Bonus, Expected Surrender Value, Growth Rate)
- Numeric rows follow, with index references into `strings`

### PDF files

Use `ocr-and-documents` skill or `marker-pdf` to extract text, then manually map columns.

### Expected data structure per year

| Field | Description |
|-------|-------------|
| Year | 保单年度 |
| Annual Premium | 当年保费 |
| Cumulative Premium | 累计保费 |
| Discounted Annual Premium | 优惠后当年保费 |
| Discounted Cumulative | 优惠后累计保费 |
| Guaranteed Surrender Value | 保证退保价值 |
| Surrender Reversion Bonus | 退保复归红利 |
| Surrender Final Bonus | 退保终期红利 |
| Expected Surrender Value | 预期退保价值 |
| Expected Growth Rate | 预期退保价值增长率 |

## Step 2: Build Withdrawal Scenarios

Extract key milestones and model typical withdrawal patterns:

| Milestone | Age | Typical Use |
|-----------|-----|------------|
| University | 18 | Education (海外大学) |
| Master's | 22 | Further education |
| Career start / Marriage | 28-30 | 创业/婚嫁金 |
| Children's independence | 36 | 子女而立/自我实现 |
| Policyowner retirement | 55-65 | 养老补充 |
| Transmission | 80+ | 传承第三代 |

Key metrics to compute:
- Total premium paid (5-year term typical)
- Breakeven year (expected surrender value > cumulative premium)
- IRR (internal rate of return, typically 5.5-7% for HK savings)
- Multiples at key ages (1x, 2x, 5x, 10x)

## Step 3: Client-Specific Sales Language

### Profile-driven framework

For each client, identify:
1. **Investment profile**: high-return trader vs. conservative saver
2. **Children's nationality**: PRC vs. US/Canada/UK citizens (critical for FATCA/estate tax)
3. **Primary concern**: returns, safety, succession, tax, education
4. **Psychological barrier**: "insurance kills returns" is the most common

### Emotional anchoring structure

**Opening**: Ask the client a question about their child, not about the product.

**Frame the problem as**: "You handle the upside. This handles the '万一'." (You manage the gains. This manages the 'what if'.)

**Three-account framework**:
- 进攻型账户 (Offensive): stocks, funds — for growth
- 底线型账户 (Defensive): savings/insurance — for certainty
- 传承型账户 (Succession): trust/insurance — for legacy

**Never** tell a high-return investor their returns are bad. Instead: "Your returns are exactly why you don't need to touch this account."

### Objection handling

| Objection | Response approach |
|-----------|-------------------|
| "Insurance has low returns" | "This isn't about returns. It's about '届时一定有'." |
| "It will affect my stock portfolio" | "You don't move stocks. This is funded from income, not liquidation." |
| "Tax issues with Hong Kong" | Acknowledge CRS, then explain compliance path (see Step 4) |
| "I can invest this better myself" | "Exactly — so don't mix the two accounts. Keep both running in parallel." |

## Step 4: Tax Objections — CRS 2.0 / FATCA / US Estate Tax

### CRS 2.0 (Common Reporting Standard)

**What it means**: China and HK automatically exchange financial account info since 2018. HK life insurance policies are financial accounts and are reported.

**Key points for client**:
- "知道 ≠ 要交税" (Being aware ≠ owing tax)
- Non-taxable: education savings, wealth传承; Taxable: income/dividends if you're a tax resident
-储蓄型保单本身不是CRS打击对象；打击的是「藏钱不报」

**CRS 2.0 updates (2023+)**:
- Expanded coverage: crypto assets, trusts, investment entities
- Enhanced due diligence for high-value accounts (>$1M)
- Voluntary disclosure program (reduced penalties)

### US Person / FATCA

**Who is a US person**:
- US citizen or green card holder
- Satisfies Substantial Presence Test (≥183 days/year in US over 3-year period)
- Born in US (even if never lived there)
- **Critical for HK insurance clients**: Children with US citizenship (美籍宝宝)

**FATCA implications for HK insurers**:
- HK insurers must report US person accounts to IRS
- W-9 form required before policy issuance for US persons
- Dividends/interest income → US tax return required
- Surrender/refund → potential US tax liability

### US Estate Tax (遗产税)

**2024 thresholds**: $12.92M per person (individual); rates up to 40% above threshold

**Critical for HK insurance**:
- Death benefit paid to a US citizen beneficiary counts toward their estate
- Excess over $12.92M taxed at 40%
- **Solution**: Irrevocable Life Insurance Trust (ILIT / 不可撤销信托) — removes policy from taxable estate

### Gift Tax (赠与税)

- US persons gift to non-US persons: $17,000/year exempt (2024)
- Excess must be reported but typically no tax until death
- Children as PRC tax residents (non-US persons) receiving gifts: no US gift tax

### China → HK Fund Flow

| Method | Notes |
|--------|-------|
| Corporate wire (企业跨境支付) | Requires trade/service contract + invoice; not subject to $50K personal limit |
| ODI备案 | Outbound Direct Investment — for large transfers |
| Personal limit | $50K/year per person (current account only) |

**For HNW clients**: Use corporate account path. Cost to cover = service fee.

## Step 5: Recommended Policy Structure

For mainland Chinese parents with US-citizen children:

| Element | Recommendation |
|---------|---------------|
| Policyowner | Mother (mainland tax resident, non-US person) |
| Insured | Child (US citizen) |
| Beneficiary | ILIT (irrevocable trust) or named beneficiary |
| Premium funding | Corporate account → HK corporate → HK private → insurer |
| Tax pre-planning | Pre-issue: ILIT structure; Post-issue: annual FATCA compliance |
| Cost coverage | Advisor to absorb fund transfer cost as service fee |

## Step 6: Output Formats

- **Sales script**: Markdown, structured for in-person/WeChat use
- **Infographic**: Use `baoyu-infographic` skill with `linear-progression` layout + `morandi-journal` style for long-term value comparison chart
- **PPT**: Use `powerpoint` skill
- **Data table**: Markdown table with key milestones, values, multiples

## Pitfalls

1. **Never invent tax numbers** — CRS thresholds, FATCA reporting deadlines, US estate tax limits change annually. Verify current year values.
2. **US person ≠ US resident** — A US citizen living in Beijing may still be a PRC tax resident. Tax situation is dual-country complex. Always recommend a qualified cross-border tax advisor.
3. **Don't mix the two accounts** — The entire sales argument rests on separating "offensive" (stocks) and "defensive" (insurance) accounts. Never let the client conflate them.
4. **Excel parsing edge case** — Some insurer Excel files use merged cells, unusual column ordering, or numeric format codes. Verify column mapping against the shared string summary row.
5. **CRS ≠ blocked** — Clients often hear "CRS" and think "banned." Clarify that information exchange and taxation are different things.
6. **Tax as blocking tactic, not real objection** — HNW clients often raise tax concerns to delay decisions, not because they genuinely cannot proceed. The correct response: acknowledge briefly, hand off to tax advisor, then IMMEDIATELY pivot back to the emotional decision. Never spend >90 seconds on tax — it signals you're not confident in the product.
7. **Three types of "我再想想"** — (a) genuine concern remaining → uncover it; (b) decision fatigue → give a specific two-choice close; (c) price sensitivity → anchor on the cost of inaction (e.g., child turns 12, premium goes up, policy window closes).
8. **Always identify the real payer** — If client uses corporate funds for personal insurance, ensure the corporate-to-personal structure is clean and documented. Corporate premiums paid personally can trigger gift tax issues.
9. **宏观数据 → 销售话术的转换流程** — 当用户提供期刊/书籍并要求结合保险销售时：①先尝试weread API；②失败则用web搜索公开摘要；③提取数据卡；④转换为「场景→话术」格式输出。不要只给原始数据，要给客户能直接说的话术。

## Closing Methodology

### When to Close

The close opportunity appears when ANY of these signals occur:
- Client stops raising new objections
- Client asks about premium amount, payment term, or policy duration
- Client mentions a specific milestone ("等她上大学…")
- Client says "这个产品还不错" or similar positive language
- Client's body language / tone shifts toward decision

### The Two-Choice Close (绝对二选一)

**Never** ask: "您要不要再考虑考虑?"
**Always** ask: "您倾向5年每年140万，还是先从70万上车，后面再加保?"

This removes the "要不要买" question entirely and forces a commitment to one version of the purchase.

### Tax → Close Pivot

When client raises tax objections repeatedly:

> Step 1: "这个问题我记下来了，我们一定帮你处理到完全合规。"
> Step 2: "现在我问你一个更核心的问题——"
> Step 3: "如果税务今天就解决了，你还有别的顾虑吗？"
> Step 4: If no → go straight to two-choice close. If yes → handle remaining objection.

### Emotional Anchor Close (for investor clients)

For clients who are emotionally driven (most mothers):

> "你已经是她最好的妈妈了。
> 你在给她一个'无论发生什么，她都有底气'的人生起点。
> 这份保单，就是那个'兜底'。"

### Cost-of-Inaction Close

When client is stalling on a younger child (age is the enemy of insurance pricing):

> "你孩子现在1.5岁投保，年交140万。
> 再过两年保费会涨，而且孩子在长大——越晚买，同样的保障交的钱越多。"

### Rapport-Building Close (stock-investor clients)

For clients with notable investment portfolios (e.g., recent 120% return in a stock):

> Acknowledge their skill, then immediately separate the two accounts.
> The close: "你的投资收益这么好，更不能拿这部分钱去赌女儿的教育金。
> 这份保单让你在继续投资的同时，女儿的教育金已经锁定了。"

## Rapport Topics for Investor Clients

When client mentions a specific stock or investment, research it before the meeting and use it to build personal connection. This signals you pay attention to their world.

**Hailanxin (300065) — sample reference**:
- Company: Beijing Highlander Digital Technology (北京海兰信数据科技股份有限公司)
- Business: Marine tech — intelligent navigation, seabed data centers (UDC), offshore radar networks
- Recent catalyst: SK Group visit May 21, 2026 for UDC cooperation; stock showed 5% intraday gain May 22
- Note: Q1 2026 earnings very weak (revenue -73%, net profit -95%) — market is pricing the UDC story, not current fundamentals
- Client context: 3-month return ~120% — likely entered ~12-13元 range

## References

- `references/plan-data-sample.md` — Extracted data from 国寿海外傲珑盛世储蓄保险计划 (sample HK savings plan, 11-year-old female, 5-year pay, RMB 1.4M/year)
- `references/crs-tax-knowledge.md` — CRS 2.0, FATCA, US estate/gift tax knowledge bank
- `references/client-pitch-example.md` — Full sales script + 8-step framework + product comparison (充裕未来 vs 隽富) for client: 美籍宝宝 + 投资型母亲 + 教育金需求 + 800万预算
- `references/macro-hkinsurance-insights.md` — 财经2026年第9期宏观数据 + 港险话术（人民币国际化、港股、跨境资金）
- `references/macro-policy-hkinsurance-2026.md` — **新增** 国务院对外投资规定（2026.7.1）深度解读：政策背景/对港险影响/销售促进抑制要点/话术模板
- `references/hkinsurance-video-compliance.md` — 港险短视频合规策略：行业现状、可用内容角度、禁用词库、CTA导向（视频号→公众号→私域转化路径）
- `references/currency-hedge-objection-handling.md` — 货币风险对冲反对意见处理：核心哲学"去准备而不是预测"，三级处理话术，客户自测框架（对应港险新手入门一本通问题三）
- `references/baima-师姐-session-2026-05-22.md` — 面谈实录：8步话术 + 两个孩子方案 + Q&A + 输出物清单（白玛师姐，2026-05-23面谈）
- `scripts/printable-html-to-pdf.md` — Workflow: generate styled HTML with @page CSS, push to GitHub, user prints to PDF via Chrome
