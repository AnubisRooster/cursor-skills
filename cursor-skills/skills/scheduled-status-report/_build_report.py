#!/usr/bin/env python3
"""Build Models weekly status Confluence storage XHTML."""
from __future__ import annotations

import html
import json
from collections import Counter, defaultdict
from pathlib import Path

STATS = json.loads(Path("_stats.json").read_text(encoding="utf-8"))

EPIC_NAMES = {
    "LATC-13116": "20.4 Model Pillar Model Index",
    "LATC-10271": "R&O Requirements Evaluation",
    "LATC-10229": "Data Agent Enablement",
    "LATC-9909": "Gesture Control Models PRCP - Core Intel Requirements Intake",
    "LATC-9801": "DeepSeekV4-Flash 2-Bit Quantization",
    "LATC-9741": "Omni model test",
    "LATC-9376": "Multimodal PRCP Gesture Control",
    "LATC-8943": "Ultra-Low Bit Quantization for Large Language Models",
    "LATC-8674": "33.3 LATC value delivery into Davy",
    "LATC-8672": "33.1 Discovery, access & gap analysis",
    "LATC-8298": "9.13 Embedding Model v2 (Replacing ME5s)",
    "LATC-8295": "9.10 On-Device Speech Translation V2",
    "LATC-8292": "22.1 AIW: Listen and Act Locally Solution",
    "LATC-6782": "Daikin Supply Chain Planning",
    "LATC-6594": "9.7 Gemma-4-26B-A4B Spark Model UX and Safety Enhancement",
    "LATC-6592": "Flux2Klein v1",
    "LATC-6591": "9.5 Gemma4-e2b 1.0 - Local Agent",
    "LATC-4719": "Multimodal Capability Support for P7 Edge Device",
    "LATC-4013": "Multimodal PRCP Requirements Intake - Knowledge Base Multimodal Requirements",
    "LATC-3853": "20.1 Model Pillar General",
    "LATC-3171": "Quantization Fast Verification",
    "LATC-2711": "Model Research & Knowledge Activation",
    "LATC-2240": "7.3 Model Inference Optimization",
    "LATC-1049": "FM Evaluation Integration",
    "LATC-243": "[xCloud]4.5 Benchmark & Data & Agent evaluation for AICS project",
}

EPIC_PCT = {
    # key: (done_e, total_e, pct_e)
    "LATC-13116": (0, 7, 0),
    "LATC-9741": (1, 6, 17),
    "LATC-8295": (2, 9, 22),
    "LATC-6592": (16, 38, 42),
    "LATC-8292": (17, 35, 49),
    "LATC-2711": (11, 22, 50),
    "LATC-6591": (69, 119, 58),
    "LATC-9801": (3, 5, 60),
    "LATC-8298": (3, 5, 60),
    "LATC-10271": (3, 5, 60),
    "LATC-3853": (12, 18, 67),
    "LATC-4013": (107, 155, 69),
    "LATC-10229": (3, 4, 75),
    "LATC-1049": (36, 47, 77),
    "LATC-6782": (81, 99, 82),
    "LATC-2240": (6, 7, 86),
    "LATC-4719": (33, 38, 87),
    "LATC-8943": (15, 17, 88),
    "LATC-8672": (10, 11, 91),
    "LATC-6594": (11, 12, 92),
    "LATC-3171": (139, 149, 93),
    "LATC-243": (36, 36, 100),
    "LATC-8674": (2, 2, 100),
    "LATC-9909": (3, 3, 100),
    "LATC-9376": (6, 6, 100),
}

EXTRA = {
    "key": "LATC-12959",
    "summary": "After the program runs, it returns to the background and the interface automatically switches to the desktop",
    "assignee": "Jiaxin JX38 Li",
    "type": "Bug",
    "epic": "LATC-8295",
}


def label(epic_key: str) -> str:
    return f"{EPIC_NAMES[epic_key]} ({epic_key})"


def esc(s: str) -> str:
    return html.escape(s, quote=False)


# Dedup + add missing
seen = set()
issues = []
for i in STATS["issues"]:
    if i["key"] in seen:
        continue
    seen.add(i["key"])
    issues.append(i)
issues.append(EXTRA)

assert len(issues) == 143, len(issues)

by_type = Counter(i["type"] for i in issues)
by_epic = Counter(i["epic"] or "No Epic linked" for i in issues)
by_assignee = Counter(i["assignee"] for i in issues)
grouped_a = defaultdict(list)
grouped_e = defaultdict(list)
for i in issues:
    grouped_a[i["assignee"]].append(i)
    grouped_e[i["epic"] or "No Epic linked"].append(i)

# by_epic chart rows
epic_rows = []
singles = []
for key, n in by_epic.most_common():
    if key != "No Epic linked" and n == 1:
        singles.append((key, n))
        continue
    name = "No Epic linked" if key == "No Epic linked" else label(key)
    epic_rows.append((name, n, key))
if singles:
    epic_rows.append((f"Other ({len(singles)} epics, 1 each)", sum(n for _, n in singles), "OTHER"))

# by_contributor chart
contrib_rows = []
single_people = []
for name, n in by_assignee.most_common():
    if n == 1:
        single_people.append((name, n))
        continue
    contrib_rows.append((name, n))
if single_people:
    contrib_rows.append((f"Other ({len(single_people)} contributors, 1 each)", sum(n for _, n in single_people)))

NARR = {
    "Adrian Chan16": "Adrian closed the DeepSeekV4-Flash 2-bit path from architecture notes through hosting config and a baseline eval, so the team can judge whether that recipe is deployable. He also parked DeepSeek/GLM/Inkling hosting and documented Gemma-4-26B safety LoRA readiness. Side work on text watermarking and safety data keeps the safety story from stalling while the quantization work lands.",
    "Aoxiang AX4 Zhang": "Aoxiang moved the Gemma-4-26B Q4/Q6 safety LoRA models through GGUF conversion, inference debug, and OSC review tracking. That is the handoff the Spark UX/safety epic needed before anyone else can consume the adapters. He also stood up an HTML dataset and metric so coding-capability eval is no longer a one-off notebook.",
    "Eli Guo9": "Eli finished the Perception Engine data stack for Gemma4-E2B: schema, generation pipeline, multilingual reviewed sets, and SFT follow-up. That unblocks training that was waiting on data, not on GPUs. He also generalized image-gen/edit QC and evaluation execution, and closed a LATC Bench personal PE/safety eval so the model index has a real signal.",
    "Fei Fei4 Ma": "Fei unblocked on-device speech packaging. 16KB page alignment on the SAD/ONNX stack and ASR SDK deploy support are the kind of integration fixes that keep wearable/phone builds from dying in QA.",
    "Francisco Ponce gomez2": "Francisco completed the Davy-side coding-harness comparison against TianxiCode and AIverse. That is the evidence the value-delivery epic needed to say where LATC should plug in versus build.",
    "Gong Chen": "Gong took Gemma4-E2B onto MTK: four-precision quantization, on-device inference code and docs for MT6899, plus two comparison bugs on system-prompt/tool-call and VLM profile save. MTK eval can now run against a documented recipe instead of a laptop demo.",
    "Grant Forbes": "Grant spiked 1-2 bit quantization on 12B-class models. The result tells the research track whether ultra-low-bit is worth a full recipe or still a paper exercise.",
    "Hai Long": "Hai packaged speaker diarization as a standalone AAR and wired it back into WhisperASR with a regression pass. Diarization is now a deliverable SDK, not a folder of source.",
    "Haitao HT37 Wang": "Haitao wrote the R&O routing and planning requirements analysis. That is the contract Models needs before routing work turns into scattered tickets.",
    "Hao Hao51 Liu": "Hao deployed multiple Granite variants and sat with test on the P7 box. Fast-verification only counts if the models are actually on the device the testers use.",
    "Haoran HR3 Lu": "Haoran compared cloud vs on-device LLMs for AI Wearable summarization and built model-specific Goodsum paths for Gemma 3 1B, Gemma 4 E2B, and Granite 4.0 1B. He scored English summary quality and expanded action-item gold labels so the next training loop has something to fit to.",
    "Heming HM22 Zhang": "Heming isolated Granite-Embedding memory blow-ups on GPU and CPU. Without that diagnosis the 2-bit GSQ work would be guessing at OOMs.",
    "Hong Hong16 Wang": "Hong pushed Translation SDK v2 on two fronts: peak-memory/stability and throughput. He also ran M2M100 scale sweeps and a 40K-data recipe that tries to keep ZH-EN quality without dumping multilingual coverage.",
    "Hui Hui47 Li": "Hui delivered the second Outlook calendar/email demo dataset. That is the scenario pack local summarization and action-item models actually get judged on.",
    "Jianbang Zhang": "Jianbang closed three foundation-model epics: the training pipeline, Qira Granite v2 training, and FM evaluation integration. Those were long-running containers. Closing them clears the books for the next factory wave.",
    "Jianlin JL2 Deng": "Jianlin looked at Granite for long-token use, evaluated ColModernVBERT split-vision, and joined the CLI Router design. That is the verification epic moving past 'deploy a checkpoint' into how models get selected and routed.",
    "Jiaxin JX38 Li": "Jiaxin kept on-device speech translation testable. He shipped a stable Android QA build, added batch file recognition and ASR memory monitoring, and fixed a background/desktop-switch bug that made the demo look broken after a successful run.",
    "Jie Yang": "Jie reviewed official ONNX documentation. That is housekeeping, but it is the reference the pillar uses when runtime and quantization argue about what is supported.",
    "Jin Jin1 Yuan": "Jin advanced Flux2Klein editing: a compositional edit test and a soft-mask distillation strategy. Those are the two levers that decide whether Flux edits stay on-distribution or smear.",
    "Jinchuan JC20 Liu": "Jinchuan split the long-text embedding graph to cut memory, and he ran quantized Granite inference on low-end Qualcomm for the AI Wearable listen-and-act path. Both are 'will this fit' answers, not demos.",
    "Jinyi JY2 Zou": "Jinyi added short-chunk cross-lingual and short monolingual English data for the next training round. Short utterances are where wearable ASR usually falls over.",
    "Jundong JD1 Tan | 谭俊东": "Jundong closed a cluster of Daikin supply-chain UI work: production dashboards, planned-order type filters, and demand-planning sales-order upload/page changes. The planner workflow is now closer to something operations can click through without a Models engineer in the room.",
    "Kai Kai23 Liu": "Kai explored KV-cache quantization, llama.cpp multimodal gesture recognition, and Omni-model audio/gesture. That is the research scan for what can live on-device without a new training program.",
    "Lin Lin13 Yang | 杨琳": "Lin built target-speaker enrollment for AI Wearable diarization: the feature, a matching dev set, and the enroll-binding pipeline baseline. Without enrollment, diarization cannot lock onto the wearer.",
    "Longlong LL22 Liu | 刘龙龙": "Longlong hardened the AI Wearable speech stack. 16KB SO alignment, a SAD CRLF crash, and a WhisperASR session lifecycle refactor are the difference between a lab demo and a firmware drop that survives stop/start.",
    "Mi Mi1 Hong": "Mi cleared two integration blockers: an undefined-reference SAD crash on AP firmware link, and VAD lib support for the Andes integration team. Those are the tickets that keep device bring-up from stalling overnight.",
    "Mike Fink": "Mike closed the Davy discovery epic and the two stories that made it real: cloud model-service access options, and the Mitra vs Davy positioning memo including the PRC track. Leadership now has a written choice, not a slide.",
    "Nan Nan1 Yan": "Nan stood up the voice-model evaluation environment under FM Evaluation Integration. Voice eval can run in the same factory path as text instead of a side laptop.",
    "Shengzhe SZ2 Tao": "Shengzhe finished single-turn RL QAT for Gemma4-E2B. That is one of the training knobs the official device eval depends on.",
    "Shi Shi1 Gu": "Shi collected gesture-recognition training data for the PRCP intake epic. No more waiting on a promised corpus that was not in the repo.",
    "Shiru SR1 Bu": "Shiru finished DataAgent pre-implementation research. That is the design read DataForge needed before P0/P1 code.",
    "Sriman Donthireddi": "Sriman stood up Uni-Docker with SGLang. Shared serving for eval and research stops each engineer from inventing a one-off runtime.",
    "Tian Tian2 Zhou": "Tian ran the granite-embedding-97m-multilingual-r2 multi-test window (8/24-8/28). The embedding v2 replacement now has a week of numbers, not a single smoke run.",
    "Tom Sheffler": "Tom wrote the Davy value proposition, capacity/quality parity for the LATC-ROW coding cohort, and the coding-agent gap analysis in Confluence. He also completed the matching harness comparison on the value-delivery epic. The Davy ask is now documented end to end.",
    "Tongtong TT20 Zhang": "Tongtong delivered DataForge 1.0 P0-P1 development. The data-agent path has code, not just a research note.",
    "Tuan anh Dang1": "Tuan absorbed the ABot-World sub-1B on-device world-model paper. The research epic now has a feasibility read instead of a bookmark.",
    "Wei Wei19 Xu": "Wei implemented pre- and post-processing in the translation system. That is the glue that keeps model scores from being eaten by tokenization and formatting.",
    "Xiao Xiao3 Ma": "Xiao trained a PRCP gesture model, trained Qwen3.5-0.8B on CLIP-only data, and evaluated/optimized the multimodal embedding model for P7. Edge multimodal is moving from intake tickets to trained artifacts.",
    "Xuan Xuan3 Cao": "Xuan flooded the P7 verification box with deployable services: Cross/JA/Total KD, Gemma and Harrier distilled (including bidirectional v2), Qwen3-VL embedding plus PPOCRv6/layout I/O alignment, and Z-Image/ERNIE turbo. Testers can hit models instead of waiting on a shared notebook.",
    "Xue Xue5 Xia": "Xue stood up model services for Tesseract Japanese, NDLOCR-Lite, and the harrier-0806 quantized checkpoint. OCR and quantized vision now have the same service shape as the rest of fast verification.",
    "Yanan YN4 Wu": "Yanan researched voice-data synthesis and ran quality validation plus gap analysis. Voice training data now has a written gap list instead of 'we need more audio.'",
    "Yinglin YL4 Ji": "Yinglin ran the first official Gemma4-E2B eval on SM8750 and filed the tool-call formatting defect against the BF16 reference. He also tested Granite 2.2.0 QNN240 non-think on SM7635 for the wearable path. Device numbers exist; the remaining fight is format fidelity.",
    "Yuxuan YX25 Xu": "Yuxuan ran the LATC Gemma-4-E2B QAT eval. QAT is no longer an untested training branch.",
    "Zeyang ZY26 Yang": "Zeyang tested P7 image-generation performance against the PRCP multimodal intake. The BU now has a measured baseline, not a qualitative demo.",
    "Zhenhua ZH17 Liu": "Zhenhua closed DPO training for Gemma4-E2B. Preference alignment is in the factory path the device eval is using.",
    "Zhicheng Fu": "Zhicheng carried Gemma4-E2B through QC enablement, PTQ recipe selection, SM8750 official-eval prep/debug, and a set of release-blocking output bugs (chat-template leak, empty [END]-only responses, tool-call mismatch, missing system-prompt/tool-call input). He also added Genie profile save for VLM testing. This is the week the local-agent epic became a device program instead of a quantization experiment.",
    "Zhiyao ZY58 Zhang": "Zhiyao finished the Daikin front-end slice: production dashboards, job-finish notifications, planned-order filters, demand-planning order check, sales-order page, customer config, default display, item page, demand aggregation, and page permissions. Operations can run the planner screens without a backend engineer babysitting each click.",
    "Ziqi ZQ24 Liu": "Ziqi released trans-sys-poc, unified Windows/Android demo code, improved logging persistence, and supported test. The translation POC is a build QA can rerun, not two diverging apps.",
    "Zongfu ZF3 Qu": "Zongfu pushed ultra-low-bit on Granite embeddings (2-bit and 4-bit GSQ, 2.8-bit mixed precision, 2.9-bit mixed group size) and ran Granite inference on a low-level MTK phone via MNN. The quantization epic now has phone-side evidence, not only desktop PPL.",
}

EPIC_NARR = {
    "LATC-6591": "This week the local-agent epic actually met a device. Official SM8750 eval was prepared, run, and debugged; MTK inference code landed; QAT/DPO/PTQ recipes closed; and a cluster of tool-call, chat-template, and empty-output defects were filed and cleared. Perception Engine data that had been open for weeks also closed, so training is no longer waiting on unlabeled PE sets. The epic is still only 58% complete overall. The remaining risk is fidelity on-device, not 'can we launch a checkpoint.'",
    "LATC-6782": "Daikin supply-chain planning took the largest non-model bite of the week. Production dashboards, planned-order filters, demand-planning sales-order flows, permissions, and job notifications all moved to Done. That is productization of a planner UI the BU can operate. It is 82% complete overall and should not be mistaken for model-factory velocity.",
    "LATC-3171": "Fast verification stayed in deploy-and-measure mode. Granite, Harrier, Gemma distilled, OCR (Tesseract JP, NDLOCR-Lite), and image-turbo services were stood up on the P7 box, with I/O alignment for Qwen3-VL embedding and layout. Long-token Granite and ColModernVBERT also got a look. The epic is 93% complete. The leftover work is mostly the long tail of 'one more checkpoint on the box.'",
    "LATC-8943": "Ultra-low-bit work moved from analysis to phone. GSQ 2-bit/4-bit and mixed 2.8/2.9-bit recipes were tested on Granite embeddings, memory OOMs were diagnosed, and Granite was inferred on MTK via MNN. 88% complete. The open question is quality at those bit widths, not whether the kernels run.",
    "LATC-8292": "Listen-and-act locally got firmware-shaped fixes: 16KB SO alignment, SAD CRLF crash, WhisperASR session lifecycle, plus Granite QNN240 test on SM7635 and low-end Qualcomm inference. 49% complete. Hardware bring-up is still the gate, not model choice.",
    "LATC-8672": "Discovery closed. Cloud model-service access, Mitra vs Davy positioning (including PRC), Davy value spike, ROW cohort capacity/quality, and the Confluence gap analysis all landed. The epic is 91% complete and the parent epic itself went Done. Next step is a decision, not more research.",
    "LATC-2711": "Research tickets closed on 1-2 bit 12B feasibility, KV-cache quantization, llama.cpp gesture, and the ABot-World absorb. 50% complete. This epic will stay a mixed bag until someone sequences the next bets.",
    "LATC-9801": "DeepSeekV4-Flash 2-bit has an architecture read, a hosting config, and a baseline eval. 60% complete. Enough to say whether the recipe is worth a second week.",
    "LATC-6594": "Gemma-4-26B safety LoRA hit GGUF conversion, OSC tracking, and a deployment-readiness writeup. 92% complete. This is late-stage packaging, not new training.",
    "LATC-3853": "General pillar work: DeepSeek/GLM/Inkling hosting and an ONNX docs review. 67% complete. Useful, not a theme.",
    "LATC-1049": "FM evaluation integration closed as an epic. Child work this week was a coding-eval HTML dataset/metric and a voice eval environment. 77% complete on remaining children.",
    "LATC-243": "AICS eval enablement closed its last two children: evaluation execution/troubleshooting and generalized image-gen/edit QC. 100% complete.",
    "LATC-8674": "Both Davy harness-comparison stories closed. 100% complete. Combined with 33.1, the Davy conversation now has discovery and a value-delivery comparison.",
    "LATC-8295": "On-device speech translation shipped a stable Android QA build and a desktop-switch bug fix. 22% complete. Testability improved; the model/SDK work is still early.",
    "LATC-6592": "Flux2Klein got a compositional edit test and a soft-mask distillation strategy. 42% complete. Editing quality is still the open problem.",
    "LATC-10229": "DataAgent research and DataForge 1.0 P0-P1 development closed. 75% complete. Implementation has started.",
    "LATC-4719": "P7 multimodal embedding eval/optimize and a CLIP-only Qwen3.5-0.8B train closed. 87% complete. Edge multimodal is in the last mile.",
    "LATC-13116": "One LATC Bench PE/safety eval closed under the model-index epic. Overall child completion is 0/7 in Jira (the Done ticket may not be linked as a child). Treat the index as not started from a rollup view.",
    "LATC-10271": "R&O routing and planning requirements analysis closed. 60% complete. Contract written; build not done.",
    "LATC-2240": "Long-text embedding graph-split memory work closed. 86% complete.",
    "LATC-9741": "Omni audio/gesture research closed. 17% complete. Still a thin epic.",
    "LATC-9909": "Gesture training data collection closed. 100% complete.",
    "LATC-8298": "A week of granite-embedding-97m-multilingual-r2 tests closed. 60% complete.",
    "LATC-9376": "PRCP gesture-recognition training closed. 100% complete.",
    "LATC-4013": "P7 image-generation performance test closed. 69% complete on a large intake epic.",
}

NO_EPIC_NARR = (
    "Thirty-five completions had no Epic Link. A large share is on-device speech and translation plumbing: "
    "SAD/VAD/ASR SDK alignment, diarization AAR, Translation SDK v2 memory and M2M100 data, target-speaker enrollment, "
    "Goodsum on-device vs cloud, trans-sys-poc release, and voice-data synthesis/QC. Four closed epics also sit here "
    "because Jira does not put an Epic Link on an Epic. Treat this bucket as real delivery, but it will not show in epic % bars."
)


def ticket_li(i: dict) -> str:
    epic = "No Epic linked" if not i["epic"] else label(i["epic"])
    return f"<li><strong>{esc(i['key'])}</strong> | Epic: {esc(epic)} | {esc(i['summary'])}</li>"


def chart_bar(title, xlabel, ylabel, headers, rows, width, height, extra_params=""):
    body_rows = "".join(f"<tr><td>{esc(a)}</td><td>{b}</td></tr>" for a, b in rows)
    extras = extra_params
    return (
        f'<ac:structured-macro ac:name="chart">'
        f'<ac:parameter ac:name="type">bar</ac:parameter>'
        f'<ac:parameter ac:name="orientation">horizontal</ac:parameter>'
        f'<ac:parameter ac:name="dataOrientation">vertical</ac:parameter>'
        f'<ac:parameter ac:name="legend">false</ac:parameter>'
        f'<ac:parameter ac:name="xLabel">{xlabel}</ac:parameter>'
        f'<ac:parameter ac:name="yLabel">{ylabel}</ac:parameter>'
        f'<ac:parameter ac:name="title">{title}</ac:parameter>'
        f'{extras}'
        f'<ac:parameter ac:name="width">{width}</ac:parameter>'
        f'<ac:parameter ac:name="height">{height}</ac:parameter>'
        f'<ac:rich-text-body><table><tbody><tr><th>{headers[0]}</th><th>{headers[1]}</th></tr>'
        f"{body_rows}</tbody></table></ac:rich-text-body></ac:structured-macro>"
    )


def pie(title, headers, rows, width=360, height=300):
    body_rows = "".join(f"<tr><td>{esc(a)}</td><td>{b}</td></tr>" for a, b in rows)
    return (
        f'<ac:structured-macro ac:name="chart">'
        f'<ac:parameter ac:name="type">pie</ac:parameter>'
        f'<ac:parameter ac:name="title">{title}</ac:parameter>'
        f'<ac:parameter ac:name="legend">true</ac:parameter>'
        f'<ac:parameter ac:name="width">{width}</ac:parameter>'
        f'<ac:parameter ac:name="height">{height}</ac:parameter>'
        f'<ac:rich-text-body><table><tbody><tr><th>{headers[0]}</th><th>{headers[1]}</th></tr>'
        f"{body_rows}</tbody></table></ac:rich-text-body></ac:structured-macro>"
    )


total_scope = 1836
done_total = 1388
todo_total = 186
inprog_total = 262
open_total = todo_total + inprog_total
pct = round(100 * done_total / total_scope)
completed_total = 143
velocity = 143
median = 9
mean = 16
named = 49
closed_epics = 4

type_rows = by_type.most_common()
pct_chart_rows = []
for k, (done_e, total_e, pct_e) in sorted(EPIC_PCT.items(), key=lambda kv: (kv[1][2], kv[0])):
    pct_chart_rows.append((f"{label(k)} — {done_e}/{total_e}", pct_e))

# Epic activity table rows: real epics by completed desc, then No Epic, then Other
activity = []
for key, n in by_epic.most_common():
    if key == "No Epic linked" or n == 1:
        continue
    done_e, total_e, pct_e = EPIC_PCT[key]
    activity.append((key, n, pct_e, done_e, total_e))
# singles as Other
other_n = sum(n for k, n in by_epic.items() if k != "No Epic linked" and n == 1)
no_epic_n = by_epic.get("No Epic linked", 0)

parts = []
parts.append(
    "<p><strong>Component:</strong> Models<br/>"
    "<strong>Reporting Window:</strong> 2026-08-28 to 2026-09-04 &middot; "
    "<strong>Generated:</strong> 2026-09-04</p>"
)
parts.append("<h2>Project Snapshot</h2>")
parts.append(
    "<table><tbody>"
    "<tr><th>Metric</th><th>Value</th></tr>"
    f"<tr><td>Component scope</td><td>{total_scope} issues</td></tr>"
    f"<tr><td>Overall completion</td><td><strong>{done_total} / {total_scope} Done ({pct}%)</strong></td></tr>"
    f"<tr><td>Open remaining</td><td>{open_total} issues ({todo_total} To Do, {inprog_total} In Progress)</td></tr>"
    f"<tr><td>Completed this period</td><td>{completed_total} issues</td></tr>"
    f"<tr><td>Contributors active (this period)</td><td>{named} named + 0 unassigned</td></tr>"
    f"<tr><td>Velocity (this period)</td><td>~{velocity} issues/wk</td></tr>"
    f"<tr><td>Cycle time, open&rarr;done</td><td>Median ~{median} days, mean ~{mean} days</td></tr>"
    f"<tr><td>Completed Epics this period</td><td>{closed_epics}</td></tr>"
    "</tbody></table>"
)
parts.append("<h2>Progress Charts</h2>")
parts.append("<table><tbody><tr><td>")
parts.append(pie(f"Component Completion (all {total_scope})", ["Status", "Issues"], [("Done", done_total), ("Open", open_total)]))
parts.append("</td><td>")
parts.append(pie("Completed This Period by Type", ["Type", "Count"], type_rows))
parts.append("</td></tr></tbody></table>")

# Open work bar — include BOTH orientation params per critical rules
parts.append(
    chart_bar(
        "Open Work Remaining by Status",
        "Status",
        "Issues open",
        ["Status", "Issues"],
        [("To Do", todo_total), ("In Progress", inprog_total)],
        520,
        280,
    )
)
parts.append(
    chart_bar(
        "Completed This Period by Epic",
        "Epic",
        "Issues completed",
        ["Epic", "Completed"],
        [(name, n) for name, n, _ in epic_rows],
        820,
        380,
    )
)
parts.append(
    chart_bar(
        "Epic % Complete (all child issues)",
        "Epic",
        "% complete",
        ["Epic", "% Complete"],
        pct_chart_rows,
        820,
        420,
        extra_params='<ac:parameter ac:name="rangeMax">100</ac:parameter>',
    )
)
parts.append(
    "<p><em>Bar = overall epic completion (Done child issues / all child issues, point-in-time across the full epic, "
    "not just this window). Bars are comparable regardless of epic size; absolute Done/Total appear in each label "
    "and in the table below.</em></p>"
)
parts.append(
    chart_bar(
        "Completed This Period by Contributor",
        "Contributor",
        "Issues completed",
        ["Contributor", "Completed"],
        contrib_rows,
        760,
        420,
    )
)

parts.append("<h2>Epic Activity &amp; Velocity (this period)</h2>")
parts.append(
    "<table><tbody><tr><th>Epic</th><th>Completed (this wk)</th><th>Velocity (/wk)</th><th>Epic % Complete</th></tr>"
)
for key, n, pct_e, done_e, total_e in activity:
    href = f"https://jira.xpaas.lenovo.com/browse/{key}"
    parts.append(
        f"<tr><td>{esc(EPIC_NAMES[key])} &middot; <a href=\"{href}\">{key}</a></td>"
        f"<td>{n}</td><td>{n:.1f}</td><td>{pct_e}% ({done_e}/{total_e})</td></tr>"
    )
parts.append(
    f"<tr><td>No Epic linked</td><td>{no_epic_n}</td><td>{no_epic_n:.1f}</td><td>&mdash;</td></tr>"
)
parts.append(
    f"<tr><td>Other ({len(singles)} epics, 1 each)</td><td>{other_n}</td><td>{other_n:.1f}</td><td>&mdash;</td></tr>"
)
parts.append(
    f"<tr><td><strong>Total</strong></td><td><strong>{completed_total}</strong></td>"
    f"<td><strong>{velocity}</strong></td><td><strong>&mdash;</strong></td></tr>"
)
parts.append("</tbody></table>")
parts.append(
    "<p><em>Velocity = issues moved to Done during the window. Epic % Complete = Done child issues / all child issues "
    "of that epic (overall progress, point-in-time), so it does not sum and is independent of this window's throughput.</em></p>"
)

parts.append("<h2>Completed Epics (Done in period)</h2>")
parts.append(
    "<table><tbody><tr><th>Epic</th><th>Epic Name</th><th>Assignee</th></tr>"
    '<tr><td><a href="https://jira.xpaas.lenovo.com/browse/LATC-8672">LATC-8672</a></td>'
    "<td>33.1 Discovery, access &amp; gap analysis</td><td>Mike Fink</td></tr>"
    '<tr><td><a href="https://jira.xpaas.lenovo.com/browse/LATC-1136">LATC-1136</a></td>'
    "<td>9.4 Qira Granite v2 Model Training</td><td>Jianbang Zhang</td></tr>"
    '<tr><td><a href="https://jira.xpaas.lenovo.com/browse/LATC-1049">LATC-1049</a></td>'
    "<td>FM Evaluation Integration</td><td>Jianbang Zhang</td></tr>"
    '<tr><td><a href="https://jira.xpaas.lenovo.com/browse/LATC-1048">LATC-1048</a></td>'
    "<td>FM Training Pipeline</td><td>Jianbang Zhang</td></tr>"
    "</tbody></table>"
)

parts.append("<h2>Executive Summary</h2>")
parts.append("<ul>")
parts.append(
    f"<li><strong>Total issues moved to Done:</strong> {completed_total} across {named} contributors</li>"
)
parts.append(f"<li><strong>Completed Epics in this window:</strong> {closed_epics}</li>")
parts.append(f"<li><strong>Velocity:</strong> ~{velocity} tickets/week</li>")
parts.append(
    "<li><strong>Key themes this window:</strong> Gemma4-E2B reached a first official SM8750 eval while tool-call "
    "and empty-output defects were cleared on device. Fast-verification flooded the P7 box with Granite, Harrier, OCR, "
    "and image services. Davy discovery closed with a written Mitra vs Davy choice. Cycle time median is ~9 days; "
    "the ~16-day mean is pulled up by 25 tickets older than 30 days (PE data, Daikin UI, long eval datasets).</li>"
)
parts.append("</ul>")

parts.append("<h2>Completed Work by Epic</h2>")
parts.append("<p><em>What moved this period, grouped by epic.</em></p>")
# real epics by completed desc
for key, n in by_epic.most_common():
    if key == "No Epic linked":
        continue
    done_e, total_e, pct_e = EPIC_PCT[key]
    parts.append(
        f"<h3>{esc(label(key))} &mdash; {n} done this period &middot; {pct_e}% complete overall</h3>"
    )
    parts.append(f"<p>{esc(EPIC_NARR[key])}</p>")
parts.append(f"<h3>No Epic linked &mdash; {no_epic_n} done this period</h3>")
parts.append(f"<p>{esc(NO_EPIC_NARR)}</p>")

parts.append("<h2>Contributor Summaries</h2>")
parts.append(
    "<p><em>Each section includes a narrative of what the contributor accomplished, followed by their closed tickets.</em></p>"
)
for name in sorted(grouped_a.keys(), key=lambda s: s.lower()):
    tickets = grouped_a[name]
    parts.append(f"<h3>{esc(name)} ({len(tickets)} tickets)</h3>")
    narr = NARR.get(name)
    if not narr:
        raise SystemExit(f"missing narrative for {name!r}")
    parts.append(f"<p>{esc(narr)}</p>")
    parts.append("<ul>" + "".join(ticket_li(t) for t in tickets) + "</ul>")

parts.append("<h2>Notes</h2>")
parts.append(
    "<ul>"
    "<li>Report scope is based on Jira issues that <strong>changed to Done</strong> during 2026-08-28 through 2026-09-04 "
    "and include component <strong>Models</strong>.</li>"
    "<li>Epic names are resolved from Epic Link (<code>customfield_10006</code>) where available.</li>"
    "<li>Charts are a point-in-time snapshot generated from Jira via MCP. For always-current charts see the live charts "
    "on the parent <em>00-Regular Updates - MODELS</em> page.</li>"
    "</ul>"
)

Path("_detailed_storage.xml").write_text("".join(parts), encoding="utf-8")
print("detailed bytes", Path("_detailed_storage.xml").stat().st_size)
print("type", type_rows)
print("epic_rows", [(a, b) for a, b, *_ in epic_rows])
print("contrib", contrib_rows)
print("assignees", len(grouped_a), "jiaxin", len(grouped_a["Jiaxin JX38 Li"]))
