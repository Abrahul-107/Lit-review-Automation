const newButton = document.querySelector('.new-button button');
const newOptions = document.querySelector('.new-options');
const pricingButton = document.querySelector('.pricing-button');
const pricingOptions = document.querySelector('.pricing-options');


newButton.addEventListener('click', () => {
    newOptions.classList.toggle('show');
});


pricingButton.addEventListener('click', () => {
    pricingOptions.classList.toggle('show');
});


document.addEventListener('click', (event) => {
    if (!newButton.contains(event.target) && !newOptions.contains(event.target)) {
        newOptions.classList.remove('show');
    }
});


document.addEventListener('click', (event) => {
    if (!pricingButton.contains(event.target) && !pricingOptions.contains(event.target)) {
        pricingOptions.classList.remove('show');
    }
});