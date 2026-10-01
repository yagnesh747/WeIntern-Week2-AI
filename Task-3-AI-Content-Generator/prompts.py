"""
prompts.py - Prompt engineering templates for AI Content Generator
"""

CONTENT_PROMPTS = {
    "Blog Post": {
        "Short": "Write a concise blog post (150-250 words) about: {topic}. Tone: {tone}. Include a catchy title, a brief introduction, 2-3 key points, and a conclusion. Format with clear headings.",
        "Medium": "Write a well-structured blog post (400-600 words) about: {topic}. Tone: {tone}. Include an engaging title, introduction that hooks the reader, 3-4 main sections with headings, and a strong conclusion with a call to action.",
        "Long": "Write a comprehensive blog post (800-1200 words) about: {topic}. Tone: {tone}. Include: an SEO-friendly title, a compelling introduction, 5-6 detailed sections with subheadings, real-world examples or tips, and a conclusion with key takeaways."
    },
    "Social Media Caption": {
        "Short": "Write a punchy social media caption (50-80 words) about: {topic}. Tone: {tone}. Include 3-5 relevant hashtags and an emoji or two. Make it shareable and engaging.",
        "Medium": "Write an engaging social media caption (100-150 words) about: {topic}. Tone: {tone}. Include a hook in the first line, value-packed body, a call-to-action, and 5-7 relevant hashtags.",
        "Long": "Write a detailed social media post (200-300 words) about: {topic}. Tone: {tone}. Include a strong opening hook, storytelling elements, key insights or value, a clear call-to-action, and 8-10 relevant hashtags."
    },
    "Text Summary": {
        "Short": "Provide a brief summary (80-120 words) of the following content. Tone: {tone}. Capture only the most essential points clearly and concisely:\n\n{topic}",
        "Medium": "Write a structured summary (200-300 words) of the following content. Tone: {tone}. Include the main topic, key points, important details, and conclusion:\n\n{topic}",
        "Long": "Create a comprehensive summary (400-500 words) of the following content. Tone: {tone}. Organize with: an overview paragraph, key themes and findings, supporting details, implications, and final takeaways:\n\n{topic}"
    },
    "Email Newsletter": {
        "Short": "Write a short email newsletter (150-200 words) about: {topic}. Tone: {tone}. Include a subject line, greeting, main message, and sign-off.",
        "Medium": "Write an email newsletter (350-450 words) about: {topic}. Tone: {tone}. Include: a compelling subject line, personalized greeting, 2-3 sections with value-adding content, and a clear CTA.",
        "Long": "Write a full email newsletter (600-800 words) about: {topic}. Tone: {tone}. Include: subject line, engaging intro, featured article section, tips/insights section, event or update section, and a warm sign-off with CTA."
    },
    "Product Description": {
        "Short": "Write a compelling product description (80-120 words) for: {topic}. Tone: {tone}. Highlight key features and benefits. Make it persuasive.",
        "Medium": "Write a detailed product description (200-300 words) for: {topic}. Tone: {tone}. Include: an attention-grabbing opener, key features list, benefits for the user, and a persuasive closing.",
        "Long": "Write a comprehensive product description (400-500 words) for: {topic}. Tone: {tone}. Include: headline, detailed feature breakdown, use cases, target audience benefits, comparison advantages, and a strong CTA."
    }
}

TONE_INSTRUCTIONS = {
    "Professional": "Use formal, authoritative, and expert language. Avoid slang. Be precise and credible.",
    "Casual": "Use relaxed, conversational language. Feel free to use contractions and everyday vocabulary.",
    "Friendly": "Use warm, approachable, and positive language. Sound like a helpful friend.",
    "Creative": "Use imaginative, expressive language. Feel free to use metaphors, vivid descriptions, and unique perspectives.",
    "Formal": "Use strictly formal language, proper grammar, and academic-style writing. Avoid any colloquialisms."
}

def build_prompt(content_type: str, topic: str, tone: str, length: str) -> str:
    """Build a structured prompt from the templates."""
    template = CONTENT_PROMPTS.get(content_type, {}).get(length, "")
    if not template:
        template = "Write {length} content about: {topic}. Tone: {tone}."
    
    tone_instruction = TONE_INSTRUCTIONS.get(tone, "")
    
    prompt = template.format(topic=topic, tone=tone, length=length.lower())
    
    system_instruction = f"""You are a professional content writer. {tone_instruction}
Generate high-quality, original content that is engaging, well-structured, and ready to publish.
Do not add any meta-commentary like "Here is your blog post:" - start the content directly."""
    
    return f"{system_instruction}\n\n{prompt}"
