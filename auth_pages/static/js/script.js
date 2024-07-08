let timer = 60;

function startTimer() {
  let otpTimerElement = document.getElementById('otpTimer');
  let requestNewOTPBtnElement = document.getElementById('requestNewOTPBtn');

  otpTimerElement.textContent = `You can request OTP again in ${timer} seconds.`;

  let intervalId = setInterval(() => {
    timer--;
    otpTimerElement.textContent = `You can request OTP again in ${timer} seconds.`;

    if (timer <= 0) {
      clearInterval(intervalId);
      requestNewOTPBtnElement.style.display = 'block';
    }
  }, 1000);
}

startTimer();

function submitOTP() {
  const enteredOTP = document.getElementById("otpInput").value;
  // Check if OTP is valid (mock validation)
  if (enteredOTP === "123456") {
    alert("OTP verified successfully!");
    clearInterval(timer);
    countdown = 30;
    startTimer();
    document.getElementById("otpInput").value = "";
    document.getElementById("otpExpiredMsg").style.display = "none";
    document.getElementById("otpTimer").style.display = "block";
    document.getElementById("requestNewOTPBtn").style.display = "none";
  } else {
    alert("Invalid OTP. Please try again.");
  }
}

function requestNewOTP() {
  document.getElementById("requestNewOTPBtn").style.display = "none";
  countdown = 30;
  startTimer();
  document.getElementById("otpTimer").style.display = "block";
  document.getElementById("otpExpiredMsg").style.display = "none";
}

// Initial timer start
startTimer();
