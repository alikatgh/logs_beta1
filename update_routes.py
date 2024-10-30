import logging
import os
import re
from pathlib import Path
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("endpoint_updates.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# Define the mapping
endpoint_mapping = {
    "main.deliveries": "delivery.index",
    "main.manage_supermarkets": "supermarket.manage",
    "main.view_product": "product.manage_products",
    "main.edit_product": "product.edit_product",
    "main.delete_product": "product.delete_product",
    "main.create_return": "return.create",
    "main.view_reports": "report.generate_report",
    "main.returns": "return.index",
    # Add more mappings as needed
}

# Improved regex pattern to handle more cases
PATTERNS = [
    r"url_for\(['\"]main\.([\w_]+)['\"](?:[,\s]*[^)]*)??\)",  # Basic url_for with optional args
    r"redirect\(\s*url_for\(['\"]main\.([\w_]+)['\"](?:[,\s]*[^)]*)??\)\)",  # redirect(url_for(...))
    r"{%\s*url_for\s*['\"]main\.([\w_]+)['\"](?:[,\s]*[^)]*)??\s*%}",  # Jinja2 template syntax
]


class EndpointUpdater:
    def __init__(self, directory=None, dry_run=False):
        self.directory = Path(directory or Path(__file__).parent)
        self.dry_run = dry_run
        self.backup_dir = (
            self.directory / "backups" / datetime.now().strftime("%Y%m%d_%H%M%S")
        )
        self.file_extensions = {".py", ".html", ".js", ".css"}
        self.exclude_dirs = {
            ".git",
            "__pycache__",
            "venv",
            "env",
            "node_modules",
            "backups",
        }
        self.modified_files = []
        self.skipped_files = []
        self.patterns = [re.compile(pattern) for pattern in PATTERNS]

    def create_backup(self, filepath):
        """Create a backup of the file in a dated backup directory"""
        if self.dry_run:
            return

        relative_path = filepath.relative_to(self.directory)
        backup_path = self.backup_dir / relative_path
        backup_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(filepath, "rb") as src, open(backup_path, "wb") as dst:
                dst.write(src.read())
            logger.info(f"Created backup: {backup_path}")
        except Exception as e:
            logger.error(f"Failed to create backup for {filepath}: {str(e)}")
            raise

    def process_file(self, filepath):
        """Process a single file and return whether it was modified"""
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            original_content = content
            modified = False

            # Apply all patterns
            for pattern in self.patterns:
                matches = pattern.finditer(content)

                for match in matches:
                    old_endpoint = f"main.{match.group(1)}"
                    if old_endpoint in endpoint_mapping:
                        new_endpoint = endpoint_mapping[old_endpoint]
                        full_match = match.group(0)
                        new_text = full_match.replace(old_endpoint, new_endpoint)
                        content = content.replace(full_match, new_text)
                        modified = True
                        logger.debug(
                            f"Replacing {old_endpoint} with {new_endpoint} in {filepath}"
                        )

            if modified and not self.dry_run:
                self.create_backup(filepath)
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(content)
                logger.info(f"Updated {filepath}")
                return True
            elif modified:
                logger.info(f"Would update {filepath} (dry run)")
                return True

            return False

        except Exception as e:
            logger.error(f"Error processing {filepath}: {str(e)}")
            self.skipped_files.append(filepath)
            return False

    def run(self):
        """Run the endpoint updater"""
        logger.info(f"Starting endpoint updates in {self.directory}")
        logger.info("Dry run: %s", self.dry_run)

        for subdir, dirs, files in os.walk(self.directory, topdown=True):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]

            for file in files:
                filepath = Path(subdir) / file

                if filepath.suffix not in self.file_extensions:
                    continue

                try:
                    if self.process_file(filepath):
                        self.modified_files.append(filepath)
                except Exception as e:
                    logger.error(f"Unexpected error processing {filepath}: {str(e)}")
                    self.skipped_files.append(filepath)

        self._print_summary()

    def _print_summary(self):
        """Print a summary of the changes made"""
        logger.info("\nSummary:")
        logger.info(
            f"{'Would modify' if self.dry_run else 'Modified'} {len(self.modified_files)} files:"
        )
        for file in self.modified_files:
            logger.info(f"  - {file}")

        if self.skipped_files:
            logger.warning(f"\nSkipped {len(self.skipped_files)} files due to errors:")
            for file in self.skipped_files:
                logger.warning(f"  - {file}")


def main():
    # Ask about dry run
    dry_run_response = input("Perform a dry run first? (recommended) (y/N): ").lower()
    dry_run = dry_run_response in ["y", "yes"]

    if not dry_run:
        response = input(
            "This script will modify files in your project by replacing old endpoint references.\n"
            "It's highly recommended to back up your files or ensure they are under version control.\n"
            "Do you want to proceed? (yes/no): "
        ).lower()

        if response not in ["yes", "y"]:
            logger.info("Operation cancelled.")
            return

    updater = EndpointUpdater(dry_run=dry_run)
    updater.run()


if __name__ == "__main__":
    main()
