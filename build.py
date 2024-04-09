from datetime import date, timedelta
import logging
import pyodbc
import random
import sys

r""" Automated creation of arbitrarily large Iris certificate databases

Usage: 'python build.py <path>\<name>.mdb <number_of_records>'

Requires a database with ICD-11 tables called 'BidIdent' and 'BigMedCod'
Will delete all data in those tables each time it's run.

Uses a list of terms from an external document. A good starting point is
a dictionary, e.g. taking just the 'DiagnosisText' from
https://github.com/ONSdigital/icd11-ons-english-dictionary/blob/main/Dictionary.txt

Because the script selects at random from the list you provide, the certs
it creates will often be nonsensical because it doesn't understand the
due to sequence. So the cert could show 'brain cancer due to a cough'!
The purpose is to create large databases for load/performance testing
of Iris, not to create meaningful data.
"""


# Setup database connection
db_file = sys.argv[1]  # read database file from command-line argument, inc path
conn_str = r"DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};" r"DBQ={};".format(
    db_file
)
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()


# Clear existing data from tables we want to update
def cleanup():
    cursor.execute("DELETE FROM BigIdent")
    cursor.execute("DELETE FROM BigMedCod")
    conn.commit()


# Random date of birth from the last 100 years, limiting so that the person is an adult
def dob():
    start = date(year=date.today().year - 100, month=1, day=1)
    return str(start + timedelta(days=random.randint(0, 30_000)))


# Random date of death from the last year
def dod():
    return str(date.today() - timedelta(days=random.randint(1, 365)))


# Random sex
def set_sex():
    return str(random.randint(1, 2))


# Create a random combination of 1 to N terms from the list of possible conditions
def create_textline(terms: list, maximum: int):
    return ", ".join(random.sample(terms, random.randint(1, maximum)))


# Read a list of possible terms from a plain text file
def initialise_terms():
    with open("conditions.txt") as f:
        return list(f)


# Create the requested number of certificates, randomising the number of terms added,
# and whether each record has a line 1 and line 5
def update_database():
    start = 100_000
    end = start + int(sys.argv[2])
    terms = initialise_terms()
    sql_ident = "INSERT INTO BigIdent (CertificateKey, DateBirth, DateDeath, Sex) VALUES (?, ?, ?, ?)"
    sql_medcod = (
        "INSERT INTO BigMedCod (CertificateKey, LineNb, TextLine) VALUES (?, ?, ?)"
    )

    for id in range(start, end):
        cursor.execute(sql_ident, id, dob(), dod(), set_sex())

        cursor.execute(sql_medcod, id, 0, create_textline(terms, 2))

        if random.choice([True, False]):  # 50/50 chance of a line 1
            cursor.execute(sql_medcod, id, 1, create_textline(terms, 2))

        if random.choice([True, False]):  # 50/50 chance of a line 5
            cursor.execute(sql_medcod, id, 5, create_textline(terms, 2))


# Main function
def main():
    """Main function to run the script."""
    try:
        # Call update functions
        cleanup()
        update_database()

        # Commit changes and close connection
        conn.commit()
        conn.close()

        # Log success message
        logging.info("Database updated successfully.")
    except Exception as e:
        # Log error message and exit
        logging.error(f"An error occurred: {e}")
        sys.exit(1)


# Run main function
if __name__ == "__main__":
    main()
