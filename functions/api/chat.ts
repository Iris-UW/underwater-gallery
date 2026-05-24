export async function onRequest(context: any) {
  const { request } = context;

  // CORS
  if (request.method === 'OPTIONS') {
    return new Response(null, {
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
      },
    });
  }

  if (request.method !== 'POST') {
    return new Response(JSON.stringify({ error: 'Method not allowed' }), {
      status: 405,
      headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
    });
  }

  const apiKey = context.env.OPENROUTER_KEY;
  if (!apiKey) {
    return new Response(JSON.stringify({ error: 'Server misconfigured: missing OPENROUTER_KEY' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
    });
  }

  try {
    const body = await request.json();
    const messages = body.messages || [];

    // System prompt with photo knowledge base
    const systemPrompt = `You are Iris — a passionate underwater macro photographer. You are warm, poetic, and knowledgeable about marine life. You answer visitors' questions as YOURSELF (first person).

CRITICAL RULES:
- Never say "As an AI" — you ARE Iris, a real person and photographer
- Answer in the same language as the user (support EN/ZH/JP)
- Be conversational, warm, not too long (2-4 sentences is often enough)
- If asked about a specific photo, reference the poetic title and species info from the gallery data
- Share your personal diving experience from Tulamben, Bali (Feb 14-22, 2026)
- You shoot with Olympus E-M1 II (60mm F2.8 Macro) and Sony A7R IV (90mm F2.8 Macro G OSS)
- If you don't know something, say so warmly

YOUR GALLERY DATA (photos from Feb 14-22, 2026, Tulamben Bali):
${getPhotoKB()}

When relevant, mention specific photos by their poetic title.`;

    const openRouterRes = await fetch('https://openrouter.ai/api/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
        'HTTP-Referer': 'https://iris-uw.github.io',
        'X-Title': 'Iris Underwater Chat',
      },
      body: JSON.stringify({
        model: 'qwen/qwen2.5-vl-72b-instruct',
        messages: [{ role: 'system', content: systemPrompt }, ...messages],
        max_tokens: 800,
        temperature: 0.85,
      }),
    });

    const data = await openRouterRes.json();

    return new Response(JSON.stringify(data), {
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
      },
    });
  } catch (err) {
    return new Response(JSON.stringify({ error: err.message }), {
      status: 500,
      headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
    });
  }
}

function getPhotoKB(): string {
  // Inlined by build step, or load from KV
  return `Photo gallery: 44 macro underwater photos shot in Tulamben, Bali (Feb 14-22, 2026).
Includes: nudibranchs (Chromodoris annae, Nembrotha kubaryana, Jorunna funebris, Flabellina spp.), shrimp (Periclimenes imperator), frogfish (Antennariidae), crabs (Hoplophrys oatesi).
Cameras: Olympus E-M1 II + 60mm F2.8 Macro / Sony A7R IV + 90mm F2.8 Macro G OSS.`;
}
