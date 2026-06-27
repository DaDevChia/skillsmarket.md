import React from 'react';

// Minimal history-based router. Vite preview + the Cloudflare tunnel serve the
// SPA index for unknown paths, so /resume deep-links resolve client-side.

const NAV_EVENT = 'app:navigate';

export function navigate(to: string) {
  if (window.location.pathname === to) return;
  window.history.pushState({}, '', to);
  window.dispatchEvent(new Event(NAV_EVENT));
}

export function useRoute(): string {
  const [path, setPath] = React.useState(() => window.location.pathname);
  React.useEffect(() => {
    const sync = () => setPath(window.location.pathname);
    window.addEventListener('popstate', sync);
    window.addEventListener(NAV_EVENT, sync);
    return () => {
      window.removeEventListener('popstate', sync);
      window.removeEventListener(NAV_EVENT, sync);
    };
  }, []);
  return path;
}

/** Parse a pathname into ["skills", ":id"] style segments. */
export function routeSegments(path: string): string[] {
  return path.split('/').filter(Boolean);
}

export function Link({
  to,
  children,
  className,
  ...rest
}: { to: string; children: React.ReactNode } & React.AnchorHTMLAttributes<HTMLAnchorElement>) {
  return (
    <a
      href={to}
      className={className}
      onClick={(event) => {
        if (event.metaKey || event.ctrlKey || event.shiftKey) return;
        event.preventDefault();
        navigate(to);
      }}
      {...rest}
    >
      {children}
    </a>
  );
}
