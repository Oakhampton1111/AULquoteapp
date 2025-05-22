# User Flow Overview

This document summarizes how a typical user interacts with the AUL Quote App, from registration to accepting a quote.

## Registration

1. A new user signs up by providing contact information.
2. The system sends a confirmation email allowing the user to set a password.
3. After confirming their account, the user can log in.

## Dashboard Access

- Upon logging in, customers see the **Client Dashboard** with their existing quotes and quick actions to start a new request.
- Administrators are redirected to the **Admin Dashboard**, where they can manage quotes and customer accounts.

## Quote Generation Options

From the dashboard, a user can generate a quote in two main ways:

1. **AI-Powered Quote** – Fill out a form describing their storage or service needs. The system calculates pricing using rate cards and AI optimization.
2. **Manual Quote Request** – Upload documents or specify custom requirements for a tailored estimate.

Both methods return a detailed price breakdown that can be further negotiated.

## Negotiation

- Users may counter the provided price or adjust service levels.
- Negotiation history is tracked so both the customer and administrator can review changes.
- Administrators approve or decline negotiation proposals, triggering real-time notifications.

## Acceptance

Once both parties agree on a price:

1. The customer accepts the quote.
2. Acceptance time and user are recorded in the database.
3. The quote status updates so downstream logistics steps can begin.

## CRM Deal Updates

The application keeps the CRM in sync with quote outcomes using
`CRMService`. When a customer **accepts** a quote, the associated deal moves
from the `QUOTE_REQUESTED` stage to `CLOSED_WON`. A **rejected** quote causes
the deal stage to transition to `CLOSED_LOST`. These stage changes update win
and loss metrics so the sales team can track pipeline performance accurately.

This flow helps new contributors and users understand the overall experience and expected interactions within the system.
