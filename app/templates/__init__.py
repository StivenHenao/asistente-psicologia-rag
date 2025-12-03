from pathlib import Path
from typing import Any

class TemplateLoader:
    def __init__(self, templates_dir: Path = None):
        if templates_dir is None:
            self.templates_dir = Path(__file__).parent
        else:
            self.templates_dir = templates_dir
    
    def load_template(self, template_path: str) -> str:
        """Carga un template desde un archivo."""
        full_path = self.templates_dir / template_path
        if not full_path.exists():
            raise FileNotFoundError(f"Template no encontrado: {full_path}")
        
        with open(full_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def render_template(self, template_path: str, **kwargs: Any) -> str:
        """Carga y renderiza un template con las variables proporcionadas."""
        template = self.load_template(template_path)
        return self._render(template, **kwargs)
    
    def _render(self, template: str, **kwargs: Any) -> str:
        """Renderiza un template string simple."""
        for key, value in kwargs.items():
            template = template.replace(f"{{{{{key}}}}}", str(value))
        return template

# Crear una instancia global
template_loader = TemplateLoader()

# Funciones de conveniencia
def load_template(template_path: str) -> str:
    return template_loader.load_template(template_path)

def render_template(template_path: str, **kwargs) -> str:
    return template_loader.render_template(template_path, **kwargs)

# Definir rutas constantes para los templates
WELCOME_EMAIL = "email/welcome_email.html"
FACTOR_UPDATED_EMAIL = "email/factor_updated.html"
