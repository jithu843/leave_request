
## Setup Instructions
### Prerequisites
- Python 3.9 or later
- SQLite
- Git

### Installation Steps
1. Clone the repository:
 
   git clone https://github.com/jithu843/leave_request.git
   cd leave_request


2. Create a virtual environment:

   python -m venv venv
   source venv/bin/activate  # For Linux/Mac
   venv\Scripts\activate  # For Windows
 

3. Install dependencies:
 
   pip install -r requirements.txt
  

4. Configure Database:
   - The project uses SQLite as the default database.
   - No additional configuration is required.
   - The database file will be automatically created as `test.db` in the project directory.


5. Start the application:
   
   uvicorn main:app --reload


The API will be available at: **http://localhost:8000**




