import { Link, useRoute } from '../router';

const NAV = [
  { to: '/', label: 'Overview' },
  { to: '/resume', label: 'Resume' },
  { to: '/skills', label: 'Skills' },
  { to: '/methodology', label: 'Methodology' },
  { to: '/sources', label: 'Sources' },
];

export function TopNav() {
  const route = useRoute();
  const isActive = (to: string) => (to === '/' ? route === '/' : route.startsWith(to));
  return (
    <nav className="top-nav" data-testid="top-nav" aria-label="Primary">
      {NAV.map((item) => (
        <Link
          key={item.to}
          to={item.to}
          className={`nav-link ${isActive(item.to) ? 'active' : ''}`}
          data-testid={`nav-${item.label.toLowerCase()}`}
          aria-current={isActive(item.to) ? 'page' : undefined}
        >
          {item.label}
        </Link>
      ))}
    </nav>
  );
}
