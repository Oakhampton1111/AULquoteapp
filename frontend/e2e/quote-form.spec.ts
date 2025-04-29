import { test, expect } from '@playwright/test';

test.describe('Quote Form E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Set up mock environment
    await page.addInitScript(() => {
      window.localStorage.setItem('token', 'mock-jwt-token');
      window.localStorage.setItem('user', JSON.stringify({
        id: 'user-2',
        name: 'Jane Client',
        email: 'client@example.com',
        role: 'client'
      }));
    });

    // Navigate to the quote form page
    await page.goto('/client/quotes/new');

    // Wait for the form to be fully loaded
    await page.waitForSelector('form[data-testid="quote-form"]', { state: 'visible', timeout: 10000 });
  });

  test('should create a new quote successfully', async ({ page }) => {
    // Fill client information
    await page.fill('input[name="clientName"]', 'John Doe');
    await page.fill('input[name="email"]', 'john.doe@example.com');
    await page.fill('input[name="phone"]', '555-123-4567');

    // Fill vehicle details
    await page.fill('input[name="vehicleDetails_make"]', 'Toyota');
    await page.fill('input[name="vehicleDetails_model"]', 'Camry');
    await page.fill('input[name="vehicleDetails_year"]', '2022');
    await page.fill('input[name="vehicleDetails_vin"]', '1HGCM82633A123456');

    // Select coverage type
    await page.selectOption('select[name="coverage_type"]', { index: 0 });

    // Select coverage duration
    await page.selectOption('select[name="coverage_duration"]', '12');

    // Set start date to today
    const today = new Date();
    const formattedDate = today.toISOString().split('T')[0]; // YYYY-MM-DD
    await page.fill('input[name="coverage_startDate"]', formattedDate);

    // Add an additional option
    await page.click('button:has-text("Add Option")');
    await page.fill('.additional-option input[placeholder="Option Name"]', 'Extended Warranty');
    await page.fill('.additional-option input[placeholder="Cost"]', '250');

    // Take a screenshot before submission
    await page.screenshot({ path: 'e2e-screenshots/quote-form-filled.png' });

    // Submit the form
    await page.click('button:has-text("Create Quote")');

    // Wait for success notification
    await page.waitForSelector('.ant-notification-notice-success', { state: 'visible' });

    // Verify success message
    const successMessage = await page.textContent('.ant-notification-notice-message');
    expect(successMessage).toContain('Quote Created');

    // Take a screenshot after submission
    await page.screenshot({ path: 'e2e-screenshots/quote-created.png' });
  });

  test('should show validation errors for required fields', async ({ page }) => {
    // Try to submit the form without filling required fields
    await page.click('button:has-text("Create Quote")');

    // Check for validation messages
    const validationMessages = await page.$$('.ant-form-item-explain-error');
    expect(validationMessages.length).toBeGreaterThan(0);

    // Take a screenshot of validation errors
    await page.screenshot({ path: 'e2e-screenshots/validation-errors.png' });

    // Verify specific error message
    const clientNameError = await page.textContent('.ant-form-item:has(input[name="clientName"]) .ant-form-item-explain-error');
    expect(clientNameError).toContain('Please enter the client name');
  });

  test('should calculate total cost correctly', async ({ page }) => {
    // Fill required fields
    await page.fill('input[name="clientName"]', 'Jane Smith');
    await page.fill('input[name="email"]', 'jane.smith@example.com');
    await page.fill('input[name="phone"]', '555-987-6543');
    await page.fill('input[name="vehicleDetails_make"]', 'Honda');
    await page.fill('input[name="vehicleDetails_model"]', 'Accord');
    await page.fill('input[name="vehicleDetails_year"]', '2021');
    await page.fill('input[name="vehicleDetails_vin"]', '5J8TB4H36LL000000');

    // Select coverage type (assuming first option has a base cost of 100)
    await page.selectOption('select[name="coverage_type"]', { index: 0 });

    // Select coverage duration (12 months with 1.0 multiplier)
    await page.selectOption('select[name="coverage_duration"]', '12');

    // Add two additional options
    await page.click('button:has-text("Add Option")');
    await page.fill('.additional-option:nth-child(1) input[placeholder="Option Name"]', 'Roadside Assistance');
    await page.fill('.additional-option:nth-child(1) input[placeholder="Cost"]', '50');

    await page.click('button:has-text("Add Option")');
    await page.fill('.additional-option:nth-child(2) input[placeholder="Option Name"]', 'Rental Car Coverage');
    await page.fill('.additional-option:nth-child(2) input[placeholder="Cost"]', '75');

    // Wait for total cost to update
    await page.waitForTimeout(500);

    // Get the total cost
    const totalCostText = await page.textContent('.quote-summary h3');
    const totalCost = parseFloat(totalCostText.replace('Total Cost: $', ''));

    // Expected cost: base cost (100) + additional options (50 + 75) = 225
    expect(totalCost).toBe(225);

    // Take a screenshot of the quote summary
    await page.screenshot({ path: 'e2e-screenshots/quote-summary.png' });
  });

  test('should be accessible via keyboard navigation', async ({ page }) => {
    // Start with the first input field
    await page.focus('input[name="clientName"]');

    // Tab through all form fields
    const tabSequence = [
      'input[name="clientName"]',
      'input[name="email"]',
      'input[name="phone"]',
      'input[name="vehicleDetails_make"]',
      'input[name="vehicleDetails_model"]',
      'input[name="vehicleDetails_year"]',
      'input[name="vehicleDetails_vin"]',
      'select[name="coverage_type"]',
      'input[name="coverage_startDate"]',
      'select[name="coverage_duration"]',
      'button:has-text("Add Option")',
      'button:has-text("Create Quote")'
    ];

    for (let i = 0; i < tabSequence.length; i++) {
      // Check if the current element is focused
      const isFocused = await page.evaluate((selector) => {
        const element = document.querySelector(selector);
        return element === document.activeElement;
      }, tabSequence[i]);

      expect(isFocused).toBe(true);

      // Press Tab to move to the next element
      await page.keyboard.press('Tab');
    }
  });
});
