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

    def _generate_content(self, topic: str, search_results: List[Dict], style: str) -> Dict:
        """Generate content using OpenAI based on search results."""
        # Prepare context from search results
        context = "\n\n".join([
            f"Title: {result.title}\nContent: {result.text[:500]}..."  # Limit content length
            for result in search_results[:3]  # Use top 3 results
        ])

        style_instructions = {
            "Technical": "Create a technical blog post with detailed explanations and focus on implementation details.",
            "Tutorial": "Create a step-by-step tutorial that guides readers through learning and implementation.",
            "Overview": "Create a high-level overview that introduces key concepts and their importance.",
            "Deep Dive": "Create an in-depth analysis that explores advanced concepts and their implications."
        }

        prompt = f"""Based on the following recent information about {topic}, {style_instructions.get(style, '')}

Context:
{context}

Generate a comprehensive blog post that includes:
1. An engaging title
2. A well-structured main content
3. Key takeaways or conclusions
4. If relevant, code examples or technical specifications
"""

        completion = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert technical writer who creates high-quality blog content."},
                {"role": "user", "content": prompt}
            ]
        )

        content = completion.choices[0].message.content

        # Extract title and content
        lines = content.split("\n")
        title = lines[0].replace("# ", "").strip()
        main_content = "\n".join(lines[1:]).strip()

        return {
            "title": title,
            "content": main_content,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "tags": [topic, style],
            "code_examples": []  # TODO: Extract code examples if present
        }

    def generate_blog_post(self, topic: str, style: str = "technical") -> Dict:
        """Generate a complete blog post about a given topic."""
        # Generate optimized search query
        search_query = self._generate_search_query(topic, style)
        
        # Search for recent content
        search_results = self._search_recent_content(search_query)
        
        # Generate the blog post
        return self._generate_content(topic, search_results, style)

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