"""
Message Template Manager for Business Lead Automation System
Handles message templates and personalization
"""
import json
import re
from typing import Dict, List, Any, Optional
from pathlib import Path

from utils.config import config
from utils.logger import get_logger, log_info, log_error, log_warning
from utils.validators import InputValidator

class MessageTemplateManager:
    """Manages message templates and personalization"""

    def __init__(self, templates_file: Optional[str] = None):
        self.logger = get_logger('MessageTemplateManager')
        self.templates_file = templates_file or config.get_templates_path()
        self.templates = {}

        # Default templates
        self.default_templates = {
            'construction_website': {
                'name': 'Construction Website Offer',
                'content': """Merhaba {business_name},

{location} bölgesinde faaliyet gösteren işletmeniz için profesyonel bir web sitesi hazırlayabiliriz.

Dijital varlığınızı güçlendirerek daha fazla müşteriye ulaşmanıza yardımcı olalım.

Ücretsiz görüşme için mesaj atabilirsiniz.

İyi çalışmalar,
[Your Agency Name]""",
                'variables': ['business_name', 'location'],
                'category': 'Website Services'
            },

            'restaurant_website': {
                'name': 'Restaurant Website Offer',
                'content': """Merhaba {business_name},

{location} bölgesindeki restoranınız için özel tasarım web sitesi ve online sipariş sistemi hazırlayabiliriz.

✅ Menü yönetimi
✅ Online rezervasyon
✅ Sipariş sistemi
✅ Sosyal medya entegrasyonu

Detaylı bilgi için mesaj atabilirsiniz.

Afiyet olsun,
[Your Agency Name]""",
                'variables': ['business_name', 'location'],
                'category': 'Website Services'
            },

            'general_business': {
                'name': 'General Business Offer',
                'content': """Merhaba {business_name},

{industry} sektöründe faaliyet gösteren işletmeniz için dijital çözümler sunuyoruz:

🌐 Profesyonel web sitesi
📱 Mobil uyumlu tasarım
🔍 Google'da üst sıralarda çıkma
📊 Sosyal medya yönetimi

{location} bölgesindeki işletmelere özel fiyatlarımız var.

Bilgi almak için mesaj atabilirsiniz.

Saygılarımla,
[Your Agency Name]""",
                'variables': ['business_name', 'industry', 'location'],
                'category': 'General Services'
            },

            'follow_up': {
                'name': 'Follow-up Message',
                'content': """Merhaba {business_name},

Daha önce {industry} işletmeniz için web sitesi konusunda mesaj göndermiştim.

Konuyla ilgili düşüncelerinizi merak ediyorum. Ücretsiz bir görüşme yaparak size nasıl yardımcı olabileceğimizi anlatabiliriz.

Müsait olduğunuz bir zaman dilimi var mı?

İyi çalışmalar,
[Your Agency Name]""",
                'variables': ['business_name', 'industry'],
                'category': 'Follow-up'
            }
        }

        # Load existing templates
        self.load_templates()

        log_info("MessageTemplateManager initialized")

    def load_templates(self) -> bool:
        """Load templates from file"""
        try:
            if Path(self.templates_file).exists():
                with open(self.templates_file, 'r', encoding='utf-8') as f:
                    loaded_templates = json.load(f)
                    self.templates.update(loaded_templates)
                    log_info(f"Loaded {len(loaded_templates)} templates from file")
            else:
                # Create file with default templates
                self.templates = self.default_templates.copy()
                self.save_templates()
                log_info("Created templates file with default templates")

            return True

        except Exception as e:
            log_error("Failed to load templates", e)
            # Use default templates as fallback
            self.templates = self.default_templates.copy()
            return False

    def save_templates(self) -> bool:
        """Save templates to file"""
        try:
            # Ensure directory exists
            Path(self.templates_file).parent.mkdir(parents=True, exist_ok=True)

            with open(self.templates_file, 'w', encoding='utf-8') as f:
                json.dump(self.templates, f, ensure_ascii=False, indent=2)

            log_info(f"Saved {len(self.templates)} templates to file")
            return True

        except Exception as e:
            log_error("Failed to save templates", e)
            return False

    def save_template(self, template_id: str, name: str, content: str, category: str = 'Custom') -> bool:
        """Save a new template"""
        try:
            # Validate template content
            is_valid, errors = InputValidator.validate_message_template(content)
            if not is_valid:
                log_error(f"Invalid template content: {errors}")
                return False

            # Extract variables from template
            variables = self.get_template_variables(content)

            # Save template
            self.templates[template_id] = {
                'name': name,
                'content': content,
                'variables': variables,
                'category': category
            }

            # Save to file
            success = self.save_templates()

            if success:
                log_info(f"Saved template: {name}")

            return success

        except Exception as e:
            log_error(f"Failed to save template {name}", e)
            return False

    def get_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Get a template by ID"""
        return self.templates.get(template_id)

    def get_all_templates(self) -> Dict[str, Dict[str, Any]]:
        """Get all templates"""
        return self.templates.copy()

    def get_templates_by_category(self, category: str) -> Dict[str, Dict[str, Any]]:
        """Get templates by category"""
        return {
            template_id: template
            for template_id, template in self.templates.items()
            if template.get('category') == category
        }

    def delete_template(self, template_id: str) -> bool:
        """Delete a template"""
        try:
            if template_id in self.templates:
                template_name = self.templates[template_id].get('name', template_id)
                del self.templates[template_id]

                # Save changes
                success = self.save_templates()

                if success:
                    log_info(f"Deleted template: {template_name}")

                return success
            else:
                log_warning(f"Template not found: {template_id}")
                return False

        except Exception as e:
            log_error(f"Failed to delete template {template_id}", e)
            return False

    def personalize_message(self, template_id: str, business_data: Dict[str, Any]) -> Optional[str]:
        """Personalize a message template with business data"""
        try:
            template = self.get_template(template_id)
            if not template:
                log_error(f"Template not found: {template_id}")
                return None

            content = template['content']

            # Replace placeholders with business data
            personalized = self._replace_placeholders(content, business_data)

            log_info(f"Personalized template {template_id} for {business_data.get('business_name', 'Unknown')}")
            return personalized

        except Exception as e:
            log_error(f"Failed to personalize template {template_id}", e)
            return None

    def personalize_message_content(self, content: str, business_data: Dict[str, Any]) -> str:
        """Personalize message content directly"""
        try:
            return self._replace_placeholders(content, business_data)
        except Exception as e:
            log_error("Failed to personalize message content", e)
            return content

    def _replace_placeholders(self, content: str, business_data: Dict[str, Any]) -> str:
        """Replace placeholders in content with business data"""
        # Available placeholders
        placeholders = {
            'business_name': business_data.get('business_name', '[Business Name]'),
            'location': business_data.get('location', '[Location]'),
            'industry': business_data.get('industry', '[Industry]'),
            'address': business_data.get('address', '[Address]'),
            'phone': business_data.get('phone', '[Phone]'),
            'email': business_data.get('email', '[Email]'),
            'website': business_data.get('website', '[Website]')
        }

        # Replace placeholders
        personalized = content
        for placeholder, value in placeholders.items():
            pattern = '{' + placeholder + '}'
            personalized = personalized.replace(pattern, str(value) if value else f'[{placeholder.title()}]')

        return personalized

    def get_template_variables(self, content: str) -> List[str]:
        """Extract variables from template content"""
        try:
            # Find all placeholders in format {variable_name}
            variables = re.findall(r'\{([^}]+)\}', content)
            return list(set(variables))  # Remove duplicates

        except Exception as e:
            log_error("Failed to extract template variables", e)
            return []

    def validate_template(self, content: str) -> tuple[bool, List[str]]:
        """Validate template content"""
        return InputValidator.validate_message_template(content)

    def get_template_preview(self, template_id: str, sample_data: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Get a preview of the template with sample data"""
        try:
            template = self.get_template(template_id)
            if not template:
                return None

            # Use sample data or default values
            if not sample_data:
                sample_data = {
                    'business_name': 'Örnek İşletme',
                    'location': 'İzmir',
                    'industry': 'İnşaat',
                    'address': 'Konak, İzmir',
                    'phone': '+90 555 123 45 67',
                    'email': 'info@ornek.com',
                    'website': 'https://ornek.com'
                }

            return self.personalize_message(template_id, sample_data)

        except Exception as e:
            log_error(f"Failed to generate template preview for {template_id}", e)
            return None

    def duplicate_template(self, source_template_id: str, new_template_id: str, new_name: str) -> bool:
        """Duplicate an existing template"""
        try:
            source_template = self.get_template(source_template_id)
            if not source_template:
                log_error(f"Source template not found: {source_template_id}")
                return False

            # Create new template with same content but different name
            return self.save_template(
                new_template_id,
                new_name,
                source_template['content'],
                source_template.get('category', 'Custom')
            )

        except Exception as e:
            log_error(f"Failed to duplicate template {source_template_id}", e)
            return False

    def get_categories(self) -> List[str]:
        """Get all template categories"""
        categories = set()
        for template in self.templates.values():
            categories.add(template.get('category', 'Uncategorized'))
        return sorted(list(categories))

    def search_templates(self, query: str) -> Dict[str, Dict[str, Any]]:
        """Search templates by name or content"""
        try:
            query_lower = query.lower()
            results = {}

            for template_id, template in self.templates.items():
                name = template.get('name', '').lower()
                content = template.get('content', '').lower()

                if query_lower in name or query_lower in content:
                    results[template_id] = template

            log_info(f"Template search for '{query}' returned {len(results)} results")
            return results

        except Exception as e:
            log_error(f"Failed to search templates for '{query}'", e)
            return {}

    def export_templates(self, export_file: str) -> bool:
        """Export templates to a file"""
        try:
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(self.templates, f, ensure_ascii=False, indent=2)

            log_info(f"Exported {len(self.templates)} templates to {export_file}")
            return True

        except Exception as e:
            log_error(f"Failed to export templates to {export_file}", e)
            return False

    def import_templates(self, import_file: str, overwrite: bool = False) -> bool:
        """Import templates from a file"""
        try:
            with open(import_file, 'r', encoding='utf-8') as f:
                imported_templates = json.load(f)

            imported_count = 0
            for template_id, template in imported_templates.items():
                if template_id not in self.templates or overwrite:
                    self.templates[template_id] = template
                    imported_count += 1

            # Save changes
            success = self.save_templates()

            if success:
                log_info(f"Imported {imported_count} templates from {import_file}")

            return success

        except Exception as e:
            log_error(f"Failed to import templates from {import_file}", e)
            return False