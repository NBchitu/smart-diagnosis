import { NextRequest, NextResponse } from 'next/server';

export async function GET() {
  return NextResponse.json({
    env: {
      AI_PROVIDER: process.env.AI_PROVIDER || 'not set',
      OPENROUTER_API_KEY: process.env.OPENROUTER_API_KEY ? 'set' : 'not set',
      OPENROUTER_MODEL: process.env.OPENROUTER_MODEL || 'not set',
      NODE_ENV: process.env.NODE_ENV,
    }
  });
}

export async function POST() {
  return GET();
}