Here is the structure of current evaluation backend:
The backend server is deployed on an Azure VM.

project_postgeneation_root/
├── main.py                 # The main entry point to run the server and initialize endpoints
├── requirements.txt        # All dependencies required by the backend
├── config.py               # Configuration file for any global settings
├── app/                    # Directory for the server application 
│   ├── __init__.py         # Initializes app as a package
│   ├── routes.py           # Defines API endpoints
│   └── utils.py            # Utility functions for formatting, logging, etc.
├── checks/                 # Directory for different checks
│   ├── static_analysis/    # Static analysis checking
│   │   ├── __init__.py
│   │   ├── run_py_check.py          # Run Banddit, mypy, an pylint for Python
│   │   ├── run_clangtidy_check.py   # Run clang-tidy for C/C++
│   │   └── run_sonarqube_check.py   # Run SonarQube for other languages
│   ├── dynamic_analysis/   # Dynamic analysis checking
│   │   ├── __init__.py
│   │   └── run_valgrind_check.py    # Run Valgrind for memory checking
│   ├── formal_verification/ # Formal verification checking
│   │   ├── __init__.py
│   │   └── run_dafny_check.py       # Run Dafny for formal verification
│   └── rankme/             # Ranking mechanism based on embeddings
│       ├── __init__.py
│       └── rankme_computation.py    # Compute RankMe score based on embeddings
├── embeddings/             # Directory for handling LLM embeddings
│   ├── __init__.py
│   └── embedding_utils.py   # Helper functions for managing and extracting embeddings
├── feedback/               # Directory for feedback processing
│   ├── __init__.py
│   └── send_feedback.py     # Functions to format and send feedback back to LLMs
└── results/                # Directory to save combined results (JSON)
│   └── combined_results.json   # Final output file with all results
└── temp/                     # Temporary files directory
    └── code_files/           # Subdirectory for temporary code files
