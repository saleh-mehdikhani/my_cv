#!/usr/bin/env python3
"""
Resume Build Script
Orchestrates the complete workflow: Markdown → JSON → PDF
"""

import subprocess
import sys
from pathlib import Path
import json


class ResumeBuilder:
    """Orchestrates the resume building process"""
    
    def __init__(self):
        self.build_dir = Path("build")
        self.json_file = self.build_dir / "resume.json"
        self.pdf_file = self.build_dir / "resume.pdf"
        self.theme = "stackoverflow"
    
    def print_header(self, message: str):
        """Print a formatted header"""
        print("\n" + "=" * 60)
        print(f"  {message}")
        print("=" * 60)
    
    def print_step(self, step: int, message: str):
        """Print a step message"""
        print(f"\n[Step {step}] {message}")
        print("-" * 60)
    
    def create_build_directory(self):
        """Create build directory if it doesn't exist"""
        self.print_step(1, "Creating build directory")
        self.build_dir.mkdir(exist_ok=True)
        print(f"✓ Build directory ready: {self.build_dir}")
    
    def convert_markdown_to_json(self):
        """Run the markdown to JSON converter"""
        self.print_step(2, "Converting Markdown to JSON Resume format")
        
        try:
            result = subprocess.run(
                [sys.executable, "md_to_json.py"],
                capture_output=True,
                text=True,
                check=True
            )
            print(result.stdout)
            
            # Verify JSON file was created
            if not self.json_file.exists():
                raise FileNotFoundError(f"JSON file not created: {self.json_file}")
            
            # Validate JSON
            with open(self.json_file, 'r', encoding='utf-8') as f:
                resume_data = json.load(f)
            
            print(f"✓ JSON Resume validated successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"✗ Error converting markdown to JSON:")
            print(e.stderr)
            return False
        except json.JSONDecodeError as e:
            print(f"✗ Invalid JSON generated: {e}")
            return False
        except Exception as e:
            print(f"✗ Unexpected error: {e}")
            return False
    
    def check_node_installed(self) -> bool:
        """Check if Node.js is installed"""
        try:
            result = subprocess.run(
                ["node", "--version"],
                capture_output=True,
                text=True,
                check=True
            )
            print(f"✓ Node.js is installed: {result.stdout.strip()}")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("✗ Node.js is not installed")
            print("  Please install Node.js from: https://nodejs.org/")
            return False
    
    def check_npm_installed(self) -> bool:
        """Check if npm is installed"""
        try:
            result = subprocess.run(
                ["npm", "--version"],
                capture_output=True,
                text=True,
                check=True
            )
            print(f"✓ npm is installed: {result.stdout.strip()}")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("✗ npm is not installed")
            return False
    
    def check_resume_cli_installed(self) -> bool:
        """Check if resume-cli is installed globally"""
        try:
            result = subprocess.run(
                ["resume", "--version"],
                capture_output=True,
                text=True,
                check=True
            )
            print(f"✓ resume-cli is installed: {result.stdout.strip()}")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("✗ resume-cli is not installed globally")
            return False
    
    def install_resume_cli(self):
        """Install resume-cli globally"""
        print("\nInstalling resume-cli globally...")
        try:
            subprocess.run(
                ["npm", "install", "-g", "resume-cli"],
                check=True
            )
            print("✓ resume-cli installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to install resume-cli: {e}")
            print("  You may need to run with sudo: sudo npm install -g resume-cli")
            return False
    
    def install_theme(self):
        """Install the Stack Overflow theme"""
        print(f"\nInstalling {self.theme} theme...")
        try:
            subprocess.run(
                ["npm", "install", "-g", f"jsonresume-theme-{self.theme}"],
                check=True
            )
            print(f"✓ Theme '{self.theme}' installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to install theme: {e}")
            return False
    
    def setup_dependencies(self):
        """Setup all required dependencies"""
        self.print_step(3, "Checking and installing dependencies")
        
        # Check Node.js and npm
        if not self.check_node_installed():
            return False
        
        if not self.check_npm_installed():
            return False
        
        # Check and install resume-cli
        if not self.check_resume_cli_installed():
            print("\nresume-cli not found. Installing...")
            if not self.install_resume_cli():
                return False
        
        # Install theme
        if not self.install_theme():
            print("⚠ Theme installation failed, but will try to continue...")
        
        return True
    
    def generate_pdf(self):
        """Generate PDF from JSON Resume"""
        self.print_step(4, "Generating PDF with Stack Overflow theme")
        
        try:
            # Use resume export command
            cmd = [
                "resume",
                "export",
                str(self.pdf_file),
                "--theme", self.theme,
                "--resume", str(self.json_file)
            ]
            
            print(f"Running: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            if result.stdout:
                print(result.stdout)
            
            # Verify PDF was created
            if not self.pdf_file.exists():
                raise FileNotFoundError(f"PDF file not created: {self.pdf_file}")
            
            # Check file size
            file_size = self.pdf_file.stat().st_size
            print(f"✓ PDF generated successfully")
            print(f"  File: {self.pdf_file}")
            print(f"  Size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"✗ Error generating PDF:")
            print(f"  stdout: {e.stdout}")
            print(f"  stderr: {e.stderr}")
            return False
        except Exception as e:
            print(f"✗ Unexpected error: {e}")
            return False
    
    def verify_outputs(self):
        """Verify all output files exist"""
        self.print_step(5, "Verifying outputs")
        
        all_good = True
        
        # Check JSON
        if self.json_file.exists():
            size = self.json_file.stat().st_size
            print(f"✓ JSON Resume: {self.json_file} ({size:,} bytes)")
        else:
            print(f"✗ JSON Resume not found: {self.json_file}")
            all_good = False
        
        # Check PDF
        if self.pdf_file.exists():
            size = self.pdf_file.stat().st_size
            print(f"✓ PDF Resume: {self.pdf_file} ({size:,} bytes)")
        else:
            print(f"✗ PDF Resume not found: {self.pdf_file}")
            all_good = False
        
        return all_good
    
    def build(self):
        """Execute the complete build process"""
        self.print_header("Resume PDF Builder")
        print("Building resume from Markdown files...")
        
        # Step 1: Create build directory
        self.create_build_directory()
        
        # Step 2: Convert Markdown to JSON
        if not self.convert_markdown_to_json():
            print("\n✗ Build failed at JSON conversion step")
            return False
        
        # Step 3: Setup dependencies
        if not self.setup_dependencies():
            print("\n✗ Build failed at dependency setup step")
            return False
        
        # Step 4: Generate PDF
        if not self.generate_pdf():
            print("\n✗ Build failed at PDF generation step")
            return False
        
        # Step 5: Verify outputs
        if not self.verify_outputs():
            print("\n✗ Build completed with missing outputs")
            return False
        
        # Success!
        self.print_header("Build Completed Successfully! 🎉")
        print(f"\nYour resume is ready:")
        print(f"  📄 JSON: {self.json_file}")
        print(f"  📕 PDF:  {self.pdf_file}")
        print(f"\nTo rebuild, simply run: python build_resume.py")
        print("=" * 60 + "\n")
        
        return True


def main():
    """Main execution function"""
    builder = ResumeBuilder()
    success = builder.build()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()