// Shared formatting utilities for both frontend and backend

export const formatters = {
    /**
     * Format currency amount
     */
    formatCurrency: (amount: number, currency: string = 'USD'): string => {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency
        }).format(amount);
    },

    /**
     * Format date to ISO string
     */
    formatDateISO: (date: Date): string => {
        return date.toISOString();
    },

    /**
     * Format date to local string
     */
    formatDateLocal: (date: Date | string): string => {
        const d = typeof date === 'string' ? new Date(date) : date;
        return d.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    },

    /**
     * Format phone number
     */
    formatPhone: (phone: string): string => {
        // Remove all non-numeric characters
        const cleaned = phone.replace(/\D/g, '');
        
        // Format as (XXX) XXX-XXXX
        if (cleaned.length === 10) {
            return `(${cleaned.slice(0,3)}) ${cleaned.slice(3,6)}-${cleaned.slice(6)}`;
        }
        
        // Format as +X (XXX) XXX-XXXX for international
        if (cleaned.length === 11) {
            return `+${cleaned[0]} (${cleaned.slice(1,4)}) ${cleaned.slice(4,7)}-${cleaned.slice(7)}`;
        }
        
        return phone;
    },

    /**
     * Format file size
     */
    formatFileSize: (bytes: number): string => {
        const units = ['B', 'KB', 'MB', 'GB', 'TB'];
        let size = bytes;
        let unitIndex = 0;
        
        while (size >= 1024 && unitIndex < units.length - 1) {
            size /= 1024;
            unitIndex++;
        }
        
        return `${size.toFixed(1)} ${units[unitIndex]}`;
    }
};
