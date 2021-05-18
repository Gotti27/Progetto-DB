let nav = 0;
let delta = 0;
let clicked = null;
let events = localStorage.getItem('events') ? JSON.parse(localStorage.getItem('events')) : [];
let tempCourses = document.getElementById('courses');
let coursesList = tempCourses.innerText;
let corsi = [];
const patt = /\<.+?\>/g;

coursesList = coursesList.match(patt);

class Corso {
    constructor(s) {
        let arr = [];
        s = s.replace('<','').replace('>','');
        s = s.split(', ');
        s.forEach(i => {arr.push(i.split(/:(.+)/)[1])});
        this.id = arr[0];
        this.nome = arr[1]
        this.maxP = arr[2];
        this.idSala = arr[3];
        this.oraI = arr[4];
        this.oraF = arr[5];
        this.data = arr[6];
        this.idPacchetto = arr[7];
        this.descrizione = arr[8];
        this.idIstruttore = arr[9];

        if (this.data[5] === '0'){this.data = this.data.slice(0,5) + this.data.slice(6)}
    }
}

coursesList.forEach(i =>{
    corsi.push(new Corso(i))
})

console.log(corsi)

const calendar = document.getElementById('calendar');
const dayModal = document.getElementById('dayModal');
const backDrop = document.getElementById('modalBackDrop');
const weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
const mesi = ['gen', 'feb', 'mar', 'apr', 'mag', 'giu', 'lug', 'ago', 'set', 'ott', 'nov', 'dic']


function openCoursePage(x){
    console.log(x);
}

function openModal(date) {
    clicked = date;
    date = date.split('-')

    document.getElementById('eventText').innerHTML = '';
    document.getElementById('modalHeader').innerHTML = date[2].toString() + ' ' + mesi[date[1]-1] + ' '+ date[0];

    let eventsForDay = [];
    console.log(clicked)
    corsi.forEach(e => {
        if (e.data === clicked)
            eventsForDay.push(e)
    });
    eventsForDay.sort(function(a, b){return (parseFloat(a.oraI.slice(0,2)) + parseFloat(a.oraI.slice(3,5))/60.0 ) - (parseFloat(b.oraI.slice(0,2)) + parseFloat(b.oraI.slice(3,5))/60.0) })
    console.log(eventsForDay)

    eventsForDay.forEach( x => {
        const infoCorso = document.createElement('div');
        infoCorso.addEventListener('click', () => openCoursePage(x.id))
        infoCorso.classList.add('courseInfo');
        infoCorso.innerHTML = x.id;
        document.getElementById('eventText').appendChild(infoCorso);
    });

    dayModal.style.display = 'block';

    backDrop.style.display = 'block';
}

function load() {
    const dt = new Date();

    if (nav !== 0) {
        dt.setMonth(new Date().getMonth() + nav);
    }

    const day = dt.getDate();
    const month = dt.getMonth();
    const year = dt.getFullYear();

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
    tempCourses.innerHTML = '';

    for(let i = 1; i <= paddingDays + daysInMonth; i++) {
        const daySquare = document.createElement('div');
        daySquare.classList.add('day');

        const dayString = `${year}-${month + 1}-${i - paddingDays}`;

        if (i > paddingDays) {
            daySquare.innerText = i - paddingDays;
            const eventForDay = corsi.find(e => e.data == dayString);
            const nEventsForDay = corsi.filter(e => e.data == dayString).length;

            if (i - paddingDays === day && nav === 0) {
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
        nav++;
        delta--;
        load();
    });

    document.getElementById('todayButton').addEventListener('click', () => {
        nav += delta;
        delta = 0
        load();
    });

    document.getElementById('backButton').addEventListener('click', () => {
        nav--;
        delta++;
        load();
    });

    document.getElementById('closeButton').addEventListener('click', closeModal);
}

initButtons();
load();