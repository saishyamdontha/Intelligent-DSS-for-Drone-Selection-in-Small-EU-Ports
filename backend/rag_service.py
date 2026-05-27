"""
RAG Service — AI Explanation & Chat for Drone Selection DSS
DV2573: Intelligent DSS for Drone Selection in Small EU Ports
Blekinge Institute of Technology

Provides two public functions:
  - generate_explanation(evaluation_result, question) -> str
  - answer_followup(question, evaluation_result, chat_history) -> str

Uses the Groq API (llama-3.3-70b-versatile) when GROQ_API_KEY is set in the
environment, and falls back to a deterministic template-based response so the
service remains fully functional without an API key.
"""

import os
import logging
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# ── Groq client (optional) ────────────────────────────────────────────────────

_groq_client = None

def _get_groq_client():
    """Lazily initialise the Groq client; returns None if unavailable."""
    global _groq_client
    if _groq_client is not None:
        return _groq_client

    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key:
        return None

    try:
        from groq import Groq  # type: ignore
        _groq_client = Groq(api_key=api_key)
        logger.info("Groq client initialised successfully.")
        return _groq_client
    except Exception as exc:
        logger.warning("Failed to initialise Groq client: %s", exc)
        return None


# ── Prompt builders ───────────────────────────────────────────────────────────

_SYSTEM_PROMPT = """\
You are an expert decision-support analyst specialising in unmanned aerial \
vehicle (UAV/drone) selection for small EU port operations. You have deep \
knowledge of:
- Multi-criteria decision analysis (AHP + TOPSIS methodology)
- EU drone regulations (EASA EU 2019/947, Open/Specific/Certified categories)
- Port operational requirements (surveillance, cargo inspection, security)
- Sensitivity analysis and ranking stability

Your role is to explain evaluation results clearly and concisely to port \
managers and procurement officers who may not have a technical background. \
Always ground your answers in the data provided. Be precise, professional, \
and helpful. Avoid unnecessary jargon; when technical terms are unavoidable, \
briefly define them.\
"""


def _build_context_block(evaluation_result: Dict[str, Any]) -> str:
    """Serialise the evaluation result into a compact, readable context block."""
    lines: List[str] = []

    # Scenario
    scenario = evaluation_result.get("scenario", {})
    if scenario:
        lines.append("=== SCENARIO ===")
        lines.append(f"ID          : {scenario.get('id', 'N/A')}")
        lines.append(f"Name        : {scenario.get('name', 'N/A')}")
        lines.append(f"Description : {scenario.get('description', 'N/A')}")
        lines.append(f"Mission     : {scenario.get('mission', 'N/A')}")
        lines.append(f"Environment : {scenario.get('environment', 'N/A')}")

    # Filter summary
    fs = evaluation_result.get("filter_summary", {})
    if fs:
        lines.append("\n=== KNOWLEDGE BASE FILTER ===")
        lines.append(f"Total drones    : {fs.get('total_drones', 'N/A')}")
        lines.append(f"Eligible        : {fs.get('eligible', 'N/A')}")
        lines.append(f"Eliminated      : {fs.get('eliminated', 'N/A')}")
        lines.append(f"Rules applied   : {fs.get('rules_applied', 'N/A')}")
        eliminated = fs.get("eliminated_drones", [])
        if eliminated:
            lines.append("Eliminated drones:")
            for d in eliminated[:5]:  # cap at 5 to keep prompt concise
                name = d.get("name", d.get("id", "?"))
                reasons = d.get("elimination_reasons", [])
                reason_str = "; ".join(reasons[:2]) if reasons else "see rules"
                lines.append(f"  - {name}: {reason_str}")
            if len(eliminated) > 5:
                lines.append(f"  ... and {len(eliminated) - 5} more")

    # AHP
    ahp = evaluation_result.get("ahp", {})
    if ahp:
        lines.append("\n=== AHP WEIGHTS ===")
        lines.append(f"Consistency Ratio : {ahp.get('consistency_ratio', 'N/A')}")
        lines.append(f"Consistent        : {ahp.get('is_consistent', 'N/A')}")
        top5 = ahp.get("top5_criteria_by_weight", [])
        if top5:
            lines.append("Top-5 criteria by weight:")
            for item in top5:
                if isinstance(item, (list, tuple)) and len(item) == 2:
                    crit, w = item
                    lines.append(f"  - {crit:<30} {float(w):.4f}")
                elif isinstance(item, dict):
                    lines.append(f"  - {item}")

    # Ranking (top 5)
    ranking = evaluation_result.get("ranking", [])
    if ranking:
        lines.append("\n=== TOPSIS RANKING (top 5) ===")
        for r in ranking[:5]:
            lines.append(
                f"  #{r.get('rank', '?')}  {r.get('name', '?'):<35} "
                f"CC={r.get('closeness_coefficient', 0):.4f}  "
                f"({r.get('manufacturer', '?')}, {r.get('type', '?')})"
            )

    # Sensitivity (top 5)
    sensitivity = evaluation_result.get("sensitivity", {})
    sa_results = sensitivity.get("results", [])
    if sa_results:
        lines.append("\n=== SENSITIVITY ANALYSIS (top 5) ===")
        settings = sensitivity.get("settings", {})
        lines.append(
            f"Simulations: {settings.get('n_simulations', '?')}, "
            f"Perturbation: ±{int(float(settings.get('perturbation_pct', 0)) * 100)}%"
        )
        for r in sa_results[:5]:
            lines.append(
                f"  #{r.get('base_rank', '?')}  {r.get('name', '?'):<35} "
                f"Top-3%={r.get('top3_frequency_pct', 0):.1f}%  "
                f"Stability={r.get('stability', '?')}"
            )

    # Recommendation
    rec = evaluation_result.get("recommendation", {})
    if rec:
        lines.append("\n=== RECOMMENDATION ===")
        lines.append(f"Top drone   : {rec.get('top_drone', 'N/A')}")
        lines.append(f"Drone ID    : {rec.get('top_drone_id', 'N/A')}")
        lines.append(f"CC score    : {rec.get('closeness_coefficient', 'N/A')}")
        lines.append(f"Stability   : {rec.get('stability', 'N/A')}")

    return "\n".join(lines)


# ── LLM call ──────────────────────────────────────────────────────────────────

def _call_groq(
    messages: List[Dict[str, str]],
    model: str = "llama-3.3-70b-versatile",
    max_tokens: int = 1024,
    temperature: float = 0.4,
) -> Optional[str]:
    """Call the Groq API and return the assistant message, or None on failure."""
    client = _get_groq_client()
    if client is None:
        return None

    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return response.choices[0].message.content.strip()
    except Exception as exc:
        logger.warning("Groq API call failed: %s", exc)
        return None


# ── Template fallback ─────────────────────────────────────────────────────────

def _template_explanation(
    evaluation_result: Dict[str, Any],
    question: Optional[str],
) -> str:
    """
    Generate a structured, human-readable explanation from the evaluation data
    without calling any external API.
    """
    scenario = evaluation_result.get("scenario", {})
    fs = evaluation_result.get("filter_summary", {})
    ahp = evaluation_result.get("ahp", {})
    ranking = evaluation_result.get("ranking", [])
    sensitivity = evaluation_result.get("sensitivity", {})
    rec = evaluation_result.get("recommendation", {})

    scenario_name = scenario.get("name", "the selected scenario")
    top_drone = rec.get("top_drone", ranking[0]["name"] if ranking else "N/A")
    cc = rec.get("closeness_coefficient", ranking[0].get("closeness_coefficient", 0) if ranking else 0)
    stability = rec.get("stability", "UNKNOWN")
    eligible = fs.get("eligible", "?")
    eliminated = fs.get("eliminated", "?")
    total = fs.get("total_drones", "?")
    cr = ahp.get("consistency_ratio", "?")
    is_consistent = ahp.get("is_consistent", True)

    top5_criteria = ahp.get("top5_criteria_by_weight", [])
    criteria_str = ""
    if top5_criteria:
        parts = []
        for item in top5_criteria[:3]:
            if isinstance(item, (list, tuple)) and len(item) == 2:
                crit, w = item
                parts.append(f"{crit.replace('_', ' ')} ({float(w):.3f})")
        criteria_str = ", ".join(parts) if parts else ""

    sa_results = sensitivity.get("results", [])
    top3_pct = ""
    if sa_results:
        top_sa = next((r for r in sa_results if r.get("base_rank") == 1), sa_results[0])
        top3_pct = f"{top_sa.get('top3_frequency_pct', 0):.1f}%"

    lines = [
        f"## DSS Evaluation Summary — {scenario_name}",
        "",
        f"**Recommended Drone: {top_drone}**",
        "",
        f"The Intelligent Decision Support System evaluated {total} candidate drones "
        f"against the requirements of the '{scenario_name}' scenario. After applying "
        f"the Knowledge Base rule engine ({fs.get('rules_applied', '?')} rules covering "
        f"regulatory compliance, operational constraints, and expert heuristics), "
        f"{eliminated} drones were eliminated, leaving {eligible} eligible candidates "
        f"for the AHP-TOPSIS multi-criteria ranking.",
        "",
        f"**Why {top_drone}?**",
        f"{top_drone} achieved the highest TOPSIS Closeness Coefficient (CC = {float(cc):.4f}), "
        f"meaning it is closest to the ideal solution and furthest from the worst-case "
        f"solution across all {len(top5_criteria) if top5_criteria else 20} weighted criteria. "
        + (f"The most influential criteria in this evaluation were: {criteria_str}." if criteria_str else ""),
        "",
        f"**AHP Weight Consistency**",
        f"The pairwise comparison matrix produced a Consistency Ratio (CR) of {cr}. "
        + ("This is below the 0.10 threshold, confirming the expert judgements are logically consistent."
           if is_consistent
           else "This exceeds the 0.10 threshold — the weight judgements show some inconsistency and results should be interpreted with caution."),
        "",
        f"**Ranking Stability**",
        f"Monte Carlo sensitivity analysis perturbed the AHP weights by ±20% across "
        f"{sensitivity.get('settings', {}).get('n_simulations', '?')} simulations. "
        + (f"{top_drone} appeared in the top-3 in {top3_pct} of simulations, " if top3_pct else "")
        + f"indicating {stability.lower()} ranking stability.",
    ]

    if ranking and len(ranking) >= 2:
        lines += [
            "",
            f"**Top-3 Ranked Drones**",
        ]
        for r in ranking[:3]:
            lines.append(
                f"  {r['rank']}. {r['name']} (CC = {r['closeness_coefficient']:.4f}, "
                f"{r['manufacturer']}, {r['type']})"
            )

    if question:
        lines += [
            "",
            f"**Regarding your question:** \"{question}\"",
            "For a detailed answer to this specific question, please ensure the GROQ_API_KEY "
            "environment variable is configured to enable AI-powered responses. The data above "
            "contains all the information needed to address your query.",
        ]

    return "\n".join(lines)


def _template_followup(
    question: str,
    evaluation_result: Dict[str, Any],
    chat_history: List[Dict[str, str]],
) -> str:
    """
    Generate a context-aware template response for follow-up questions
    when the LLM is unavailable.
    """
    ranking = evaluation_result.get("ranking", [])
    rec = evaluation_result.get("recommendation", {})
    scenario = evaluation_result.get("scenario", {})
    ahp = evaluation_result.get("ahp", {})
    sensitivity = evaluation_result.get("sensitivity", {})
    fs = evaluation_result.get("filter_summary", {})

    top_drone = rec.get("top_drone", ranking[0]["name"] if ranking else "N/A")
    scenario_name = scenario.get("name", "the selected scenario")
    q_lower = question.lower()

    # Keyword-based routing for common question patterns
    if any(kw in q_lower for kw in ["why", "reason", "explain", "how"]):
        cc = rec.get("closeness_coefficient", 0)
        top5 = ahp.get("top5_criteria_by_weight", [])
        criteria_str = ""
        if top5:
            parts = []
            for item in top5[:3]:
                if isinstance(item, (list, tuple)) and len(item) == 2:
                    crit, w = item
                    parts.append(f"{crit.replace('_', ' ')} (weight {float(w):.3f})")
            criteria_str = ", ".join(parts)
        return (
            f"{top_drone} was recommended for '{scenario_name}' because it achieved "
            f"the highest TOPSIS Closeness Coefficient (CC = {float(cc):.4f}), "
            f"indicating it best balances all evaluation criteria. "
            + (f"The top-weighted criteria driving this result were: {criteria_str}. " if criteria_str else "")
            + "These weights were derived from the AHP pairwise comparison matrix, "
            "reflecting expert judgements about the relative importance of each criterion "
            "for this type of port operation."
        )

    if any(kw in q_lower for kw in ["rank", "second", "third", "alternative", "compare"]):
        if len(ranking) >= 2:
            alts = [
                f"#{r['rank']} {r['name']} (CC = {r['closeness_coefficient']:.4f})"
                for r in ranking[1:4]
            ]
            return (
                f"The top alternatives to {top_drone} are: {', '.join(alts)}. "
                "These drones passed all Knowledge Base constraints and scored well "
                "across the weighted criteria, but did not achieve as high a Closeness "
                "Coefficient as the top recommendation. They may be worth considering "
                "if budget, availability, or specific operational requirements differ "
                "from the scenario defaults."
            )
        return f"Only one drone was eligible after applying the Knowledge Base rules for '{scenario_name}'."

    if any(kw in q_lower for kw in ["stable", "stability", "robust", "reliable", "sensitivity"]):
        sa_results = sensitivity.get("results", [])
        settings = sensitivity.get("settings", {})
        if sa_results:
            top_sa = next((r for r in sa_results if r.get("base_rank") == 1), sa_results[0])
            return (
                f"The sensitivity analysis ran {settings.get('n_simulations', '?')} Monte Carlo "
                f"simulations, perturbing AHP weights by ±{int(float(settings.get('perturbation_pct', 0.2)) * 100)}%. "
                f"{top_drone} appeared in the top-3 in {top_sa.get('top3_frequency_pct', 0):.1f}% "
                f"of simulations, giving it a '{top_sa.get('stability', 'UNKNOWN')}' stability rating. "
                "This means the recommendation is "
                + ("robust to changes in expert weight judgements."
                   if top_sa.get("stability") == "HIGH"
                   else "moderately sensitive to weight changes — consider reviewing the AHP matrix."
                   if top_sa.get("stability") == "MEDIUM"
                   else "sensitive to weight changes — the ranking may shift if priorities are adjusted.")
            )

    if any(kw in q_lower for kw in ["cost", "price", "budget", "expensive", "cheap"]):
        top_ranked = ranking[0] if ranking else {}
        initial_cost = top_ranked.get("criteria_scores", {}).get("initial_cost")
        op_cost = top_ranked.get("criteria_scores", {}).get("operational_cost")
        return (
            f"Cost is one of the criteria evaluated in the TOPSIS model. "
            f"{top_drone} was selected as the best overall value considering all "
            f"20 weighted criteria — not just cost alone. "
            + (f"Its weighted initial cost score was {float(initial_cost):.4f} and "
               f"operational cost score was {float(op_cost):.4f} (lower weighted scores "
               f"indicate higher cost relative to other candidates). "
               if initial_cost is not None and op_cost is not None else "")
            + "If cost is your primary concern, you can adjust the AHP pairwise matrix "
            "to increase the weight of 'initial_cost' and 'operational_cost' criteria "
            "and re-run the evaluation."
        )

    if any(kw in q_lower for kw in ["regulat", "compliance", "easa", "legal", "category"]):
        eliminated = fs.get("eliminated_drones", [])
        reg_eliminated = [
            d for d in eliminated
            if any("REG-" in r for r in d.get("elimination_reasons", []))
        ]
        return (
            f"All drones were evaluated against EU EASA regulations (EU 2019/947). "
            f"{len(reg_eliminated)} drone(s) were eliminated due to regulatory non-compliance "
            f"for the '{scenario_name}' scenario. "
            f"{top_drone} meets all applicable regulatory requirements for this scenario. "
            "The regulatory compliance criterion is also included as a weighted factor "
            "in the TOPSIS ranking, rewarding drones with higher compliance categories "
            "(e.g. Specific > Open-A3 > Open-A2 > Open-A1)."
        )

    if any(kw in q_lower for kw in ["weight", "criteria", "ahp", "priority", "important"]):
        top5 = ahp.get("top5_criteria_by_weight", [])
        if top5:
            parts = []
            for item in top5:
                if isinstance(item, (list, tuple)) and len(item) == 2:
                    crit, w = item
                    parts.append(f"{crit.replace('_', ' ')} ({float(w):.4f})")
            return (
                f"The AHP (Analytic Hierarchy Process) derived the following top criteria "
                f"weights for this evaluation: {', '.join(parts)}. "
                "These weights reflect expert judgements encoded in the pairwise comparison "
                "matrix and determine how much each criterion influences the final TOPSIS ranking. "
                f"The Consistency Ratio is {ahp.get('consistency_ratio', 'N/A')}, which is "
                + ("within the acceptable threshold (< 0.10)."
                   if ahp.get("is_consistent") else "above the 0.10 threshold — consider revising the matrix.")
            )

    # Generic fallback
    turns = len(chat_history)
    context_note = (
        f" (This is follow-up question #{turns + 1} in our conversation.)"
        if turns > 0 else ""
    )
    return (
        f"Based on the DSS evaluation for '{scenario_name}', the recommended drone is "
        f"{top_drone} with a Closeness Coefficient of "
        f"{rec.get('closeness_coefficient', 0):.4f}.{context_note} "
        "To get a more detailed AI-powered answer to your specific question, "
        "please configure the GROQ_API_KEY environment variable. "
        "In the meantime, you can explore the full evaluation data returned by the "
        "/evaluate endpoint, which contains the complete ranking, AHP weights, "
        "and sensitivity analysis results."
    )


# ── Public API ────────────────────────────────────────────────────────────────

def generate_explanation(
    evaluation_result: Dict[str, Any],
    question: Optional[str] = None,
) -> str:
    """
    Generate an AI explanation of the DSS evaluation result.

    Parameters
    ----------
    evaluation_result : dict
        The full evaluation payload returned by the /evaluate endpoint,
        containing scenario, filter_summary, ahp, ranking, sensitivity,
        and recommendation keys.
    question : str, optional
        An optional specific question from the user to focus the explanation.

    Returns
    -------
    str
        A human-readable explanation of the evaluation results.
    """
    context = _build_context_block(evaluation_result)

    user_content = (
        f"Please explain the following drone selection evaluation results for a "
        f"port operations manager. Be clear, concise, and highlight the key "
        f"reasons why the top-ranked drone was recommended.\n\n"
        f"{context}"
    )
    if question:
        user_content += f"\n\nAdditionally, please address this specific question: {question}"

    messages = [
        {"role": "system", "content": _SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]

    result = _call_groq(messages, max_tokens=1200, temperature=0.4)
    if result:
        return result

    logger.info("Using template fallback for generate_explanation.")
    return _template_explanation(evaluation_result, question)


def answer_followup(
    question: str,
    evaluation_result: Dict[str, Any],
    chat_history: List[Dict[str, str]],
) -> str:
    """
    Answer a follow-up question about the evaluation results, maintaining
    multi-turn conversation context.

    Parameters
    ----------
    question : str
        The user's follow-up question.
    evaluation_result : dict
        The evaluation payload (same structure as generate_explanation).
    chat_history : list of dict
        Previous conversation turns, each with 'role' ('user' or 'assistant')
        and 'content' keys.

    Returns
    -------
    str
        A contextual answer to the follow-up question.
    """
    context = _build_context_block(evaluation_result)

    # Build the message list: system → context injection → history → new question
    messages: List[Dict[str, str]] = [
        {"role": "system", "content": _SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                "Here is the drone selection evaluation data for our conversation:\n\n"
                f"{context}\n\n"
                "I will now ask you questions about this evaluation."
            ),
        },
        {
            "role": "assistant",
            "content": (
                "Understood. I have reviewed the evaluation results. I can see the "
                "scenario details, the Knowledge Base filtering, AHP weights, TOPSIS "
                "ranking, and sensitivity analysis. Please go ahead with your questions."
            ),
        },
    ]

    # Append prior conversation turns (cap at last 10 to stay within token limits)
    for turn in chat_history[-10:]:
        role = turn.get("role", "user")
        content = turn.get("content", "")
        if role in ("user", "assistant") and content:
            messages.append({"role": role, "content": content})

    # Append the new question
    messages.append({"role": "user", "content": question})

    result = _call_groq(messages, max_tokens=900, temperature=0.5)
    if result:
        return result

    logger.info("Using template fallback for answer_followup.")
    return _template_followup(question, evaluation_result, chat_history)
