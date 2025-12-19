from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import List, Sequence, Tuple

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT / "stage4_predicate"))

from reasoner import KB  # type: ignore

Fact = Tuple[str, ...]
Rule = Tuple

DEFAULT_FACTS = """parent(alice,bob)
parent(bob,carol)
parent(carol,dana)"""

DEFAULT_RULES = """forall x,y: parent(x,y) -> ancestor(x,y)
forall x,y,z: parent(x,y) & ancestor(y,z) -> ancestor(x,z)
forall x,y: ancestor(x,y) -> connected(x,y)"""

DEFAULT_QUERY = "ancestor(?who, dana)"


class ParseError(Exception):
    """Raised when the text-based KB format cannot be parsed."""


def parse_fact(line: str) -> Fact:
    # === QUIZ: parse a textual fact into predicate tuple ===
    return parse_predicate(line, [])


def parse_predicate(token: str, variables: Sequence[str]) -> Fact:
    # === QUIZ: parse predicate tokens, normalizing variables and constants ===
    raw_token = token.strip()
    # "name(arg1, arg2)" 형태 매칭
    regex_match = re.match(r"(\w+)\s*\((.*)\)", raw_token)
    if not regex_match:
        raise ParseError(f"잘못된 술어 형식입니다: {raw_token}")

    pred_name = regex_match.group(1)
    args_str = regex_match.group(2)

    # 쉼표로 인자 분리 및 공백 제거
    raw_args = [arg.strip() for arg in args_str.split(",") if arg.strip()]

    normalized_args = []
    for arg in raw_args:
        # 1. 이미 '?'로 시작하면 변수 그대로 사용
        if arg.startswith("?"):
            normalized_args.append(arg)
        # 2. 규칙의 forall 변수 목록에 포함된 경우 '?' 붙여서 변수화
        elif arg in variables:
            normalized_args.append(f"?{arg}")
        # 3. 그 외에는 상수(Constant)로 처리
        else:
            normalized_args.append(arg)

    return (pred_name, *normalized_args)


def parse_rule(line: str) -> Rule:
    # === QUIZ: translate surface rule syntax into Stage 4 format ===
    clean_line = line.strip()

    # "forall x,y: ..." 파싱
    header_match = re.match(r"forall\s+([^:]+):\s*(.*)", clean_line, re.IGNORECASE)
    if not header_match:
        raise ParseError(f"규칙은 'forall'로 시작해야 합니다: {clean_line}")

    vars_part = header_match.group(1)
    body_part = header_match.group(2)

    # 변수 목록 추출 (예: ['x', 'y'])
    scope_vars = [v.strip() for v in vars_part.split(",")]

    # "전제 -> 결론" 분리
    if "->" not in body_part:
        raise ParseError(f"규칙에 함의 기호('->')가 없습니다: {clean_line}")

    lhs_str, rhs_str = body_part.split("->", 1)

    # 전제(Premises) 파싱
    premises_list = [parse_predicate(p, scope_vars) for p in lhs_str.split("&")]

    # 결론(Conclusion) 파싱
    conclusion_pred = parse_predicate(rhs_str, scope_vars)

    # 내부 표현용 변수명 변환 (x -> ?x)
    internal_vars = [f"?{v}" for v in scope_vars]

    return ("FORALL", internal_vars, (premises_list, conclusion_pred))


def parse_facts_block(text: str) -> List[Fact]:
    # === QUIZ: split multi-line facts and parse each line ===
    return [parse_fact(l) for l in text.splitlines() if l.strip()]


def parse_rules_block(text: str) -> List[Rule]:
    # === QUIZ: parse a block of rule lines ===
    return [parse_rule(l) for l in text.splitlines() if l.strip()]


def parse_query(text: str) -> Fact:
    # === QUIZ: parse a query string into predicate form ===
    return parse_predicate(text, [])


def main() -> None:
    st.set_page_config(page_title="Logic Reasoner", layout="wide")
    st.title("Stage 6 — Streamlit KB UI")

    with st.sidebar:
        st.header("설정 (Settings)")
        if st.button("샘플 데이터 로드 (Load Sample)"):
            st.session_state["f_input"] = DEFAULT_FACTS
            st.session_state["r_input"] = DEFAULT_RULES
            st.session_state["q_input"] = DEFAULT_QUERY
        if st.button("결과 초기화 (Clear Results)"):
            st.session_state.pop("last_facts", None)
            st.session_state.pop("last_query_results", None)

    if "f_input" not in st.session_state:
        st.session_state["f_input"] = DEFAULT_FACTS
    if "r_input" not in st.session_state:
        st.session_state["r_input"] = DEFAULT_RULES
    if "q_input" not in st.session_state:
        st.session_state["q_input"] = DEFAULT_QUERY

    left, right = st.columns([1.2, 1])

    # --- 입력 영역 (왼쪽) ---
    with left:
        st.subheader("입력 (Input)")

        with st.form("kb_form", clear_on_submit=False):
            f_col, r_col = st.columns(2)

            with f_col:
                facts_text = st.text_area(
                    "Facts (사실)",
                    value=st.session_state["f_input"],
                    height=280,
                )

            with r_col:
                rules_text = st.text_area(
                    "Rules (규칙)",
                    value=st.session_state["r_input"],
                    height=280,
                )

            query_text = st.text_input(
                "Query (질의)",
                value=st.session_state["q_input"],
            )

            run_button = st.form_submit_button(
                "추론 실행 (Run Inference)",
                use_container_width=True,
            )

    # --- 실행/결과 영역 (오른쪽) ---
    with right:
        st.subheader("결과 (Results)")

        if run_button:
            # 입력값 세션 저장(다음 rerun에도 유지)
            st.session_state["f_input"] = facts_text
            st.session_state["r_input"] = rules_text
            st.session_state["q_input"] = query_text

            try:
                parsed_facts = parse_facts_block(facts_text)
                parsed_rules = parse_rules_block(rules_text)
                parsed_query = parse_query(query_text)

                kb = KB(facts=parsed_facts, rules=parsed_rules)
                kb.forward_chain()

                display_facts = sorted([f"{f[0]}({', '.join(f[1:])})" for f in kb.facts])
                query_results = kb.query(parsed_query)

                st.session_state["last_facts"] = display_facts
                st.session_state["last_query_results"] = query_results

                st.success("추론이 성공적으로 완료되었습니다!")

            except ParseError as e:
                st.error(f"⚠️ 파싱 에러 (Parse Error): {e}")
            except Exception as e:
                st.error(f"⚠️ 실행 에러 (Runtime Error): {e}")

        # 최근 결과 표시(버튼 누른 뒤에도 유지)
        if "last_facts" in st.session_state:
            st.markdown("**지식 베이스 (KB Facts)**")
            st.write(st.session_state["last_facts"])
        else:
            st.info("아직 결과가 없습니다. 왼쪽에서 입력 후 실행하세요.")

        if "last_query_results" in st.session_state:
            st.markdown("**질의 결과 (Substitutions)**")
            if st.session_state["last_query_results"]:
                st.table(st.session_state["last_query_results"])
            else:
                st.info("매칭되는 결과가 없습니다.")


if __name__ == "__main__":
    main()
