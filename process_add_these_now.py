import os
import shutil
import datetime
import re
import logging
import sqlite3
import subprocess

DATABASE_PATH = "/home/herb/Desktop/AIDEV-Hub/Databases/Project/ChangeArchive.db"
CODEBASE_SUMMARY_SCRIPT = "Scripts/CodebaseSummary.sh"
LOG_FILE_NAME = "process_add_these_now_{}.txt".format(datetime.datetime.now().strftime("%Y%m%d%H%M%S"))

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler(LOG_FILE_NAME), logging.StreamHandler()])

def create_database():
    """Creates the SQLite database and the log table if they don't exist."""
    conn = None
    try:
        os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                level TEXT,
                message TEXT,
                program TEXT,
                directory TEXT,
                log_date DATETIME
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_logs_program ON logs (program)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_logs_directory ON logs (directory)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_logs_log_date ON logs (log_date)")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS summary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                files_processed INTEGER,
                files_with_path INTEGER,
                files_archived INTEGER,
                files_copied INTEGER,
                database_status TEXT
            )
        """)
        conn.commit()
        logging.info("Database and table created successfully.")
    except sqlite3.Error as e:
        logging.exception(f"Database error: {e}")
    finally:
        if conn:
            conn.close()

def check_and_create_database():
    """Checks if the database exists, and creates it if it doesn't."""
    conn = None
    try:
        if not os.path.exists(DATABASE_PATH):
            logging.info("Database not found. Creating database...")
            create_database()
        else:
            logging.info("Database found.")
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
    finally:
        if conn:
            conn.close()

class DatabaseHandler(logging.Handler):
    """
    Custom logging handler to store logs in an SQLite database.
    """
    def __init__(self):
        logging.Handler.__init__(self)
        check_and_create_database()
        self.current_program = None
        self.current_directory = None

    def emit(self, record):
        """
        Emits a log record to the SQLite database.
        """
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO logs (level, message, program, directory, log_date)
                VALUES (?, ?, ?, ?, ?)
            """, (record.levelname, record.getMessage(), self.current_program, self.current_directory, datetime.datetime.now()))
            conn.commit()
        except sqlite3.Error as e:
            logging.exception(f"Database error: {e}")
        finally:
            if conn:
                conn.close()

def run_codebase_summary():
    """Runs the CodebaseSummary.sh script."""
    try:
        subprocess.run([CODEBASE_SUMMARY_SCRIPT], check=True, capture_output=True, text=True, cwd="/home/herb/Desktop/AIDEV-Hub")
        logging.info("Codebase summary script executed successfully.")
    except subprocess.CalledProcessError as e:
        logging.error("Error running codebase summary script")

def process_files(source_dir):
    """
    Reads all files in the source directory, extracts the 'Path:' from the header of Python files,
    copies the files to the destination directory, and handles existing files by renaming them
    and moving them to the archive directory.
    """
    db_status = "Unknown"
    num_files_processed = 0
    num_files_with_path = 0
    num_files_archived = 0
    num_files_copied = 0

    # Check and create database
    check_and_create_database()

    # Configure logging to write to the database and file
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    # Create handlers
    fh = logging.FileHandler(LOG_FILE_NAME)
    sh = logging.StreamHandler()

    # Set level and formatter
    fh.setLevel(logging.INFO)
    sh.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    sh.setFormatter(formatter)

    # Add handlers to logger
    logger.addHandler(fh)
    logger.addHandler(sh)

    db_handler = DatabaseHandler()
    logger.addHandler(db_handler)

    try:
        for filename in os.listdir(source_dir):
            source_path = os.path.join(source_dir, filename)
            db_handler.current_program = filename
            db_handler.current_directory = source_dir

            # Check if it's a file
            if os.path.isfile(source_path):
                # Check if it's a Python file
                if filename.endswith(".py"):
                    try:
                        with open(source_path, 'r') as file:
                            header = ""
                            for i in range(5):  # Read the first 5 lines
                                header += file.readline()
                            match = re.search(r"Path:\s*(.+)", header)

                            if match:
                                num_files_with_path += 1
                                dest_dir = match.group(1).strip()
                                dest_filename = filename
                                dest_path = os.path.join(dest_dir, dest_filename)

                                # Check if the destination directory exists, create if it doesn't
                                os.makedirs(dest_dir, exist_ok=True)

                                # Check if the file already exists in the destination directory
                                if os.path.exists(dest_path):
                                    # Run CodebaseSummary.sh before archiving
                                    run_codebase_summary()

                                    # Rename the existing file with a timestamp
                                    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                                    archive_filename = f"{os.path.splitext(dest_filename)[0]}_{timestamp}{os.path.splitext(dest_filename)[1]}"
                                archive_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(source_dir))), "..Exclude", "ProjectArchive")
                                os.makedirs(archive_dir, exist_ok=True)
                                archive_path = os.path.join(archive_dir, archive_filename)
                                shutil.move(dest_path, archive_path)
                                logging.info(f"File already exists: {dest_path}. Moved to {archive_path}")
                                num_files_archived += 1

                            # Copy the file to the destination directory
                            shutil.copy2(source_path, dest_path)  # Use copy2 to preserve metadata
                            logging.info(f"Copied {source_path} to {dest_path}")
                            num_files_copied += 1
                        else:
                            logging.warning(f"No 'Path:' found in header of {source_path}")

                        num_files_processed += 1

                    except Exception as e:
                        logging.exception(f"Error processing {source_path}")

    except Exception as e:
        logging.exception(f"General error in process_files: {e}")
        db_status = "Error"

    # Test the database
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM logs")
        count = cursor.fetchone()[0]
        logging.info(f"Database contains {count} log entries.")
        if count >= num_files_processed and num_files_processed > 0:
            logging.info("Database updated successfully with new data.")
            db_status = "Success"
        else:
            logging.warning("Database may not have been updated with new data.")
            db_status = "Failed"

        # Insert summary data
        try:
            cursor.execute("""
                INSERT INTO summary (files_processed, files_with_path, files_archived, files_copied, database_status)
                VALUES (?, ?, ?, ?, ?)
            """, (num_files_processed, num_files_with_path, num_files_archived, num_files_copied, db_status))
            conn.commit()
        except sqlite3.Error as e:
            logging.exception(f"Database error during test: {e}")
        finally:
            if conn:
                conn.close()

    except sqlite3.Error as e:
        logging.exception(f"Database connection error: {e}")
        db_status = "Error"

    logging.info("---- Summary ----")
    logging.info(f"Files processed: {num_files_processed}")
    logging.info(f"Files with Path: {num_files_with_path}")
    logging.info(f"Files archived: {num_files_archived}")
    logging.info(f"Files copied: {num_files_copied}")
    logging.info(f"Database status: {db_status}")

if __name__ == "__main__":
    # Ensure database exists before running process_files
    source_directory = "AddTheseNow"
    process_files(source_directory)
