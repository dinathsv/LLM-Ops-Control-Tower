import type { Metadata } from 'next'
import './globals.css'
import Link from 'next/link'

export const metadata: Metadata = {
  title: 'LLM Ops Control Tower',
  description: 'Visibility and telemetry for your LLM applications',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        <div className="app-container">
          <aside className="sidebar">
            <h1>Control Tower</h1>
            <nav>
              <Link href="/" className="nav-link">
                Dashboard (Cost Governor)
              </Link>
              <Link href="/traces" className="nav-link">
                Trace Explorer
              </Link>
            </nav>
          </aside>
          <main className="main-content">
            {children}
          </main>
        </div>
      </body>
    </html>
  )
}
