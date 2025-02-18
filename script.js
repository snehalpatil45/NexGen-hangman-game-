function animateHangman() {
    fetch('/animate')
        .then(response => response.json())
        .then(data => {
            if (data.frame) {
                document.getElementById("hangman_display").innerText = data.frame;
                setTimeout(animateHangman, 500); // Smooth transition every 500ms
            }
        });
}

document.addEventListener("DOMContentLoaded", function () {
    animateHangman();
});


























