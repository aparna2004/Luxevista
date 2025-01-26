# Luxevista
A hotel reservation system implemented as a part of learning SDLC. 

## Planning and Requirement Analysis
#### Case study
A Five star hotel decided to open up its reservation system for online booking. 
- Consider the following requirements
- Hotel has multiple rooms classified into three types ((Deluxe, Super Deluxe and Suite)
- Room tariff is based on the room type, season and day of the week (Weekday Vs. Weekend)
- A room can be booked for a minimum of 1 night and maximum of 10 nights
- Multiple rooms can be booked by the same customer based on the number of guests accompanying
- Customers details will be maintained along with their preference for future reference and booking
- Advance payment (50%) is required to confirm a booking (can be paid thru payment gateway)
- Balance payment along with food and other service bill need to be paid at the time of check-out
- Cancellation of room (Partial days / full booking) is possible 3 days prior to check-in date. This should remove booking entries

## Design
<img width="3349" alt="ERD (1)" src="https://github.com/user-attachments/assets/6f586536-64b1-42ee-b9e4-c2607fc6ecd8" />
<img width="4913" alt="ERD (2)" src="https://github.com/user-attachments/assets/ceae72a9-1fcc-49ee-a16b-1feb8301e47e" />

## Coding 
#### Backend - Django
#### Frontend - HTML, CSS, JavaScript
## Installation
1. Clone the repository
```bash
git clone https://github.com/hajay180505/sistema-de-reserva-de-hote.git
```
2. Set up a virtual environment
```bash
python -m venv .venv
source .venv/bin/activate 
```
3. Install dependencies
```bash
pip install -r requirements.txt
```
4. Set up the database
```bash
python manage.py makemigrations
python manage.py migrate
```
5. Run the server
```bash
python manage.py runserver
```
6. View the application by visiting `http://127.0.0.1:8000/`

## Deployment
https://luxevista-d8da5d2dec40.herokuapp.com




