import { NextRequest, NextResponse } from 'next/server';

const PY_BACKEND = 'http://localhost:8000';

export async function POST(req: NextRequest) {
  const body = await req.text();
  const res = await fetch(`${PY_BACKEND}/api/capture`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body,
  });
  const data = await res.text();
  console.log('=========api/capture post')
  return new NextResponse(data, { status: res.status, headers: { 'Content-Type': 'application/json' } });
}

export async function GET(req: NextRequest) {
  const url = req.nextUrl;
  const search = url.search;
  // 路径判断：/api/capture/status、/api/capture/result 或 /api/capture/interfaces
  if (url.pathname.endsWith('/status')) {
    const res = await fetch(`${PY_BACKEND}/api/capture/status${search}`);
    const data = await res.text();
    return new NextResponse(data, { status: res.status, headers: { 'Content-Type': 'application/json' } });
  } else if (url.pathname.endsWith('/result')) {
    const res = await fetch(`${PY_BACKEND}/api/capture/result${search}`);
    const data = await res.text();
    return new NextResponse(data, { status: res.status, headers: { 'Content-Type': 'application/json' } });
  } else if (url.pathname.endsWith('/interfaces')) {
    const res = await fetch(`${PY_BACKEND}/api/capture/interfaces`);
    const data = await res.text();
    return new NextResponse(data, { status: res.status, headers: { 'Content-Type': 'application/json' } });
  }
  // 默认404
  return NextResponse.json({ error: 'Not found' }, { status: 404 });
}