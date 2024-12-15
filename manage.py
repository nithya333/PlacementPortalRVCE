#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import psycopg2

def main():
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "placement.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)

def save_pdf():
    # Connect to the database
    conn = psycopg2.connect("dbname=marks user=postgres password=cse")
    cur = conn.cursor()

    # Read PDF file
    with open('example.pdf', 'rb') as f:
        pdf_data = f.read()

    # Insert PDF into the database
    cur.execute("INSERT INTO testmarks (dsa, resume) VALUES (%s, %s)", ('{1}', psycopg2.Binary(pdf_data)))

    conn.commit()
    cur.close()
    conn.close()

def fetch_pdf():
    conn = psycopg2.connect("dbname=marks user=postgres password=cse")
    cur = conn.cursor()
    cur.execute("SELECT dsa, resume FROM testmarks WHERE dsa = %s", '{1}')
    dsa, doc_content = cur.fetchone()
    print("Fetching")
    # Save to a file
    with open("example_write.pdf", 'wb') as f:
        f.write(doc_content)

    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    main()
    # save_pdf()
    # fetch_pdf()
