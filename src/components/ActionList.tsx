import type { ResumeAction } from '../types';

export function ActionList({ actions }: { actions: ResumeAction[] }) {
  return (
    <section className="panel action-list" data-testid="action-list">
      <header className="panel-head">
        <h2>Next moves</h2>
        <span className="panel-tag">{actions.length} concrete actions</span>
      </header>
      <div className="action-cards">
        {actions.map((action, index) => (
          <article key={`${action.type}-${index}`} className={`action-card action-${action.type}`} data-testid="action-card">
            <div className="action-head">
              <h3>{action.title}</h3>
              {action.market_price != null && <span className="action-price">{action.market_price.toFixed(0)} pts</span>}
            </div>
            <p className="action-why">{action.why}</p>
            <dl className="action-meta">
              <div>
                <dt>Prove it</dt>
                <dd>{action.how_to_prove}</dd>
              </div>
              <div>
                <dt>Role direction</dt>
                <dd>{action.role_direction}</dd>
              </div>
            </dl>
            {action.course_url && (
              <div className="action-course">
                <a
                  className="course-link"
                  data-testid="course-link"
                  href={action.course_url}
                  target="_blank"
                  rel="noreferrer"
                >
                  Find {action.course_query} courses on MySkillsFuture ↗
                </a>
                <p className="course-note muted">{action.course_note}</p>
              </div>
            )}
          </article>
        ))}
      </div>
    </section>
  );
}
