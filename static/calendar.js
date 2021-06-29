let clicked = null;
let corsi = [];

const calendar = $('div #calendar');
const dayModal = $('#dayModal');
const backDrop = $('#modalBackDrop');
const weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
const mesi = ['gen', 'feb', 'mar', 'apr', 'mag', 'giu', 'lug', 'ago', 'set', 'ott', 'nov', 'dic']
const url = window.location.href.split('/');
const month = getMese() -1;
const year = getAnno();

function openCoursePage(x){
    window.location.href = "http://" + url[2] + "/corso/" + x;
}

function openPrenotazionePage(x){
    window.location.href = "http://" + url[2] + "/prenotazione/" + x;
}

function isPrenotato(corso){
    let out = true;
    corsi.forEach(p => {
        if (p.type === "prenotazione" && p.IDCorso === corso.IDCorso && p.Data === corso.Data){
            console.log("True")
            out =  false
        }
    })
    return out;
}

function openModal(date) {
    clicked = date;
    date = date.split('-')

    $('#eventText').empty();
    $('#modalHeader').html(date[2].toString() + ' ' + mesi[date[1]-1] + ' ' + date[0]);

    corsi.forEach(c => {
        if (c.Data === clicked)
            if (c.type == "corso"){
                if(isPrenotato(c)){
                    $('#eventText').append(jQuery('<div/>',{
                        "class": 'courseInfo'
                    }).html(c.Nome).on('click', () => openCoursePage(c.IDCorso)));
                }
            }
            else {
                $('#eventText').append(jQuery('<div/>',{
                    "class": 'prenotazioneInfo'
                }).html( () => {
                    let out = "Allenamento libero"
                    if (c.IDCorso != "None")
                        corsi.forEach(corso => {
                            if(corso.type === "corso" &&  corso.IDCorso === c.IDCorso)
                                out = corso.Nome;
                        })
                    return out
                } ).on('click', () => openPrenotazionePage(c.IDPrenotazione)));
            }

    });

    dayModal.show();
    backDrop.show();
}

function load() {
    const dt = new Date(year, month, (new Date().getDate()));
    const day = dt.getDate();
    const firstDayOfMonth = new Date(year, month, 1);
    const daysInMonth = new Date(year, month + 1, 0).getDate();
    const dateString = firstDayOfMonth.toLocaleDateString('en-us', {
        weekday: 'long',
        year: 'numeric',
        month: 'numeric',
        day: 'numeric',
    });
    const paddingDays = weekdays.indexOf(dateString.split(', ')[0]);

    corsi = getCorsi();
    corsi.forEach(c => {
        c.Data = c.Data.split('-')
        c.Data = c.Data[0] + '-' + parseInt(c.Data[1]) + '-' + parseInt(c.Data[2])
    })

    $('#monthDisplay').text(`${mesi[month]} ${year}`);

    calendar.empty();

    for(let i = 1; i <= paddingDays + daysInMonth; i++) {
        const daySquare = jQuery('<div/>',{
            "class": 'day'
        })
        const dayString = `${year}-${month + 1}-${i - paddingDays}`;

        if (i > paddingDays) {
            daySquare.on('click', () => openModal(dayString));
            daySquare.text(i - paddingDays);
            const eventsForDay = corsi.filter(e => e.Data == dayString).length;

            if (i - paddingDays === day && month == (new Date().getMonth()) && year == (new Date().getFullYear())) {
                daySquare.attr('id','currentDay');
            }
            if (eventsForDay > 0) {
                daySquare.append(jQuery("<div/>", {
                    "class": 'event',
                    "style": 'line-height:50%'
                }).text(eventsForDay))
            }
        } else {
            daySquare.addClass('padding');
        }

        calendar.append(daySquare);
    }
}

function closeModal() {
    dayModal.hide();
    backDrop.hide();
    clicked = null;
    load();
}

function initButtons() {
    $('#nextButton').on('click', () => { nextDate(); });

    $('#todayButton').on('click', () => { todayDate(); });

    $('#backButton').on('click', () => { prevDate(); });

    $('#closeButton').on('click', closeModal);

    $('#reloadButton').on('click', ()=>{ reloadDate(); })
}

initButtons();
load();