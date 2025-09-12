"""
Blog generation specialized service endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import logging
import time

from src.services.litellm_service import get_litellm_service, LiteLLMService

logger = logging.getLogger(__name__)

router = APIRouter()


class BlogGenerationRequest(BaseModel):
    """Blog generation request model"""
    topic: str = Field(..., description="Blog post topic")
    keywords: Optional[List[str]] = Field(None, description="SEO keywords to include")
    tone: Optional[str] = Field("professional", description="Writing tone (professional, casual, friendly, etc.)")
    length: Optional[str] = Field("medium", description="Blog length (short, medium, long)")
    target_audience: Optional[str] = Field(None, description="Target audience description")
    include_outline: Optional[bool] = Field(True, description="Whether to include an outline")
    model: Optional[str] = Field(None, description="Specific model to use")


class BlogOutline(BaseModel):
    """Blog outline model"""
    title: str
    sections: List[str]
    estimated_word_count: int


class BlogGenerationResponse(BaseModel):
    """Blog generation response model"""
    id: str
    title: str
    content: str
    outline: Optional[BlogOutline]
    keywords_used: List[str]
    word_count: int
    tone: str
    created_at: int
    model_used: str


@router.post("/generate", response_model=BlogGenerationResponse)
async def generate_blog_post(
    request: BlogGenerationRequest,
    litellm_service: LiteLLMService = Depends(get_litellm_service)
) -> BlogGenerationResponse:
    """Generate a blog post based on the provided topic and parameters"""
    logger.info(f"Blog generation request for topic: {request.topic}")
    
    try:
        generation_id = f"blog-{int(time.time())}"
        
        # Determine the model to use
        model = request.model or litellm_service.get_model_for_task("blog")
        
        # Build the prompt for blog generation
        length_instructions = {
            "short": "Write a concise blog post (400-600 words)",
            "medium": "Write a comprehensive blog post (800-1200 words)",
            "long": "Write a detailed, in-depth blog post (1500-2500 words)"
        }
        
        length_instruction = length_instructions.get(request.length, length_instructions["medium"])
        
        keywords_text = ""
        if request.keywords:
            keywords_text = f"\n- Include these SEO keywords naturally: {', '.join(request.keywords)}"
        
        audience_text = ""
        if request.target_audience:
            audience_text = f"\n- Target audience: {request.target_audience}"
        
        system_prompt = f"""You are an expert content writer specializing in creating high-quality blog posts. 
Your task is to create engaging, informative, and well-structured blog content.

Guidelines:
- Write in a {request.tone} tone
- {length_instruction}
- Use proper markdown formatting with headers, lists, and emphasis
- Include actionable insights and practical advice
- Ensure the content is SEO-friendly and engaging{keywords_text}{audience_text}
- Structure the content with clear sections and smooth transitions"""

        user_prompt = f"""Create a comprehensive blog post about: {request.topic}

Please provide:
1. An engaging title
2. Well-structured content with clear sections
3. Practical insights and actionable advice
4. A compelling conclusion

Make sure the content is valuable, informative, and engaging for readers interested in {request.topic}."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # Generate the blog content
        response = await litellm_service.chat_completion(
            model=model,
            messages=messages,
            temperature=0.7,
            max_tokens=3000
        )
        
        # Extract the generated content
        content = response['choices'][0]['message']['content']
        
        # Extract title from content (assuming it starts with # Title)
        lines = content.split('\n')
        title = request.topic  # fallback
        for line in lines:
            if line.startswith('# '):
                title = line[2:].strip()
                break
        
        # Generate outline if requested
        outline = None
        if request.include_outline:
            sections = []
            for line in lines:
                if line.startswith('## '):
                    sections.append(line[3:].strip())
            
            if sections:
                outline = BlogOutline(
                    title=title,
                    sections=sections,
                    estimated_word_count=len(content.split())
                )
        
        # Extract keywords used (simple implementation)
        keywords_used = request.keywords or [request.topic.lower()]
        
        blog_response = BlogGenerationResponse(
            id=generation_id,
            title=title,
            content=content,
            outline=outline,
            keywords_used=keywords_used,
            word_count=len(content.split()),
            tone=request.tone or "professional",
            created_at=int(time.time()),
            model_used=model
        )
        
        logger.info(f"Blog generation successful: {generation_id}, words: {blog_response.word_count}")
        return blog_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Blog generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

