#!/usr/bin/env python3
"""
Markdown to JSON Resume Converter
Converts Hugo markdown content files to JSON Resume format (v1.0.0)
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional


class MarkdownToJsonConverter:
    """Converts markdown content files to JSON Resume format"""
    
    def __init__(self, content_dir: str = "content", hugo_config: str = "hugo.toml"):
        self.content_dir = Path(content_dir)
        self.hugo_config = Path(hugo_config)
        self.resume_data = {
            "basics": {},
            "work": [],
            "education": [],
            "skills": [],
            "projects": [],
            "volunteer": [],
            "awards": [],
            "publications": [],
            "languages": [],
            "interests": [],
            "references": [],
            "meta": {
                "version": "v1.0.0",
                "canonical": "https://github.com/jsonresume/resume-schema/blob/v1.0.0/schema.json"
            }
        }
    
    def parse_hugo_config(self) -> Dict[str, Any]:
        """Parse hugo.toml for basic information"""
        config_data = {}
        if not self.hugo_config.exists():
            return config_data
        
        content = self.hugo_config.read_text(encoding='utf-8')
        
        # Extract basic info
        if match := re.search(r'title\s*=\s*["\']([^"\']+)["\']', content):
            config_data['name'] = match.group(1)
        
        if match := re.search(r'baseURL\s*=\s*["\']([^"\']+)["\']', content):
            config_data['url'] = match.group(1).rstrip('/')
        
        # Extract author info
        if match := re.search(r'author\s*=\s*["\']([^"\']+)["\']', content):
            config_data['author'] = match.group(1)
        
        if match := re.search(r'info\s*=\s*\[([^\]]+)\]', content):
            info_content = match.group(1)
            info_items = re.findall(r'["\']([^"\']+)["\']', info_content)
            if info_items:
                config_data['label'] = info_items[0]
        
        # Extract social profiles
        profiles = []
        social_blocks = re.finditer(r'\[\[params\.social\]\](.*?)(?=\[\[params\.social\]\]|\Z)', content, re.DOTALL)
        for block in social_blocks:
            block_content = block.group(1)
            profile = {}
            if match := re.search(r'name\s*=\s*["\']([^"\']+)["\']', block_content):
                profile['network'] = match.group(1)
            if match := re.search(r'url\s*=\s*["\']([^"\']+)["\']', block_content):
                profile['url'] = match.group(1)
            if profile:
                profiles.append(profile)
        
        config_data['profiles'] = profiles
        return config_data
    
    def parse_front_matter(self, content: str) -> tuple[Dict[str, str], str]:
        """Extract TOML front matter and return it with remaining content"""
        front_matter = {}
        body = content
        
        if content.startswith('+++'):
            parts = content.split('+++', 2)
            if len(parts) >= 3:
                front_matter_text = parts[1].strip()
                body = parts[2].strip()
                
                # Parse simple TOML key-value pairs
                for line in front_matter_text.split('\n'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"\'')
                        front_matter[key] = value
        
        return front_matter, body
    
    def parse_contact_info(self) -> Dict[str, Any]:
        """Parse contact information from contact.md and other.md"""
        contact_info = {}
        
        # Parse contact.md
        contact_file = self.content_dir / "contact.md"
        if contact_file.exists():
            content = contact_file.read_text(encoding='utf-8')
            
            # Extract email
            if match := re.search(r'saleh\.mehdikhani\s*\[at\]\s*gmail\s*dot\s*com', content, re.IGNORECASE):
                contact_info['email'] = 'saleh.mehdikhani@gmail.com'
            elif match := re.search(r'[\w\.-]+@[\w\.-]+\.\w+', content):
                contact_info['email'] = match.group(0)
            
            # Extract LinkedIn
            if match := re.search(r'linkedin\.com/in/([\w-]+)', content):
                linkedin_username = match.group(1)
                contact_info['linkedin'] = f'https://www.linkedin.com/in/{linkedin_username}/'
        
        # Parse other.md
        other_file = self.content_dir / "other.md"
        if other_file.exists():
            content = other_file.read_text(encoding='utf-8')
            
            # Extract phone
            if match := re.search(r'\*\*Phone:\*\*\s*(\d+)', content):
                phone = match.group(1).strip()
                # Format Finnish phone number
                if not phone.startswith('+'):
                    phone = '+358 ' + phone.lstrip('0')
                contact_info['phone'] = phone
            
            # Extract city
            if match := re.search(r'\*\*City:\*\*\s*(\w+)', content):
                contact_info['city'] = match.group(1)
            
            # Extract country
            if match := re.search(r'\*\*Country:\*\*\s*(\w+)', content):
                contact_info['country'] = match.group(1)
        
        return contact_info
    
    def parse_skills(self, content: str) -> List[Dict[str, Any]]:
        """Parse skills section from markdown content"""
        skills = []
        
        # Find skills section
        skills_match = re.search(r'##\s+Skills\s*\n(.*?)(?=\n##\s+[^#]|\n---|\Z)', content, re.DOTALL)
        if not skills_match:
            return skills
        
        skills_content = skills_match.group(1)
        
        # Parse each skill line: - **Category:** item1, item2, item3
        skill_lines = re.finditer(r'-\s+\*\*([^:]+):\*\*\s+(.+)', skills_content)
        for match in skill_lines:
            category = match.group(1).strip()
            items = match.group(2).strip()
            keywords = [item.strip() for item in items.split(',')]
            skills.append({
                "name": category,
                "keywords": keywords
            })
        
        return skills
    
    def parse_date(self, date_str: str) -> tuple[Optional[str], Optional[str]]:
        """Parse date string and return start and end dates in ISO format"""
        date_str = date_str.strip('()*')
        
        # Handle date ranges
        if '–' in date_str or '-' in date_str:
            separator = '–' if '–' in date_str else '-'
            parts = [p.strip() for p in date_str.split(separator)]
            
            start_date = self._convert_date(parts[0])
            end_date = None if len(parts) < 2 or 'present' in parts[1].lower() else self._convert_date(parts[1])
            
            return start_date, end_date
        else:
            # Single date
            date = self._convert_date(date_str)
            return date, date
    
    def _convert_date(self, date_str: str) -> Optional[str]:
        """Convert various date formats to ISO format"""
        date_str = date_str.strip()
        
        # Month Year format (e.g., "Sep 2020", "May 2015")
        month_map = {
            'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04',
            'may': '05', 'jun': '06', 'jul': '07', 'aug': '08',
            'sep': '09', 'oct': '10', 'nov': '11', 'dec': '12'
        }
        
        if match := re.match(r'(\w+)\s+(\d{4})', date_str, re.IGNORECASE):
            month_name = match.group(1).lower()[:3]
            year = match.group(2)
            if month_name in month_map:
                return f"{year}-{month_map[month_name]}"
        
        # Year only format (e.g., "2011", "2013")
        if match := re.match(r'(\d{4})', date_str):
            return match.group(1)
        
        return None
    
    def parse_work_experience(self, content: str) -> List[Dict[str, Any]]:
        """Parse work experience section from markdown content"""
        work = []
        
        # Find experience section - include content until next ## heading or end
        exp_match = re.search(r'##\s+Experience\s*\n(.*?)(?=\n##\s+[^#]|\Z)', content, re.DOTALL)
        if not exp_match:
            return work
        
        exp_content = exp_match.group(1)
        # Remove horizontal rules (---) as they're just separators
        exp_content = re.sub(r'\n---\n', '\n\n', exp_content)
        
        # Split by ### to get individual job entries
        job_sections = re.split(r'###\s+', exp_content)
        
        for section in job_sections:
            if not section.strip():
                continue
            # Parse each job entry
            lines = section.strip().split('\n')
            if len(lines) < 3:
                continue
            
            position = lines[0].strip()
            
            # Parse company and location line: **Company** – Location
            company_line = lines[1] if len(lines) > 1 else ""
            company_match = re.match(r'\*\*([^*]+)\*\*\s*[–-]\s*(.+)', company_line)
            if not company_match:
                continue
            
            company = company_match.group(1).strip()
            location = company_match.group(2).strip()
            
            # Parse dates line: (*Date – Date*)
            dates_line = lines[2] if len(lines) > 2 else ""
            dates_match = re.match(r'\(\*([^)]+)\*\)', dates_line)
            if not dates_match:
                continue
            
            dates = dates_match.group(1).strip()
            
            # Get description (everything after the empty line)
            description_lines = []
            found_empty = False
            for line in lines[3:]:
                if not line.strip() and not found_empty:
                    found_empty = True
                    continue
                if found_empty:
                    description_lines.append(line)
            
            description = '\n'.join(description_lines).strip()
            
            start_date, end_date = self.parse_date(dates)
            
            work_entry = {
                "position": position,
                "name": company,
                "location": location,
                "startDate": start_date,
                "summary": description
            }
            
            if end_date:
                work_entry["endDate"] = end_date
            
            work.append(work_entry)
        
        return work
    
    def parse_education(self, content: str) -> List[Dict[str, Any]]:
        """Parse education section from markdown content"""
        education = []
        
        # Find education section - include content until next ## heading or end
        edu_match = re.search(r'##\s+Education\s*\n(.*?)(?=\n##\s+[^#]|\Z)', content, re.DOTALL)
        if not edu_match:
            return education
        
        edu_content = edu_match.group(1)
        # Remove horizontal rules (---) and italic text at the end
        edu_content = re.sub(r'\n---\n', '\n\n', edu_content)
        edu_content = re.sub(r'\n\*[^*]+\*\s*$', '', edu_content)
        
        # Split by ### to get individual education entries
        edu_sections = re.split(r'###\s+', edu_content)
        
        for section in edu_sections:
            if not section.strip():
                continue
            # Parse each education entry
            lines = section.strip().split('\n')
            if len(lines) < 3:
                continue
            
            degree_info = lines[0].strip()
            
            # Parse institution line: **Institution**
            institution_line = lines[1] if len(lines) > 1 else ""
            institution_match = re.match(r'\*\*([^*]+)\*\*', institution_line)
            if not institution_match:
                continue
            
            institution = institution_match.group(1).strip()
            
            # Parse dates line: (*Date – Date*)
            dates_line = lines[2] if len(lines) > 2 else ""
            dates_match = re.match(r'\(\*([^)]+)\*\)', dates_line)
            if not dates_match:
                continue
            
            dates = dates_match.group(1).strip()
            
            # Get description (everything after the empty line)
            description_lines = []
            found_empty = False
            for line in lines[3:]:
                if not line.strip() and not found_empty:
                    found_empty = True
                    continue
                if found_empty and line.strip():
                    description_lines.append(line)
            
            description = '\n'.join(description_lines).strip()
            
            # Parse degree info (e.g., "Master of Science (MS), Computer Architecture")
            degree_match = re.match(r'([^,]+)(?:,\s*(.+))?', degree_info)
            study_type = degree_match.group(1).strip() if degree_match else degree_info
            area = degree_match.group(2).strip() if degree_match and degree_match.group(2) else ""
            
            start_date, end_date = self.parse_date(dates)
            
            edu_entry = {
                "institution": institution,
                "studyType": study_type,
                "area": area,
                "startDate": start_date,
                "endDate": end_date,
                "score": "",
                "courses": []
            }
            
            # Extract thesis information if present
            if 'thesis' in description.lower():
                thesis_match = re.search(r'Thesis:\s*([^\n]+)', description, re.IGNORECASE)
                if thesis_match:
                    edu_entry["courses"].append(thesis_match.group(1).strip())
            
            education.append(edu_entry)
        
        return education
    
    def parse_projects(self) -> List[Dict[str, Any]]:
        """Parse projects from projects.md"""
        projects = []
        
        projects_file = self.content_dir / "projects.md"
        if not projects_file.exists():
            return projects
        
        content = projects_file.read_text(encoding='utf-8')
        _, body = self.parse_front_matter(content)
        
        # Parse each project section
        project_pattern = r'##\s+([^\n]+)\n\*\*Technologies:\*\*\s*([^\n]+)\n\n\*\*Descri[pt]tions?:\*\*\s*((?:.|\n)*?(?=\n##|\n---|\Z))'
        projects_matches = re.finditer(project_pattern, body)
        
        for match in projects_matches:
            title_line = match.group(1).strip()
            technologies = match.group(2).strip()
            description = match.group(3).strip()
            
            # Parse title and entity (e.g., "Project Name: [Entity]")
            title_match = re.match(r'([^:\[]+)(?::\s*\[([^\]]+)\])?', title_line)
            name = title_match.group(1).strip() if title_match else title_line
            entity = title_match.group(2).strip() if title_match and title_match.group(2) else ""
            
            # Parse technologies
            tech_list = [tech.strip() for tech in technologies.split(',')]
            
            # Extract URLs from description
            url = ""
            # Look for View on or Demo links
            urls = re.findall(r'\[(?:View on [^\]]+|Demo)\]\(([^)]+)\)', description)
            if urls:
                url = urls[0]  # Use first URL as primary
            # Also check for plain URLs in markdown links
            if not url:
                plain_urls = re.findall(r'\]\((https?://[^)]+)\)', description)
                if plain_urls:
                    url = plain_urls[0]
            
            # Clean description (remove markdown links and bold markers)
            clean_desc = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', description)
            clean_desc = re.sub(r'\*\*([^*]+)\*\*', r'\1', clean_desc)
            clean_desc = clean_desc.strip()

            # Separate a main description from a bulleted list
            description_text = ""
            highlights = []
            
            if "\n-" in clean_desc:
                parts = clean_desc.split("\n-")
                description_text = parts[0].strip()
                highlights = [item.strip().lstrip('* ').rstrip() for item in parts[1:]]
            else:
                description_text = clean_desc
            
            project_entry = {
                "name": name,
                "summary": description_text,
                "highlights": highlights,
                "keywords": tech_list,
                "startDate": "",
                "endDate": "",
                "url": url,
                "roles": [],
                "entity": entity,
                "type": ""
            }
            
            projects.append(project_entry)
        
        return projects
    
    def build_resume(self) -> Dict[str, Any]:
        """Build complete resume JSON from all markdown files"""
        
        # Parse Hugo config
        config_data = self.parse_hugo_config()
        
        # Parse contact info
        contact_info = self.parse_contact_info()
        
        # Build basics section
        self.resume_data["basics"] = {
            "name": config_data.get('name', 'Saleh Mehdikhani'),
            "label": config_data.get('label', 'Senior System Software Developer'),
            "email": contact_info.get('email', ''),
            "phone": contact_info.get('phone', ''),
            "url": config_data.get('url', ''),
            "summary": "",
            "location": {
                "city": contact_info.get('city', ''),
                "countryCode": "FI",
                "region": contact_info.get('country', 'Finland')
            },
            "profiles": config_data.get('profiles', [])
        }
        
        # Add LinkedIn to profiles if found in contact info
        if contact_info.get('linkedin'):
            linkedin_profile = {
                "network": "LinkedIn",
                "username": contact_info.get('linkedin', '').split('/')[-2],
                "url": contact_info.get('linkedin', '')
            }
            # Check if LinkedIn not already in profiles
            if not any(p.get('network') == 'LinkedIn' for p in self.resume_data["basics"]["profiles"]):
                self.resume_data["basics"]["profiles"].append(linkedin_profile)
        
        # Parse about.md for summary, skills, experience, and education
        about_file = self.content_dir / "about.md"
        if about_file.exists():
            content = about_file.read_text(encoding='utf-8')
            _, body = self.parse_front_matter(content)
            
            # Extract summary (first paragraph after front matter)
            summary_match = re.match(r'([^\n]+(?:\n(?!##)[^\n]+)*)', body.strip())
            if summary_match:
                self.resume_data["basics"]["summary"] = summary_match.group(1).strip()
            
            # Parse sections
            self.resume_data["skills"] = self.parse_skills(body)
            self.resume_data["work"] = self.parse_work_experience(body)
            self.resume_data["education"] = self.parse_education(body)
        
        # Parse projects
        self.resume_data["projects"] = self.parse_projects()
        
        return self.resume_data
    
    def save_json(self, output_path: str):
        """Save resume data to JSON file"""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with output_file.open('w', encoding='utf-8') as f:
            json.dump(self.resume_data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Resume JSON saved to: {output_file}")


def main():
    """Main execution function"""
    print("Converting Markdown to JSON Resume format...")
    print("-" * 50)
    
    converter = MarkdownToJsonConverter()
    resume_data = converter.build_resume()
    
    # Save to build directory
    output_path = "build/resume.json"
    converter.save_json(output_path)
    
    print("-" * 50)
    print(f"✓ Conversion complete!")
    print(f"  - Basics: {resume_data['basics']['name']}")
    print(f"  - Skills: {len(resume_data['skills'])} categories")
    print(f"  - Work Experience: {len(resume_data['work'])} positions")
    print(f"  - Education: {len(resume_data['education'])} degrees")
    print(f"  - Projects: {len(resume_data['projects'])} projects")


if __name__ == "__main__":
    main()