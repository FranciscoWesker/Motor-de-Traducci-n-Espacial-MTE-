interface HeaderProps {
  title?: string
  subtitle?: string
}

export default function Header({ title, subtitle }: HeaderProps) {
  return (
    <header className="bg-white border-b border-gray-200 px-8 py-6 flex justify-between items-center sticky top-0 z-40 shadow-sm">
      <div className="flex-1">
        {title && <h1 className="text-2xl font-bold text-gray-900">{title}</h1>}
        {subtitle && <p className="text-sm text-gray-600 mt-1">{subtitle}</p>}
      </div>
      <div className="flex gap-2">
        <button className="w-10 h-10 rounded-lg border border-gray-200 bg-white text-gray-600 hover:bg-gray-50 hover:text-gray-900 transition-colors flex items-center justify-center">
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
            <path d="M10 2V18M2 10H18" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
          </svg>
        </button>
        <button className="w-10 h-10 rounded-lg border border-gray-200 bg-white text-gray-600 hover:bg-gray-50 hover:text-gray-900 transition-colors flex items-center justify-center">
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
            <path d="M15 17.5C15 16.672 15.672 16 16.5 16C17.328 16 18 16.672 18 17.5C18 18.328 17.328 19 16.5 19C15.672 19 15 18.328 15 17.5Z" fill="currentColor"/>
            <path d="M10 17.5C10 16.672 10.672 16 11.5 16C12.328 16 13 16.672 13 17.5C13 18.328 12.328 19 11.5 19C10.672 19 10 18.328 10 17.5Z" fill="currentColor"/>
            <path d="M5 17.5C5 16.672 5.672 16 6.5 16C7.328 16 8 16.672 8 17.5C8 18.328 7.328 19 6.5 19C5.672 19 5 18.328 5 17.5Z" fill="currentColor"/>
          </svg>
        </button>
      </div>
    </header>
  )
}
