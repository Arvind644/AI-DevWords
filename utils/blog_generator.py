import os
import openai
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dotenv import load_dotenv
from exa_py import Exa

load_dotenv()

class BlogGenerator:
    def __init__(self):
        self.exa_api_key = os.getenv("EXA_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        if not self.exa_api_key:
            raise ValueError("EXA_API_KEY not found in environment variables")
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
            
        self.exa = Exa(self.exa_api_key)
        openai.api_key = self.openai_api_key

    def _generate_search_query(self, topic: str, style: str) -> str:
        """Generate an optimized search query using OpenAI."""
        prompt = f"Generate a search query to find recent information about {topic} "
        if style == "Technical":
            prompt += "focusing on technical details and implementation"
        elif style == "Tutorial":
            prompt += "focusing on tutorials and how-to guides"
        elif style == "Overview":
            prompt += "focusing on high-level concepts and introductions"
        elif style == "Deep Dive":
            prompt += "focusing on in-depth analysis and advanced concepts"

        completion = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Generate a concise search query based on the topic and style. Only return the query text."},
                {"role": "user", "content": prompt}
            ]
        )
        return completion.choices[0].message.content

    def _search_recent_content(self, query: str, days: int = 30) -> List[Dict]:
        """Search for recent content using Exa."""
        date_cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        search_response = self.exa.search_and_contents(
            query,
            use_autoprompt=True,
            start_published_date=date_cutoff
        )
        return search_response.results

    def _get_length_instruction(self, length: str) -> tuple:
        """Get word count and instruction based on desired length."""
        length_configs = {
            "short": (800, "Create a concise and focused article around 800 words"),
            "medium": (1500, "Create a comprehensive article around 1500 words"),
            "long": (2500, "Create a detailed, in-depth article around 2500 words"),
            "very_long": (4000, "Create an extensive, thoroughly detailed article around 4000 words")
        }
        return length_configs.get(length, length_configs["medium"])

    def _get_model_config(self, length: str) -> Dict:
        """Get model configuration based on content length."""
        configs = {
            "short": {
                "model": "gpt-3.5-turbo",
                "max_tokens": 1200,  # ~800 words
                "temperature": 0.7,
                "presence_penalty": 0.0
            },
            "medium": {
                "model": "gpt-3.5-turbo",
                "max_tokens": 2200,  # ~1500 words
                "temperature": 0.7,
                "presence_penalty": 0.1
            },
            "long": {
                "model": "gpt-4",  # Using GPT-4 for better long-form content
                "max_tokens": 3700,  # ~2500 words
                "temperature": 0.75,
                "presence_penalty": 0.2
            },
            "very_long": {
                "model": "gpt-4",  # Using GPT-4 for better long-form content
                "max_tokens": 6000,  # ~4000 words
                "temperature": 0.8,
                "presence_penalty": 0.3
            }
        }
        return configs.get(length, configs["medium"])

    def _generate_content_in_chunks(self, topic: str, context: str, style: str, length: str) -> str:
        """Generate content in chunks for very long articles."""
        word_count, length_instruction = self._get_length_instruction(length)
        model_config = self._get_model_config(length)
        
        if length != "very_long":
            # For shorter content, generate in one go
            return self._generate_single_chunk(topic, context, style, length_instruction, model_config)
        
        # For very long content, generate in sections
        sections = [
            "Introduction and Background",
            "Main Concepts and Technical Details",
            "Analysis and Implementation",
            "Advanced Topics and Future Implications",
            "Conclusion and Key Takeaways"
        ]
        
        content_parts = []
        section_word_count = word_count // len(sections)
        
        for i, section in enumerate(sections):
            section_prompt = f"""Based on the following information about {topic}, create the {section} section.
            
{context}

This is section {i+1} of {len(sections)}. Target length: ~{section_word_count} words.
Style: {style}

Make sure this section flows naturally with the other sections and maintains a cohesive narrative.
"""
            
            completion = openai.chat.completions.create(
                model=model_config["model"],
                messages=[
                    {"role": "system", "content": "You are an expert technical writer creating a section of a comprehensive article."},
                    {"role": "user", "content": section_prompt}
                ],
                max_tokens=model_config["max_tokens"] // len(sections),
                temperature=model_config["temperature"],
                presence_penalty=model_config["presence_penalty"]
            )
            
            content_parts.append(completion.choices[0].message.content)
        
        # Generate title separately
        title_prompt = f"Generate a compelling title for a comprehensive article about {topic} in {style} style."
        title_completion = openai.chat.completions.create(
            model=model_config["model"],
            messages=[
                {"role": "system", "content": "Generate only the title, nothing else."},
                {"role": "user", "content": title_prompt}
            ],
            max_tokens=50,
            temperature=0.7
        )
        
        title = title_completion.choices[0].message.content.strip()
        return f"# {title}\n\n" + "\n\n".join(content_parts)

    def _generate_single_chunk(self, topic: str, context: str, style: str, length_instruction: str, model_config: Dict) -> str:
        """Generate content in a single chunk for shorter articles."""
        style_instructions = {
            "Technical": "Create a technical blog post with detailed explanations and focus on implementation details.",
            "Tutorial": "Create a step-by-step tutorial that guides readers through learning and implementation.",
            "Overview": "Create a high-level overview that introduces key concepts and their importance.",
            "Deep Dive": "Create an in-depth analysis that explores advanced concepts and their implications."
        }

        prompt = f"""Based on the following recent information about {topic}, {style_instructions.get(style, '')}

{length_instruction}

Context:
{context}

Generate a comprehensive blog post that includes:
1. An engaging title
2. A well-structured main content with appropriate headings and subheadings
3. Key takeaways or conclusions
4. If relevant, code examples or technical specifications

Use appropriate section breaks and formatting for better readability.
"""

        completion = openai.chat.completions.create(
            model=model_config["model"],
            messages=[
                {"role": "system", "content": "You are an expert technical writer who creates high-quality blog content."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=model_config["max_tokens"],
            temperature=model_config["temperature"],
            presence_penalty=model_config["presence_penalty"]
        )

        return completion.choices[0].message.content

    def _generate_content(self, topic: str, search_results: List[Dict], style: str, length: str = "medium") -> Dict:
        """Generate content using OpenAI based on search results."""
        # Prepare context from search results
        num_results = 7 if length in ["long", "very_long"] else 3
        context = "\n\n".join([
            f"Title: {result.title}\nContent: {result.text[:2000] if length in ['long', 'very_long'] else result.text[:500]}..."
            for result in search_results[:num_results]
        ])

        # Generate content
        content = self._generate_content_in_chunks(topic, context, style, length)

        # Extract title and content
        lines = content.split("\n")
        title = lines[0].replace("# ", "").strip()
        main_content = "\n".join(lines[1:]).strip()

        return {
            "title": title,
            "content": main_content,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "tags": [topic, style],
            "length": length,
            "target_word_count": self._get_length_instruction(length)[0],
            "code_examples": []  # TODO: Extract code examples if present
        }

    def generate_blog_post(self, topic: str, style: str = "technical", length: str = "medium") -> Dict:
        """
        Generate a complete blog post about a given topic.
        
        Args:
            topic (str): The main topic of the blog post
            style (str): The writing style ("Technical", "Tutorial", "Overview", "Deep Dive")
            length (str): Desired length of the article ("short", "medium", "long", "very_long")
        """
        # Generate optimized search query
        search_query = self._generate_search_query(topic, style)
        
        # Search for recent content
        search_results = self._search_recent_content(search_query)
        
        # Generate the blog post
        return self._generate_content(topic, search_results, style, length)

    def generate_tutorial(self, topic: str, difficulty: str = "intermediate") -> Dict:
        """Generate a step-by-step tutorial with code examples."""
        return self.generate_blog_post(topic, style="Tutorial")

    def track_tech_trends(self, technology: str) -> List[Dict]:
        """Track recent developments and trends for a specific technology."""
        search_results = self._search_recent_content(f"latest developments in {technology}")
        return [{"title": r.title, "url": r.url, "summary": r.text[:200]} for r in search_results]

    def generate_code_examples(self, topic: str, language: str) -> List[Dict]:
        """Generate relevant code examples for a given topic."""
        search_query = f"{topic} code examples in {language}"
        search_results = self._search_recent_content(search_query)
        
        # Extract code blocks from search results
        code_examples = []
        for result in search_results:
            if "```" in result.text:
                code_blocks = result.text.split("```")
                for i in range(1, len(code_blocks), 2):
                    code_examples.append({
                        "language": language,
                        "code": code_blocks[i].strip(),
                        "source": result.url
                    })
        
        return code_examples

    def format_content(self, content: Dict, output_format: str = "markdown") -> str:
        """
        Format the generated content in the specified format.
        """
        return "" 