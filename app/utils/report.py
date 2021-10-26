def get_report_reason(reason: int) -> str:
    if reason == 1:
        report_reason = "부적절한 홍보/영리 목적"
    elif reason == 2:
        report_reason = "욕설/반말/부적절한 언어 사용"
    elif reason == 3:
        report_reason = "도배/스팸성"
    else:
        report_reason = "분란유도"
    return report_reason