<<<<<<< HEAD
let countdown = 30;
const countdownDisplay = document.getElementById('countdown');
const resendBtn = document.getElementById('resendBtn');
const form = document.querySelector('form');

function updateCountdown() {
    countdownDisplay.textContent = countdown;
    if (countdown > 0) {
        countdown--;
        resendBtn.disabled = true;
        setTimeout(updateCountdown, 1000);
    } else {
        resendBtn.disabled = false;
        countdownDisplay.style.color = '#dc3545';
    }
}

function resendOTP() {
    if (countdown === 0) {
        fetch(window.location.href, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: 'resend_otp=true'
        }).then(() => {
            window.location.reload();
        });
    }
}

=======
let countdown = 30;
const countdownDisplay = document.getElementById('countdown');
const resendBtn = document.getElementById('resendBtn');
const form = document.querySelector('form');

function updateCountdown() {
    countdownDisplay.textContent = countdown;
    if (countdown > 0) {
        countdown--;
        resendBtn.disabled = true;
        setTimeout(updateCountdown, 1000);
    } else {
        resendBtn.disabled = false;
        countdownDisplay.style.color = '#dc3545';
    }
}

function resendOTP() {
    if (countdown === 0) {
        fetch(window.location.href, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: 'resend_otp=true'
        }).then(() => {
            window.location.reload();
        });
    }
}

>>>>>>> d9514b76b8bb3845c664cb087a3c05eee1a58c18
updateCountdown();