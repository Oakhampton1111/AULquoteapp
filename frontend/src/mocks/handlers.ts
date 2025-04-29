import { rest } from 'msw';
import { mockQuotes } from './data/quotes';
import { mockRateCards } from './data/rateCards';
import { mockUsers } from './data/users';

const API_URL = 'http://localhost:8000';
const API_PATH = '/api/v1';

export const handlers = [
  // Auth endpoints
  rest.post(`${API_URL}${API_PATH}/auth/login`, (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        data: {
          user: mockUsers[0],
          token: 'mock-jwt-token',
        },
        status: 200,
        message: 'Login successful',
      })
    );
  }),

  rest.get(`${API_URL}${API_PATH}/auth/me`, (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        data: mockUsers[0],
        status: 200,
      })
    );
  }),

  // Quote endpoints
  rest.get(`${API_URL}${API_PATH}/quotes`, (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        data: mockQuotes,
        status: 200,
      })
    );
  }),

  rest.post(`${API_URL}${API_PATH}/quotes`, async (req, res, ctx) => {
    const quoteData = await req.json();
    const newQuote = {
      id: 'quote-' + Date.now(),
      ...quoteData,
      status: 'pending',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };

    return res(
      ctx.status(201),
      ctx.json({
        data: newQuote,
        status: 201,
        message: 'Quote created successfully',
      })
    );
  }),

  rest.get(`${API_URL}${API_PATH}/quotes/:id`, (req, res, ctx) => {
    const { id } = req.params;
    const quote = mockQuotes.find(q => q.id === id);

    if (!quote) {
      return res(
        ctx.status(404),
        ctx.json({
          status: 404,
          message: 'Quote not found',
        })
      );
    }

    return res(
      ctx.status(200),
      ctx.json({
        data: quote,
        status: 200,
      })
    );
  }),

  // Rate card endpoints
  rest.get(`${API_URL}${API_PATH}/rate-cards`, (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        data: mockRateCards,
        status: 200,
      })
    );
  }),

  rest.get(`${API_URL}${API_PATH}/rate-cards/:id`, (req, res, ctx) => {
    const { id } = req.params;
    const rateCard = mockRateCards.find(rc => rc.id === id);

    if (!rateCard) {
      return res(
        ctx.status(404),
        ctx.json({
          status: 404,
          message: 'Rate card not found',
        })
      );
    }

    return res(
      ctx.status(200),
      ctx.json({
        data: rateCard,
        status: 200,
      })
    );
  }),
];
