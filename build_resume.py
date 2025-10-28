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
    
    
    
    def generate_pdf(self):
        """Generate PDF from JSON Resume"""
        self.print_step(4, "Generating PDF with Stack Overflow theme")
        
        try:
            # Use resume export command
            cmd = [
                "npx",
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
                check=False  # Don't throw on non-zero exit
            )
            
            # Always print output for debugging
            if result.stdout:
                print("--- stdout ---")
                print(result.stdout)
            if result.stderr:
                print("--- stderr ---")
                print(result.stderr)

            # Check for non-zero exit code first
            if result.returncode != 0:
                print(f"✗ PDF generation command failed with exit code {result.returncode}")
                return False

            # Verify PDF was created
            if not self.pdf_file.exists():
                print(f"✗ Command appeared to succeed, but PDF file was not created at: {self.pdf_file}")
                return False
            
            # Check file size
            file_size = self.pdf_file.stat().st_size
            print(f"✓ PDF generated successfully")
            print(f"  File: {self.pdf_file}")
            print(f"  Size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"✗ Error generating PDF:")
            print(f"✗ Error generating PDF.")
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