'use client';

interface ExcelExportButtonProps {
    onClick: () => void;
    loading?: boolean;
    disabled?: boolean;
    className?: string;
}

export default function ExcelExportButton({
    onClick,
    loading = false,
    disabled = false,
    className = ''
}: ExcelExportButtonProps) {
    return (
        <button
            onClick={onClick}
            disabled={disabled || loading}
            className={`px-6 py-2.5 bg-transparent border border-[#1e3a5f] rounded-lg text-[#94a3b8] text-sm font-medium cursor-pointer hover:bg-[#0d1f35] hover:text-[#00e5a0] transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 ${className}`}
        >
            {loading ? (
                <>
                    <svg className="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    İndiriliyor...
                </>
            ) : (
                <>
                    📊 Excel İndir
                </>
            )}
        </button>
    );
}
