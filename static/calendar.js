let clicked = null;
let corsi = [];

console.log(window.location.pathname)

const calendar = document.getElementById('calendar');
const dayModal = document.getElementById('dayModal');
const backDrop = document.getElementById('modalBackDrop');
const weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
const mesi = ['gen', 'feb', 'mar', 'apr', 'mag', 'giu', 'lug', 'ago', 'set', 'ott', 'nov', 'dic']
const url = window.location.pathname.split('/');
const month = getMese() -1;
const year = getAnno();

function openCoursePage(x){
    window.location.href = "http://127.0.0.1:5000/corso/"+x;
}

function openModal(date) {
    clicked = date;
    date = date.split('-')

    document.getElementById('eventText').innerHTML = '';
    document.getElementById('modalHeader').innerHTML = date[2].toString() + ' ' + mesi[date[1]-1] + ' '+ date[0];

    let eventsForDay = [];
    corsi.forEach(c => {
        if (c.Data === clicked)
            eventsForDay.push(c)
    });

    eventsForDay.forEach( c => {
        const infoCorso = document.createElement('div');
        infoCorso.addEventListener('click', () => openCoursePage(c.IDCorso))
        infoCorso.classList.add('courseInfo');
        infoCorso.innerHTML = c.Nome;
        document.getElementById('eventText').appendChild(infoCorso);
    });

    dayModal.style.display = 'block';

    backDrop.style.display = 'block';
}

function load() {
    const dt = new Date(year, month, (new Date().getDate()));

    const day = dt.getDate();

    console.log(month, year)

    //updateMonth(month, year);
    corsi = [];
    corsi = getCorsi();
    corsi.forEach(c => {
        if (c.Data[5] === '0'){c.Data = c.Data.slice(0,5) + c.Data.slice(6)}
    })

    console.log(corsi)

    const firstDayOfMonth = new Date(year, month, 1);
    const daysInMonth = new Date(year, month + 1, 0).getDate();

    const dateString = firstDayOfMonth.toLocaleDateString('en-us', {
        weekday: 'long',
        year: 'numeric',
        month: 'numeric',
        day: 'numeric',
    });
    const paddingDays = weekdays.indexOf(dateString.split(', ')[0]);

    document.getElementById('monthDisplay').innerText =
        `${dt.toLocaleDateString('it', { month: 'long' })} ${year}`;

    calendar.innerHTML = '';

    for(let i = 1; i <= paddingDays + daysInMonth; i++) {
        const daySquare = document.createElement('div');
        daySquare.classList.add('day');

        const dayString = `${year}-${month + 1}-${i - paddingDays}`;

        if (i > paddingDays) {
            daySquare.innerText = i - paddingDays;
            const eventForDay = corsi.find(e => e.Data == dayString);
            const nEventsForDay = corsi.filter(e => e.Data == dayString).length;

            if (i - paddingDays === day && month == (new Date().getMonth()) && year == (new Date().getFullYear())) {
                daySquare.id = 'currentDay';
            }

            if (eventForDay) {
                const eventDiv = document.createElement('div');
                eventDiv.classList.add('event');
                eventDiv.innerText = nEventsForDay;
                daySquare.appendChild(eventDiv);
            }

            daySquare.addEventListener('click', () => openModal(dayString));
        } else {
            daySquare.classList.add('padding');
        }

        calendar.appendChild(daySquare);
    }
}

function closeModal() {
    dayModal.style.display = 'none';
    backDrop.style.display = 'none';
    clicked = null;
    load();
}


function initButtons() {
    document.getElementById('nextButton').addEventListener('click', () => {
        nextDate();
    });

    document.getElementById('todayButton').addEventListener('click', () => {
        let dt = new Date()
        window.location.href = "http://127.0.0.1:5000/dashboard/"+dt.getFullYear()+"/"+(dt.getMonth()+1);
    });

    document.getElementById('backButton').addEventListener('click', () => {
        prevDate();
    });

    document.getElementById('closeButton').addEventListener('click', closeModal);
}


initButtons();
load();