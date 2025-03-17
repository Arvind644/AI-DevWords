import markdown
import json
from typing import Dict, List
from bs4 import BeautifulSoup
import frontmatter

class ContentProcessor:
    def __init__(self):
        self.supported_formats = ["markdown", "html", "json"]

    def process_content(self, content: Dict, output_format: str = "markdown") -> str:
        """
        Process and format the content in the specified format.
        """
        if output_format not in self.supported_formats:
            raise ValueError(f"Unsupported format: {output_format}")

        if output_format == "markdown":
            return self._to_markdown(content)
        elif output_format == "html":
            return self._to_html(content)
        else:
            return json.dumps(content, indent=2)

    def _to_markdown(self, content: Dict) -> str:
        """
        Convert content to markdown format.
        """
        md = f"# {content.get('title', 'Untitled')}\n\n"
        md += f"*Generated on {content.get('date', '')}*\n\n"
        
        if 'content' in content:
            md += content['content'] + "\n\n"
            
        if 'code_examples' in content and content['code_examples']:
            md += "## Code Examples\n\n"
            for example in content['code_examples']:
                md += f"```{example.get('language', '')}\n{example.get('code', '')}\n```\n\n"
                
        if 'tags' in content and content['tags']:
            md += "**Tags:** " + ", ".join(content['tags'])
            
        return md

    def _to_html(self, content: Dict) -> str:
        """
        Convert content to HTML format.
        """
        md_content = self._to_markdown(content)
        return markdown.markdown(md_content)

    def add_metadata(self, content: Dict) -> Dict:
        """
        Add metadata to the content.
        """
        metadata = {
            "generated_at": content.get("date", ""),
            "generator": "Technical Blog Generator",
            "version": "1.0",
            "type": content.get("type", "blog_post")
        }
        content["metadata"] = metadata
        return content

    def validate_content(self, content: Dict) -> bool:
        """
        Validate the content structure and required fields.
        """
        required_fields = ["title", "content"]
        return all(field in content for field in required_fields) 