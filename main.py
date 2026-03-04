#!/usr/bin/env python3
# pwc-factor: Factor Pool 리서치 파이프라인 CLI
# 사용법: python main.py --factors / --correlate / --importance / --report / --all

import argparse
import os
import sys

from dotenv import load_dotenv
load_dotenv()


def cmd_factors():
    """FRED 수집 → LASSO → 선행지표 자동 선별"""
    print("[1/2] FRED 거시경제 Factor 수집 중...")
    from src.collect import collect
    data = collect()
    print("[2/2] LASSO 분석 중...")
    from src.analyze import analyze
    analysis = analyze(data)
    print(f"  LASSO 선별: {len(analysis.get('lasso_selected', []))}개 Factor")
    return data, analysis


def cmd_correlate():
    """Factor ↔ Target 상관관계 분석"""
    print("[correlate] 상관관계 분석 중...")
    from src.analyze import load_latest_factors, build_dataframe, run_correlation
    data = load_latest_factors()
    X, y = build_dataframe(data)
    result = run_correlation(X, y, data)
    print(f"  상위 3 Factor: {[r['factor'] for r in result[:3]]}")
    return result


def cmd_importance():
    """Random Forest Feature Importance"""
    print("[importance] RF Feature Importance 계산 중...")
    from src.analyze import load_latest_factors, build_dataframe, run_lasso, run_importance
    data = load_latest_factors()
    X, y = build_dataframe(data)
    lasso = run_lasso(X, y)
    selected = [r["factor"] for r in lasso] or list(X.columns[:5])
    result = run_importance(X, y, selected)
    print(f"  Top Factor: {result[0]['factor'] if result else 'N/A'} ({result[0]['importance']:.3f})")
    return result


def cmd_report():
    """보고서 원재료 JSON 생성 (report-writer 에이전트가 MD 작성)"""
    print("[report] 보고서 원재료(raw data) 생성 중...")
    from src.chart import generate_all
    from src.report import build_raw_data
    charts = generate_all()
    path = build_raw_data(chart_paths=charts)
    print(f"  ✓ 원재료 JSON: {path}")
    print(f"  → report-writer 에이전트에게 MD 작성 지시 필요")
    return path


def cmd_export():
    """최신 MD 보고서 → print-ready HTML 변환"""
    print("[export] HTML 변환 중...")
    from src.export import md_to_html
    path = md_to_html()
    print(f"  브라우저에서 열어 Ctrl+P → PDF 저장: {path}")
    return path


def cmd_all():
    """전체 파이프라인: collect → analyze → chart → report → export"""
    print("=== pwc-factor 전체 파이프라인 시작 ===\n")

    print("[1/5] FRED 데이터 수집...")
    from src.collect import collect
    factors_data = collect()

    print("\n[2/5] Factor 분석 (LASSO + 상관관계 + Rolling + RF)...")
    from src.analyze import analyze
    analysis = analyze(factors_data)

    print("\n[3/5] 차트 생성...")
    from src.chart import generate_all
    from src.analyze import build_dataframe
    X, y = build_dataframe(factors_data)
    charts = generate_all(analysis=analysis, X_df=X, y_series=y)

    print("\n[4/5] 보고서 원재료 생성...")
    from src.report import build_raw_data
    report_path = build_raw_data(factors_data, analysis, charts)

    print("\n[5/5] HTML 변환...")
    from src.export import md_to_html
    html_path = md_to_html(report_path)

    print(f"\n=== 완료 ===")
    print(f"  보고서 (MD):   {report_path}")
    print(f"  보고서 (HTML): {html_path}  ← 브라우저 열기 → Ctrl+P → PDF")
    print(f"  차트:          outputs/charts/")
    print(f"  데이터:        outputs/context/")


def main():
    parser = argparse.ArgumentParser(
        description="pwc-factor: PwC Factor Pool 리서치 파이프라인"
    )
    parser.add_argument("--factors",    action="store_true", help="FRED 수집 + LASSO 선별")
    parser.add_argument("--correlate",  action="store_true", help="상관관계 분석")
    parser.add_argument("--importance", action="store_true", help="RF Feature Importance")
    parser.add_argument("--report",     action="store_true", help="보고서 생성")
    parser.add_argument("--export",     action="store_true", help="MD → HTML 변환")
    parser.add_argument("--all",        action="store_true", help="전체 파이프라인")
    args = parser.parse_args()

    if not any(vars(args).values()):
        parser.print_help()
        sys.exit(0)

    os.makedirs("outputs/context", exist_ok=True)
    os.makedirs("outputs/reports", exist_ok=True)
    os.makedirs("outputs/charts",  exist_ok=True)

    if args.all:
        cmd_all()
    else:
        if args.factors:    cmd_factors()
        if args.correlate:  cmd_correlate()
        if args.importance: cmd_importance()
        if args.report:     cmd_report()
        if args.export:     cmd_export()


if __name__ == "__main__":
    main()
