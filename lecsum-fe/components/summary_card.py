import html
from datetime import datetime

def render_summary_card_html(
    filename: str,
    summary_html: str,
    keywords: list[str],
    created_at: str | None = None,
):
    if created_at:
        try:
            created_at = datetime.fromisoformat(created_at).strftime(
                "%Y년 %m월 %d일 %p %I:%M"
            )
        except Exception:
            pass
    else:
        created_at = datetime.now().strftime("%Y년 %m월 %d일 %p %I:%M")

    kw_html = "".join(
        f"<span class='kw-chip'>{html.escape(k)}</span>"
        for k in keywords
    ) or "<span style='color:#6b7280;'>키워드가 없습니다.</span>"

    word_count = len(summary_html.split())
    keyword_count = len(keywords)
    est_minutes = "5분"

    return f"""
    <div class="summary-card">
      <div class="summary-header">
        <div class="summary-badge">✨ AI 요약</div>
        <div class="summary-title">{html.escape(filename)}</div>
        <div class="summary-date">{created_at}</div>
      </div>

      <div class="summary-section">
        <h3>요약 내용</h3>
        <div class="summary-box">{summary_html}</div>
      </div>

      <div class="summary-stats">
        <div class="stat blue">
          <div class="stat-value">{word_count}</div>
          <div>단어 수</div>
        </div>
        <div class="stat purple">
          <div class="stat-value">{keyword_count}</div>
          <div>핵심 키워드</div>
        </div>
        <div class="stat pink">
          <div class="stat-value">{est_minutes}</div>
          <div>예상 복습 시간</div>
        </div>
      </div>

      <div class="summary-keywords">
        <h4>핵심 키워드</h4>
        <div class="keyword-list">{kw_html}</div>
      </div>
    </div>
    """