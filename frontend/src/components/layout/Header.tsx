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
    </header>
  )
}
