import pystache
from typing import Dict


class TemplateEngine:
    """Mustache template engine for variable substitution."""

    def __init__(self):
        self.renderer = pystache.Renderer()

    def render(self, template: str, variables: Dict[str, str]) -> str:
        """
        Render template with variable substitution.

        Args:
            template: Template string with {{variable}} placeholders
            variables: Dict of variable names to values

        Returns:
            Rendered string with variables substituted (missing vars → empty string)
        """
        return self.renderer.render(template, variables)
