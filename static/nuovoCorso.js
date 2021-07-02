const salaSelect = $('#sala');
const maxPInput = $('#maxPersone');
const errMessage = $('#errMessage');

let maxPersone = 0;

salaSelect.change(()=>{
    let oldMax = maxPersone;
    maxPersone = parseInt(salaSelect.val().split(',')[1]);
    if (oldMax > maxPersone && maxPInput.val() && maxPInput.val() > maxPersone){
        maxPInput.val(maxPersone)
    }
    errMessage.empty()
})

maxPInput.click(()=>{
    maxPInput.attr("max", getMaxPersone())
})

function getMaxPersone() {
    if (salaSelect.val()) {
        return maxPersone
    }
    else{
        errMessage.text("Seleziona prima una sala");
        return 0;
    }
}




