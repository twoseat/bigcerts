Automated creation of arbitrarily large Iris certificate databases

Usage: `python build.py <path>\<name>.mdb <number_of_records`

Example: `python build.py D:\dev\big.mdb 200000`

Requires a database with ICD-11 tables called 'BidIdent' and 'BigMedCod'. It will delete all data in those tables each time it's run.

Uses a list of terms from an external document. A good starting point is a dictionary, e.g. taking just the 'DiagnosisText' from https://github.com/ONSdigital/icd11-ons-english-dictionary/blob/main/Dictionary.txt. A sample file is included to get you started.

Because the script selects at random from the list you provide, the certs it creates will often be nonsensical because it doesn't understand the due to sequence. So the cert could show 'brain cancer due to a cough'! The purpose is to create large databases for load/performance testing of Iris, not to create meaningful data.

On a modest laptop the script generates around 100,000 records per minute.