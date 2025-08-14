# NextSteps College Research Website

A modern, user-friendly web application for exploring and recommending colleges based on your academic, financial, and personal preferences. Built with Flask, SQLAlchemy, and a responsive frontend.

## Features

- College recommendation engine using real Scorecard data
- Filter by state, cost, SAT/ACT/GPA, diversity, urbanicity, prestige, and more
- Adjustable weight sliders for personalized recommendations
- College detail pages with rich information
- Save colleges to custom lists
- Modern, responsive UI with tooltips and help icons
- Secure user authentication

## Getting Started

### Prerequisites
- Python 3.10+
- PostgreSQL (or compatible database)
- Node.js (optional, for frontend tooling)

### Installation
1. Clone the repository:
	```bash
	git clone https://github.com/dhu27/NextSteps-College-Research-Website.git
	cd NextSteps-College-Research-Website
	```
2. Create and activate a virtual environment:
	```bash
	python3 -m venv venv
	source venv/bin/activate
	```
3. Install Python dependencies:
	```bash
	pip install -r requirements.txt
	```
4. Set up your database (PostgreSQL recommended):
	- Create a database and update `config.py` with your credentials.
	- Run migrations:
	  ```bash
	  flask db upgrade
	  ```
	- Load college data into the database (see `scripts/load.py`).

5. Run the development server:
	```bash
	flask run
	```

### Frontend Assets
- Static files are in `app/static/`
- Templates are in `app/templates/`

## Usage
- Register and log in to save colleges to lists.
- Use the recommendations form to find colleges matching your preferences.
- Explore college details and add to your lists.

## Project Structure
```
app/
  routes/         # Flask route handlers
  models.py       # SQLAlchemy models
  db.py           # Database setup
  ml/             # Recommendation engine
  static/         # CSS, JS, images
  templates/      # Jinja2 HTML templates
config.py         # App configuration
run.py            # App entry point
requirements.txt  # Python dependencies
migrations/       # Alembic migrations
scripts/          # Data loading scripts
```

## Contributing
Pull requests are welcome! Please open an issue to discuss major changes first.

## License
MIT License

## Acknowledgments
- U.S. Department of Education College Scorecard
- Flask, SQLAlchemy, Bootstrap, and other open-source libraries