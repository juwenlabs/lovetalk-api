const express = require('express');

function mountMediation(app, options = {}) {
  const corePromise = import('./core.mjs');
  // Handle module failures through the route error response instead of an unhandled rejection.
  corePromise.catch(() => {});
  const env = options.env || process.env;
  const buckets = new Map();
  const allowed = new Set(['https://localhost', 'http://localhost', 'https://lovetalk-api.onrender.com', ...(env.URI_SAI_ALLOWED_ORIGINS || '').split(',').map(x => x.trim()).filter(Boolean)]);
  function cors(req, res, next) {
    const origin = req.get('Origin');
    res.set('Cache-Control', 'no-store');
    res.set('X-Content-Type-Options', 'nosniff');
    if (origin && !allowed.has(origin)) return res.status(403).json({ error: '허용되지 않은 접속입니다.' });
    if (origin) { res.set('Access-Control-Allow-Origin', origin); res.vary('Origin'); }
    if (req.method === 'OPTIONS') {
      res.set('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
      res.set('Access-Control-Allow-Headers', 'Content-Type');
      return res.sendStatus(204);
    }
    next();
  }
  app.use(['/api/health', '/api/mediate'], cors);
  app.get('/api/health', (req, res) => res.json({ ok: true, product: 'uri-sai', aiConfigured: !!env.OPENAI_API_KEY?.trim() }));
  const parse = express.json({ limit: '60kb' });
  app.post('/api/mediate', (req, res, next) => {
    if (!req.is('application/json')) return res.status(415).json({ error: 'JSON 요청만 사용할 수 있습니다.' });
    parse(req, res, next);
  }, async (req, res) => {
    const now = Date.now();
    for (const [key, entry] of buckets) if (now - entry.start > 600000 && !entry.active) buckets.delete(key);
    // Use Express/socket addressing only; never trust a client-provided forwarding header here.
    const ip = req.ip || req.socket.remoteAddress || 'unknown';
    let bucket = buckets.get(ip);
    if (!bucket) { bucket = { start: now, count: 0, active: 0 }; buckets.set(ip, bucket); }
    if (bucket.count >= 20 || bucket.active >= 2) return res.status(429).json({ error: '요청이 많습니다. 잠시 후 다시 시도해 주세요.' });
    bucket.count++; bucket.active++;
    try {
      const core = await corePromise;
      const input = core.validateInput(req.body);
      const analyze = options.analyze || core.analyze;
      const result = await analyze(input, { apiKey: env.OPENAI_API_KEY, model: env.URI_SAI_OPENAI_MODEL || 'gpt-4.1-mini' });
      res.json(result);
    } catch (error) {
      const core = await corePromise.catch(() => null);
      res.status(error.status || 500).json({ error: core && error instanceof core.RequestError ? error.message : '중재 처리 중 문제가 발생했습니다. 잠시 후 다시 시도해 주세요.' });
    } finally { bucket.active--; }
  });
  app.use(['/api/health', '/api/mediate'], (error, req, res, next) => {
    if (res.headersSent) return next(error);
    res.status(error.status || 400).json({ error: error.type === 'entity.too.large' ? '입력이 너무 깁니다.' : '입력 형식이 올바르지 않습니다.' });
  });
}
module.exports = { mountMediation };
