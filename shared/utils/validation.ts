// Shared validation utilities for both frontend and backend

// Validation rules and constants
export const VALIDATION_RULES = {
    // Customer validation
    CUSTOMER: {
        NAME_MIN_LENGTH: 2,
        NAME_MAX_LENGTH: 100,
        PHONE_PATTERN: /^\+?[1-9]\d{1,14}$/, // E.164 format
        EMAIL_PATTERN: /^[^@]+@[^@]+\.[^@]+$/,
    },

    // Quote validation
    QUOTE: {
        MIN_AMOUNT: 0,
        MAX_AMOUNT: 1000000,
        EXPIRY_DAYS: 30,
    },

    // Rate validation
    RATE: {
        MIN_RATE: 0,
        MAX_RATE: 100,
        MIN_TERM: 1,
        MAX_TERM: 120,
    },
} as const;

// Common error messages
export const ERROR_MESSAGES = {
    REQUIRED_FIELD: 'This field is required',
    INVALID_EMAIL: 'Invalid email address',
    INVALID_PHONE: 'Invalid phone number',
    AMOUNT_RANGE: 'Amount must be between {min} and {max}',
    RATE_RANGE: 'Rate must be between {min}% and {max}%',
    TERM_RANGE: 'Term must be between {min} and {max} months',
} as const;

// Validation response types
export const VALIDATION_SEVERITY = {
    ERROR: 'error',
    WARNING: 'warning',
    INFO: 'info',
} as const;

export const validators = {
    /**
     * Validate email format
     */
    isValidEmail: (email: string): boolean => {
        const emailRegex = VALIDATION_RULES.CUSTOMER.EMAIL_PATTERN;
        return emailRegex.test(email);
    },

    /**
     * Validate phone number format
     */
    isValidPhone: (phone: string): boolean => {
        const phoneRegex = VALIDATION_RULES.CUSTOMER.PHONE_PATTERN;
        return phoneRegex.test(phone);
    },

    /**
     * Validate VIN (Vehicle Identification Number)
     */
    isValidVIN: (vin: string): boolean => {
        const vinRegex = /^[A-HJ-NPR-Z0-9]{17}$/;
        return vinRegex.test(vin);
    },

    /**
     * Validate year format
     */
    isValidYear: (year: number): boolean => {
        const currentYear = new Date().getFullYear();
        return year >= 1900 && year <= currentYear + 1;
    },

    /**
     * Validate currency amount
     */
    isValidCurrency: (amount: number): boolean => {
        return amount >= VALIDATION_RULES.QUOTE.MIN_AMOUNT && amount <= VALIDATION_RULES.QUOTE.MAX_AMOUNT;
    },

    /**
     * Validate password strength
     */
    isStrongPassword: (password: string): boolean => {
        // At least 8 characters, 1 uppercase, 1 lowercase, 1 number, 1 special character
        const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
        return passwordRegex.test(password);
    }
};
