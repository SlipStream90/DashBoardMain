let timer;
let countdown = 30; // seconds
const expirationTime = 60; // 1 minute in seconds

function startTimer() {
  timer = setInterval(updateTimer, 1000);
}

function updateTimer() {
  if (countdown > 0) {
    document.getElementById(
      "otpTimer"
    ).textContent = `You can request OTP again in ${countdown} seconds.`;
    countdown--;
  } else {
    clearInterval(timer);
    document.getElementById("otpTimer").style.display = "none";
    document.getElementById("otpExpiredMsg").style.display = "block";
    document.getElementById("requestNewOTPBtn").style.display = "block";
  }
}

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
