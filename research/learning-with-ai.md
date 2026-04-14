# How developers actually learn from LLMs: an arXiv research synthesis

**Developers who treat LLMs as Socratic tutors rather than answer machines are the ones who genuinely upskill—and a fast-growing body of empirical research now shows exactly which strategies separate deep learners from cognitive offloaders.** Between October 2025 and April 2026, at least two dozen arXiv papers (spanning CS, HCI, and education) tackled this question through randomized controlled trials, longitudinal classroom studies, EEG neuroimaging, and systematic reviews. The consensus is striking: unstructured LLM use correlates with declining learning outcomes, but carefully scaffolded interaction—pedagogical prompting, co-decomposition, friction-induced engagement—can produce measurable skill gains. This report synthesizes those findings across five thematic areas, drawing on **30+ papers** with empirical evidence.

---

## 1. Pedagogical prompting strategies that produce real skill gains

The single most actionable finding from this period comes from a **semester-long RCT with 979 CS1 students** (Xiao et al., arXiv:2602.16033, February 2026). The study tested four instructional conditions based on the ICAP framework's cognitive engagement hierarchy (Interactive > Constructive > Active > Passive). All conditions significantly improved prompting skills, with gains increasing progressively as engagement intensity rose. Students who learned to construct "pedagogical prompts"—structured around five components: problem identification, problem context, learning goal, output constraints (e.g., "give hints, not answers"), and reflection—showed more productive struggle and deeper conceptual engagement than controls.

This builds on the pedagogical prompting framework introduced by Xiao et al. (arXiv:2506.19107), which surveyed 36 CS educators and tested the approach with 22 novice students. The core insight: **prompting literacy is itself a teachable curricular object**. Students who learned to specify what they *didn't* understand, constrain LLM output to hints rather than solutions, and add reflection steps showed significantly improved help-seeking skills.

Three other scaffolded systems validated complementary strategies. **SocraticAI** (Sunil & Thakkar, arXiv:2512.03501, December 2025) enforced well-formulated questions, reflective engagement, and daily usage limits through technical guardrails. Within 2–3 weeks, over 75% of students progressed from vague help-seeking to sophisticated problem decomposition. **DBox** (Ma et al., arXiv:2502.19133) used a co-decomposition paradigm where learners must specify their own decomposition steps before the LLM assists—a within-subjects study (N=24) found this significantly improved learning gains, cognitive engagement, and critical thinking compared to unrestricted ChatGPT. And **Owlgorithm** (Nieto-Cardenas et al., arXiv:2511.09969, November 2025), which uses GPT-4o to generate Bloom's Taxonomy-aligned reflection prompts, showed promise for filling the "reflection gap" in competitive programming where students typically skip self-evaluation.

The strategies that consistently work share a common mechanism: they **force the learner to do cognitive work before the LLM responds**. Whether that means decomposing a problem, specifying a learning goal, or predicting an output, the friction is the feature.

---

## 2. Debugging helps most, code generation helps least—for learning

A systematic review of **58 peer-reviewed studies** (arXiv:2510.03884, October 2025) found that 94.8% reported enhanced programming support from AI, but **65.5% flagged over-reliance and superficial learning** as a key challenge. The task type matters enormously for whether LLM assistance produces learning or mere completion.

**Debugging and error localization** emerge as the highest-value learning tasks. A survey of LLM applications in programming education (Pitts et al., arXiv:2510.03719, October 2025) found debugging assistance is the **#1 reason students seek LLM help**, and when structured properly—through hypothesis-driven approaches—it produces genuine skill development. The HypoCompass system (arXiv:2310.05292, updated 2025) demonstrated this: students focus on constructing hypotheses about code errors while the LLM handles adjacent code-completion tasks, yielding a **12% improvement in pre-to-post test scores** and 14% faster completion. The key is task delegation—students practice the hard cognitive skill (diagnosis) while offloading the routine part (writing fix code).

**Code explanation and conceptual understanding** rank second. LLM-generated explanations are generally rated as good or better than peer-generated ones, and students report high value from being able to interrogate code logic interactively. However, a critical study titled "Beginners Struggle to Understand LLM-Generated Code" (arXiv:2504.19037) found that CS1 students often cannot explain how LLM-generated code works even when it passes all tests—highlighting that **code comprehension is an underexplored learning dimension**.

**Code generation and completion** produce the largest productivity gains but the **weakest learning outcomes**. A controlled experiment with GitHub Copilot (Shihab et al., arXiv:2506.10051) found students completed tasks 35% faster and made 50% more progress, but students who adopted Copilot suggestions at a granular level learned significantly more than those who accepted suggestions wholesale. A counterbalanced study in CS1 (Andleeb et al., arXiv:2510.00946, October 2025) confirmed that ChatGPT use improved rubric scores and code quality but produced **mixed results for conceptual understanding**—gains for some topics, losses for others.

**Personalized tutoring with guardrails** shows the most consistent positive results. The landmark CodeAid deployment (Kazemitabaar et al., arXiv:2401.11314)—12 weeks, 700 students, 8,000+ interactions—demonstrated that providing pseudo-code explanations and annotated fix suggestions *without revealing code solutions* achieves ~90% helpfulness while maintaining learning engagement. A scoping review of 32 studies (arXiv:2512.20714, December 2025) confirmed that **explanation-first guidance, solution withholding, graduated hint ladders, and artifact grounding consistently outperform unconstrained chat interfaces**.

---

## 3. "Learning mode" versus "getting work done" triggers different prompting behaviors

Several studies now document distinct interaction patterns depending on whether developers seek understanding or output. A survey of 199 scientific researchers (arXiv:2502.17348) found a clean split: **chat interfaces (ChatGPT) are used for learning and understanding, while inline tools (Copilot) are used for speed**. One participant captured the divide: "I don't read documentation anymore because I can ask ChatGPT to read them."

The most granular evidence comes from the BNY Mellon study (arXiv:2602.03593, February 2026), surveying **2,989 engineers** with follow-up interviews. Senior developers reported deliberately **avoiding AI for learning-oriented tasks** while embracing it for productivity tasks. One engineer noted: "If I have a team member who is brand new, they need to learn new technology. However, if the code just works, then you just accept it." The concern was specific: junior developers are no longer learning to "analyze stack traces" or debug from first principles.

Ma et al.'s three-year longitudinal study of 10,000+ student-AI dialogue logs (arXiv:2511.04144, November 2025) revealed that most student interactions were confined to a single metacognitive phase—predominantly **monitoring** (checking outputs)—rather than traversing a complete planning→monitoring→evaluation cycle. Students in learning mode, when prompted to do so, engaged in planning (specifying what they wanted to understand) and evaluation (reflecting on whether they understood the response). Students in task-completion mode skipped directly to monitoring: paste code, check if it works, move on.

The behavioral study "Not Everyone Wins with LLMs" (arXiv:2509.21890) documented **"prompting rabbit holes"** where less-experienced users iterate on prompts without convergence—a pattern characteristic of task-completion mode without clear learning goals. In contrast, effective learners specified success criteria before requesting code, verified assumptions explicitly, and inspected data deeply. **Technical experience, not LLM experience, predicted performance**—suggesting that domain knowledge is prerequisite to productive LLM interaction.

---

## 4. What separates genuine learners from cognitive offloaders

The evidence here is now robust and converges from multiple methodological angles. A systematic review screening 3,453 records (arXiv:2509.21972) proposed an **LLM-Risk Adapted Learning Model** identifying the cascade: technical risks → pedagogical risks → learning outcome risks. The core distinction: **more competent learners engage strategically** (revisiting, integrating, refining information) while less competent learners rely on the immediacy and convenience of LLM outputs, bypassing essential processes like paraphrasing, reflection, and synthesis.

Neuroimaging evidence reinforces this. An EEG study with 54 participants over four months (Kosmyna et al., arXiv:2506.08872, updated December 2025) found that **LLM users displayed the weakest brain connectivity patterns** while brain-only participants showed the strongest, most distributed networks. Most concerning: when LLM users were switched to working without AI, they showed persistently reduced engagement—what the authors termed accumulated **"cognitive debt."** Self-reported ownership of work was lowest in the LLM group.

A randomized experiment in an operations research course (arXiv:2510.16019, October 2025) demonstrated the practical consequence: students given AI tools showed **decreased knowledge acquisition and increased over-reliance** compared to controls. The authors invoke the "Law of Less Work"—people systematically avoid cognitive demand, so AI tools producing results with minimal mental effort will be popular but ineffective at building lasting knowledge.

Several behavioral markers now distinguish learners from offloaders:

- **Leading vs. being led**: Bo et al. (arXiv:2505.08063) categorized novice debugging interactions as either "leading the LLM" (formulating hypotheses, directing investigation) or "led by the LLM" (passively following suggestions). Users with incorrect mental models asked poorly phrased queries, triggering rabbit holes of over-reliance where the LLM's sycophancy reinforced faulty understanding.
- **Granular vs. wholesale adoption**: Copilot users who adopted suggestions at a granular level—examining, modifying, and integrating small pieces—learned significantly more than those who accepted large blocks wholesale (arXiv:2506.10051).
- **Viewing AI as tutor vs. answer provider**: A study of 20 undergraduates (arXiv:2508.05999) found that students who framed AI as a "learning facilitator or debugging aid" demonstrated reflective use and deeper comprehension, while those viewing it as an "answer provider" showed superficial engagement and **difficulty transferring knowledge to unaided tasks**.
- **Self-efficacy and need for cognition**: Pitts et al. (arXiv:2506.13845) found that appropriate reliance on AI was significantly predicted by programming self-efficacy, programming literacy, and need for cognition—but not by self-reported AI knowledge.

The two-year longitudinal SE study (Kataoka et al., arXiv:2511.23157, November 2025) adds a structural dimension: powerful LLMs act as both **"equalizers"** (boosting weaker students' average performance) and **"amplifiers"** (dramatically widening absolute performance gaps), creating new equity challenges.

---

## 5. Metacognitive scaffolding and friction-induced design make knowledge stick

The most sophisticated design work focuses on building metacognitive checkpoints into LLM interactions. Kazemitabaar et al. (arXiv:2410.08922, presented at CHI 2025) tested **seven cognitive engagement techniques** for AI-generated code across two studies (N=82 between-subjects, N=42 within-subjects). The top performers were **Lead-and-Reveal** (learner first decomposes the problem, then AI code is gradually revealed) and **Trace-and-Predict** (learner traces through AI-generated code and predicts outputs before seeing results). Lead-and-Reveal significantly improved alignment between perceived and actual coding ability without increasing cognitive load. The authors coined the concept of **"Friction-Induced AI"**—deliberately adding productive friction to prevent long-term skill erosion from over-reliance.

The metacognition-focused longitudinal study by Ma et al. (arXiv:2511.04144, November 2025) identified specific design principles from analyzing 10,000+ dialogue logs: AI responses providing overly complete solutions **discourage persistence and exploration**, while step-by-step pseudo-code scaffolds **encourage reflection**. The study found that most student-AI exchanges were confined to a single metacognitive phase, highlighting what the authors call **"metacognitive laziness"**—the tendency to let AI do the thinking. Effective designs should nudge students through the full planning→monitoring→evaluation cycle.

A theoretical framework for metacognitive intervention in human-AI interaction (Lopez-Lopez et al., arXiv:2602.01959, February 2026) proposes specific intervention points: interaction initiation and role gating (asking "am I using this as a tool, advisor, or crutch?"), confidence calibration (checking whether you actually understand the output), and stake-sensitive rules (higher-stakes learning tasks should involve more friction). The framework addresses **cognitive-behavioral drift**—the gradual, often unconscious shift toward dependency that occurs over repeated AI interactions.

On the system design front, the scoping review of 32 GenAI personalization studies (arXiv:2512.20714, December 2025) identified four successful implementation patterns: **(1)** context-aware tutoring anchored in student artifacts (not generic responses), **(2)** multi-level hint structures requiring reflection before advancing, **(3)** composition with traditional CS infrastructure (IDEs, autograders), and **(4)** explanation-first guidance with solution withholding. These patterns consistently produced better learning processes than unconstrained chat.

Finally, the question of whether assessment design can rescue learning even with unrestricted AI use received a cautiously optimistic answer. Chung (arXiv:2601.17024, January 2026) found **no meaningful correlation between GenAI usage levels and assessment outcomes** when understanding was verified through independent, AI-free written quizzes—suggesting that cognitive offloading risks can be mitigated through assessment design that separates production from comprehension.

---

## Papers referenced in this report

| arXiv ID | Title (abbreviated) | Date | Type |
|---|---|---|---|
| 2602.16033 | Transforming GenAI Policy to Prompting Instruction (RCT, N=979) | Feb 2026 | RCT |
| 2511.04144 | Scaffolding Metacognition in Programming Education | Nov 2025 | Longitudinal empirical |
| 2512.03501 | SocraticAI: Guided CS Tutors Through Scaffolded Interaction | Dec 2025 | System + deployment |
| 2511.09969 | Owlgorithm: SRL in Competitive Programming | Nov 2025 | System + evaluation |
| 2510.03884 | Teaching with AI: Systematic Review (58 studies) | Oct 2025 | Systematic review |
| 2510.03719 | Survey of LLM-Based Applications in Programming Education | Oct 2025 | Survey |
| 2509.21972 | From Superficial Outputs to Superficial Learning | Sep 2025 | Systematic review |
| 2512.20714 | GenAI-Enabled Personalization in CS Education (32 studies) | Dec 2025 | Scoping review |
| 2510.16019 | Impact of AI Tools: Decreasing Knowledge and Over-Reliance | Oct 2025 | Randomized experiment |
| 2510.00946 | ChatGPT in Introductory Programming | Oct 2025 | Counterbalanced experiment |
| 2511.23157 | Amplifiers or Equalizers? LLM Evolution in SE PBL | Nov 2025 | Longitudinal study |
| 2602.03593 | Beyond the Commit: Developer Perspectives (N=2,989) | Feb 2026 | Survey + interviews |
| 2601.08045 | Cognitive Biases in LLM-Assisted Software Development | Jan 2026 | Mixed-methods |
| 2602.01959 | Boosting Metacognition in Human-AI Interaction | Feb 2026 | Theoretical framework |
| 2601.17024 | Ensuring CS Learning: Open GenAI Policies + Written Quizzes | Jan 2026 | Empirical study |
| 2601.20112 | AI Coding Assistants in the Enterprise | Jan 2026 | Enterprise empirical |
| 2511.18985 | LLM Chatbots in High School Programming | Nov 2025 | Design-based research |
| 2511.06428 | Walking the Tightrope of LLMs for Software Development | Nov 2025 | Qualitative interviews |
| 2512.23327 | Empirical Study of GenAI Adoption in SE | Dec 2025 | Survey (N=204) |
| 2410.08922 | Cognitive Engagement Techniques with AI-Generated Code | Oct 2024 (CHI 2025) | Two empirical studies |
| 2506.19107 | Pedagogical Prompting in CS Education | Jun 2025 | Framework + user study |
| 2502.19133 | DBox: Learner-LLM Co-Decomposition | Feb 2025 | Within-subjects study |
| 2506.08872 | Your Brain on ChatGPT: Cognitive Debt (EEG) | Jun 2025 | Neuroimaging study |
| 2509.21890 | Not Everyone Wins with LLMs: Behavioral Patterns | Sep 2025 | Behavioral study |
| 2506.10051 | GitHub Copilot Effects on Student Programming | Jun 2025 | Controlled experiment |
| 2506.13845 | Students' Reliance on AI: Contributing Factors | Jun 2025 | Controlled experiment |
| 2508.05999 | Student Attitudes Toward AI in Programming Education | Aug 2025 | Qualitative study |
| 2505.08063 | Novice Workflows in LLM-Assisted Debugging | May 2025 | Formative user study |
| 2502.17348 | How Scientists Use LLMs to Program | Feb 2025 | Survey + interviews |
| 2401.11314 | CodeAid: LLM-Based Programming Assistant (700 students) | Jan 2024 (CHI 2024) | Deployment study |
| 2310.05292 | HypoCompass: LLM-Augmented Debugging Tutor | 2023 (updated 2025) | System + evaluation |

---

## Conclusion

The research from this six-month window converges on a clear thesis: **the default mode of LLM interaction—ask for code, receive code, paste code—actively undermines learning**, with evidence now spanning behavioral studies, longitudinal classroom data, and even neuroimaging. But the picture is not deterministic. Structured interventions work. The most robust finding is that **pedagogical prompting**—teaching learners to specify their knowledge gaps, constrain LLM output to hints, and reflect on responses—transforms the same tool from a learning inhibitor into a learning accelerator. The RCT with 979 students (arXiv:2602.16033) provides the strongest causal evidence to date.

Three design principles emerge as most actionable: first, **require learner cognitive work before LLM output appears** (co-decomposition, lead-and-reveal, hypothesis-first debugging); second, **withhold complete solutions and use graduated hint structures** anchored in student artifacts; third, **build metacognitive checkpoints** that prompt planning, monitoring, and evaluation rather than just answer-checking. The critical gap remaining is longitudinal evidence on whether these interventions produce durable skill transfer—most studies still measure immediate post-test performance rather than retention weeks or months later. The field is moving fast, but the message for practitioners is already actionable: the friction is the feature.