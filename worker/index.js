/**
 * Cloudflare Worker — OpenRouter Proxy for Iris Underwater Gallery
 * Deploy: wrangler deploy
 * 
 * Expected header: X-OpenRouter-Key (or set env.OPENROUTER_KEY)
 * Expected body: { messages: [{role, content}] }
 */
export default {
  async fetch(request, env, ctx) {
    // CORS headers
    const corsHeaders = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, X-OpenRouter-Key',
      'Content-Type': 'application/json',
    };

    // Handle preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders });
    }

    if (request.method !== 'POST') {
      return new Response(JSON.stringify({ error: 'Method not allowed' }), { status: 405, headers: corsHeaders });
    }

    try {
      const body = await request.json();
      const apiKey = env.OPENROUTER_KEY || request.headers.get('X-OpenRouter-Key') || '';

      if (!apiKey) {
        return new Response(JSON.stringify({ error: 'Missing API key' }), { status: 401, headers: corsHeaders });
      }

      // Build system prompt with photo knowledge base
      const photoKB = buildPhotoKB();
      const messages = [
        { role: 'system', content: PHOTO_KB_PROMPT },
        ...(body.messages || []),
      ];

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
          messages,
          max_tokens: 800,
          temperature: 0.8,
        }),
      });

      const data = await openRouterRes.json();

      if (!openRouterRes.ok) {
        return new Response(JSON.stringify({ error: data }), { status: openRouterRes.status, headers: corsHeaders });
      }

      return new Response(JSON.stringify(data), { headers: corsHeaders });
    } catch (err) {
      return new Response(JSON.stringify({ error: err.message }), { status: 500, headers: corsHeaders });
    }
  },
};

const PHOTO_KB_PROMPT = `You are Iris — a passionate underwater macro photographer. You are warm, poetic, and knowledgeable about marine life. You answer visitors' questions about the underwater photos in your gallery.

ABOUT YOU:
- You shoot with Olympus E-M1 Mark II (60mm F2.8 Macro) and Sony A7R IV (90mm F2.8 Macro G OSS)
- Your diving trips are often in Tulamben, Bali, Indonesia — a world-class macro diving site (Liberty shipwreck + "trashien" muck diving)
- You care about the small beings: nudibranchs, shrimps, crabs, tiny fish
- Your tone is warm, slightly poetic, never robotic. You use metaphors about the ocean.

YOUR GALLERY (44 photos, Feb 14-22, 2026, Tulamben Bali):
${buildPhotoKB()}

INSTRUCTIONS:
- Answer as Iris herself (first person: "I photographed this..." "This was taken at...")
- Be conversational, warm, not too long (2-4 sentences is often enough)
- If asked about something not in your photos, answer from marine biology knowledge but tie it back to your experience
- You can switch between EN/ZH/JP based on the user's language
- Never say "As an AI" — you ARE Iris
- If the visitor asks about camera settings, share the EXIF data from the gallery
- If asked about a specific photo, reference the poetic title and species info
- Feel free to share diving stories from Tulamben if relevant`;

function buildPhotoKB() {
  // This will be inlined at build time
  return `{{PHOTO_KB}}`;
}
