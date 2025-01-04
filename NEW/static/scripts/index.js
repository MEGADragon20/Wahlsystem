function hexToRgba(hex, opacity) {
    // Entferne das # am Anfang des Hex-Werts
    hex = hex.replace('#', '');

    // Zerlege den Hex-Wert in die RGB-Komponenten
    let r = parseInt(hex.substring(0, 2), 16);
    let g = parseInt(hex.substring(2, 4), 16);
    let b = parseInt(hex.substring(4, 6), 16);

    // Gib den rgba-Wert mit der gewünschten Opazität zurück
    return `rgba(${r}, ${g}, ${b}, ${opacity})`;
}

// css zeug holen
const root = document.documentElement;
const loginButton = document.getElementById("loginbutton");
const signupButton = document.getElementById("signupbutton");
const box = document.querySelector(".box");
const body = document.querySelector("body")


// get colours
const loginColourHex = getComputedStyle(root).getPropertyValue('--logincolour');
const signupColourHex = getComputedStyle(root).getPropertyValue('--signupcolour');

// transform in rbga
const loginColour = hexToRgba(loginColourHex, 0.8);
const signupColour = hexToRgba(signupColourHex, 0.8);

// Hover-Effekte hinzufügen
loginButton.addEventListener("mouseenter", () => {
    box.style.boxShadow = `0 0px 20px ${loginColour}`; // Schatten hinzufügen
});

loginButton.addEventListener("mouseleave", () => {
    box.style.boxShadow = `0 0px 20px rgba(255, 255, 255, 0.8)`; // Schatten entfernen
});

loginButton.addEventListener("mouseenter", () => {
    body.style.boxShadow = `inset 0px 0px 10px ${loginColour}`;
});

loginButton.addEventListener("mouseleave", () => {
    body.style.boxShadow = `none`;
});

signupButton.addEventListener("mouseenter", () => {
    box.style.boxShadow = `0 0px 20px ${signupColour}`; // Schatten hinzufügen
});

signupButton.addEventListener("mouseleave", () => {
    box.style.boxShadow = `0 0px 20px rgba(255, 255, 255, 0.8)`; // Schatten entfernen
    console.log("daisteinauto")
});

signupButton.addEventListener("mouseenter", () => {
    body.style.boxShadow = `inset 0px 0px 10px ${signupColour}`;
});

signupButton.addEventListener("mouseleave", () => {
    body.style.boxShadow = `none`;
});
